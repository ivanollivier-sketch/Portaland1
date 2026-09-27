"""Pages 8–14: calculate auditable inputs before any Excel or PDF rendering.

Scenario 1 is a counterfactual removal of E7 records, not a savings forecast.
Other scenarios expose candidate populations without inventing effectiveness.
"""
from .report_model import fmt, number, slug, DECISIONS


def extend_pages(usages, active, claims, metrics, metric, element, header, kpi, refs):
    def v(mid): return metrics[mid]['metric_value']
    def total(rows):
        return sum(r['annual_cost_ke'] for r in rows) if all(number(r.get('annual_cost_ke')) for r in rows) else None
    def ids(rows): return [r['record_id'] for r in rows]
    def fields(rows): return refs(rows, ['id','nom','statut','domaine','categorie','owner','environnement','valeur','usage','cout_annuel_ke','risque','decision','fournisseur'])
    def count(mid, label, rows, columns, method):
        metric(mid,label,len(rows),'count',active,columns,method)
    byid={r['record_id']:r for r in usages}
    ranked=sorted(claims,key=lambda c:(-c['severity'],-(c['cost_ke'] or 0),c['interpretation_id']))
    outside=[r for r in active if r['environment']=='Hors SI']
    e7ids={c['record_id'] for c in claims if c['rule']=='E7'}
    removed=[r for r in active if r['record_id'] in e7ids]
    retained=[r for r in active if r['record_id'] not in e7ids]
    highrisk=[r for r in active if r['risk']=='Haut risque']
    unclassified=[r for r in active if r['risk'] in ('Non classé','Unknown',None,'')]
    count('high_risk','Haut risque déclaré',highrisk,['statut','risque'],'COUNT active declared risk=Haut risque; not legal assessment')
    count('unclassified','Classification à compléter',unclassified,['statut','risque'],'COUNT active risk missing or Non classé')
    metric('black_boxes','Boîtes noires éditeur',None,'count',active,[],'Transparency ratings unavailable','MISSING')
    metric('outside_cost','Coût actif déclaré hors SI',total(outside),'kEUR/an',outside,['statut','environnement','cout_annuel_ke'],'SUM cost active environment=Hors SI; not proof of ungoverned spending')
    metric('outside_domains','Domaines concernés',len({r['function'] for r in outside if r['function'] not in (None,'','Unknown')}),'count',outside,['domaine','environnement','statut'],'COUNT DISTINCT documented domains among active Hors SI')
    count('e7_candidates','Usages concernés par E7',removed,['statut','valeur','usage','cout_annuel_ke'],'COUNT DISTINCT active usage IDs with existing E7 claim')
    # These outputs depend on the retained rule findings as well as source cells.
    metrics['e7_candidates']['evidence_ids']=sorted(set(metrics['e7_candidates']['evidence_ids'])|{e for c in claims if c['rule']=='E7' for e in c['evidence_ids']})

    header(8,'É C R A N  ·  É C A R T S  &  R I S Q U E S','Là où IA, compétences et systèmes ne se répondent pas',
           f"{fmt(v('issue_count'))} écarts issus de E7 / E13 / E21. Les autres expositions sont des constats source, à qualifier.",mids=['issue_count'])
    cards=[('IA sans propriétaire documenté','missing_owners','Nommer un responsable métier et conserver sa validation.'),
           ('IA déclarées hors du SI','outside_si','Rencontrer le métier, qualifier les données et vérifier les liens SI.'),
           ('Boîte noire éditeur','black_boxes','Renseigner la transparence, la documentation et les conditions de sortie.'),
           ('Coût et valeur à examiner · E7','e7_candidates','Mesurer la valeur, puis examiner arrêt, renégociation ou nouveau périmètre.'),
           ('IA à haut risque déclaré','high_risk','Faire confirmer la classification et instruire la conformité.'),
           ('Classification à compléter','unclassified','Passer les usages concernés en revue avec leur responsable.')]
    for i,(label,mid,detail) in enumerate(cards,1):
        element(8,f'CARD_{i}','card',label,value=v(mid),display='N/D' if v(mid) is None else fmt(v(mid)),detail=detail,mids=[mid])
    sample=ranked[0] if ranked else None
    if sample:
        row=byid[sample['record_id']]
        element(8,'EXAMPLE','insight',row['ai_usage'],display=sample['conclusion'],
                detail=f"{sample['rule']} · Sévérité {sample['severity']} / 3 · À valider",records=[row['record_id']],ev=sample['evidence_ids']+fields([row]),status='DERIVED',analysis_id=sample['interpretation_id'])
    else: element(8,'EXAMPLE','note','Aucun écart détecté',display='Les règles non implémentées restent à instruire.',mids=['issue_count'])
    element(8,'LEGEND','note','Lire une carte',display='Titre : type et usage\nConstat : règle et preuves\nAction : proposition à valider\nDécision : arbitrage humain\nSévérité : 3 critique · 2 important · 1 à surveiller')

    rule_evidence=sorted({e for c in claims if c['rule']=='E7' for e in c['evidence_ids']})
    metric('scenario_stop_cost','Coût actif après retrait E7',total(retained),'kEUR/an',active,['statut','valeur','usage','cout_annuel_ke'],'COUNTERFACTUAL remove active usage IDs with E7; sum remaining annual cost; not net savings',extra=rule_evidence)
    score=sum(r['value_score']*r['adoption_score'] for r in retained)/(25*len(retained))*100 if retained and all(number(r.get('value_score')) and number(r.get('adoption_score')) for r in retained) else None
    metric('scenario_stop_score','Score après retrait E7',score,'/100',active,['statut','valeur','usage','cout_annuel_ke'],'COUNTERFACTUAL remove E7 usages; SUM(value*adoption)/(25*remaining active count)*100; no causal gain claimed',extra=rule_evidence+['rule:M6 Indices:8'])
    remaining_claims=[c for c in claims if c['record_id'] not in e7ids]
    metric('scenario_stop_issues','Écarts restants après retrait E7',len(remaining_claims),'count',usages,['statut','owner','valeur','usage','cout_annuel_ke'],'COUNTERFACTUAL retain existing E7/E13/E21 findings for records not removed; other records unchanged',extra=sorted({e for c in claims for e in c['evidence_ids']}))
    pilots=[r for r in usages if r['status']=='Pilote' and number(r['value_score']) and r['value_score']>=4]
    ideas=[r for r in usages if r['status']=='Idée' and number(r['value_score']) and r['value_score']>=4]
    for mid,label,rows,status in [('strategic_pilots','Pilotes de valeur ≥ 4/5',pilots,'Pilote'),('valuable_ideas','Idées de valeur ≥ 4/5',ideas,'Idée')]:
        metric(mid,label,len(rows),'count',usages,['statut','valeur'],f'COUNT status={status} AND value_score>=4; candidate population only')
    header(9,'É C R A N  ·  A I D E  À  L A  D É C I S I O N',"Simuler avant d'agir, puis arbitrer",'Simulation statique du retrait des usages E7. Le portefeuille source reste inchangé.')
    scenarios=[('Retirer les usages concernés par E7','e7_candidates','Scénario illustré : arrêt total, sans frais de sortie.'),('Industrialiser les pilotes stratégiques','strategic_pilots','Candidats uniquement ; coûts et adoption futurs N/D.'),('Intégrer les IA hors SI','outside_si','Candidats uniquement ; liens SI et effet sur score N/D.'),('Lancer les idées à forte valeur','valuable_ideas','Candidats uniquement ; budget de lancement N/D.')]
    for i,(label,mid,detail) in enumerate(scenarios,1):
        element(9,f'SCENARIO_{i}','scenario',label,display=f"{fmt(v(mid))} candidats",detail=detail,mids=[mid],selected=i==1)
    for i,(label,before,after) in enumerate([('Indice global','alignment','alignment'),('Couverture','coverage','coverage'),('Compétences','skills','skills'),('Intégration SI','integration','integration'),('Valeur / 100','portfolio_score','scenario_stop_score'),('Écarts MVP','issue_count','scenario_stop_issues'),('Coût actif · kEUR/an','active_cost','scenario_stop_cost')],1):
        display=lambda mid:'N/D' if v(mid) is None else fmt(v(mid),1 if 'score' in mid else 0)
        element(9,f'IMPACT_{i}','comparison',label,display=f'{display(before)}  >  {display(after)}',mids=[before,after])
    element(9,'ARBITRATION','note',"Registre d'arbitrage",display='Valider · Reporter · Rejeter',detail="Décisions humaines : N/D. Aucun registre d'arbitrage n'est fourni. Les étiquettes du fichier source ne prouvent pas une validation.",status='MISSING')
    element(9,'CAUTION','note',display="Simulation mécanique : le coût retiré n'est pas une économie confirmée. Les scores des usages conservés restent constants.")

    header(10,'É C R A N  ·  P L A N  D E  R É A L I G N E M E N T','Chaque écart devient une action à arbitrer','Ordre des familles du modèle. Dans chaque famille : sévérité, coût annuel, identifiant ; impact financier N/D.')
    action_for={'E7':'Arrêter','E13':'Protéger','E21':'Augmenter'}
    descriptions={'Arrêter':('Libérer du budget','Examiner les coûts et mesurer la valeur.'),'Automatiser':('Investir','Instruire les pilotes et idées de forte valeur.'),'Augmenter':('Renforcer',"Accompagner l'adoption."),'Mutualiser':('Simplifier','Documenter les recouvrements.'),'Protéger':('Sécuriser','Nommer les propriétaires et qualifier les risques.'),'Garder':('Industrialiser','Suivre les usages maintenus.')}
    for i,name in enumerate(['Arrêter','Automatiser','Augmenter','Mutualiser','Protéger','Garder'],1):
        subset=[c for c in ranked if action_for.get(c['rule'])==name]
        color=next(d[1] for d in DECISIONS if d[0]==name)
        mid=f'action_{slug(name)}'
        metric(mid,f'Propositions {name}',len(subset),'count',usages,['id','statut','valeur','usage','owner','cout_annuel_ke'],'COUNT implemented claims mapped E7→Arrêter, E13→Protéger, E21→Augmenter; proposal only',extra=[e for c in subset for e in c['evidence_ids']])
        title,desc=descriptions[name]
        element(10,f'FAMILY_{i}','family',name,display=title,detail=desc,mids=[mid],value=len(subset),color=color)
    # All actions are exported even though the page shows a bounded priority excerpt.
    for i,c in enumerate(ranked,1):
        r=byid[c['record_id']]
        element(10,f'ACTION_{i}','action',r['ai_usage'],display=c['conclusion'],detail=f"{action_for.get(c['rule'],'À instruire')} · {c['rule']} · Sév. {c['severity']} · {fmt(r['annual_cost_ke'])} kEUR/an",records=[r['record_id']],ev=c['evidence_ids']+fields([r]),status='DERIVED',analysis_id=c['interpretation_id'],severity=c['severity'])
    element(10,'NOTE','note',display=f"{len(ranked)} propositions dans le classeur ; extrait des trois premières ci-dessous. Plusieurs actions peuvent concerner le même usage. Aucun impact R7.1 calculé.")

    header(11,'É C R A N  ·  C A P I T A L  I A',"L'inventaire vivant des IA",f"{fmt(v('usage_count'))} IA · {fmt(v('active_count'))} actives · {fmt(v('active_cost'))} kEUR/an. Fiche du plus grand coût actif documenté.",mids=['usage_count','active_count','active_cost'])
    candidates=sorted(active,key=lambda r:(-(r['annual_cost_ke'] or 0),r['record_id']))
    if candidates:
        r=candidates[0]
        element(11,'FEATURED','inventory',r['ai_usage'],display=f"{r['function']} · {r['category']}",detail=f"{r['owner']} · {r['provider']}",records=[r['record_id']],ev=fields([r]),status='SOURCE',
                state=r['status'],risk=r['risk'],environment=r['environment'],cost=fmt(r['annual_cost_ke'])+' kEUR/an',decision=r['source_decision'] or 'N/D',scores=f"Valeur {fmt(r['value_score'])}/5     Usage {fmt(r['adoption_score'])}/5")
    else: element(11,'FEATURED','inventory','Aucune IA active',display='N/D',detail='Aucune fiche active à sélectionner.',state='N/D',risk='N/D',environment='N/D',cost='N/D',decision='N/D',scores='N/D',mids=['active_count'])
    groups=[('Identité','Nom, catégorie, statut et domaine : disponibles.'),('Responsabilité','Propriétaire : selon la fiche ; direction responsable : N/D.'),('Technique','Fournisseur : disponible. Modèle précis, hébergement et transparence : N/D.'),('Risque','Classification déclarée : disponible, à confirmer par un responsable.'),('Économie','Coût annuel, valeur et usage : disponibles. Ventilation et retour financier : N/D.'),('Liens','Capacités, compétences et identifiants des systèmes : N/D.')]
    for i,(label,detail) in enumerate(groups,1):element(11,f'FIELD_{i}','field',label,display=detail,records=ids(usages),ev=fields(usages),status='DERIVED')
    element(11,'NOTE','note',display='Inventaire complet dans 02_AI_USAGES ; champs effectifs et preuves dans 08_FLOW_ATLAS. Les données absentes restent explicites.')

    header(12,'É C R A N  ·  S H A D O W  A I','Aller voir les métiers, pas interdire',"Les IA déclarées hors SI : cartographier, comprendre le besoin, qualifier l'intégration et la gouvernance.")
    for i,mid in enumerate(['outside_si','outside_cost','outside_domains','black_boxes'],1):kpi(12,f'KPI_{i}',mid)
    domains=sorted({r['function'] or 'Unknown' for r in outside},key=lambda d:(-(total([r for r in outside if (r['function'] or 'Unknown')==d]) or 0),d))
    for i,domain in enumerate(domains,1):
        rows=[r for r in outside if (r['function'] or 'Unknown')==domain]
        mid=f'outside_domain_{slug(domain)}'
        metric(mid,domain,total(rows),'kEUR/an',rows,['statut','environnement','domaine','cout_annuel_ke'],'SUM active Hors SI annual cost in domain; missing cost => null')
        element(12,f'DOMAIN_{i}','domain',domain,display=f'{len(rows)} IA · {fmt(total(rows))} kEUR/an',detail=' ; '.join(sorted({str(r['owner']) for r in rows if r['owner'] not in (None,'','Unknown')})) or 'Interlocuteur N/D',records=ids(rows),ev=fields(rows),mids=[mid])
    for i,(label,detail) in enumerate([('Rencontrer','Confirmer le responsable et le besoin réel du métier.'),('Qualifier','Recenser données, fréquence, sensibilité et responsabilités.'),('Intégrer',"Relier à un système ou encadrer l'usage après examen.")],1):element(12,f'STEP_{i}','step',label,display=detail)
    element(12,'NOTE','note',display='Hors SI ne prouve pas une absence de gouvernance. Engagement des métiers et transparence éditeur : N/D. Détail nominatif dans le classeur.')

    header(13,'É C R A N S  ·  R É F É R E N T I E L S','Les trois piliers qui donnent du sens aux scores',"Sans référentiels et liens documentés, couverture, cohérence et intégration restent N/D.")
    pillars=[('Systèmes & ERP','systems','Le socle transactionnel auquel relier les IA.','Nom · type · domaine · ouverture IA · description','#20D3E8'),('Architecture métier','capabilities',"Les capacités : ce que l'entreprise doit savoir produire.",'Nom · domaine · criticité · valeur · description','#8584FF'),('Compétences','skill_count','Le capital humain : niveaux, criticités et fragilités.','Nom · domaine · criticité · niveau · effectif · description','#2AD1A0')]
    for i,(label,mid,desc,detail,color) in enumerate(pillars,1):element(13,f'PILLAR_{i}','pillar',label,display=desc,detail=detail,mids=[mid],color=color)
    element(13,'NOTE','note',display="À compléter : trois inventaires et leurs liens aux IA. Les profils EDA disponibles appartiennent à un autre périmètre et ne remplacent pas un référentiel automobile.",mids=['systems','capabilities','skill_count'],status='MISSING')

    header(14,'É C R A N  ·  D O N N É E S  &  I M P O R T',"Alimenter le cockpit avec des données traçables",'Parcours de référence et capacités locales disponibles. Chaque export conserve les preuves et les données manquantes.')
    for i,(label,detail) in enumerate([('Capacités','À fournir'),('Compétences','À fournir'),('Systèmes','À fournir'),('IA',f"{fmt(v('usage_count'))} recensées"),('Cockpit','Excel + PDF')],1):element(14,f'STEP_{i}','step',label,display=detail,mids=['usage_count'] if i==4 else [])
    element(14,'CARD_1','card','Sources disponibles',display='Classeur profils et usages',detail='Les usages automobiles alimentent ce rapport. Les profils EDA restent séparés. La démo Meridian du document de référence ne fournit aucune donnée à ce rapport.',mids=['usage_count'])
    element(14,'CARD_2','card','Import local',display='Excel > Atlas > modèle',detail='Lecture du classeur, preuves par cellule, règles E7/E13/E21, puis données des pages. Assistant interactif et import CSV de la référence : non implémentés.')
    element(14,'CARD_3','card','Exports auditables',display='JSON · Excel · PDF',detail='Le modèle JSON est enregistré avant Excel et PDF. Les identifiants relient chaque élément à ses sources. Sauvegarde serveur et restauration multi-compte : non implémentées.')
    element(14,'NOTE','note',display='Ordre de génération : sources > Atlas > modèle du rapport > classeur de contrôle > pages PDF. Aucun chiffre de démonstration injecté.')
