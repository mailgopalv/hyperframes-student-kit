const w=require('./transcript.json');
const pts=process.argv.slice(2).map(s=>{const[m,x]=s.split(':');return +m*60+ +x});
for(const p of pts){
  const ws=w.filter(x=>x.start>=p-5&&x.start<=p+5);
  console.log(`== ${Math.floor(p/60)}:${String(p%60).padStart(2,'0')}: `+ws.map(x=>`${x.text}@${x.start.toFixed(2)}`).join(' '));
}
