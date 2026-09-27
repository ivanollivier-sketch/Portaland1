"""Vector layouts for the cover, promise and report pages 15–32.

Only geometry and formatting live here. Business data comes from the page payload.
"""
from html import escape
from math import cos,sin,pi
from reportlab.lib.colors import HexColor
from ..components import Painter
from ..charts import horizontal_bars
from .. import theme

COLORS=['#20D3E8','#8584FF','#2AD1A0','#FFC432','#FF7477','#ED6EC0']


def draw(canvas,rows):
    p=Painter(canvas);page=int(rows[0]['element_id'].split('_')[0][1:]);e={r['element_id'].split('_',1)[1]:r for r in rows}
    def items(kind):return [r for r in rows if r['kind']==kind]
    def para(x,top,w,text,size=11,color=theme.TEXT,height=90):p.para(x,top,w,escape(str(text)).replace('\n','<br/>'),size,color,height)
    def card(r,x,y,w,h,color=None,size=11):
        p.box(x,y,w,h)
        para(x+18,y+h-17,w-36,r['label'],12,color or r.get('color',theme.CYAN),40)
        body_offset=46 if h<120 else 61
        para(x+18,y+h-body_offset,w-36,r['display_text'],size,theme.TEXT,h-body_offset-14)
        if r.get('detail'):para(x+18,y+42,w-36,r['detail'],9,theme.MUTED,34)
    def note(key='NOTE',top=75):
        r=e[key];p.box(43,43,872,top-34,fill='#1B283E');para(60,top-3,838,r['display_text'],10,theme.MUTED,top-51)
    def rowcards(kind='card',x=620,y=49,w=295,h=344):
        rr=items(kind);pitch=h/len(rr)
        for i,r in enumerate(rr):
            yy=y+h-(i+1)*pitch;p.box(x,yy,w,pitch-9)
            para(x+16,yy+pitch-17,w-32,r['label'],11,r.get('color',theme.CYAN),20)
            para(x+16,yy+pitch-36,w-32,r['display_text'],9.5,theme.MUTED,pitch-41)
    if page==1:
        canvas.setFillColor(HexColor(theme.BACKGROUND));canvas.rect(0,0,960,540,fill=1,stroke=0)
        p.pill(43,440,56,55,'FF','#6366F1');p.text(119,465,e['HEADER']['eyebrow'],11,theme.MUTED,True)
        p.text(43,333,e['HEADER']['display_text'],38,bold=True)
        para(43,308,550,e['HEADER']['detail'],18,theme.CYAN,60)
        para(43,237,548,e['INTRO']['display_text'],12,theme.MUTED,83)
        para(43,157,550,e['SCOPE']['display_text'],12,theme.TEXT,34)
        for i,r in enumerate(items('tag')):p.pill(43+i*130,87,117,29,r['label'],COLORS[i])
        p.box(620,89,295,333);canvas.setStrokeColor(HexColor(theme.BORDER));canvas.setLineWidth(15);canvas.circle(767,304,71,fill=0,stroke=1)
        p.text(730,293,e['GAUGE']['display_text'],32,theme.MUTED,True)
        para(646,202,245,e['GAUGE']['label'],13,theme.TEXT,40);para(646,146,245,e['GAUGE']['detail'],10,theme.MUTED,38)
        p.text(43,23,e['FOOTER']['display_text'],8,theme.MUTED);p.text(910,23,'1',8,theme.MUTED)
        return
    p.base(rows)
    if page==2:
        for i,r in enumerate(items('card')):card(r,43+i*294,122,280,271,size=12)
        note(top=101)
    elif page==15:
        for i,r in enumerate(items('step')):
            x=43+i*147;p.pill(x+37,327,47,47,str(i+1),COLORS[i]);para(x,312,137,r['label'],11,theme.TEXT,33);para(x,272,134,r['display_text'],9,theme.MUTED,40)
            if i<5:p.text(x+130,345,'>',15,theme.MUTED)
        for i,r in enumerate(items('card')):card(r,43+i*294,47,280,161,size=11)
    elif page==16:
        p.box(43,48,288,345);p.text(61,366,'Palette du rapport',13,bold=True)
        for i,r in enumerate(items('swatch')):
            y=320-i*39;p.box(61,y,35,28,fill=r['color'],radius=4);p.text(109,y+10,r['label'],10);p.text(249,y+10,r['display_text'],8,theme.MUTED)
        p.box(345,48,570,345);p.text(363,366,'Composants récurrents',13,bold=True)
        for i,r in enumerate(items('row')):
            top=337-i*40;para(363,top,162,r['label'],10,theme.CYAN,29);para(538,top,354,r['display_text'],9.5,theme.MUTED,33)
    elif page==17:
        for i,r in enumerate(items('card')):card(r,43+(i%2)*443,279-(i//2)*115,429,104,color=COLORS[i%6],size=10)
    elif page==18:
        for i,r in enumerate(items('row')):
            top=379-i*65;p.pill(43,top-32,39,39,str(i+1),theme.CYAN);para(101,top,315,r['label'],13,theme.TEXT,48);para(439,top,469,r['display_text'],11,theme.MUTED,48)
    elif page==19:
        # Keep the title in the header for navigation, then a large section divider.
        para(43,353,860,e['FROM']['label'],28,theme.MUTED,50)
        para(43,281,852,e['TO']['label'],30,theme.TEXT,126)
        para(43,124,852,e['NOTE']['display_text'],12,theme.MUTED,63)
    elif page==20:
        p.box(43,49,403,344);p.text(61,369,e['CHART']['label'],12,bold=True)
        slices=items('slice');total=sum(r['value'] for r in slices);angle=90
        for r in slices:
            extent=360*r['value']/total if total else 0
            canvas.setFillColor(HexColor(r['color']));canvas.wedge(76,145,290,359,angle,extent,fill=1,stroke=0);angle+=extent
        canvas.setFillColor(HexColor(theme.CARD));canvas.circle(183,252,78,fill=1,stroke=0)
        p.text(138,247,e['CHART']['display_text'],24,'#8584FF',True)
        for i,r in enumerate(slices):p.text(309,322-i*59,r['display_text'],22,r['color'],True);p.text(309,302-i*59,r['label'],10,theme.MUTED)
        para(61,107,365,e['CHART']['detail'],11,theme.MUTED,38)
        rowcards(x=465,w=450)
    elif page==21:
        p.text(225,389,"AUJOURD'HUI",10,theme.MUTED,True);p.text(501,389,'DEMAIN',10,theme.CYAN,True)
        for i,r in enumerate(items('row')):
            y=333-i*43;p.box(43,y,872,37,fill=theme.CARD if i%2 else '#1B283E',radius=5);p.text(61,y+14,r['label'],10,theme.CYAN,True)
            para(225,y+27,230,r['display_text'],10,theme.MUTED,28);p.text(475,y+14,'>',11,theme.MUTED);para(501,y+27,395,r['detail'],10,theme.TEXT,28)
    elif page==22:
        p.box(43,49,556,344);p.text(61,371,e['CHART']['label'],12,bold=True);p.text(61,350,e['CHART']['display_text'],8,'#FFC432')
        points=items('point');labels=list(dict.fromkeys(r['label'] for r in points));x0=87;y0=112;w=476;h=215
        canvas.setLineWidth(.5)
        for value in range(0,101,20):
            yy=y0+value/100*h;canvas.setStrokeColor(HexColor(theme.BORDER));canvas.line(x0,yy,x0+w,yy);p.text(x0-28,yy-3,value,9,theme.MUTED)
        for i,label in enumerate(labels):p.text(x0+i*w/max(1,len(labels)-1)-13,y0-18,label,8,theme.MUTED)
        for j,series in enumerate(dict.fromkeys(r['group'] for r in points)):
            last=None;color=COLORS[j];canvas.setStrokeColor(HexColor(color));canvas.setFillColor(HexColor(color));canvas.setLineWidth(2)
            for r in [r for r in points if r['group']==series]:
                if r['value'] is None:last=None;continue
                pos=(x0+labels.index(r['label'])*w/max(1,len(labels)-1),y0+r['value']/100*h)
                if last:canvas.line(*last,*pos)
                canvas.circle(*pos,2.5,fill=1,stroke=0);last=pos
            p.text(101+j*155,68,series,9,color)
        if not points:para(87,248,470,'Illustration indisponible : fichier PPTX source absent.',13,theme.MUTED,70)
        rowcards()
    elif page==23:
        p.box(43,49,571,344);p.text(61,370,e['TABLE']['label'],12,bold=True);p.text(61,349,e['TABLE']['display_text'],8,'#FFC432')
        for x,label in [(61,'Capacité'),(294,'Experts'),(351,'IA'),(397,'Départs < 3 ans'),(499,'Risque')]:p.text(x,316,label,8,theme.MUTED)
        for i,r in enumerate(items('table_row')):
            y=256-i*42;p.box(55,y,548,35,fill='#1B283E',radius=4);para(61,y+24,224,r['label'],9,theme.TEXT,25)
            for x,key in [(308,'experts'),(355,'ai'),(430,'departures')]:p.text(x,y+13,r[key],11,bold=True)
            p.pill(489,y+7,105,21,r['display_text'],['#FF7477','#FFC432','#FFC432','#2AD1A0','#8584FF'][i])
        rowcards(x=630,w=285)
    elif page==24:
        for i,r in enumerate(items('step')):
            x=43+i*177;p.box(x,281,164,112);para(x+13,377,138,r['label'],10,r['color'],28);para(x+13,343,138,r['display_text'],10,theme.TEXT,53)
            if i<4:p.text(x+165,330,'>',12,theme.MUTED)
        p.box(43,49,438,218);p.text(61,245,e['CHART']['label'],12,bold=True);p.text(61,227,e['CHART']['display_text'],8,'#FFC432')
        bars=items('illustration_bar');maximum=max((r['value'] for r in bars),default=1)*1.15
        for i,r in enumerate(bars):
            x=74+i*100;height=121*r['value']/maximum;canvas.setFillColor(HexColor(r['color']));canvas.rect(x,90,64,height,fill=1,stroke=0);p.text(x+5,96+height,r['display_text'],10);para(x-8,81,96,r['label'],8,theme.MUTED,28)
        if not bars:para(61,178,393,'Illustration indisponible : fichier PPTX source absent.',11,theme.MUTED,60)
        # Compact right-hand explanations.
        for i,r in enumerate(items('card')):
            y=199-i*75;p.box(498,y,417,68);p.text(514,y+48,r['label'],10,theme.CYAN,True);para(514,y+35,382,r['display_text'],9,theme.MUTED,29)
    elif page==25:
        p.box(43,49,330,344,fill='#1B283E');r=e['PROVIDER'];p.text(61,368,r['label'],12,'#FFC432',True);para(61,335,293,r['display_text'],23,theme.TEXT,70);para(61,257,290,r['detail'],12,theme.MUTED,65)
        for i,r in enumerate(items('provider_usage')[:4]):para(61,183-i*30,288,r['label']+' · '+r['display_text'],9,theme.MUTED,27)
        para(61,70,285,'Libellé source ; famille de modèle N/D.',8,theme.MUTED,18)
        rowcards('row',x=391,w=524)
    elif page==26:
        p.box(43,49,404,344);p.text(61,368,e['CHART']['label'],12,bold=True)
        horizontal_bars(p,items('bar'),66,322,104,228,205)
        para(61,124,364,e['CHART']['display_text'],11,theme.MUTED,57)
        rowcards(x=465,w=450)
    elif page==27:
        cx=226;cy=235;rad=128;canvas.setLineWidth(1);canvas.setDash(4,4);canvas.setStrokeColor(HexColor(theme.BORDER));canvas.circle(cx,cy,rad,fill=0,stroke=1);canvas.setDash()
        for i,r in enumerate(items('step')):
            angle=pi/2-i*pi/3;x=cx+rad*cos(angle);y=cy+rad*sin(angle);p.pill(x-22,y-22,44,44,str(i+1),COLORS[i]);p.text(426,367-i*42,f"{i+1}. {r['label']}",11,COLORS[i],True);para(562,378-i*42,345,r['display_text'],10,theme.MUTED,30)
        p.text(180,240,'Trimestre',16,bold=True);p.text(165,216,'Le cycle recommence',10,theme.MUTED)
        p.box(410,49,505,66,fill='#1B283E');para(426,98,472,e['NOTE']['display_text'],10,theme.MUTED,43)
    elif page==28:
        for i,r in enumerate(items('card')):
            x=43+(i%3)*199;y=228-(i//3)*161;p.box(x,y,185,150);p.pill(x+15,y+104,30,30,r['label'][0],r['color']);p.text(x+56,y+115,r['label'],12,bold=True);para(x+15,y+86,155,r['display_text'],10,r['color'],29);para(x+15,y+50,155,r['detail'],9,theme.MUTED,43)
        r=e['SYNTHESIS'];p.box(648,67,267,311,fill='#1B283E');p.text(667,349,r['label'],16,theme.CYAN,True);para(667,309,227,r['display_text'],12,theme.TEXT,88);para(667,184,227,r['detail'],11,theme.MUTED,95)
        para(43,55,872,e['NOTE']['display_text'],9,theme.CYAN,20)
    elif page==29:
        for i,r in enumerate(items('card')):
            x=43+(i%3)*294;y=226-(i//3)*177;p.box(x,y,280,164);p.text(x+17,y+141,r['label'],12,r['color'],True);p.text(x+17,y+105,r['display_text'],24,bold=True);para(x+17,y+83,246,r['detail'],10,theme.MUTED,72)
    elif page==30:
        for i,r in enumerate(items('row')):
            y=327-i*66;p.box(43,y,872,56);p.pill(57,y+13,29,29,str(i+1),r['color']);para(99,y+39,148,r['label'],11,theme.TEXT,31);para(263,y+39,366,r['display_text'],10,theme.MUTED,36);para(663,y+39,236,r['detail'],10,r['color'],36)
    elif page==31:
        for i,r in enumerate(items('card')):
            x=43+i*294;p.box(x,49,280,344);p.pill(x+19,350,131,25,r['display_text'],r['color']);para(x+19,330,241,r['label'],18,r['color'],56)
            for j,text in enumerate(r['detail'].split('\n')):p.text(x+20,253-j*48,'•',16,r['color']);para(x+38,263-j*48,222,text,11,theme.TEXT,43)
    elif page==32:
        for i,r in enumerate(items('card')):
            x=43+i*294;p.box(x,125,280,215);p.text(x+20,299,str(i+1),26,r['color'],True);para(x+20,265,241,r['label'],16,theme.TEXT,82);para(x+20,167,241,r['display_text'],11,r['color'],30)
        para(43,70,872,e['NOTE']['display_text'],10,theme.MUTED,27)
    else:raise ValueError(f'Unsupported page {page}')
