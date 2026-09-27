# Flow Atlas MVP

## Rapport Portaland, pages 3 à 7

À partir du classeur Flow Atlas existant :

```powershell
python report.py --validate
```

Cette commande produit `output/portaland_report.pdf` (cinq pages dans l'ordre 3–7),
`output/portaland_report_data.xlsx` (15 feuilles d'audit), les PDF individuels sous
`output/pages/` et les comparaisons visuelles/contrôles de traçabilité sous `output/validation/`.
Le modèle canonique est conservé dans `output/portaland_report_model.json`.

Pour actualiser également les données d'entrée, lancer `python main.py` puis `python report.py --validate`.
Le pipeline d'extraction/RAG existant et le test Gradium restent indépendants du rapport.

```powershell
python report.py --atlas chemin/flow_atlas.xlsx --dataset mon_perimetre --output output
python report.py --page 7
```

`--page` produit une page indépendante pour la revue de mise en page. Sans `--page`,
le classeur et le PDF sont produits depuis le même objet canonique. Le rapport est
un instantané : les calculs appartiennent au modèle Python, aucune page ne relit
des cellules arbitraires ou ne recalcule les KPI. Les feuilles de page contiennent
les valeurs et textes exacts reçus par les renderers, y compris les balises de mise
en forme de la page 6.

Le classeur contient les sources originales, preuves, validations, interprétations,
Atlas, métriques, cinq jeux de données de page, lignage et anomalies. Les liens
activité/profil absents restent manquants. Les décisions sont celles déclarées dans
les sources ; leur somme « Arrêter » n'est pas une économie prouvée. Le score de
portefeuille est déclaratif, pas un rendement financier.

La spécification détaillée est dans `docs/report_page_specification.md`. La validation
échantillonne trois KPI, deux graphiques et deux insights avec une graine fixe ; elle
vérifie les IDs, feuilles, cellules et empreintes des sources. Les éléments manquants
sont listés séparément. Les indices de similarité d'image sont indicatifs : le grand
fond commun augmente leur valeur. La régression de page 6 utilise la capture initiale
conservée sous `tmp/report_validation/`; si elle est absente, ce contrôle est signalé
comme indisponible, sans prétendre à une équivalence visuelle.

Le périmètre peut être changé avec `--dataset` dans un classeur respectant le contrat
Flow Atlas. Les limites de l'adaptateur d'entrée historique restent distinctes de
la réutilisabilité de ce nouveau module. Des catégories trop nombreuses ou du texte
dépassant les cadres entraînent une erreur explicite, sans troncature silencieuse.

Pipeline local : Excel source → recherche de références → validation → interprétation → `output/flow_atlas.xlsx` → `output/flow_atlas_page6.pdf`.

## Lancer

```powershell
python main.py
```

Sur ce poste, le lanceur utilise automatiquement le Python fourni par Codex si les bibliothèques manquent au Python courant. L'export Excel utilise **Node.js et `@oai/artifact-tool`**, déjà présents. Le reste du traitement est en Python.

Sur un autre poste : installer `requirements.txt`, Node.js et disposer d'Artifact Tool. La variable `FLOW_ATLAS_NODE_MODULES` permet d'indiquer son répertoire `node_modules`. Ce MVP dépend donc de cet exporteur ; il n'est pas distribué comme un exécutable Python autonome.

```powershell
python -m pip install -r requirements.txt
python main.py --inputs inputs --output output
python main.py --pdf-only output/flow_atlas.xlsx
```

La dernière commande lit les valeurs enregistrées dans le classeur. Après une modification manuelle des formules, recalculer et enregistrer dans Excel avant cette commande. Pour actualiser les interprétations, modifier les entrées ou réponses et relancer le pipeline complet.

## Périmètre réellement livré

- Détection du classeur par ses feuilles, lecture des cellules, empreintes SHA-256 et identifiants préfixés par jeu.
- Conservation des 10 profils EDA et des 15 usages automobiles **sans jointure inventée**. L'organisation, l'activité et les outils non explicitement identifiés restent `Unknown`.
- RAG 1 : recherche lexicale extractive dans les documents autorisés d'un même jeu. Chaque passage reste candidat à validation. Aucun appel à un LLM.
- RAG 2 : contrôles déterministes, questions et réponses humaines documentées. Les dix questions historiques restent un benchmark séparé.
- RAG 3 : règles E7, E13 et E21 du classeur, avec preuves et statut `inference / To validate`. Aucun verdict réglementaire automatique, aucune application intégrale de M8.
- Classeur : Synthese, Atlas, Questions, Interpretations, Preuves. Les totaux et le score M6 sont des formules recalculées.
- PDF : une page 960 × 540 points, reprenant la disposition de la page 6. Les indicateurs et propositions sont lus dans le classeur exporté.
- Comparaison automatique : `output/comparison_page6.json` vérifie dimensions, sections et rapprochements chiffrés. Elle ne prouve pas une équivalence visuelle ni métier avec l'ancien cockpit.

**Limite actuelle : les documents EDA-01 à EDA-06 et `index.html` sont absents. Les trois modèles RAG génératifs demandés ne sont pas connectés. Le pipeline technique fonctionne en mode local extractif et règles ; l'enrichissement métier EDA et sa validation end-to-end restent à effectuer avec le corpus original.** Aucun score historique Dust n'est revendiqué comme résultat de ce programme.

## Ajouter le corpus

Placer les vrais documents dans `reference/`, puis déclarer chacun dans `reference/corpus.json` :

```json
{
  "documents": [
    {"path": "EDA-03.md", "dataset": "eda", "purpose": "reference"}
  ]
}
```

Formats : UTF-8 Markdown/texte ou PDF avec texte extractible. Pas d'OCR. Un document EDA n'est jamais recherché pour un usage automobile. Les noms connus du corrigé, des questions et des résultats sont refusés. Le manifeste doit rester réservé aux documents de référence : le contrôle des noms ne constitue pas un détecteur universel de corrigés renommés.

La recherche utilise un recouvrement lexical d'au moins deux termes ; ses scores sont des scores de recherche, pas des probabilités de vérité. Les passages sont conservés comme données et ne sont pas exécutés comme instructions.

## Intégrer une réponse humaine

Utiliser les identifiants de la feuille Questions dans `reference/validation_answers.json` :

```json
{
  "automobile:AI-13:owner": {
    "value": "Nom du responsable confirmé",
    "reviewer": "Nom du validateur",
    "timestamp": "2026-09-27T15:00:00+02:00",
    "evidence": "Compte rendu ou référence de confirmation"
  }
}
```

Cette illustration n'est pas chargée dans les données. Une réponse réelle conserve auteur, date et preuve. L'organisation et le propriétaire confirmés alimentent Atlas ; une confirmation du propriétaire ferme E13. Les autres réponses sont conservées dans Questions et `human_validations`, sans conversion automatique en jointures ou économies. Une valeur monétaire renseignée reste séparée des scores déclaratifs et n'est pas assimilée à une économie.

Les cellules sources ne sont jamais modifiées. Les sorties sont remplacées au prochain lancement. Les anciennes réponses dont la question n'existe plus provoquent une erreur explicite pour éviter leur application silencieuse.

## Architecture

| Module | Responsabilité |
|---|---|
| `loading.py` | Détection, tables, preuves et règles |
| `normalization.py` | Nettoyage conservateur et contrôle des scores/coûts |
| `rag1.py` | Corpus autorisé et récupération de passages |
| `rag2.py` | Questions et confirmations humaines |
| `rag3.py` | Interprétations E7, E13, E21 |
| `consolidation.py` | Projection du modèle canonique en lignes Atlas |
| `export_excel.py`, `.mjs` | Export Excel et vérification du recalcul |
| `pdf_report.py` | Lecture du classeur et rendu PDF |
| `verification.py` | Rapprochement indépendant et comparaison page 6 |
| `config.py`, `main.py` | Configuration, orchestration et journalisation |

Le modèle canonique JSON conserve `records`, `atlas`, `evidence`, `questions` et `interpretations`. Les champs `record_id`, `evidence_ids`, `validation_ids` et `interpretation_id` relient les étapes. `confidence_score` reste nul lorsqu'aucune calibration ne permet de le calculer ; un score artificiel ne serait pas justifié.

## Vérification

```powershell
python -m unittest discover -s tests -v
```

Utiliser un Python avec les dépendances installées. Les tests de livrables supposent un lancement préalable du pipeline. Sur ce poste, le Python complet se trouve sous `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

L'exporteur vérifie aussi les effets d'un changement de coût, d'un coût nul et d'un coût absent, puis restaure la valeur originale avant export. Les aperçus PNG sont des supports de revue. Le dossier `tmp/` peut être recréé par le pipeline.

## Suite nécessaire pour un RAG complet

1. Récupérer le corpus EDA original et un inventaire d'usages EDA, ou les profils automobiles correspondants.
2. Définir un adaptateur LLM/Dust/Pipelex avec sorties structurées, citations contrôlées et configuration explicite du modèle. Aucun service payant n'est appelé dans ce MVP.
3. Réconcilier les règles conflictuelles avant d'activer M8 et R8.3 ; rejouer le benchmark EDA séparément du corpus.

Voir `docs/inspection.md` pour l'inventaire et le contrat de la page 6.

## Rapport complet — pages de référence 1 à 32

Le générateur séparé conserve le pipeline existant. Il lit `output/flow_atlas.xlsx`,
calcule le modèle et écrit les données avant de dessiner les pages.

```powershell
python report.py --data-only
python report.py --validate
python report.py --page 12
```

Sorties par défaut dans `output/report_01_32/` :

- `portaland_report_model.json` : données canoniques, métriques et preuves.
- `portaland_report_data.xlsx` : 45 feuilles, dont les données de chacune des 32 pages, une synthèse avec quatre graphiques Excel natifs et deux graphiques illustratifs séparés.
- `portaland_report.pdf` : rapport complet de 32 pages, couverture et conclusion incluses.
- `pages/page_01.pdf` à `pages/page_32.pdf` : pages individuelles.
- `validation/` : rapprochements des données et comparaisons visuelles.

`--output` permet un autre dossier si Excel ou un lecteur PDF verrouille une sortie.
`--data-only` génère JSON et Excel ; `--page` génère une page avec son modèle JSON.
Ces deux options ne se combinent pas. Les tableaux de traçabilité conservent les
longues listes d'identifiants sur une ligne, consultables dans la barre de formule.

La page 9 simule uniquement le retrait des usages actifs concernés par E7 : coût
restant, score déclaratif et écarts restants. Elle ne prédit pas des économies nettes.
Les trois autres scénarios recensent des candidats, sans inventer leurs coûts ou
effets futurs. Les référentiels, décisions humaines et indices absents restent N/D.
Les fonctions interactives du PDF de référence ne sont pas implémentées par cet export.

Les pages 15–32 reproduisent le parcours, la charte visuelle, la lecture critique et
la vision cible. Les décisions (page 20), statuts (26) et indicateurs disponibles (29)
sont calculés à partir du portefeuille. La page 25 groupe les libellés exacts du
champ fournisseur : elle n'infère ni une entreprise juridique ni une famille de modèles.
Le choc de prix x3 est une hypothèse explicite appliquée au coût annuel du groupe.

Les exemples de trajectoire, continuité et bilan financier (pages 22–24) sont signalés
`REFERENCE_ILLUSTRATION`. Les données des graphiques sont extraites du PPTX source ;
elles ne modifient jamais les usages, coûts ou indices du portefeuille. Le classeur
les isole dans `44_REFERENCE_EXAMPLES` et `04_REFERENCE_CHARTS`. Les graphiques Excel
sont liés par formules aux données exportées ; les règles métier restent calculées
par le modèle Python. Les fonctions futures et les horizons de la feuille de route
restent des propositions, sans prétendre à une implémentation ou un engagement.
