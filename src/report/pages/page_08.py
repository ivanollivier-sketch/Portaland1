from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    for i in range(6):
        r=e[f'P8_CARD_{i+1}'];x=43+(i%2)*290;y=291-(i//2)*115
        p.box(x,y,275,102)
        p.para(x+18,y+86,210,escape(r['label']),11,height=32)
        p.text(x+233,y+82,r['display_text'],14,theme.CYAN,True)
        p.para(x+18,y+49,238,escape(r['detail']),9.5,theme.CYAN,height=44)
    p.box(633,61,282,332)
    r=e['P8_LEGEND'];p.text(651,368,r['label'],13,bold=True)
    p.para(651,343,242,escape(r['display_text']).replace('\n','<br/><br/>'),10,theme.MUTED,height=158)
    r=e['P8_EXAMPLE'];p.para(651,184,242,'<b>'+escape(r['label'])+'</b>',12,theme.CYAN,height=36)
    p.para(651,140,242,escape(r['display_text']),10,height=45)
    p.para(651,91,242,escape(r['detail']),9,theme.MUTED,height=24)
