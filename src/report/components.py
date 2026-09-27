from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from . import theme


class Painter:
    def __init__(self,canvas):
        self.c=canvas

    def text(self,x,y,value,size=12,color=theme.TEXT,bold=False):
        self.c.setFillColor(HexColor(color));self.c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
        self.c.drawString(x,y,str(value))

    def para(self,x,top,width,content,size=11,color=theme.TEXT,height=90):
        p=Paragraph(content,ParagraphStyle('body',fontName='Helvetica',fontSize=size,leading=size*1.4,textColor=HexColor(color)))
        _,h=p.wrap(width,height)
        if h>height:raise ValueError(f'PDF content exceeds reserved area: {content}')
        p.drawOn(self.c,x,top-h)

    def box(self,x,y,w,h,fill=theme.CARD,radius=9):
        self.c.setLineWidth(.8);self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(theme.BORDER))
        self.c.roundRect(x,y,w,h,radius,fill=1,stroke=1)

    def pill(self,x,y,w,h,label,color):
        self.c.setFillColor(HexColor(color));self.c.roundRect(x,y,w,h,h/2,fill=1,stroke=0)
        self.text(x+12,y+h/2-3,label,9,theme.BACKGROUND,True)

    def base(self,rows):
        index={r['element_id']:r for r in rows};page=rows[0]['element_id'].split('_')[0][1:]
        header=index[f'P{page}_HEADER'];footer=index[f'P{page}_FOOTER']
        self.c.setFillColor(HexColor(theme.BACKGROUND));self.c.rect(0,0,960,540,fill=1,stroke=0)
        self.text(43,501,header['eyebrow'],10,theme.CYAN,True)
        from reportlab.pdfbase.pdfmetrics import stringWidth
        title_size=min(27,874/stringWidth(header['display_text'],'Helvetica-Bold',1))
        self.text(43,462,header['display_text'],title_size,bold=True)
        self.para(43,438,874,header['detail'],12,theme.MUTED,height=37)
        self.text(43,23,footer['display_text'],8,'#7285A2');self.text(910,23,footer['detail'],8,'#7285A2')
        return index
