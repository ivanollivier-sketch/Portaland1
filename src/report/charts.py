"""Chart geometry only: values/categories are supplied by the report model."""
from html import escape
from reportlab.lib.colors import HexColor
from . import theme


def horizontal_bars(p,rows,x,top,label_width,bar_width,height):
    if not rows:
        p.text(x,top-20,'Aucune donnée disponible',11,theme.MUTED)
        return
    pitch=min(43,height/len(rows))
    if pitch<24:
        raise ValueError('Too many chart categories for one page; narrow the report scope.')
    maximum=max((r['value'] for r in rows if isinstance(r['value'],(int,float))),default=0)
    for i,row in enumerate(rows):
        y=top-i*pitch
        p.para(x,y+10,label_width-10,escape(row['label']),11,theme.MUTED,height=pitch-2)
        value=row['value']
        width=bar_width*value/maximum if isinstance(value,(int,float)) and maximum>0 else 0
        if width>0:
            p.c.setFillColor(HexColor(row.get('color',theme.CYAN)))
            p.c.rect(x+label_width,y-8,width,min(28,pitch-11),fill=1,stroke=0)
        p.text(x+label_width+width+6,y+1,row['display_text'],11)
