from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    for i in range(4):
        r=e[f'P12_KPI_{i+1}'];x=43+i*220;p.box(x,311,206,82)
        p.text(x+17,365,r['display_text'],22,'#FFC432' if i==0 else theme.TEXT,True)
        p.para(x+17,349,174,escape(r['label']+(' (kEUR/an)' if i==1 else '')),9.5,theme.MUTED,height=29)
    p.box(43,76,362,220);p.text(61,272,'Cartographie par domaine',12,bold=True)
    domain_rows=[r for r in rows if r['kind']=='domain']
    for i,r in enumerate(domain_rows[:5]):
        y=245-i*33
        p.text(61,y,r['label'],10,bold=True);p.text(207,y,r['display_text'],10,theme.CYAN)
        p.para(61,y-7,324,escape(r['detail']),8,theme.MUTED,height=23)
    p.box(419,76,496,220);p.text(437,272,'Plan de rencontre en 3 étapes, par IA',12,bold=True)
    for i in range(3):
        r=e[f'P12_STEP_{i+1}'];y=226-i*54;p.pill(437,y,31,29,str(i+1),theme.CYAN)
        p.para(482,y+29,411,'<font color="#20D3E8"><b>'+escape(r['label'])+'</b></font> : '+escape(r['display_text']),10,height=44)
    p.para(43,64,872,escape(e['P12_NOTE']['display_text']),9,theme.MUTED,height=28)
