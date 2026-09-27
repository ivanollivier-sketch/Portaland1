"""Generate the complete 32-page Portaland report from a Flow Atlas workbook."""
import argparse
import importlib
import json
from pathlib import Path
from main import ensure_runtime


def main():
    ensure_runtime()
    from src.data.report_model import build_model,save_model
    from reportlab.pdfgen import canvas
    root=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas',type=Path,default=root/'output/flow_atlas.xlsx')
    parser.add_argument('--output',type=Path,default=root/'output/report_01_32')
    parser.add_argument('--reference',type=Path,default=root/'inputs/1. Fichier et RAG/Flow_Atlas_presentation.pdf')
    parser.add_argument('--dataset')
    parser.add_argument('--page',type=int,choices=range(1,33))
    parser.add_argument('--data-only',action='store_true',help='Generate canonical JSON and audit Excel without rendering PDF')
    parser.add_argument('--validate',action='store_true',help='Render and compare reference/generated pages and verify traceability')
    args=parser.parse_args()
    if args.page and args.data_only:parser.error('--data-only cannot be combined with --page')
    model=build_model(args.atlas,args.dataset,args.reference)
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'pages').mkdir(exist_ok=True)
    save_model(model,args.output/'portaland_report_model.json')
    if not args.page:
        from src.report.data_book import export_book
        export_book(model,args.output,root)
    if args.data_only:return
    for page in ([args.page] if args.page else range(1,33)):
        module=importlib.import_module(f'src.report.pages.page_{page:02}' if 3<=page<=14 else 'src.report.pages.completion')
        target=args.output/'pages'/f'page_{page:02}.pdf'
        c=canvas.Canvas(str(target),pagesize=(960,540));c.setTitle(f'Portaland - page {page}')
        module.draw(c,model['pages'][str(page)]);c.showPage();c.save()
        print(f'Generated {target.name}')
    if not args.page:
        from pypdf import PdfWriter
        merged=PdfWriter()
        for page in range(1,33):merged.append(args.output/'pages'/f'page_{page:02}.pdf')
        merged.add_metadata({'/Title':'Portaland - Flow Atlas - Rapport complet 32 pages'})
        merged.write(args.output/'portaland_report.pdf');merged.close()
        from src.report.validation import validate_snapshot
        validate_snapshot(model,args.output,args.reference,visual=args.validate)


if __name__=='__main__':main()
