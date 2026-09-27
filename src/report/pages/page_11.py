from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows);r=e['P11_FEATURED']
    p.box(43,96,260,297)
    p.para(61,377,224,escape(r['display_text']),9,'#FFC432',height=30)
    p.para(61,338,224,'<b>'+escape(r['label'])+'</b>',16,theme.CYAN,height=45)
    p.para(61,285,224,escape(r['detail']),9.5,theme.MUTED,height=39)
    p.pill(61,209,116,22,r['state'],'#2AD1A0')
    p.para(61,196,224,escape('Risque : '+r['risk']+' · '+r['environment']),10,'#FFC432',height=29)
    p.text(61,152,r['scores'],11,theme.MUTED)
    p.text(61,124,r['cost'],15,bold=True)
    p.pill(203,118,84,22,r['decision'],'#FF7477' if r['decision']=='Arrêter' else theme.CYAN)
    p.box(321,46,594,347);p.text(339,369,'La fiche IA — champs disponibles et à compléter',13,bold=True)
    for i in range(6):
        row=e[f'P11_FIELD_{i+1}'];top=336-i*47
        p.text(339,top-11,row['label'],11,theme.CYAN,True)
        p.para(454,top,440,escape(row['display_text']),10,height=39)
    p.para(43,82,260,escape(e['P11_NOTE']['display_text']),8.5,theme.MUTED,height=36)
