# Portaland report: pages 3–7

## Audit baseline

Reference: `inputs/1. Fichier et RAG/Flow_Atlas_presentation.pdf`, pages 3–7, 960 × 540 pt. Editable counterpart: adjacent PPTX. Existing result: `output/flow_atlas_page6.pdf`. Before refactoring, its PDF and 96 dpi PNG were saved to `tmp/report_validation/page6_before.*`.

Current flow: `main.py` → source `Profils` and `Usages IA` → `loading`, `normalization`, `rag1`, `rag2`, `rag3`, `consolidation` → `flow_atlas.json` → Artifact Tool exporter → `flow_atlas.xlsx` → `src/pdf_report.py` → ReportLab PDF. Page 6 reads three sheets and ranks interpretations by severity, cost, ID, retaining one per usage. It uses Helvetica/Helvetica-Bold and vector shapes, no image assets. The intermediate JSON preserves raw records and evidence. Gradium is an isolated audio test, unrelated to report generation. No MTHDS/Pipelex execution output or original EDA corpus is available. The two JPEGs provide context, not report data.

## Shared visual system

- Canvas 960 × 540 pt, margins around 43 pt, footer baseline 23 pt.
- Background `#0B1220`; cards `#141F31`; borders `#29374F`; body `#E4ECF8`; muted `#9BAEC9`.
- Accent cyan `#20D3E8`, green `#2AD1A0`, red `#FF7477`, yellow `#FFC432`, violet and pink for decision categories.
- Upper section label: 10 pt bold at y=501. Title: 27 pt bold at y=462. Subtitle: 12 pt at y=429. Body 10–12 pt.
- Rounded cards, horizontal bars and gauges are programmatic vectors. No reference screenshot in output.
- Page numbers retain reference identities 3,4,5,6,7, although these are physical pages 1–5 of the output.
- Every content element has a stable `P{page}_...` identifier in the page payload and lineage. Static titles/layout labels are SOURCE metadata, with a reference page locator. Numeric source/derived/missing data remain separately classified.

## Page 3 — Architecture

**Purpose:** show the twelve application screens and the scope currently documented.

**Reference content:** three families: six Piloter screens, five Capital cognitif screens, one Administration screen. Counters on Cockpit, Écarts & risques, Capital IA, Shadow AI, Systèmes & ERP, Architecture métier, Compétences. Administration note describes account/license and persistence controls.

**Layout:** three cards x≈43,338,633, widths≈277, top≈389, bottom≈50. Six navigation rows, 35 pt high with 8 pt gaps. Small outlined counter badges on the right. Family headings cyan/violet/green.

**Inputs/calculations:** screen metadata from the reference; inventory count from scoped Atlas usages; number of detected interpretation records; global index and system/capability/skill inventory counts remain missing. “Hors SI déclarées” counts active records explicitly marked Hors SI; no automatic assertion of confirmed shadow AI. Administration describes available local data, not a nonexistent live server.

**Dependencies/missing:** architecture metadata plus canonical metrics; no LLM needed. No verified inventory of business architecture or systems.

**Implementation:** `page_03.py`, shared cards, labels and badges. Count the screen configuration to form the title rather than hardcode a business KPI.

## Page 4 — Decision vocabulary

**Purpose:** explain the decision labels and show their declared distribution.

**Reference content:** Garder, Arrêter, Mutualiser, Automatiser, Augmenter, Protéger; six colored pills and definitions; six-bar chart at right.

**Layout:** left labels x≈43 width123, explanations x≈180. Six rows y≈367 down to97 at54 pt pitch. Right chart card x≈525,y≈57,w≈391,h≈339; title inside.

**Inputs/calculations:** count distinct scoped usages by `source_decision`, across active and idea statuses. The six standard categories are vocabulary, zero is a real zero if absent. Additional/unknown labels are not discarded; appear as extra chart categories. No recommendation is promoted to a validated decision.

**Missing:** no confirmed arbitration or justification for all source labels. E7 inconsistency is separately flagged.

**Implementation:** `page_04.py` and shared horizontal-bar component. Definitions are cautious report wording with reference provenance. They do not promise immediately recoverable savings.

## Page 5 — Cockpit

**Purpose:** show alignment availability, portfolio scale and priority issues.

**Reference content:** overall gauge; coverage, skill coherence, integration, portfolio value; active/total, annual cost, critical/important issues; priority panel. The reference says top five but visibly shows four cards.

**Layout:** gauge left x43,w238; 2×2 score grid in the middle x295/465,w159; priority card x655,w260. Bottom KPI strip below main scores. Fit five issue rows into the right panel without obscuring the KPI strip (the reference slightly crowds these areas).

**Inputs/calculations:** active Production/Pilote usages, summed annual costs; portfolio score = sum(value_score×adoption_score)/(25×active_count)×100 when all active scores exist. Count severity 3 and 2 among scoped E7/E13/E21 outputs. Rank existing issues by severity, annual cost, stable ID, preserving the existing MVP policy (not R7.1 impact).

**Missing:** three subscores/global index. Zero detected critical issues is labeled “règles MVP”, not assurance of no critical risk.

**Implementation:** `page_05.py`, gauge, score/KPI cards, five issue cards. Any issue proposal retains TO_VALIDATE status and links to rule evidence.

## Page 6 — Existing executive view

**Purpose:** executive synthesis with three subjects to validate.

**Layout preservation:** original x/y positions, typography, card geometry and text retained. The existing gauge is N/D. Existing source footer preserved in the compatibility output. No redesign.

**Inputs/calculations:** same canonical counts, cost, source Arrêter amount and portfolio score as page 5/7. Recommendations rank by severity/cost/ID, distinct usage, maximum three. No reference constants (131, 656, 1282) enter business calculations.

**Reference differences:** current subset 15 usages/12 active; active cost 1274 kEUR vs reference1282; score50.3 vs invalid reference656; global index unavailable. The 693kEUR source Arrêter cost is not confirmed savings. Role/activity/system mappings remain absent.

**Implementation:** move existing drawing to `page_06.py`; `src/pdf_report.render` remains a compatibility wrapper. Page data contains exact ready-to-render strings, metrics and selected recommendation IDs. Pixel regression against saved existing result required; intentional changes must be documented.

## Page 7 — Quantified portfolio

**Purpose:** cost allocation, declared exposure, limits on value and investment decisions.

**Reference content:** active cost including consumption, savings, shadow AI, fragile skills; domain cost chart; yield, risk register and go-to-market panels.

**Layout:** four equal KPI cards x43,263,483,703,top396,bottom309. Chart x43,y47,w425,h≈249. Three narrative cards on right x482,w432,heights≈76 with9 pt gaps.

**Inputs/calculations:** total active annual cost; source Arrêter cost (explicitly relabeled); count active declared Hors SI; fragile skills missing. Aggregate active cost by `function`/source `domaine`; do not call it consumption-only. Risk classification counts and named exposure rows in audit workbook. Cost leaders sorted from current records, not hardcoded names. Monetary yield unavailable.

**Missing:** consumption breakdown, confirmed savings, measured monetary benefit, critical skills, strategic capability mappings. None is zero-filled.

**Implementation:** `page_07.py`, shared KPI cards/bars/narrative panels. All narrative strings assembled in the model with source references, not inferred in the renderer.

## Data availability and provenance

| Element | Pages | Required data | Available | Source | Method | Missing |
|---|---|---|---|---|---|---|
| Usage/active counts | 3,5,6,7 | scoped IDs,status | yes | Atlas / source usages | distinct count, Production/Pilote | none |
| Alignment | 3,5,6 | capabilities,skills,systems | no | absent referentials | M6 requires relationships | three subscores |
| Decisions chart | 4 | decision label | yes, unvalidated | source usages | count by label | confirmation |
| Portfolio score | 5,6 | value,usage scores | yes | source usages, M6B8 | product sum /25n | measured financial value |
| Costs/domain chart | 5,6,7 | annual cost,status,domain | yes | source usages | filter/sum | consumption-only breakdown |
| Issues/top list | 3,5,6 | interpretations,severity,cost | partial | E7/E13/E21 outputs | sort/count | other rules |
| Arrêter cost | 6,7 | decision,cost,status | yes | source usages | conditional sum | actual savings |
| Risk/owner/SI | 7 | risk,owner,environment | declared | source cells, human answers | count/classify | compliance validation |
| Exposure/go-to-market | 6,7 | critical activities,links | no | absent | cannot evaluate | business map |

## Architecture and workbook contract

`Flow Atlas XLSX → src/data/report_model.py → immutable report snapshot → report_data.xlsx + page renderers → combined PDF`.

The model reads Atlas, Preuves, Questions and Interpretations once. No page opens a workbook or recomputes a business metric. Numeric values remain numeric; missing values are null plus MISSING status. Display text explicitly uses Unknown/N/D. Origins use SOURCE, DERIVED, RAG_RETRIEVED, RAG_INFERRED, HUMAN_VALIDATED, MISSING, TO_VALIDATE. Existing rule inferences are DERIVED with TO_VALIDATE review status, not described as LLM output. Confidence is null unless a real assessment exists.

Workbook sheets: 00_README; 01_PROFILES; 02_AI_USAGES; 05_RAG_REFERENCE (source cell evidence, rule passages and any retrieved passages); 06_RAG_VALIDATION; 07_RAG_INTERPRETATION; 08_FLOW_ATLAS; 09_REPORT_METRICS; 10_PAGE_03_DATA through14_PAGE_07_DATA; 15_DATA_LINEAGE;16_DATA_QUALITY. Omit activity/link sheets while there are no supported records. Each page worksheet contains exact element payloads (numbers, text, category arrays, IDs and statuses); charts' category rows are individually auditable.

00_README includes native Excel generation datetime in UTC, version, scope, hashes/files, sheet meanings, page mapping and missing conventions. The workbook is a generated snapshot: edit original inputs and regenerate, rather than independently recalculate and drift from the PDF. Shared calculation ownership remains in the Python model, per the user's single-source requirement.

## Sequence and acceptance

1. Complete this audit/spec before changing page code.
2. Implement canonical model/common components and page3; standalone PDF, render/review.
3. Implement page4; standalone PDF, render/review.
4. Implement page5; standalone PDF, render/review.
5. Refactor page6 preserving its picture and compatibility interface; regression check.
6. Implement page7; standalone PDF, render/review.
7. Export all workbook sheets from the same snapshot, check page payload equality, combine pages3–7.
8. Render paired references/generated pages at96dpi. Report mean pixel similarity as a diagnostic, not a correctness threshold.
9. With a fixed random seed sample at least3 KPIs,2 charts,2 insights/classifications; traverse page row→metric→Atlas ID→source cell/hash. Missing elements have explicit unavailable lineage; do not invent completion.
10. Verify another dataset label and changed inputs propagate through the same model. Keep Gradium and the existing extraction/rule pipeline untouched.

## Risks

EDA profiles cannot be joined to automobile usages. Organisation names are not confirmed. Existing rule coverage is partial. The reference contains known faulty scores. Layouts must tolerate changed labels, categories and absent insights. The new report is reusable for another scoped Flow Atlas dataset, but the earlier raw workbook adapter retains its original demo mappings. The report layer cannot reconstruct absent knowledge or claim a full RAG evaluation.

## Extension: reference pages 8–14 (report-1.1)

The canonical model calls `src/data/report_extension.py` before exporting any page.
The existing pipeline and rule engine are unchanged. The combined report now contains
12 pages, labelled 3 through 14. Default output is `output/report_03_14/` to avoid the
previous workbook, which was open and locked during this extension.

| Reference page | Layout | Canonical data and policy |
|---|---|---|
| 8 — Risks | Six cards and an example panel | Owner gaps, declared Hors SI, E7 unique usages, declared high/unclassified risk. Transparency count is null. These cards are overlapping observations, not six additional implemented rules. Example uses the first severity/cost-ranked claim. |
| 9 — Decision support | Four scenarios, before/after, arbitration | Only scenario 1 is simulated: remove active E7 usage IDs, retain other scores and existing rule findings. Recalculate annual cost and portfolio score with remaining active count. Other scenarios count candidates (Pilote/Idée value ≥4, Hors SI). Global and missing subscores remain null. No human decisions supplied. |
| 10 — Actions | Six families and three priority examples | Explicit proposal mapping E7→Arrêter, E13→Protéger, E21→Augmenter. Counts are partial-rule outputs. Sort severity descending, cost descending, stable ID. All eight actions in page worksheet; first three displayed. No M8/R7.1 impact claims. |
| 11 — IA inventory | Largest-cost active IA card and six field groups | Deterministic selection by cost then ID. Source owner/provider, status/risk/environment, value/adoption and declared decision. No name expansion or synthetic fields. Empty active inventory supported. |
| 12 — Outside SI | Four KPIs, domain mapping, three steps | Active Hors SI count/cost/distinct documented domains; transparency unknown. Domain costs descending, up to five displayed; all rows exported. Declared owners listed, missing interlocutors explicit. No assumed engagement or lack of governance. |
| 13 — Referentials | Three pillars and a missing-data note | System, capability and skill inventories remain null. Required field lists describe the reference schema. EDA profiles are not reused as automobile skills. |
| 14 — Data/import | Five steps and three cards | Actual Excel→Atlas→model→Excel/PDF workflow; missing inventories and unavailable interactive/CSV/server features explicitly identified. No Meridian demo business values imported. |

New page sheets are `17_PAGE_08_DATA` through `23_PAGE_14_DATA`; existing worksheet
names remain stable. There are 22 sheets. Metrics, evidence and lineage include all
new pages. Blank values mean missing, while counted empty sets legitimately equal zero.
Long JSON arrays are unwrapped to keep audit row heights usable; the full value is
available in Excel's formula bar and the JSON snapshot.

Acceptance checks: all 12 page payloads equal Excel, all metric values match, evidence
and record IDs resolve, page order/dimensions match, seven sampled source chains verify
file hashes, and every new page is rendered for visual review. Tests cover scenario
non-mutation, missing-cost propagation, no active records, domain/action reconciliation,
and the existing source isolation and human-validation behavior.

## Completion: all 32 pages (report-2.0)

`report.py` now defaults to `output/report_01_32/` and supports `--page 1` through
`--page 32`. The cover and promise pages are included, so PDF page numbers match
the reference. Pages 3–14 retain their existing renderers. New geometry is in
`src/report/pages/completion.py`; all inputs are prepared in
`src/data/report_completion.py` before Excel/PDF generation.

| Page | Layout and content | Data policy |
|---|---|---|
| 1 | Cover, three tags, alignment gauge | Actual portfolio scope/count/cost; missing alignment remains N/D |
| 2 | Three promise cards | Reference concepts and decision vocabulary |
| 15 | Six journey steps and three audiences | Proposed workflow, not active UI functionality |
| 16 | Palette and component list | The actual report colors and graphic conventions |
| 17 | Six review cards | Current scores, missing relationships and count grains; reference anomalies distinguished |
| 18 | Five short-term actions | Current owners, declared risks and Arrêter-labelled cost; no savings claim |
| 19 | Vision divider | Future product direction |
| 20 | Decision donut and four limitations | Source decisions grouped defensive/maintain/offensive; all usages denominator; unknown labels preserved |
| 21 | Seven before/after rows | Proposed conceptual changes |
| 22 | Line chart with four explanation cards | Exact chart7.xml values read from supplied PPTX; explicit REFERENCE_ILLUSTRATION role; missing series points stay null |
| 23 | Five-row continuity table and three cards | Example table from reference PDF page 23; no real employee/capability facts inferred |
| 24 | Five-step value chain, columns and three cards | Exact chart8.xml illustration; actual cost/savings status separately labelled |
| 25 | Provider-label card and five shocks | Exact supplier label groups, no identity/family resolution; illustrative x3 cost shock; missing provider/cost disables ranking |
| 26 | Status bars and three opportunity cards | Actual source statuses and strategic pilot count |
| 27 | Six-stage circular governance cycle | Proposed human process; no executed decision or compliance proof invented |
| 28 | Six viewpoints plus synthesis | Reference Council concept; no agents or LLM services executed |
| 29 | Six indicator cards | Calculable offensive share/provider-label concentration; unavailable continuity/net value/speed/compliance; classification distinguished from compliance |
| 30 | Five audience rows | Questions and expected future outputs |
| 31 | Three roadmap horizons | Indicative source horizons, not committed dates |
| 32 | Closing promise and three questions | Strategic conclusion |

Workbook: 45 worksheets. Two native chart sheets, 32 exact page-data sheets, existing
source/rule/metric/lineage/quality sheets, and `44_REFERENCE_EXAMPLES`. Existing sheet
names remain stable; pages 15–32 use 24_PAGE_15_DATA through 41_PAGE_32_DATA, and pages
1–2 use 42_PAGE_01_DATA and 43_PAGE_02_DATA. Native charts are linked by formulas to
canonical exported cells. No independent business rule calculation lives in Excel.
`ISBLANK` guards preserve counted zeros while retaining missing illustration points.

The reference illustrations never enter business metrics. Each chart point cites
the PPTX chart part, series, category and file SHA256. The continuity table cites the
PDF page. Missing PPTX leaves chart data unavailable; it does not invent substitute
points. Future functionality is described as a target, not claimed as shipped.

Validation additionally compares reference-example cells and chart helper results,
verifies illustration source hashes and exclusion from business metrics, and compares
pages 3–14 pixel-for-pixel with the preceding release. Tests also cover unknown
decision labels, missing suppliers, native charts, numeric zeros and missing values.
