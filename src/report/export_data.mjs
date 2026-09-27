import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const [input,output]=process.argv.slice(2);
const {tables}=JSON.parse(await fs.readFile(input,'utf8'));
const wb=Workbook.create();
const dashboard=wb.worksheets.add('03_REPORT_DASHBOARD');
const illustrations=wb.worksheets.add('04_REFERENCE_CHARTS');
const previews=path.join(output,'validation','workbook');
await fs.mkdir(previews,{recursive:true});
function col(n){let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function safe(v){
 if(v===null || v===undefined)return null;
 if(typeof v==='object')return JSON.stringify(v);
 return typeof v==='string' && v.startsWith('=')?"'"+v:v;
}
const sheetInfo=[];
for(const [name,rows] of Object.entries(tables)){
 const sheet=wb.worksheets.add(name);
 const headers=[...new Set(rows.flatMap(r=>Object.keys(r)))];
 const matrix=[headers,...rows.map(r=>headers.map(h=>safe(r[h])))];
 const range=sheet.getRange(`A1:${col(headers.length-1)}${matrix.length}`);
 range.values=matrix;
 range.format={font:{name:'Arial',size:10,color:'#172338'},rowHeight:28,columnWidth:25,wrapText:true,verticalAlignment:'center'};
 sheet.showGridLines=false;sheet.freezePanes.freezeRows(1);
 sheet.tables.add(`A1:${col(headers.length-1)}${matrix.length}`,true,'Table'+name.replace(/[^a-zA-Z0-9]/g,''));
 for(let i=0;i<headers.length;i++){
  const h=headers[i],cells=sheet.getRange(`${col(i)}1:${col(i)}${matrix.length}`);
  if(/text|detail|method|issue$|notes|comment|file|answer|value$|conclusion|question$|transformation/.test(h))cells.format.columnWidth=52;
  if(/ids|evidence|source_record/.test(h))cells.format.columnWidth=46;
  // Long machine-readable arrays stay accessible in the formula bar without
  // expanding a single audit row to hundreds of pixels.
  rows.forEach((r,j)=>{
   if(r[h]!==null && typeof r[h]==='object')sheet.getCell(j+1,i).format.wrapText=false;
  });
  if(/status/.test(h)){
   cells.conditionalFormats.add('containsText',{text:'MISSING',format:{fill:'#FFF1CD',font:{color:'#875B00'}}});
   cells.conditionalFormats.add('containsText',{text:'TO_VALIDATE',format:{fill:'#FFF6E3'}});
  }
  if(h==='severity')cells.conditionalFormats.add('containsText',{text:'critical',format:{fill:'#FFE0E0'}});
  if(h==='confidence_score')cells.setNumberFormat('0.0%');
  if(['metric_value','value','annual_cost_ke','cost_ke'].includes(h)){
   rows.forEach((r,j)=>{if(typeof r[h]==='number')sheet.getCell(j+1,i).setNumberFormat(Number.isInteger(r[h])?'#,##0':'#,##0.0');});
  }
  if(h==='timestamp'){
   rows.forEach((r,j)=>{if(r[h])sheet.getCell(j+1,i).values=[[new Date(r[h])]];});
   cells.setNumberFormat('yyyy-mm-dd hh:mm:ss');
  }
 }
 if(name==='00_README'){
  const i=rows.findIndex(r=>r.item==='Generated at (UTC)');
  sheet.getRange(`C${i+2}`).values=[[new Date(rows[i].value)]];
  sheet.getRange(`C${i+2}`).setNumberFormat('yyyy-mm-dd hh:mm:ss');
  sheet.getRange(`B1:B${matrix.length}`).format.columnWidth=32;
  sheet.getRange(`C1:D${matrix.length}`).format.columnWidth=74;
 }
 range.format.autofitRows();
 sheet.getRange(`A1:${col(headers.length-1)}1`).format={fill:'#15243A',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},rowHeight:36,wrapText:true};
 sheetInfo.push({name,last:matrix.length,columns:headers.length});
}
// Reader-facing charts link to the canonical audit rows, without recalculating
// business rules in a second engine. Reference examples have a separate sheet.
for(const sheet of [dashboard,illustrations]){
 sheet.showGridLines=false;sheet.freezePanes.freezeRows(3);
 sheet.getRange('A1:T46').format={font:{name:'Arial',size:10,color:'#172338'},columnWidth:12,rowHeight:24,verticalAlignment:'center'};
 sheet.getRange('A1:T2').merge();sheet.getRange('A1').values=[[sheet===dashboard?'PORTALAND — Synthèse du portefeuille':'ILLUSTRATIONS DE LA RÉFÉRENCE — aucune prévision du portefeuille']];
 sheet.getRange('A1:T2').format={fill:'#15243A',font:{name:'Arial',size:15,color:'#FFFFFF',bold:true}};
 sheet.getRange('A4:A46').format.columnWidth=29;sheet.getRange('B4:B46').format.columnWidth=15;
}
dashboard.getRange('A3:T3').merge();dashboard.getRange('A3').values=[['Valeurs liées à 09_REPORT_METRICS. Rafraîchir les sources avec report.py ; les décisions restent à valider.']];
illustrations.getRange('A3:T3').merge();illustrations.getRange('A3').values=[['Exemples des pages 22 et 24, liés aux données du document source ; séries réelles du portefeuille indisponibles.']];
const metrics=tables['09_REPORT_METRICS'];
function linkedMetric(sheet,cell,mid){
 const i=metrics.findIndex(r=>r.metric_id===mid);if(i<0)throw new Error('Missing metric '+mid);
 const ref=`'09_REPORT_METRICS'!C${i+2}`;
 sheet.getRange(cell).formulas=[[`=IF(ISBLANK(${ref}),"",${ref})`]];
}
function addChart(sheet,range,type,title,start,end,colors=['#20A9BE','#818CF8','#24B889']){
 const chart=sheet.charts.add(type,sheet.getRange(range));chart.title=title;chart.setPosition(start,end);
 chart.titleTextStyle.fontSize=13;chart.titleTextStyle.typeface='Arial';
 chart.legend={position:'bottom',textStyle:{typeface:'Arial',fontSize:10}};
 chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
 chart.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
 chart.series.items.forEach((s,i)=>{s.fill=colors[i%colors.length];if(type==='line')s.line={fill:colors[i%colors.length],style:'solid',width:2};});
 return chart;
}
const metricGroups=[
 {top:5,title:'Décisions (usages)',mids:['defensive','maintain','offensive','other_decisions'],start:'F5',end:'M20'},
 {top:15,title:'Statuts (usages)',mids:metrics.filter(r=>r.metric_id.startsWith('stage_')).map(r=>r.metric_id),start:'N5',end:'U20'},
 {top:25,title:'Coûts actifs par domaine (kEUR/an)',mids:metrics.filter(r=>r.metric_id.startsWith('domain_')).map(r=>r.metric_id),start:'F23',end:'M39'},
 {top:36,title:'Risques déclarés (IA actives)',mids:metrics.filter(r=>r.metric_id.startsWith('risk_')).map(r=>r.metric_id),start:'N23',end:'U39'},
];
for(const g of metricGroups){
 dashboard.getRange(`A${g.top}:B${g.top}`).values=[['Catégorie',g.title]];
 dashboard.getRange(`A${g.top}:B${g.top}`).format={fill:'#E6EEF5',font:{bold:true},wrapText:true,rowHeight:40};
 g.mids.forEach((mid,i)=>{const row=g.top+i+1;dashboard.getRange(`A${row}`).values=[[metrics.find(m=>m.metric_id===mid).metric_name]];linkedMetric(dashboard,`B${row}`,mid);});
 addChart(dashboard,`A${g.top}:B${g.top+g.mids.length}`,'bar',g.title,g.start,g.end);
}
const sourceExamples=tables['44_REFERENCE_EXAMPLES']||[];
const chartRows=sourceExamples.filter(r=>r.reference_page===22);
const periods=[...new Set(chartRows.map(r=>r.category))],series=[...new Set(chartRows.map(r=>r.series))];
if(periods.length){
 illustrations.getRange('A5:D5').values=[['Trimestre',...series]];
 periods.forEach((period,i)=>{
  illustrations.getRange(`A${i+6}`).values=[[period]];
  series.forEach((s,j)=>{const idx=sourceExamples.findIndex(r=>r.reference_page===22&&r.category===period&&r.series===s);const ref=`'44_REFERENCE_EXAMPLES'!D${idx+2}`;illustrations.getRange(`${col(j+1)}${i+6}`).formulas=[[`=IF(ISBLANK(${ref}),"",${ref})`]];});
 });
 addChart(illustrations,`A5:D${periods.length+5}`,'line','Trajectoire illustrative (/100)','F5','P19');
}
const finance=sourceExamples.filter(r=>r.reference_page===24);
if(finance.length){
 illustrations.getRange('A22:B22').values=[['Catégorie','Exemple (kEUR)']];
 finance.forEach((r,i)=>{illustrations.getRange(`A${i+23}`).values=[[r.category]];const idx=sourceExamples.indexOf(r);illustrations.getRange(`B${i+23}`).formulas=[[`='44_REFERENCE_EXAMPLES'!D${idx+2}`]];});
 addChart(illustrations,`A22:B${finance.length+22}`,'bar','Bilan financier illustratif (kEUR)','F22','P37');
}
illustrations.getRange('A5:D5').format={fill:'#FFF1CD',font:{bold:true}};illustrations.getRange('A22:B22').format={fill:'#FFF1CD',font:{bold:true}};
wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:5},maxChars:600})).ndjson);
for(const info of sheetInfo){
 const end=info.name==='00_README'?'D':'F';
 const blob=await wb.render({sheetName:info.name,range:`A1:${end}${Math.min(info.last,5)}`,scale:1,format:'png'});
 await fs.writeFile(path.join(previews,info.name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
for(const sheet of [dashboard,illustrations]){
 const blob=await wb.render({sheetName:sheet.name,range:'A1:U43',scale:1,format:'png'});
 await fs.writeFile(path.join(previews,sheet.name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(output,'portaland_report_data.xlsx'));
console.log(`Exported ${sheetInfo.length} audit worksheets and 2 chart worksheets.`);
