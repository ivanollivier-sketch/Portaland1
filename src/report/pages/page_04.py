from html import escape
from ..components import Painter
from ..charts import horizontal_bars
from .. import theme


def draw(canvas,rows):
    p=Painter(canvas);index=p.base(rows)
    definitions=[r for r in rows if r['kind']=='definition']
    for i,row in enumerate(definitions):
        y=353-i*54
        p.pill(43,y,123,27,row['label'].upper(),row['color'])
        p.para(180,y+24,328,escape(row['display_text']),11,height=42)
    p.box(525,57,391,339)
    p.para(547,380,350,index['P4_CHART_01']['label'],13,height=22)
    p.text(547,344,index['P4_CHART_01']['detail'],10,theme.MUTED)
    bars=[r for r in rows if r.get('group')=='P4_CHART_01']
    horizontal_bars(p,bars,551,312,86,236,253)
