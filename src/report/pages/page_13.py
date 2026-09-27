from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    for i in range(3):
        r=e[f'P13_PILLAR_{i+1}'];x=43+i*294;p.box(x,122,280,271)
        p.pill(x+21,329,43,43,str(i+1),r['color']);p.text(x+187,345,'N/D',12,theme.MUTED,True)
        p.text(x+21,296,r['label'],18,bold=True)
        p.para(x+21,271,235,escape(r['display_text']),11,height=64)
        p.para(x+21,196,235,'Champs à fournir :<br/>'+escape(r['detail']),10,theme.MUTED,height=60)
    p.box(43,46,868,62,fill='#1B283E')
    p.para(64,91,824,escape(e['P13_NOTE']['display_text']),11,height=41)
