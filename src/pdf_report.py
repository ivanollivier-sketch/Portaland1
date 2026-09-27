"""Backward-compatible page-six entry point, using the common report model."""
from reportlab.pdfgen import canvas
from .data.report_model import build_model,read_table as read_sheet
from .report.pages.page_06 import draw


def render(workbook, output):
    model=build_model(workbook)
    c=canvas.Canvas(str(output),pagesize=(960,540))
    c.setTitle('Flow Atlas - Synthèse dirigeant')
    draw(c,model['pages']['6']);c.showPage();c.save()
    m={r['metric_id']:r['metric_value'] for r in model['metrics']}
    labels={'Usages inventoriés':'usage_count','Usages actifs':'active_count',
            'Coût actif (kEUR/an)':'active_cost','Coût étiqueté Arrêter (kEUR/an)':'stop_cost',
            'Score de portefeuille (/100)':'portfolio_score','Indice global':'alignment'}
    metrics={label:m[mid] if m[mid] is not None else 'Unknown' for label,mid in labels.items()}
    metrics.update({'Périmètre':model['scope'],'Verdict':'Cockpit incomplet','Profils EDA':len(model['profiles']),
                    'Validation':'To validate','Économies confirmées':'Unknown'})
    return {'metrics':metrics,'recommendation_ids':[r['analysis_id'] for r in model['pages']['6'] if r.get('analysis_id')]}
