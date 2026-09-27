"""Flatten the canonical snapshot into human-readable, verifiable tables."""
import json
from pathlib import Path
from ..export_excel import run_builder

PAGE_SHEETS={str(p):f'{p+7:02}_PAGE_{p:02}_DATA' for p in range(3,8)}
PAGE_SHEETS.update({str(p):f'{p+9:02}_PAGE_{p:02}_DATA' for p in range(8,15)})
PAGE_SHEETS.update({str(p):f'{p+9:02}_PAGE_{p:02}_DATA' for p in range(15,33)})
PAGE_SHEETS.update({'1':'42_PAGE_01_DATA','2':'43_PAGE_02_DATA'})
PAGE_SHEETS=dict(sorted(PAGE_SHEETS.items(),key=lambda item:int(item[0])))


def tables_for(model):
    tables={
        '01_PROFILES':model['profiles'],
        '02_AI_USAGES':model['usages'],
        '05_RAG_REFERENCE':model['evidence'],
        '06_RAG_VALIDATION':model['questions'],
        '07_RAG_INTERPRETATION':model['interpretations'],
        '08_FLOW_ATLAS':model['atlas'],
        '09_REPORT_METRICS':model['metrics'],
        **{PAGE_SHEETS[p]:rows for p,rows in model['pages'].items()},
        '15_DATA_LINEAGE':model['lineage'],
        '16_DATA_QUALITY':model['quality'],
        '44_REFERENCE_EXAMPLES':model['illustrations'],
    }
    readme=[]
    def note(section,item,value,details=''):
        readme.append(dict(section=section,item=item,value=value,details=details))
    note('Report','Purpose','Auditable source for all 32 PDF pages','Page sheets contain the exact renderer inputs; formulas are owned by the canonical Python model.')
    note('Method','Reference illustrations','Pages 22, 23, 24','REFERENCE_ILLUSTRATION data is separate from portfolio metrics. Curves and financial chart are read from the supplied PPTX caches; continuity examples cite reference PDF page 23. These are not actual results or forecasts.')
    note('Method','Simulation','Read-only removal of active E7 usages','Annual cost and declarative portfolio score recalculated on remaining usages. Remaining rule findings exclude removed IDs. No exit costs, new adoption, confirmed savings or human decisions assumed.')
    note('Report','Generated at (UTC)',model['generated_at'],'Stored as an Excel date, displayed in UTC.')
    note('Report','Version',model['version'])
    note('Report','Dataset',model['dataset'],model['scope'])
    note('Source','Flow Atlas workbook',model['input_workbook'],model['input_sha256'])
    for file in sorted({e['file'] for e in model['evidence'] if e.get('file')}):
        hashes=sorted({e['sha256'] for e in model['evidence'] if e.get('file')==file and e.get('sha256')})
        note('Source',Path(file).name,file,'SHA256: '+', '.join(hashes))
    note('Method','Grain','Separate profile and usage records','Missing organisation/profile/activity links are not inferred. No activity or relationship sheets are created without evidence.')
    note('Method','Origins','SOURCE, DERIVED, RAG_RETRIEVED, RAG_INFERRED, HUMAN_VALIDATED, MISSING, TO_VALIDATE','Deterministic rule outputs are DERIVED and their review status is TO_VALIDATE; no LLM ran for this report.')
    note('Method','Missing values','Blank typed value + MISSING status; PDF shows Unknown or N/D','Zero is a measured or counted zero, never a missing-value replacement.')
    note('Method','Confidence','Blank when uncalibrated','No artificial probabilities assigned.')
    note('Method','Refresh','Edit source inputs and regenerate','This is a frozen report snapshot, not a separate calculation engine. Excel and PDF originate from one model.')
    note('Method','Priority policy','Severity, annual cost, stable ID','MVP policy, not full R7.1 impact or M8/R8.3 arbitration. Page 6 retains one subject per usage.')
    note('Method','Formatting','Whole numbers in PDF; exact numeric values in metric rows','Example: /100 scores retain fractional values in 09_REPORT_METRICS.')
    note('Method','Coverage','E7, E13, E21 only','The absence of a detected issue is not proof that other risks are absent.')
    descriptions={
        '01_PROFILES':'Original persona/profile cells, with source rows; no join to a different dataset.',
        '02_AI_USAGES':'Original usage records; source owner and decisions preserved.',
        '05_RAG_REFERENCE':'Cell evidence, rules, reference-page metadata, retrieved passages and human evidence when available.',
        '06_RAG_VALIDATION':'Questions, answers, reviewer, time and supporting reference.',
        '07_RAG_INTERPRETATION':'Existing interpretations, original evidence IDs and validation state.',
        '08_FLOW_ATLAS':'Canonical analytical rows and explicit missing links.',
        '09_REPORT_METRICS':'Calculated values, units, filters, records and source evidence.',
        '15_DATA_LINEAGE':'One row per PDF content element; joins to metrics, Atlas records and evidence.',
        '16_DATA_QUALITY':'Missing fields/relationships, scope mismatches and conflicting decisions.',
    }
    for p,sheet in PAGE_SHEETS.items():
        note('PDF mapping',f'Page {p}',sheet,'Exact final page elements; bar rows are chart categories. Text and numeric values match the rendered snapshot.')
    for sheet,rows in tables.items():
        note('Worksheet',sheet,len(rows),descriptions.get(sheet,'Exact page data with stable element IDs.'))
    return {'00_README':readme,**{s:r for s,r in tables.items() if r}}


def export_book(model,output,root):
    payload={'tables':tables_for(model),'generated_at':model['generated_at']}
    path=output/'portaland_report_tables.json'
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    run_builder(root,root/'src/report/export_data.mjs',[str(path),str(output)])
    return output/'portaland_report_data.xlsx'
