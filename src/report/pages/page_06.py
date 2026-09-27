"""Existing page-six geometry, fed only by the canonical page payload."""
from reportlab.lib.colors import HexColor
from ..components import Painter


def draw(c,rows):
    e={r['element_id']:r for r in rows};p=Painter(c)
    c.setFillColor(HexColor('#0B1220'));c.rect(0,0,960,540,fill=1,stroke=0)
    h=e['P6_HEADER'];f=e['P6_FOOTER']
    p.text(43,501,h['eyebrow'],10,'#20D3E8',True)
    p.text(43,462,h['display_text'],27,bold=True)
    p.text(43,429,h['detail'],12,'#9BAEC9')
    p.box(43,51,453,340)
    c.setStrokeColor(HexColor('#52627A'));c.setLineWidth(9);c.circle(128,304,44,stroke=1,fill=0)
    p.text(104,296,e['P6_KPI_01']['display_text'],24,bold=True)
    p.para(202,342,268,e['P6_VERDICT']['display_text'],18,height=75)
    p.para(202,280,261,e['P6_VERDICT']['detail'],11,'#9BAEC9',height=50)
    p.para(69,220,401,e['P6_POINT']['display_text'],12,height=65)
    p.para(69,148,401,e['P6_URGENCY']['display_text'],12,height=55)
    p.para(69,88,401,e['P6_MONEY']['display_text'],11,height=43)
    p.text(525,377,e['P6_PRIORITIES']['label'],18,bold=True)
    p.text(525,352,e['P6_PRIORITIES']['detail'],10,'#9BAEC9')
    for i in range(3):
        y=251-i*80;p.box(525,y,391,68);p.text(540,y+30,str(i+1),24,'#20D3E8',True)
        r=e.get(f'P6_INSIGHT_{i+1:02}')
        if r:
            p.para(580,y+57,321,r['display_text'],11,height=42)
            p.text(580,y+10,r['detail'],8,'#FFC432')
        else:p.text(580,y+29,'Aucune proposition supplémentaire étayée.',10)
    p.para(525,75,391,e['P6_EXPOSURE']['display_text'],10,'#9BAEC9',height=35)
    p.text(43,23,f['display_text'],8,'#7285A2');p.text(850,23,f['detail'],8,'#7285A2')
