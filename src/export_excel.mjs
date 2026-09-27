import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input, output] = process.argv.slice(2);
const p = JSON.parse(await fs.readFile(input, 'utf8'));
const wb = Workbook.create();
const summary = wb.worksheets.add('Synthese');
function col(n) { let s=''; for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s; }
function safe(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === 'object') return JSON.stringify(v);
  return typeof v === 'string' && /^[=+@]/.test(v) ? "'"+v : v;
}
function table(name, rows) {
  const sheet=wb.worksheets.add(name);
  const headers=Object.keys(rows[0] ?? {information:null});
  const matrix=[headers,...rows.map(r=>headers.map(h=>safe(r[h])))];
  const range=sheet.getRange(`A1:${col(headers.length-1)}${matrix.length}`);
  range.values=matrix;
  range.format.font={name:'Arial',size:10,color:'#172338'};
  range.format.rowHeight=58;
  range.format.columnWidth=27;
  range.format.wrapText=true;
  range.format.verticalAlignment='center';
  sheet.getRange(`A1:${col(headers.length-1)}1`).format={fill:'#15243A',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:36};
  sheet.showGridLines=false;
  sheet.freezePanes.freezeRows(1);
  if(rows.length)sheet.tables.add(`A1:${col(headers.length-1)}${matrix.length}`,true,name+'Table');
  headers.forEach((h,i)=>{
    if(/evidence|ids|comment|conclusion|question|value|locator|file/.test(h))sheet.getRange(`${col(i)}1:${col(i)}${matrix.length}`).format.columnWidth=48;
  });
  range.format.autofitRows();
  return {sheet,headers,last:matrix.length};
}
const atlas=table('Atlas', p.atlas.map(r=>({...r, active:null, active_cost_ke:null, portfolio_points:null, stop_cost_ke:null})));
table('Questions',p.questions);
table('Interpretations',p.interpretations);
table('Preuves',p.evidence);
const field=h=>col(atlas.headers.indexOf(h));
const area=h=>`'Atlas'!${field(h)}2:${field(h)}${atlas.last}`;
for(let r=2;r<=atlas.last;r++){
  const cell=h=>`${field(h)}${r}`;
  atlas.sheet.getRange(cell('active')).formulas=[[`=IF(AND(${cell('dataset')}="automobile",${cell('record_type')}="usage",OR(${cell('status')}="Production",${cell('status')}="Pilote")),1,0)`]];
  atlas.sheet.getRange(cell('active_cost_ke')).formulas=[[`=IF(AND(${cell('active')}=1,ISNUMBER(${cell('annual_cost_ke')})),${cell('annual_cost_ke')},"")`]];
  atlas.sheet.getRange(cell('portfolio_points')).formulas=[[`=IF(AND(${cell('active')}=1,ISNUMBER(${cell('value_score')}),ISNUMBER(${cell('adoption_score')})),${cell('value_score')}*${cell('adoption_score')},"")`]];
  atlas.sheet.getRange(cell('stop_cost_ke')).formulas=[[`=IF(AND(${cell('active')}=1,${cell('source_decision')}="Arrêter",ISNUMBER(${cell('annual_cost_ke')})),${cell('annual_cost_ke')},"")`]];
}
const metrics=[
 ['Indicateur','Valeur','Définition'],
 ['Périmètre','Automobile','Organisation à confirmer ; profils EDA conservés séparément.'],
 ['Usages inventoriés',null,'Nombre de lignes usage dans le périmètre automobile.'],
 ['Usages actifs',null,'Production et Pilote.'],
 ['Coût actif (kEUR/an)',null,'Somme des coûts déclarés des usages actifs ; inconnue si coût manquant.'],
 ['Coût étiqueté Arrêter (kEUR/an)',null,'Décisions du fichier source. Économies réalisables : Unknown.'],
 ['Score de portefeuille (/100)',null,'M6 Indices!B8 : somme valeur × usage / (25 × nombre actif). Score déclaratif.'],
 ['Indice global','Unknown','Capacités, compétences critiques et liens systèmes absents.'],
 ['Verdict','Cockpit incomplet','M6 Indices!A15:B15 : au moins deux sous-scores non calculables.'],
 ['Profils EDA',null,'Aucun rapprochement automatique avec les usages automobiles.'],
 ['Validation','To validate','Réponses dans reference/validation_answers.json, puis relancer le pipeline.'],
 ['Recherche de références',p.retrieval_status,'Recherche locale extractive ; aucun appel à un modèle génératif.'],
 ['Économies confirmées','Unknown','Aucune économie mesurée et validée fournie.'],
];
summary.getRange('A1:C13').values=metrics;
summary.getRange('B3').formulas=[[`=COUNTIFS(${area('dataset')},"automobile",${area('record_type')},"usage")`]];
summary.getRange('B4').formulas=[[`=SUM(${area('active')})`]];
summary.getRange('B5').formulas=[[`=IF(COUNT(${area('active_cost_ke')})=B4,SUM(${area('active_cost_ke')}),"Unknown")`]];
summary.getRange('B6').formulas=[[`=IF(COUNT(${area('stop_cost_ke')})=COUNTIFS(${area('active')},1,${area('source_decision')},"Arrêter"),SUM(${area('stop_cost_ke')}),"Unknown")`]];
summary.getRange('B7').formulas=[[`=IF(AND(B4>0,COUNT(${area('portfolio_points')})=B4),SUM(${area('portfolio_points')})/(25*B4)*100,"Unknown")`]];
summary.getRange('B10').formulas=[[`=COUNTIFS(${area('dataset')},"eda",${area('record_type')},"profile")`]];
summary.showGridLines=false;
summary.getRange('A1:C13').format={font:{name:'Arial',size:11,color:'#172338'},rowHeight:46,wrapText:true,verticalAlignment:'center'};
summary.getRange('A1:C1').format={fill:'#15243A',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:28};
summary.getRange('A1:A13').format.columnWidth=38;
summary.getRange('B1:B13').format.columnWidth=27;
summary.getRange('C1:C13').format.columnWidth=85;
summary.getRange('B5:B7').setNumberFormat('#,##0.0');
summary.getRange('B8:B9').format.fill='#FFF1CD';
// Verify that summaries respond to edited costs, including missing versus zero.
const testRow=p.atlas.findIndex(r=>r.dataset==='automobile' && ['Production','Pilote'].includes(r.status))+2;
if(testRow>=2){
 const target=atlas.sheet.getRange(`${field('annual_cost_ke')}${testRow}`);
 const original=target.values[0][0];
 const baseline=summary.getRange('B5').values[0][0];
 if(typeof original==='number' && typeof baseline==='number'){
  target.values=[[original+10]];
  if(summary.getRange('B5').values[0][0]!==baseline+10)throw new Error('Cost recalculation failed');
  target.values=[[null]];
  if(summary.getRange('B5').values[0][0]!=='Unknown')throw new Error('Missing cost treated as zero');
  if(p.atlas[testRow-2].source_decision==='Arrêter' && summary.getRange('B6').values[0][0]!=='Unknown')throw new Error('Missing stop cost treated as zero');
  target.values=[[0]];
  if(summary.getRange('B5').values[0][0]!==baseline-original)throw new Error('Zero cost treated as missing');
  target.values=[[original]];
 }
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Synthese!A3:B10',tableMaxRows:8,tableMaxCols:2,maxChars:2000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
for(const name of ['Synthese','Atlas','Questions','Interpretations','Preuves']){
 const preview=await wb.render({sheetName:name,range:name==='Synthese'?'A1:C13':'A1:F5',scale:1,format:'png'});
 await fs.writeFile(path.join(output,`preview_${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(output,'flow_atlas.xlsx'));
