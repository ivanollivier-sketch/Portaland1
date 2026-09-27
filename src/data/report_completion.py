"""Complete report content, with business metrics separate from reference examples."""
import hashlib
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from .report_model import fmt,number,slug

COLORS=['#20D3E8','#8584FF','#2AD1A0','#FFC432','#FF7477','#ED6EC0']


def complete_pages(usages,active,metrics,metric,element,header,refs,reference,evidence,eid,scope):
    def v(mid):return metrics[mid]['metric_value']
    def show(mid,dec=0):return 'N/D' if v(mid) is None else fmt(v(mid),dec)
    def add(p,key,label,text='',detail='',mids=(),kind='card',**extra):
        return element(p,key,kind,label,display=text,detail=detail,mids=mids,**extra)
    def cards(p,items,kind='card'):
        for i,item in enumerate(items,1):
            label,text,*rest=item
            add(p,f'{kind.upper()}_{i}',label,text,rest[0] if rest else '',kind=kind,color=COLORS[(i-1)%6])
    def missing(mid,label,reason):metric(mid,label,None,'N/D',usages,[],reason,'MISSING')
    for mid,label,reason in [('continuity','Continuité cognitive','No critical capability inventory, expert roster or documented AI carriers'),('net_value','Valeur nette prouvée','Measured monetary gains and full cost unavailable'),('realignment_speed','Vitesse de réalignement','No dated issue closure history'),('compliance','Conformité AI Act','No verified complete compliance dossiers or human oversight register'),('model_dependency','Dépendance à un modèle','No underlying model identifiers')]:missing(mid,label,reason)
    categories=[('defensive','Défensives',{'Arrêter','Protéger'},'#FFC432'),('maintain','Maintien',{'Garder'},'#2AD1A0'),('offensive','Offensives',{'Automatiser','Augmenter','Mutualiser'},'#8584FF')]
    for mid,label,decisions,color in categories:
        metric(mid,label,sum(r['source_decision'] in decisions for r in usages),'count',usages,['id','decision'],f'COUNT source decision in {sorted(decisions)}; all scoped usages')
    metric('other_decisions','Autres décisions',len(usages)-sum(v(c[0]) for c in categories),'count',usages,['id','decision'],'COUNT decisions outside six declared categories; denominator preserved')
    metric('offensive_share','Part offensive',100*v('offensive')/len(usages) if usages else None,'%',usages,['id','decision'],'100 * COUNT source decision in Automatiser,Augmenter,Mutualiser / COUNT all scoped usages')
    for status in ['Idée','Pilote','Production','Arrêté']:
        metric('stage_'+slug(status),status,sum(r['status']==status for r in usages),'count',usages,['id','statut'],f'COUNT status={status}; all scoped usages')
    providers=sorted({r['provider'] for r in active if r['provider'] not in (None,'','Unknown')})
    known=[r for r in active if r['provider'] not in (None,'','Unknown')]
    costs={name:sum(r['annual_cost_ke'] for r in known if r['provider']==name) if all(number(r['annual_cost_ke']) for r in known if r['provider']==name) else None for name in providers}
    complete=len(known)==len(active) and bool(active) and all(number(r['annual_cost_ke']) for r in active)
    winner=sorted(providers,key=lambda name:(-(costs[name] or 0),name))[0] if providers and complete else None
    leader=[r for r in active if winner and r['provider']==winner]
    concentration=100*costs[winner]/v('active_cost') if complete and winner and number(v('active_cost')) and v('active_cost')>0 else None
    metric('provider_share','Concentration du champ fournisseur',concentration,'%',active,['statut','fournisseur','cout_annuel_ke'],'Largest exact declared provider-label cost / active annual cost * 100; requires all providers/costs; no corporate/model-family resolution')
    metric('provider_top_cost','Coût du premier libellé fournisseur',costs.get(winner),'kEUR/an',active,['statut','fournisseur','cout_annuel_ke'],'SUM active annual cost for largest exact provider label; identity/model family not inferred')
    metric('provider_top_count','IA du premier libellé fournisseur',len(leader) if winner else None,'count',active,['statut','fournisseur','cout_annuel_ke'],'COUNT active usages at selected largest-cost provider label; missing inputs => null')
    metric('provider_price_shock','Surcoût hypothétique prix x3',2*costs[winner] if winner and costs[winner] is not None else None,'kEUR/an',active,['statut','fournisseur','cout_annuel_ke'],'ASSUMPTION all annual costs of selected exact provider label triple: incremental cost=2*current cost; no contract or variable-cost breakdown')
    metric('classified_share','Classification déclarée des actives',100*sum(r['risk'] not in (None,'','Unknown','Non classé') for r in active)/len(active) if active else None,'%',active,['statut','risque'],'COUNT active usages with nonmissing risk classification / active_count *100; not compliance')

    header(1,'T H E  F L O W  F A B R I C','Flow Atlas Cloud',"Le cockpit d'alignement du capital cognitif")
    add(1,'INTRO','Portaland',f'Rapport généré à partir du portefeuille {scope}. Partie 1 : inventaire, décisions et parcours. Partie 2 : vision cible et feuille de route.',mids=['usage_count'])
    add(1,'SCOPE','Périmètre',f"{show('usage_count')} usages · {show('active_count')} actifs · {show('active_cost')} kEUR/an",mids=['usage_count','active_count','active_cost'])
    add(1,'GAUGE',"Indice d'alignement cognitif",show('alignment'),'IA × compétences × systèmes × valeur',mids=['alignment'],kind='gauge')
    cards(1,[('VOIR',''),('DÉCIDER',''),('PILOTER','')],kind='tag')
    header(2,'L A  P R O M E S S E','Donner au dirigeant une lecture décidable de son capital cognitif',"Rendre visible l'alignement entre les IA, les compétences humaines, les systèmes et la valeur créée.")
    cards(2,[('Voir','Recenser le capital cognitif : IA officielles et hors SI, compétences, systèmes, capacités métier.','Cockpit · Vue Dirigeant · Vue DSI'),('Décider',"Transformer les écarts en recommandations, simuler sous hypothèses, puis recueillir l'arbitrage.",'Écarts & risques · Aide à la décision'),('Piloter',"Classer les actions, désigner les responsables et mesurer leur exécution.",'Plan de réalignement · Suivi des usages')])
    add(2,'NOTE','Objectif',"Chaque IA devrait avoir un propriétaire, une valeur démontrée, un ancrage SI et une décision : garder, arrêter, mutualiser, automatiser, augmenter, protéger.",kind='note')
    header(15,'P A R C O U R S','Du fichier désordonné à la décision de COMEX',"Le parcours de référence, de la donnée source à l'action. Les fonctions interactives restent une cible.")
    cards(15,[('Alimenter','Données & import'),('Recenser','Capital IA · Hors SI · référentiels'),('Voir','Cockpit · Dirigeant · DSI'),('Comprendre','Écarts & risques'),('Simuler et arbitrer','Scénarios · Décision humaine'),('Piloter','Plan de réalignement · Suivi')],kind='step')
    cards(15,[('Dirigeant / COMEX','Un verdict documenté, trois sujets à arbitrer, un budget à examiner.'),('DSI · contrôle de gestion','Coûts, risques déclarés, systèmes et preuves à compléter.'),('Responsable transformation',"Écarts, simulation, responsables et suivi de l'exécution à organiser.")])
    header(16,'U X / U I','Un système visuel de cockpit sombre','Lisible en réunion ; les couleurs conservent un sens constant dans le rapport.')
    for i,(label,color) in enumerate([('Fond nuit','#0B1220'),('Cartes','#141F31'),('Action / lien','#20D3E8'),('Marque','#8584FF'),('Bon / garder','#2AD1A0'),('Attention / protéger','#FFC432'),('Alerte / arrêter','#FF7477')],1):add(16,f'SWATCH_{i}',label,color,kind='swatch',color=color)
    cards(16,[('Jauges circulaires','Indice, sous-scores, valeur centrale ; N/D si les prérequis manquent.'),('Cartes KPI','Un chiffre, une unité et un libellé explicite.'),('Badges en pilule','Décision, statut ou rôle, avec une couleur stable.'),('Notes de 1 à 5','Valeur et usage déclaratifs ; distincts du gain financier.'),('Action en cyan','Une proposition concrète, à valider par un responsable.'),('Compteurs','Distinguer le nombre d’IA du nombre d’écarts.'),('Ton','Français clair, descriptions courtes, limites visibles.')],kind='row')
    header(17,'L E C T U R E  C R I T I Q U E',"Points d'attention relevés pendant la revue",'Contrôles appliqués au rapport ; les anomalies du document source ne sont pas présentées comme des mesures actuelles.')
    add(17,'CARD_1','Scores normalisés',f"Score du portefeuille : {show('portfolio_score',1)}/100. Les valeurs 131 et 656 de la référence ne sont pas reprises comme résultats.",mids=['portfolio_score'])
    add(17,'CARD_2','Verdict cohérent','Alignement N/D : trois référentiels et leurs liens restent absents.',mids=['alignment'])
    add(17,'CARD_3','Domaines documentés','Les domaines sont lus dans les cellules sources. Les libellés numériques de la référence ne sont pas injectés.',mids=['outside_domains'])
    add(17,'CARD_4','Périmètres séparés',f"{show('usage_count')} usages automobile ; les profils EDA ne sont pas joints automatiquement.",mids=['usage_count'])
    add(17,'CARD_5','Valeur financière absente',"Le coût et les notes déclaratives sont disponibles. Rendement financier et économies confirmées : N/D.",mids=['financial_return','savings'])
    add(17,'CARD_6','Grains de comptage',f"{show('usage_count')} usages et {show('issue_count')} écarts MVP. Un usage peut produire plusieurs écarts.",mids=['usage_count','issue_count'])
    header(18,'C O U R T  T E R M E  ·  P O R T A L A N D','Rendre le cockpit pleinement décidable','Cinq chantiers proposés à partir des données actuelles ; responsables et échéances à confirmer.')
    for i,(label,text,mids) in enumerate([
        ('Compléter les trois référentiels','Systèmes, capacités, compétences et liens : prérequis des sous-scores.',['systems','capabilities','skill_count']),
        ("Qualifier l'import Capital IA",f"Revoir les {show('usage_count')} usages et confirmer le périmètre organisationnel.",['usage_count']),
        ('Nommer les propriétaires',f"{show('missing_owners')} usages actifs sans propriétaire documenté.",['missing_owners']),
        ('Classer et documenter les risques',f"{show('unclassified')} classification(s) à compléter ; {show('high_risk')} haut risque déclaré. Dossiers : N/D.",['unclassified','high_risk']),
        ('Arbitrer les coûts étiquetés Arrêter',f"{show('stop_cost')} kEUR/an à examiner. Ce montant ne constitue pas une économie confirmée.",['stop_cost','savings'])],1):add(18,f'ROW_{i}',label,text,mids=mids,kind='row')
    header(19,'P A R T I E  2  ·  L A  V I S I O N','De la gouvernance des IA au pilotage des savoir-faire','Sept déplacements pour faire progresser le capital cognitif humain et machine.')
    add(19,'FROM','De « gouvernez vos IA »','',kind='statement')
    add(19,'TO',"à « pilotez ce que votre entreprise sait faire, et faites-le progresser »",'',kind='statement')
    add(19,'NOTE','Vision cible','Les pages suivantes distinguent les mesures du portefeuille, les exemples illustratifs de la référence et les fonctions à construire.',kind='note')
    header(20,'C O N S T A T',"Aujourd'hui, le cockpit parle surtout de risques",'Répartition des décisions déclarées du portefeuille ; les décisions humaines restent à recueillir.')
    add(20,'CHART','Répartition des décisions',f"{show('offensive_share',1)} %",f"{show('usage_count')} usages recensés",mids=['usage_count','offensive_share'],kind='donut')
    for i,(mid,label,_,color) in enumerate(categories,1):add(20,f'SLICE_{i}',label,show(mid),mids=[mid],kind='slice',value=v(mid),color=color)
    if v('other_decisions'):add(20,'SLICE_4','Autres',show('other_decisions'),mids=['other_decisions'],kind='slice',value=v('other_decisions'),color='#9BAEC9')
    cards(20,[('Une photo, pas un film','Aucun historique trimestriel ni cible COMEX fourni.'),('Les humains restent à documenter','Référentiel des compétences du périmètre : N/D.'),('Une valeur déclarative','Notes de 1 à 5 disponibles ; gain financier mesuré : N/D.'),('Des dépendances à qualifier',"Le fournisseur déclaré ne prouve pas la famille de modèle ni le plan de secours.")])
    header(21,'L A  V I S I O N  E N  U N  T A B L E A U','Sept déplacements',"Ce que l'outil montre aujourd'hui et ce qu'il pourrait permettre demain.")
    for i,(label,before,after) in enumerate([('Temps','Un état à date','Une trajectoire vers une cible, trimestre après trimestre'),('Périmètre','Les IA','Les humains, IA, systèmes et leurs liens'),('Valeur','Une note de 1 à 5','Des euros reliés aux objectifs stratégiques'),('Risque','Des écarts de conformité','Des scénarios de choc et dépendances visibles'),('Posture','Protéger, arrêter','Aussi augmenter, mutualiser et investir'),('Décision','Un registre à renseigner','Un rituel de gouvernance documenté'),('Intelligence','Des règles fixes','Un conseil contradictoire avant chaque arbitrage')],1):add(21,f'ROW_{i}',label,before,after,kind='row')

    # Read exact chart caches from the supplied presentation: reference examples
    # never enter business metrics, costs, or the usage inventory.
    illustrations=[]
    pptx=reference.with_suffix('.pptx') if reference else None
    def chart_source(chart,page):
        if not pptx or not pptx.exists():return []
        ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
        with ZipFile(pptx) as z:root=ET.fromstring(z.read(f'ppt/charts/chart{chart}.xml'))
        result=[]
        for s in root.findall('.//c:ser',ns):
            name=s.find('.//c:tx//c:pt/c:v',ns).text
            labels=[x.text for x in s.findall('.//c:cat//c:pt/c:v',ns)]
            values=[float(x.text) if x.text else None for x in s.findall('.//c:val//c:pt/c:v',ns)]
            for index,(label,value) in enumerate(zip(labels,values)):
                evidence_id=f'illustration:{page}:{slug(name)}:{index}'
                record=dict(evidence_id=evidence_id,record_id='report-reference',field='illustrative_chart',value=value,origin='source',file=str(pptx),locator=f'ppt/charts/chart{chart}.xml; series={name}; category={label}',sha256=hashlib.sha256(pptx.read_bytes()).hexdigest(),data_status='SOURCE')
                evidence.append(record);eid[evidence_id]=record
                row=dict(reference_page=page,series=name,category=label,value=value,data_role='REFERENCE_ILLUSTRATION',evidence_id=evidence_id)
                result.append(row);illustrations.append(row)
        return result
    header(22,'D É P L A C E M E N T  1  ·  L E  T E M P S','De la photo à la trajectoire',"Montrer d'où l'on vient et où l'on va. Historique et cible réels du portefeuille : N/D.")
    add(22,'CHART',"Indice d'alignement : réel et cible",'ILLUSTRATION DE LA RÉFÉRENCE',kind='illustration_chart')
    for i,r in enumerate(chart_source(7,22),1):element(22,f'POINT_{i}','point',r['category'],value=r['value'],display='N/D' if r['value'] is None else fmt(r['value']),group=r['series'],ev=[r['evidence_id']],data_role='REFERENCE_ILLUSTRATION',status='SOURCE')
    cards(22,[('Historique trimestriel','Horodater chaque sous-score et les faits qui le font évoluer.'),('Cible COMEX','Fixer un niveau visé et rendre visible l’écart à la cible.'),('Vitesse de réalignement','Mesurer écarts fermés, délais et actions en retard.'),('Alerte de dérive','Repérer les nouveaux usages hors SI ou sans propriétaire.')])
    header(23,'D É P L A C E M E N T  2  ·  L E  P É R I M È T R E',"Qui sait quoi, et qu'est-ce qui peut se perdre ?",'Carte illustrative de la référence. Experts, départs et capacités réels du portefeuille : N/D.')
    add(23,'TABLE','Carte de continuité par capacité métier','ILLUSTRATION DE LA RÉFÉRENCE',kind='table')
    for i,(name,experts,ai,departures,risk) in enumerate([('Diagnostic haute tension (VE)',2,0,1,'CRITIQUE'),('Estimation-expertise VO',4,2,2,'ÉLEVÉ'),('Carrosserie-peinture',6,0,3,'ÉLEVÉ'),('Financement F&I',5,1,0,'MAÎTRISÉ'),('Pricing VO',2,1,0,'DÉPENDANCE IA')],1):
        r=element(23,f'TABLE_{i}','table_row',name,display=risk,experts=experts,ai=ai,departures=departures,data_role='REFERENCE_ILLUSTRATION',ev=['report-reference:23'])
        illustrations.append(dict(reference_page=23,series=name,category=risk,value=None,experts=experts,ai=ai,departures=departures,data_role='REFERENCE_ILLUSTRATION',evidence_id='report-reference:23'))
    cards(23,[('Indice de continuité','Part des capacités critiques tenues par au moins trois porteurs documentés.'),('Savoir substitué',"Repérer les compétences remplacées par une IA que plus personne ne sait contrôler."),('Relève','Documenter les départs, la transmission et les usages qui accélèrent l’apprentissage.')])
    header(24,'D É P L A C E M E N T  3  ·  L A  V A L E U R',"De la note à l'euro",'Relier les porteurs aux objectifs et mesurer leur valeur. Exemple financier distinct des données du portefeuille.')
    cards(24,[('Objectif stratégique','Exemple : +15 % de marge VO'),('Capacité métier','Estimer et vendre vite un VO'),('Porteurs','Experts VO · IA · systèmes'),('Indicateur métier','Jours de stock · marge par véhicule'),('Valeur en euros','Gain mesuré contre coût complet')],kind='step')
    add(24,'CHART','Bilan annuel illustratif (kEUR)','ILLUSTRATION DE LA RÉFÉRENCE',kind='illustration_chart')
    for i,r in enumerate(chart_source(8,24),1):element(24,f'BAR_{i}','illustration_bar',r['category'],value=r['value'],display=fmt(r['value']),ev=[r['evidence_id']],color=['#FF7477','#2AD1A0','#8584FF','#FFC432'][i-1],data_role='REFERENCE_ILLUSTRATION')
    add(24,'CARD_1','ROI par IA et capacité',"Comparer licences, consommation, temps humain et gain mesuré. ROI actuel : N/D.",mids=['financial_return'])
    add(24,'CARD_2','Valeur prouvée ou attendue','Distinguer le mesuré du promis. Gains financiers du portefeuille : N/D.',mids=['net_value'])
    add(24,'CARD_3','Arbitrage budgétaire',f"Coût actif réel : {show('active_cost')} kEUR/an. Coût étiqueté Arrêter : {show('stop_cost')} ; économies confirmées : N/D.",mids=['active_cost','stop_cost','savings'])
    header(25,'D É P L A C E M E N T  4  ·  L E  R I S Q U E','Des tests de résistance, pas seulement des écarts',"Répondre à « et si demain… ? ». Les identités des modèles et les dépendances métier restent à documenter.")
    add(25,'PROVIDER','Premier libellé fournisseur',winner or 'N/D',f"{show('provider_top_count')} IA · {show('provider_top_cost')} kEUR/an · {show('provider_share',1)} % du coût actif",mids=['provider_top_count','provider_top_cost','provider_share'],kind='provider')
    for i,r in enumerate(leader,1):add(25,f'USAGE_{i}',r['ai_usage'],fmt(r['annual_cost_ke'])+' kEUR/an',kind='provider_usage',records=[r['record_id']],ev=refs([r],['nom','fournisseur','cout_annuel_ke','statut']))
    add(25,'ROW_1','Choc de prix',f"Hypothèse : tous les coûts de ce libellé triplent. Surcoût : {show('provider_price_shock')} kEUR/an ; rentabilité N/D.",mids=['provider_price_shock'],kind='row')
    for i,(label,text) in enumerate([("Sortie d'un éditeur",'Quelles capacités seraient touchées et quel délai de bascule ? Liens absents.'),('Échéances réglementaires','Vérifier les obligations et dossiers avec le responsable juridique. État de conformité N/D.'),("Départ d'un expert",'La capacité resterait-elle tenue ? Effectifs et plan de relève absents.'),('Panne ou dérive du modèle',"Quels processus s'arrêtent et quel plan manuel de secours existe ?")],2):add(25,f'ROW_{i}',label,text,kind='row')
    header(26,'D É P L A C E M E N T  5  ·  L A  P O S T U R E','Montrer aussi où gagner',"Une vue opportunités pour compléter les écarts : augmenter, mutualiser et investir.")
    add(26,'CHART',"Le pipeline d'innovation IA",f"{show('stage_'+slug('Idée'))} idées · {show('stage_'+slug('Pilote'))} pilotes · {show('stage_'+slug('Production'))} en production",mids=['stage_'+slug(s) for s in ['Idée','Pilote','Production','Arrêté']],kind='chart')
    for i,(s,color) in enumerate(zip(['Idée','Pilote','Production','Arrêté'],['#8584FF','#20D3E8','#2AD1A0','#FF7477']),1):add(26,f'BAR_{i}',s,show('stage_'+slug(s)),mids=['stage_'+slug(s)],kind='bar',value=v('stage_'+slug(s)),color=color)
    cards(26,[('AUGMENTER','Renforcer les équipes ; qualifier les besoins de transmission et d’adoption.'),('MUTUALISER','Comparer les fonctionnalités et contrats avant de conclure à un doublon.')])
    add(26,'CARD_3','AUTOMATISER',f"{show('strategic_pilots')} pilotes de valeur déclarée ≥ 4/5 à instruire. Budget d'industrialisation : N/D.",mids=['strategic_pilots'])
    header(27,'D É P L A C E M E N T  6  ·  L A  D É C I S I O N','Un rituel de gouvernance, pas un tableau de bord de plus',"Cycle trimestriel proposé ; le registre d'exécution et les décisions horodatées restent à mettre en place.")
    cards(27,[('Collecter','Mettre à jour inventaires, preuves et liens SI.'),('Détecter','Relever écarts, dérives et opportunités.'),('Contredire','Confronter les options et leurs hypothèses.'),('Arbitrer','COMEX : valider, reporter, rejeter.'),('Exécuter','Désigner propriétaires et échéances.'),('Mesurer','Suivre les effets sur les scores et les euros.')],kind='step')
    add(27,'NOTE','Mémoire des décisions',"Un registre horodaté documenterait la supervision humaine. Il ne suffit pas, à lui seul, à établir la conformité.",kind='note')
    header(28,"D É P L A C E M E N T  7  ·  L ' I N T E L L I G E N C E",'Faire contredire la carte avant le COMEX','Vision du Conseil des mousquetaires : six points de vue, puis une synthèse. Aucun agent exécuté pour ce rapport.')
    cards(28,[('Richelieu','Le milieu et le pouvoir','Qui gagne, qui perd, qui bloquera ?'),('Planchet','Le réel','Est-ce vraiment utilisé sur le terrain ?'),('Fouquet','La valeur','Combien cela rapporte-t-il, preuves à l’appui ?'),('Colbert','La conformité','Quels éléments juridiques et contractuels vérifier ?'),('Raoul','La continuité et la relève','Qui saura encore le faire dans trois ans ?'),('Milady','La contradiction','Et si la carte se trompait ?')])
    add(28,'SYNTHESIS',"D'Artagnan",'Synthèse en options, jamais en verdict : l’arbitrage reste humain.','Droit au refus\nContradictions conservées\nAucun consensus de façade',kind='synthesis')
    add(28,'NOTE','Fonction cible','Une revue contradictoire sur chaque proposition ; intégration au registre à construire.',kind='note')
    header(29,'M E S U R E R  L A  V I S I O N','Six nouveaux indicateurs pour le cockpit','Définitions de la vision cible et niveau de disponibilité dans les données actuelles.')
    for i,(label,mid,text,reader) in enumerate([('Continuité cognitive','continuity','Capacités critiques tenues par au moins trois porteurs.','DRH · COMEX'),('Valeur nette prouvée','net_value','Gain financier mesuré moins coût complet.','DAF · DSI'),('Dépendance fournisseur','provider_share','Part du premier libellé fournisseur ; familles de modèles et capacités non documentées.','DSI · Achats'),('Vitesse de réalignement','realignment_speed','Écarts fermés par trimestre et délai de traitement.','Transformation'),('Part offensive','offensive_share','Décisions déclarées augmenter, automatiser ou mutualiser / tous les usages.','COMEX'),('Conformité AI Act','compliance',f"Classification déclarée : {show('classified_share',1)} % des actives. Dossiers et supervision : N/D.",'Juridique · Risques')],1):add(29,f'CARD_{i}',label,show(mid,1)+(' %' if mid in ('provider_share','offensive_share') and v(mid) is not None else ''),text+'\nPour : '+reader,mids=[mid]+(['classified_share'] if mid=='compliance' else []),color=COLORS[(i-1)%6])
    header(30,'É L A R G I R  L E  P U B L I C','Chaque direction repart avec sa réponse','Cinq lecteurs cibles ; chaque réponse doit être reliée à des mesures et des preuves.')
    for i,(label,question,outputs) in enumerate([('Dirigeant',"Savons-nous mieux faire ce qui compte qu'il y a un an ?",'Trajectoire · Cible · Trois décisions'),('DAF',"Où notre argent IA crée-t-il de la valeur ?",'Valeur nette · ROI · Budget'),('DSI',"De quoi dépendons-nous et qu'est-ce qui échappe au SI ?",'Dépendances · Hors SI · Intégration'),('DRH','Quels savoirs risquons-nous de perdre et comment les transmettre ?','Continuité · Relève · Augmenter'),('Juridique · risques','Pouvons-nous documenter notre maîtrise en cas de contrôle ?','Classification · Registre · Supervision')],1):add(30,f'ROW_{i}',label,question,outputs,kind='row',color=COLORS[(i-1)%6])
    header(31,'F E U I L L E  D E  R O U T E','Trois horizons pour y arriver','Horizons indicatifs repris de la vision cible ; ils ne constituent pas un calendrier engagé.')
    cards(31,[('Fiabiliser','0–3 MOIS','Conserver des scores normalisés et des verdicts cohérents\nVérifier le mapping des domaines\nCompléter systèmes, capacités et compétences\nHistoriser les scores chaque trimestre'),('Enrichir','3–9 MOIS','Trajectoire et cible COMEX\nValeur en euros et ROI par capacité\nTests de résistance et dépendances\nVue opportunités et pipeline d’innovation'),('Gouverner et anticiper','9–18 MOIS','Rituel trimestriel et dossier de supervision exportable\nConseil contradictoire intégré\nContinuité et relève avec la DRH\nRepères sectoriels anonymisés')])
    header(32,'L A  N O U V E L L E  P R O M E S S E',"Pilotez ce que votre entreprise sait faire, et faites-le progresser.",'Chaque trimestre, le COMEX devrait pouvoir répondre à trois questions.')
    cards(32,[('Savons-nous mieux faire ce qui compte ?','Trajectoire et continuité'),('Notre argent IA crée-t-il de la valeur ?','Valeur nette en euros'),('Sommes-nous prêts pour le prochain choc ?','Dépendances et tests de résistance')])
    add(32,'NOTE','The Flow Fabric · Voir · Décider · Piloter','Rapport Portaland : sources traçables, hypothèses explicites, arbitrage humain.',kind='note')
    return illustrations
