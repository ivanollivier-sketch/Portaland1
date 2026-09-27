from ..components import Painter
from .. import theme
from reportlab.lib.colors import HexColor


def draw(canvas,rows):
    p=Painter(canvas);p.base(rows)
    groups=[r for r in rows if r['kind']=='group']
    colors=[theme.CYAN,'#8584FF','#2AD1A0']
    for i,group in enumerate(groups):
        x=43+i*295;p.box(x,50,277,339)
        p.text(x+21,365,group['label'],10,colors[i],True)
        items=[r for r in rows if r['kind']=='navigation' and r['group']==group['group']]
        for j,item in enumerate(items):
            y=307-j*43;p.box(x+18,y,241,35,fill='#1A273B',radius=6)
            p.text(x+33,y+13,item['label'],11)
            if item['display_text']:
                canvas.setStrokeColor(HexColor(colors[i]))
                canvas.roundRect(x+205,y+7,43,21,11,fill=0,stroke=1)
                p.text(x+215,y+14,item['display_text'],9,colors[i],True)
        if i==2:
            note=next(r for r in rows if r['element_id']=='P3_NOTE')
            p.para(x+18,285,241,note['display_text'],11,theme.MUTED,height=190)
