from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    p.text(43,377,'Parcours de référence — les 5 étapes',13,bold=True)
    for i in range(5):
        r=e[f'P14_STEP_{i+1}'];x=43+i*177;p.box(x,291,156,66)
        p.text(x+14,327,str(i+1),20,theme.CYAN,True);p.text(x+41,329,r['label'],11,bold=True)
        p.text(x+41,310,r['display_text'],9,theme.MUTED)
        if i<4:p.text(x+162,319,'>',14,theme.MUTED)
    for i,color in enumerate(['#8584FF',theme.CYAN,'#2AD1A0']):
        r=e[f'P14_CARD_{i+1}'];x=43+i*294;p.box(x,93,280,177)
        p.text(x+20,242,r['label'],14,color,True)
        p.text(x+20,216,r['display_text'],11,bold=True)
        p.para(x+20,195,239,escape(r['detail']),10,theme.MUTED,height=92)
    p.para(43,70,872,escape(e['P14_NOTE']['display_text']),10,theme.MUTED,height=29)
