const w=require('./transcript.json');
const f=s=>{const m=Math.floor(s/60),r=(s%60).toFixed(1);return m+':'+r.padStart(4,'0')};
let tot=0,n=0;const rows=[];
for(let i=0;i<w.length;i++){
  const x=w[i],nx=w[i+1];
  const dead=(x.end-x.start)-0.8 + (nx?Math.max(0,nx.start-x.end):0);
  if(dead>=1.5){tot+=dead;n++;rows.push(`${f(x.start)}  dead~${dead.toFixed(1)}s  ...${w.slice(Math.max(0,i-4),i+1).map(y=>y.text).join(' ')} || ${w.slice(i+1,i+5).map(y=>y.text).join(' ')}`);}
}
console.log(rows.join('\n'));console.log('N',n,'TOTAL',tot.toFixed(0));
