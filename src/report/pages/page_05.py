from html import escape
from reportlab.lib.colors import HexColor
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    gauge=e['P5_KPI_01'];p.box(43,162,238,230)
    canvas.setStrokeColor(HexColor('#52627A'));canvas.setLineWidth(11);canvas.circle(162,309,51,stroke=1,fill=0)
    p.text(137,300,'N/D' if gauge['value'] is None else gauge['display_text'],28,bold=True)
    p.text(90,217,gauge['label'],13,bold=True);p.para(62,196,200,gauge['detail'],9,theme.MUTED,height=28)
    for i in range(4):
        x=295+(i%2)*170;y=284-(i//2)*116;r=e[f'P5_KPI_{i+2:02}']
        p.box(x,y,159,108)
        p.text(x+14,y+75,'N/D' if r['value'] is None else r['display_text'],23,'#9BAEC9' if r['value'] is None else '#2AD1A0',True)
        if r['value'] is not None:p.text(x+57,y+76,'/100',10,theme.MUTED)
        p.para(x+14,y+54,133,escape(r['label']),10,height=30)
        p.para(x+14,y+22,133,r['detail'],9,theme.MUTED,height=25)
    for i in range(4):
        r=e[f'P5_KPI_{i+6:02}'];x=43+i*150;p.box(x,50,140,98)
        p.text(x+14,116,r['display_text'],22,'#FFC432' if i==3 else theme.TEXT,True)
        p.para(x+14,96,116,escape(r['label']),9.5,theme.MUTED,height=32)
        if r['detail']:p.text(x+14,59,r['detail'],7.5,theme.MUTED)
    p.box(655,50,260,342);p.text(672,371,e['P5_PRIORITIES']['label'],13,bold=True)
    p.text(672,351,e['P5_PRIORITIES']['detail'],9,theme.MUTED)
    insights=[r for r in rows if r['kind']=='insight']
    for i,r in enumerate(insights):
        y=286-i*57;p.box(669,y,232,53,fill='#1A273B',radius=6)
        p.text(679,y+40,r['rule_title'],9,bold=True)
        p.para(679,y+32,214,escape(r['display_text']),8.5,height=25)
        p.text(679,y+6,r['detail'],7,'#FFC432')
    if not insights:p.para(675,325,220,'Aucun écart détecté par les règles implémentées.',11,height=65)
