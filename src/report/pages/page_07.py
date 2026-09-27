from html import escape
from ..components import Painter
from ..charts import horizontal_bars
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);e=p.base(rows)
    for i in range(4):
        r=e[f'P7_KPI_{i+1:02}'];x=43+i*220;p.box(x,309,206,87)
        p.text(x+16,365,'N/D' if r['value'] is None else r['display_text'],23,['#E4ECF8','#FF7477','#FFC432','#9BAEC9'][i],True)
        p.para(x+16,351,178,escape(r['label']),10,theme.MUTED,height=29)
        p.text(x+16,318,r['detail'],8,theme.MUTED)
    p.box(43,47,425,249);p.text(61,272,e['P7_CHART_01']['label'],12,bold=True)
    bars=[r for r in rows if r.get('group')=='P7_CHART_01']
    horizontal_bars(p,bars,60,235,109,262,183)
    for i,color in enumerate(['#2AD1A0','#FF7477','#8584FF']):
        r=e[f'P7_INSIGHT_{i+1:02}'];y=219-i*86;p.box(482,y,432,77)
        p.text(500,y+58,r['label'],12,color,True)
        p.para(500,y+46,396,escape(r['display_text']),9.5,theme.MUTED,height=43)
