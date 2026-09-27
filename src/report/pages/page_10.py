from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    for i in range(6):
        r=e[f'P10_FAMILY_{i+1}'];x=43+i*147
        p.box(x,239,137,154);p.pill(x+10,357,117,22,r['label'].upper(),r['color'])
        p.para(x+11,342,115,'<b>'+escape(r['display_text'])+'</b>',12,height=37)
        p.para(x+11,299,115,escape(r['detail']),9.5,theme.MUTED,height=43)
        p.text(x+11,251,f"{r['value']} proposition(s)",9,r['color'])
    p.box(43,59,872,162)
    p.para(61,207,835,escape(e['P10_NOTE']['display_text']),9.5,theme.MUTED,height=29)
    actions=[r for r in rows if r['kind']=='action'][:3]
    for i,r in enumerate(actions):
        y=158-i*33
        p.text(62,y,'•',16,'#FFC432');p.text(78,y+1,r['label'],11,bold=True)
        p.text(78,y-12,r['display_text'],8.5,theme.MUTED)
        p.para(664,y+4,232,escape(r['detail']),8.5,theme.CYAN,height=27)
