"""Single calculation owner for the PDF and its auditable Excel snapshot."""
from collections import Counter
from datetime import datetime, timezone
from html import escape
import hashlib
import json
from pathlib import Path
import re
from openpyxl import load_workbook

VERSION = 'report-2.0'
STATUSES = {'SOURCE','DERIVED','RAG_RETRIEVED','RAG_INFERRED','HUMAN_VALIDATED','MISSING','TO_VALIDATE'}
ACTIVE = {'Production','Pilote'}
DECISIONS = [
    ('Garder', '#2AD1A0', 'Usage à maintenir, selon la décision déclarée.'),
    ('Arrêter', '#FF7477', 'Arrêt à examiner ; économies à confirmer.'),
    ('Mutualiser', '#20D3E8', 'Recouvrements à examiner avant consolidation.'),
    ('Automatiser', '#8584FF', 'Potentiel à instruire avant industrialisation.'),
    ('Augmenter', '#ED6EC0', 'Accompagner les compétences et les usages.'),
    ('Protéger', '#FFC432', 'Traiter les risques et les dépendances.'),
]


def read_table(wb, sheet):
    values = list(wb[sheet].values)
    return [dict(zip(values[0], r)) for r in values[1:] if any(v is not None for v in r)]


def unpack(value, default):
    if value in (None, ''):
        return default
    return json.loads(value) if isinstance(value, str) else value


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def fmt(value, decimals=0):
    return f'{value:,.{decimals}f}'.replace(',', ' ').replace('.', ',') if number(value) else 'Unknown'


def slug(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()[:10]


def build_model(workbook, dataset=None, reference=None):
    workbook = Path(workbook).resolve()
    wb = load_workbook(workbook, data_only=True, read_only=True)
    atlas = read_table(wb, 'Atlas')
    evidence = read_table(wb, 'Preuves')
    questions = read_table(wb, 'Questions')
    claims = read_table(wb, 'Interpretations')
    wb.close()
    scopes = sorted({r['dataset'] for r in atlas if r['record_type']=='usage'})
    if dataset is None:
        if len(scopes)!=1:
            raise ValueError('Choose --dataset when the Atlas has multiple usage scopes.')
        dataset = scopes[0]
    usages = [r for r in atlas if r['record_type']=='usage' and r['dataset']==dataset]
    if not usages:
        raise ValueError(f'No usages for dataset {dataset}')
    if len({r['record_id'] for r in atlas})!=len(atlas):
        raise ValueError('Duplicate Atlas record IDs')
    for r in atlas:
        r['evidence_ids'] = unpack(r.get('evidence_ids'), {})
        r['human_validations'] = unpack(r.get('human_validations'), {})
        r['organization_id'] = None  # Never derive an identity from an unconfirmed name.
        r['activity_id'] = None if r.get('activity') in (None,'Unknown') else r['activity']
        r['usage_id'] = r['record_id'] if r['record_type']=='usage' else None
        r['analysis_id'] = r.get('rag3')
        r['data_status'] = 'SOURCE'
        r['validation_status'] = 'HUMAN_VALIDATED' if r.get('rag2')=='Human confirmed' else 'TO_VALIDATE'
    selected = {r['record_id'] for r in usages}
    active = [r for r in usages if r['status'] in ACTIVE]
    scoped_claims = [r for r in claims if r['record_id'] in selected]
    for c in claims:
        c['evidence_ids'] = unpack(c.get('evidence_ids'), [])
        c['validation_ids'] = unpack(c.get('validation_ids'), [])
        c['data_status'] = 'RAG_INFERRED' if c.get('origin')=='rag_inference' else 'DERIVED'
        c['validation_status'] = 'TO_VALIDATE'
    for q in questions:
        q['evidence_ids'] = unpack(q.get('evidence_ids'), [])
        q['data_status'] = 'HUMAN_VALIDATED' if q['status']=='Human confirmed' else 'TO_VALIDATE'
    for row_num,q in enumerate(questions,2):
        if q['data_status']=='HUMAN_VALIDATED':
            evidence.append(dict(evidence_id=f"human:{q['question_id']}",record_id=q['record_id'],field=q['field'],
                value=q['answer'],origin='human_validation',file=str(workbook),locator=f'Questions!F{row_num}:I{row_num}',
                sha256=hashlib.sha256(workbook.read_bytes()).hexdigest(),reviewer=q.get('reviewer'),timestamp=q.get('timestamp'),
                supporting_reference=q.get('answer_evidence')))
    eid = {e['evidence_id']:e for e in evidence}
    for e in evidence:
        e['data_status'] = 'HUMAN_VALIDATED' if e.get('origin')=='human_validation' else ('RAG_RETRIEVED' if e.get('origin')=='retrieval' else ('MISSING' if e.get('value') is None else 'SOURCE'))
    reference = Path(reference).resolve() if reference else None
    for page in range(1,33):
        e = dict(evidence_id=f'report-reference:{page}',record_id='report-reference',field='layout_and_vocabulary',
                 value='Reference layout and report vocabulary, not business KPI values',origin='source',
                 file=str(reference) if reference else None,locator=f'page {page}',
                 sha256=hashlib.sha256(reference.read_bytes()).hexdigest() if reference and reference.exists() else None,data_status='SOURCE')
        evidence.append(e);eid[e['evidence_id']]=e

    def refs(records, fields):
        result={r['evidence_ids'][f] for r in records for f in fields if f in r['evidence_ids']}
        result.update(f"human:{r['record_id']}:{f}" for r in records for f in fields if f in r['human_validations'])
        return sorted(result)
    # The upstream evidence keys use original Excel column names.
    metrics = {}
    def metric(mid, name, value, unit, records, fields, method, status=None, extra=()):
        metrics[mid] = dict(metric_id=mid,metric_name=name,metric_value=value,metric_unit=unit,
            calculation_method=method,source_table='08_FLOW_ATLAS',source_filter=f'dataset={dataset}; {method}',
            source_record_ids=[r['record_id'] for r in records],evidence_ids=sorted(set(refs(records,fields)+list(extra))),
            data_status=status or ('DERIVED' if value is not None else 'MISSING'),confidence_score=None,
            validation_status='TO_VALIDATE',page_used=[],visual_used=[])
        return metrics[mid]
    def total(records, field):
        return sum(r[field] for r in records) if all(number(r.get(field)) for r in records) else None
    metric('usage_count','Usages recensés',len(usages),'count',usages,['id'],'COUNT DISTINCT usage_id')
    metric('active_count','Usages actifs',len(active),'count',usages,['id','statut'],'COUNT statut IN (Production,Pilote)')
    metric('active_cost','Coût annuel actif',total(active,'annual_cost_ke'),'kEUR/an',active,['statut','cout_annuel_ke'],'SUM annual_cost_ke for active usages; missing cost => null')
    stops = [r for r in active if r['source_decision']=='Arrêter']
    metric('stop_cost','Coût étiqueté Arrêter',total(stops,'annual_cost_ke'),'kEUR/an',active,['statut','decision','cout_annuel_ke'],'SUM active cost where source decision=Arrêter; not savings')
    score = sum(r['value_score']*r['adoption_score'] for r in active)/(25*len(active))*100 if active and all(number(r.get('value_score')) and number(r.get('adoption_score')) for r in active) else None
    metric('portfolio_score','Valeur du portefeuille',score,'/100',active,['statut','valeur','usage'],'SUM(value_score * adoption_score) / (25 * active_count) * 100',extra=['rule:M6 Indices:8'])
    for mid,name,reason in [
        ('coverage','Couverture stratégique','Capabilities, criticalities and usage links unavailable'),
        ('skills','Cohérence compétences','Critical skill inventory and levels unavailable'),
        ('integration','Intégration au SI','System relationship IDs unavailable; environment label is not a mapping'),
        ('alignment','Indice global','Three required sub-scores missing'),
        ('systems','Systèmes & ERP','System inventory unavailable'),
        ('capabilities','Architecture métier','Capability inventory unavailable'),
        ('skill_count','Compétences','Scoped skill inventory unavailable'),
        ('fragile_skills','Compétences critiques fragiles','Critical skill levels and dependencies unavailable'),
        ('consumption','Consommation seule','Cost breakdown unavailable'),
        ('savings','Économies confirmées','No validated savings evidence'),
        ('financial_return','Rendement financier','No measured annual financial value')]:
        metric(mid,name,None,'Unknown',usages,[],reason,'MISSING')
    hors = [r for r in active if r['environment']=='Hors SI']
    metric('outside_si','Hors SI déclarées',len(hors),'count',active,['environnement','statut'],'COUNT active environment=Hors SI; does not prove shadow AI')
    owners = [r for r in active if r['owner'] in (None,'','Unknown')]
    metric('missing_owners','Sans propriétaire documenté',len(owners),'count',active,['owner','statut'],'COUNT missing effective owner among active usages')
    for sev,mid in [(None,'issue_count'),(3,'critical'),(2,'important')]:
        found = [c for c in scoped_claims if sev is None or c['severity']==sev]
        metric(mid,'Écarts détectés' if sev is None else f'Écarts de sévérité {sev}',len(found),'count',usages,['statut','owner','valeur','usage','cout_annuel_ke'],
               f'COUNT implemented rule outputs with severity={sev}; E7/E13/E21 only',extra=['rule:M7 Écarts:11','rule:M7 Écarts:17','rule:M7 Écarts:25']+[x for c in found for x in c['evidence_ids']])
    decision_categories = [d[0] for d in DECISIONS] + sorted({r['source_decision'] or 'Unknown' for r in usages}-{d[0] for d in DECISIONS})
    for category in decision_categories:
        rows=[r for r in usages if (r['source_decision'] or 'Unknown')==category]
        metric(f'decision_{slug(category)}',category,len(rows),'count',usages,['id','decision'],f'COUNT DISTINCT usage_id where source_decision={category}')
    domains=sorted({r['function'] or 'Unknown' for r in active})
    for domain in domains:
        rows=[r for r in active if (r['function'] or 'Unknown')==domain]
        metric(f'domain_{slug(domain)}',domain,total(rows,'annual_cost_ke'),'kEUR/an',rows,['statut','domaine','cout_annuel_ke'],f'SUM active annual_cost_ke where domain={domain}')
    for risk in sorted({r['risk'] or 'Unknown' for r in active}):
        rows=[r for r in active if (r['risk'] or 'Unknown')==risk]
        metric(f'risk_{slug(risk)}',risk,len(rows),'count',active,['statut','risque'],f'COUNT active usages where declared risk={risk}')

    pages={str(p):[] for p in range(1,33)}
    def element(page,key,kind,label='',value=None,unit='',display='',detail='',group='',mids=(),records=(),ev=(),status=None,**extra):
        mids=list(mids); related=[metrics[m] for m in mids]
        record_ids=sorted(set(records)|{x for m in related for x in m['source_record_ids']})
        evidence_ids=sorted(set(ev)|{x for m in related for x in m['evidence_ids']})
        if not related and not record_ids and not evidence_ids:
            evidence_ids=[f'report-reference:{page}']
        row=dict(element_id=f'P{page}_{key}',kind=kind,label=label,value=value,unit=unit,display_text=display,
                 detail=detail,group=group,order=len(pages[str(page)]),data_status=status or ('MISSING' if related and all(m['data_status']=='MISSING' for m in related) else ('DERIVED' if related else 'SOURCE')),
                 validation_status='TO_VALIDATE' if related or record_ids else 'Not applicable',confidence_score=None,
                 metric_ids=mids,source_record_ids=record_ids,evidence_ids=evidence_ids,**extra)
        pages[str(page)].append(row)
        for m in related:
            m['page_used']=sorted(set(m['page_used']+[page]));m['visual_used'].append(row['element_id'])
        return row
    def kpi(p,key,mid,label=None,detail=''):
        m=metrics[mid]; return element(p,key,'kpi',label or m['metric_name'],m['metric_value'],m['metric_unit'],'N/D' if m['metric_value'] is None else fmt(m['metric_value']),detail,mids=[mid])
    def header(p,eyebrow,title,subtitle,mids=()):
        element(p,'HEADER','header',title,display=title,detail=subtitle,eyebrow=eyebrow,mids=mids)
        element(p,'FOOTER','footer',display='Flow Atlas - Rapport du portefeuille',detail=str(p))
    names=sorted({r['organization'] for r in usages if r['organization'] not in (None,'','Unknown')})
    scope = names[0] if len(names)==1 else f'{dataset} à confirmer'
    def v(mid):return metrics[mid]['metric_value']
    # Architecture metadata comes from reference page 3, not business data.
    groups=[('PILOTER',[('Cockpit','alignment'),('Vue Dirigeant',None),('Vue DSI · Contrôle',None),('Écarts détectés (MVP)','issue_count'),('Aide à la décision',None),('Plan de réalignement',None)]),
            ('CAPITAL COGNITIF',[('Capital IA','usage_count'),('Hors SI déclarées','outside_si'),('Systèmes & ERP','systems'),('Architecture métier','capabilities'),('Compétences','skill_count')]),
            ('ADMINISTRATION',[('Données & import',None)])]
    header(3,'A R C H I T E C T U R E',f'{sum(len(g[1]) for g in groups)} écrans en trois familles',f'Périmètre : {scope}. Compteurs issus du jeu de données ; référentiels absents indiqués N/D.')
    for gi,(group,items) in enumerate(groups):
        element(3,f'GROUP_{gi+1}','group',group,group=group)
        for i,(label,mid) in enumerate(items):
            element(3,f'NAV_{gi+1}_{i+1}','navigation',label,value=v(mid) if mid else None,display=('N/D' if v(mid) is None else fmt(v(mid))) if mid else '',group=group,mids=[mid] if mid else [])
    element(3,'NOTE','note',display='Données locales traçables dans le classeur du rapport. Les profils EDA restent séparés du portefeuille analysé. Les compteurs ne décrivent pas une application connectée en temps réel.')
    header(4,'L E  L A N G A G E  C O M M U N','Six décisions pour tout le portefeuille','Étiquettes du fichier source ; arbitrages à valider. Tous les usages recensés sont inclus.')
    for i,(name,color,description) in enumerate(DECISIONS,1):
        element(4,f'DEF_{i}','definition',name,display=description,color=color)
    dm=[f'decision_{slug(d)}' for d in decision_categories]
    element(4,'CHART_01','chart','Répartition des décisions déclarées',detail=scope,mids=dm)
    for category,mid in zip(decision_categories,dm):
        color=next((d[1] for d in DECISIONS if d[0]==category),'#9BAEC9')
        element(4,f'CHART_01_{slug(category)}','bar',category,v(mid),'count',fmt(v(mid)),group='P4_CHART_01',mids=[mid],color=color)
    ranked=sorted(scoped_claims,key=lambda c:(-c['severity'],-(c['cost_ke'] or 0),c['interpretation_id']))
    byid={r['record_id']:r for r in atlas}
    header(5,'É C R A N  ·  C O C K P I T',"L'alignement en un coup d'œil",'Un indice global, quatre sous-scores et les écarts détectés par les règles MVP.')
    kpi(5,'KPI_01','alignment','Indice d’alignement','IA × compétences × systèmes × valeur')
    for i,mid in enumerate(['coverage','skills','integration','portfolio_score'],2):
        kpi(5,f'KPI_{i:02}',mid,detail='Référentiel absent' if v(mid) is None else 'Valeur × usage déclaratifs')
    element(5,'KPI_06','kpi','IA actives / recensées',display=f"{fmt(v('active_count'))} / {fmt(v('usage_count'))}",mids=['active_count','usage_count'])
    kpi(5,'KPI_07','active_cost','Coût annuel actif (kEUR)')
    kpi(5,'KPI_08','critical','Écarts critiques','Règles MVP uniquement')
    kpi(5,'KPI_09','important','Écarts importants','Règles MVP uniquement')
    element(5,'PRIORITIES','label','Écarts prioritaires',detail='Sévérité puis coût ; à valider')
    for i,c in enumerate(ranked[:5],1):
        element(5,f'INSIGHT_{i:02}','insight',c['conclusion'],display=byid[c['record_id']]['ai_usage'],detail=f"{c['rule']} · {'IMPORTANT' if c['severity']==2 else 'À EXAMINER'}",records=[c['record_id']],ev=c['evidence_ids']+[byid[c['record_id']]['evidence_ids']['nom']],status=c['data_status'],analysis_id=c['interpretation_id'],severity=c['severity'],rule_title={'E7':'Coût et valeur à examiner','E13':'Propriétaire absent','E21':'Valeur non adoptée'}.get(c['rule'],c['rule']))
    picks=[];seen=set()
    for c in ranked:
        if c['record_id'] not in seen:picks.append(c);seen.add(c['record_id'])
        if len(picks)==3:break
    # Page-six display strings intentionally preserve the existing renderer.
    profile_scopes=sorted({r['dataset'].upper() for r in atlas if r['record_type']=='profile' and r['dataset']!=dataset})
    profile_note=f"Profils {', '.join(profile_scopes)} traités séparément." if profile_scopes else 'Liens profil-activité à valider.'
    header(6,'FLOW ATLAS  /  VUE DIRIGEANT','La lecture stratégique, sans jargon',f"Périmètre {scope} : {fmt(v('usage_count'))} usages, {fmt(v('active_count'))} actifs. {profile_note}",mids=['usage_count','active_count'])
    pages['6'][-1]['display_text']='Flow Atlas MVP - Sources : flow_atlas.xlsx / Synthese, Atlas, Interpretations, Preuves'
    pages['6'][-1]['detail']='Vue page 6'
    element(6,'KPI_01','gauge','Indice global',display='N/D',mids=['alignment'])
    element(6,'VERDICT','insight',display='<b>Capital cognitif :<br/>cockpit incomplet.</b>',detail='Indice global non calculable.<br/>Référentiels métier à compléter.',mids=['alignment'],ev=['rule:M6 Indices:15'],status='MISSING')
    element(6,'POINT','insight',display=f"<font color='#2AD1A0'><b>Point documenté</b></font> : score de portefeuille {fmt(v('portfolio_score'))}/100. Valeur et usage déclaratifs ; rendement financier inconnu.",mids=['portfolio_score','financial_return'])
    element(6,'URGENCY','insight',display="<font color='#FF7477'><b>Urgence</b></font> : relier les usages aux activités, aux profils et aux systèmes pour établir l'alignement.",mids=['coverage','skills','integration'],status='MISSING')
    element(6,'MONEY','insight',display=f"<font color='#FFC432'><b>Argent</b></font> : {fmt(v('active_cost'))} kEUR/an actifs ; {fmt(v('stop_cost'))} kEUR étiquetés « Arrêter ». Économies confirmées : Unknown.",mids=['active_cost','stop_cost','savings'])
    element(6,'PRIORITIES','label','Trois sujets à arbitrer',detail='Propositions à valider ; sévérité puis coût décroissant.')
    for i,c in enumerate(picks,1):
        element(6,f'INSIGHT_{i:02}','insight',display=escape(c['conclusion'])+' : '+escape(byid[c['record_id']]['ai_usage']),detail=f"{c['rule']}  /  {c['record_id']}  /  À VALIDER",records=[c['record_id']],ev=c['evidence_ids']+[byid[c['record_id']]['evidence_ids']['nom']],status=c['data_status'],analysis_id=c['interpretation_id'])
    element(6,'EXPOSURE','note',display='Exposition par fonction : Unknown, architecture métier absente. Preuves et questions consultables dans le classeur Flow Atlas.',mids=['coverage'],status='MISSING')
    header(7,'É C R A N  ·  V U E  D S I  ·  C O N T R Ô L E  D E  G E S T I O N','Le portefeuille chiffré',f'Coûts annuels et risques déclarés ; usages actifs du périmètre {scope}.')
    kpi(7,'KPI_01','active_cost','Coût IA actif (kEUR/an)','Dont consommation : Unknown')
    kpi(7,'KPI_02','stop_cost','Coût étiqueté Arrêter (kEUR)','Économies confirmées : Unknown')
    kpi(7,'KPI_03','outside_si','Hors SI déclarées','Statut source, à confirmer')
    kpi(7,'KPI_04','fragile_skills','Compétences critiques fragiles','Référentiel absent')
    domain_metrics=sorted([m for m in metrics.values() if m['metric_id'].startswith('domain_')],key=lambda m:(-(m['metric_value'] or 0),m['metric_name']))
    element(7,'CHART_01','chart','Coûts actifs par domaine (kEUR/an)',mids=[m['metric_id'] for m in domain_metrics])
    for m in domain_metrics:
        element(7,f"CHART_01_{slug(m['metric_name'])}",'bar',m['metric_name'],m['metric_value'],'kEUR/an',fmt(m['metric_value']),group='P7_CHART_01',mids=[m['metric_id']],color='#20D3E8')
    leaders=sorted(active,key=lambda r:(-(r['annual_cost_ke'] or 0),r['record_id']))[:3]
    leader_text=' ; '.join(f"{r['ai_usage']} ({fmt(r['annual_cost_ke'])} kEUR)" for r in leaders)
    element(7,'INSIGHT_01','insight','Rendement du portefeuille',display=f'Valeur financière mesurée : Unknown. Principaux coûts actifs : {leader_text}.',mids=['financial_return'],records=[r['record_id'] for r in leaders],ev=refs(leaders,['nom','cout_annuel_ke','statut']),status='DERIVED')
    risk_metrics=[m for m in metrics.values() if m['metric_id'].startswith('risk_')]
    risk_text=' ; '.join(f"{m['metric_name']} : {fmt(m['metric_value'])}" for m in risk_metrics)
    element(7,'INSIGHT_02','insight','Registre des risques',display=f"Actives, classification déclarée : {risk_text}. Hors SI : {fmt(v('outside_si'))}. Sans propriétaire documenté : {fmt(v('missing_owners'))}. Liste nominative dans 02_AI_USAGES.",mids=[m['metric_id'] for m in risk_metrics]+['outside_si','missing_owners'])
    element(7,'INSIGHT_03','insight','Go-to-market',display='Couverture des capacités stratégiques : Unknown. Cartographier les activités et leurs liens aux usages avant de proposer des investissements.',mids=['coverage'],status='MISSING')

    from .report_extension import extend_pages
    extend_pages(usages, active, scoped_claims, metrics, metric, element, header, kpi, refs)
    from .report_completion import complete_pages
    illustrations=complete_pages(usages,active,metrics,metric,element,header,refs,reference,evidence,eid,scope)

    # Raw tables are reconstructed from immutable source evidence, not enriched fields.
    raw=[]
    for r in atlas:
        row={'record_id':r['record_id'],'dataset':r['dataset'],'source_id':r['record_id'].split(':',1)[-1]}
        sources=[eid[x] for x in r['evidence_ids'].values() if x in eid and eid[x].get('origin')=='source']
        row.update({e['field']:e['value'] for e in sources})
        first=sources[0] if sources else {}
        loc=first.get('locator','')
        row.update(source_file=first.get('file'),source_sheet=loc.split('!')[0],source_row=int(re.search(r'(\d+)$',loc).group(1)) if re.search(r'(\d+)$',loc) else None,source_sha256=first.get('sha256'),data_status='SOURCE')
        raw.append(row)
    profiles=[r for r in raw if byid[r['record_id']]['record_type']=='profile']
    raw_usages=[r for r in raw if byid[r['record_id']]['record_type']=='usage']
    quality=[]
    def issue(entity,field,message,severity='warning',action='Confirmer avec le propriétaire des données'):
        quality.append(dict(issue_id=f'ISSUE_{slug(entity+field+message)}',severity=severity,entity_type='record' if entity in byid else 'dataset',entity_id=entity,field=field,issue=message,source='08_FLOW_ATLAS',recommended_action=action,status='TO_VALIDATE'))
    for r in usages:
        for field in ['profile_id','activity','objective','tool']:
            if r.get(field) in (None,'','Unknown'):issue(r['record_id'],field,'Information ou relation non documentée')
        if r.get('organization') in (None,'','Unknown'):issue(r['record_id'],'organization','Organisation non confirmée')
        if r.get('risk') in ('Non classé','Unknown',None):issue(r['record_id'],'risk','Classification à confirmer')
        if r.get('owner') in (None,'','Unknown'):issue(r['record_id'],'owner','Propriétaire métier absent')
        if r['source_decision']=='Arrêter' and number(r.get('value_score')) and r['value_score']>2:issue(r['record_id'],'source_decision','Arrêter déclaré malgré valeur > 2 ; E7 non satisfaite')
        for field in ['annual_cost_ke','value_score','adoption_score']:
            if not number(r.get(field)):issue(r['record_id'],field,'Valeur numérique absente')
    if any(r['dataset']!=dataset for r in profiles):issue(dataset,'dataset','Les profils disponibles incluent un autre périmètre ; aucune jointure automatique')
    issue(dataset,'rule_coverage','Seules les règles E7/E13/E21 sont implémentées ; comptages partiels')
    issue(dataset,'reference_corpus','Corpus original non fourni ou récupération sans preuve exploitable') if not any(e.get('origin')=='retrieval' for e in evidence) else None
    lineage=[]
    for page,rows in pages.items():
        for r in rows:
            unknown_refs=set(r['evidence_ids'])-set(eid)
            if unknown_refs:raise ValueError(f"Unresolved evidence for {r['element_id']}: {unknown_refs}")
            lineage.append(dict(lineage_id=f"LIN_{r['element_id']}",pdf_page=int(page),pdf_element_id=r['element_id'],pdf_element_name=r['label'] or r['kind'],element_type=r['kind'],metric_id=r['metric_ids'],source_worksheet='08_FLOW_ATLAS' if r['source_record_ids'] else '05_RAG_REFERENCE',source_record_ids=r['source_record_ids'],evidence_ids=r['evidence_ids'],transformation='; '.join(metrics[m]['calculation_method'] for m in r['metric_ids']) or ('Existing rule interpretation' if r.get('analysis_id') else 'Reference wording / report metadata'),rag_stage='None (deterministic)' if r['data_status']=='DERIVED' else r['data_status'],validation_status=r['validation_status'],confidence_score=None,data_status=r['data_status'],notes='Missing prerequisites retained explicitly' if r['data_status']=='MISSING' else ''))
    return dict(version=VERSION,generated_at=datetime.now(timezone.utc).isoformat(),dataset=dataset,scope=scope,
                input_workbook=str(workbook),input_sha256=hashlib.sha256(workbook.read_bytes()).hexdigest(),
                profiles=profiles,usages=raw_usages,atlas=atlas,evidence=evidence,questions=questions,interpretations=claims,
                metrics=list(metrics.values()),pages=pages,lineage=lineage,quality=quality,illustrations=illustrations)


def save_model(model,path):
    Path(path).write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
