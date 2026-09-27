"""Run with python main.py. Existing source files are never changed."""
import argparse
import importlib.util
import json
import logging
import os
from pathlib import Path
import subprocess
import sys


def ensure_runtime():
    missing = [m for m in ('openpyxl','pypdf','reportlab') if importlib.util.find_spec(m) is None]
    if not missing:
        return
    runtime = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if runtime.exists() and Path(sys.executable).resolve() != runtime.resolve():
        result=subprocess.run([str(runtime),str(Path(sys.argv[0]).resolve()),*sys.argv[1:]])
        raise SystemExit(result.returncode)
    raise SystemExit(f'Missing {missing}. Run python -m pip install -r requirements.txt')


def main():
    ensure_runtime()
    from src.config import ROOT
    from src.loading import discover, read_table, read_json, rules
    from src.normalization import normalize
    from src import rag1, rag2, rag3
    from src.consolidation import consolidate
    from src.export_excel import export
    from src.pdf_report import render
    from src.verification import compare
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=ROOT/'inputs')
    parser.add_argument('--output',type=Path,default=ROOT/'output')
    parser.add_argument('--corpus',type=Path,default=ROOT/'reference/corpus.json')
    parser.add_argument('--answers',type=Path,default=ROOT/'reference/validation_answers.json')
    parser.add_argument('--pdf-only',type=Path,help='Regenerate PDF from an existing Flow Atlas XLSX')
    args=parser.parse_args()
    args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(args.output/'pipeline.log',encoding='utf-8')])
    if args.pdf_only:
        workbook=args.pdf_only
    else:
        path=discover(args.inputs);logging.info('Source: %s',path)
        profiles,ep=read_table(path,'Profils','user_id','eda')
        usages,eu=read_table(path,'Usages IA','id','automobile')
        records=normalize(profiles+usages)
        chunks=rag1.load_corpus(args.corpus)
        retrieved=rag1.run(records,chunks)
        questions=rag2.run(records,read_json(args.answers,{}))
        interpretations=rag3.run(records)
        rule_files=list(args.inputs.rglob('Flow_Atlas_Moteurs_de_regles.xlsx'))
        if len(rule_files)!=1:raise ValueError('A unique business rules workbook is required')
        evidence=ep+eu+rules(rule_files[0])+retrieved
        evidence_ids={e['evidence_id'] for e in evidence}
        for claim in interpretations:
            if not set(claim['evidence_ids'])<=evidence_ids:raise ValueError('Unresolved interpretation evidence')
        payload=dict(schema_version='1.0',mode='local_extractive_rules',records=records,atlas=consolidate(records),
            evidence=evidence,questions=questions,interpretations=interpretations,
            retrieval_status=f'{len(retrieved)} passages candidats' if retrieved else 'Not available - corpus absent ou sans résultat')
        workbook=export(payload,args.output,ROOT)
        logging.info('%s profiles, %s usages, %s questions, %s interpretations',len(profiles),len(usages),len(questions),len(interpretations))
    report=render(workbook,args.output/'flow_atlas_page6.pdf')
    (args.output/'page6_data.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if not args.pdf_only:
        compare(args.inputs,args.output)
    logging.info('Completed: %s',args.output)


if __name__=='__main__':
    main()
