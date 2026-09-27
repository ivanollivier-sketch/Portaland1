from html import escape
from ..components import Painter
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    for x,w in [(43,350),(407,231),(652,263)]:p.box(x,72,w,321)
    p.text(61,369,'Simulateur — 4 scénarios',12,bold=True)
    for i in range(4):
        r=e[f'P9_SCENARIO_{i+1}'];top=341-i*63
        p.pill(61,top-17,30,20,str(i+1),theme.CYAN if r['selected'] else '#9BAEC9')
        p.para(103,top,270,escape(r['label']),10.5,height=29)
        p.para(103,top-30,268,escape(r['display_text']+' · '+r['detail']),8.5,theme.MUTED,height=30)
    p.text(425,369,'Impact simulé',12,bold=True)
    p.text(425,343,'Avant  >  après retrait E7',9,theme.MUTED)
    for i in range(7):
        r=e[f'P9_IMPACT_{i+1}'];y=316-i*34
        p.text(425,y,r['label'],9,theme.MUTED)
        p.text(425,y-15,r['display_text'],12,theme.CYAN,True)
    r=e['P9_ARBITRATION'];p.text(670,369,r['label'],12,bold=True)
    p.para(670,339,224,escape(r['detail']),10,theme.MUTED,height=102)
    for i,(label,color) in enumerate([('Valider','#2AD1A0'),('Reporter','#FFC432'),('Rejeter','#FF7477')]):p.pill(682,212-i*37,173,26,label+' · N/D',color)
    p.para(670,122,222,'Décision à recueillir auprès du responsable. Aucun bouton actif dans ce PDF.',9,theme.MUTED,height=44)
    p.para(43,59,872,escape(e['P9_CAUTION']['display_text']),9,theme.MUTED,height=26)
