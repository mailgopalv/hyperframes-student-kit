const w=require('./transcript.json');
const f=s=>{s=Math.round(s);return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
let out=[],line=[],ls=w[0].start,gaps=0,gapTot=0;
for(let i=0;i<w.length;i++){
  const x=w[i]; if(!line.length) ls=x.start;
  line.push(x.text);
  const nx=w[i+1]; const gap=nx?nx.start-x.end:0;
  if(gap>=2){gaps++;gapTot+=gap;}
  if(!nx||gap>=1.2||(/[.?!]$/.test(x.text)&&line.length>18)||line.length>40){
    out.push(`[${f(ls)}-${f(x.end)}] ${line.join(' ')}`+(gap>=1.2?`  <gap ${gap.toFixed(1)}s>`:''));line=[];
  }
}
require('fs').writeFileSync('transcript.txt',out.join('\n'));
console.log(out.length,'lines; gaps>=2s:',gaps,'total',gapTot.toFixed(0),'s');
