# Inspection et contrat du MVP

Inspection du 27 septembre 2026, avant l'implémentation. Les 14 fichiers initiaux sont préservés.

## Inventaire

| Fichier | Rôle |
|---|---|
| `inputs/1. Fichier et RAG/flow_atlas_inputs - profil et usages.xlsx` | Entrées principales : 10 profils EDA et 15 usages automobiles, non reliables en l'état |
| `inputs/1. Fichier et RAG/Flow_Atlas_Moteurs_de_regles.xlsx` | 14 feuilles ; M1–M9, hypothèses, simulateur, scénario d'assurance et questions ouvertes |
| `inputs/1. Fichier et RAG/Regles Metiers.xlsx` | 8 feuilles NEXUS ; 8 cas, 2 agents, 7 systèmes sources, 11 composants, 5 décisions, 5 tâches |
| `inputs/1. Fichier et RAG/nexus_structures.xlsx` | 3 tables enrichies NEXUS : portefeuille, gouvernance, compétences |
| `inputs/1. Fichier et RAG/verite-de-reference_EDA.md` | Corrigé fictif d'évaluation ; explicitement exclu du corpus Dust |
| `inputs/1. Fichier et RAG/questions-validation-RAG.md` | 10 questions, réponses attendues, sources exactes et barème |
| `inputs/1. Fichier et RAG/resultats-tests-RAG.md` | Résultats déclarés du test Dust du 25 septembre : 18/20, zéro hallucination rapportée |
| `inputs/1. Fichier et RAG/Flow_Atlas_presentation.pdf` | 32 pages ; référence page 6, critique de ses résultats page 17 |
| `inputs/1. Fichier et RAG/Flow_Atlas_presentation.pptx` | Contrepartie éditable de la présentation |
| `inputs/vision globale.jpeg` | Schéma de travail et fonctionnalités envisagées |
| `inputs/vision dashboard - des objets structures.jpeg` | Capture Carlovers : 49 usages, 45 actifs, 1 282 kEUR/an ; périmètre différent des entrées |
| `PORTALAND_PROMPT.md` | Anciennes instructions de première phase d'audit |
| `codex_aidut.md` | Audit antérieur et constats détaillés |
| `codex_aidut.docx` | Version Word de l'audit |

Aucun code Python, bundle MTHDS ou corpus EDA original n'existait dans le dossier initial. Les anciennes consignes d'audit ne sont pas un blocage de l'implémentation autorisée dans la demande actuelle.

## Structure réelle des entrées

**Profils** : `user_id`, `direction`, `equipe`, `effectif_direction`, `role`, `competences_documentees`, `profil_type`, `nom_personne`, `source`.

Les personnes sont absentes ; ce sont des personas de rôle. Un effectif de direction répété sur plusieurs profils ne doit pas être additionné. Les compétences documentées ne prouvent pas à elles seules l'existence d'une activité, sa criticité ou un usage IA associé.

**Usages IA** : `id`, `domaine`, `categorie`, `nom`, `statut`, `environnement`, `owner`, `valeur`, `usage`, `cout_annuel_ke`, `risque`, `decision`, `fournisseur`.

`valeur` et `usage` sont des notes de 1 à 5. Le coût est en milliers d'euros annuels. `fournisseur` peut désigner un modèle ou un éditeur : il reste ce que la source déclare, sans conversion en outil précis. Aucune colonne ne fournit d'activité, de profil associé ou de valeur financière mesurée.

## Page 6 : contrat de reconstruction

Format horizontal 960 × 540 points. Fond bleu nuit. Titre et sous-titre en haut. Une grande carte à gauche contient la jauge et le verdict, puis point fort, urgence et argent. À droite : trois cartes numérotées et une note sur l'exposition par fonction. Pied de page discret. Aucun tableau détaillé sur cette page.

| Élément | Données nécessaires | Traitement actuel |
|---|---|---|
| Indice global | Couverture, compétences critiques, liens SI, valeur/usage | Unknown : trois sous-scores indisponibles |
| Verdict | M6, score minimum et nombre de scores manquants | Cockpit incomplet (M6 ligne 15) |
| Point documenté | Scores de valeur et d'usage des IA actives | 50,3/100, déclaratif, distinct d'un ROA |
| Urgence | Relations activités/profils/systèmes | Demande de complétude ; absence non transformée en score zéro |
| Argent | Coûts et statuts | 12 actives, 1 274 kEUR/an |
| Montant étiqueté Arrêter | Décisions sources et coûts actifs | 693 kEUR/an ; économies confirmées Unknown |
| Trois décisions | Écarts, preuves, priorité, validation | Trois propositions issues de E7/E13/E21 ; tri MVP documenté |
| Exposition par fonction | Architecture métier, criticités, dépendances | Unknown |

La référence montre 1 282 kEUR/an. L'écart de 8 kEUR n'est pas corrigé artificiellement : les périmètres et certaines valeurs diffèrent. Ses scores 131 et 656/100 sont dénoncés dans sa propre page 17.

## Politique de données et limites

- Les identifiants sont préfixés par `eda:` ou `automobile:`. Une même chaîne `AI-01` n'est pas une preuve de correspondance.
- Les profils EDA restent des lignes indépendantes dans Atlas. Le grain cible Organisation → Profil → Activité → Usage ne sera atteint qu'après apport de relations documentées.
- Les données NEXUS et le simulateur assurance sont inventoriés mais ne sont pas mélangés au MVP automobile.
- Les documents d'évaluation sont réservés au benchmark. Réutiliser le corrigé comme corpus produirait une fuite des réponses attendues.
- Le présent MVP ne revendique pas trois modèles RAG entraînés ou connectés. Il prépare leurs interfaces et produit un résultat local extractif et déterministe avec des manques explicites.
- Les règles E7/E13/E21 sont interprétées conservativement ; les décisions source restent séparées des propositions. Le conflit entre E7 et l'étiquette Arrêter de Pricing dynamique VO génère une question.
- Le tri des trois cartes n'est pas R8.3. Le moteur M8 complet et les arbitrages réglementaires restent hors périmètre tant que leurs prérequis et contradictions ne sont pas résolus.
- Aucune calibration ne justifie une probabilité de confiance : `confidence_score` demeure nul, documenté comme indisponible.

## Extension Python minimale

Conserver l'orchestrateur actuel, ajouter un adaptateur de recherche/génération avec réponses structurées et vérification des citations, puis des tables de relations explicites. Les calculs monétaires, les contrôles de clés et les exports restent déterministes. Pipelex peut porter l'orchestration des appels ; il ne remplace ni le corpus source ni les règles de jointure.
