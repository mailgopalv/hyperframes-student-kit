const fs=require('fs');
const W=require('./transcript.json'), K=require('./keep.json');
// map source time -> output time; null if inside a cut
function map(t){let o=0;for(const[s,e]of K){if(t<s)return null;if(t<=e)return o+(t-s);o+=e-s;}return null;}
let words=[];
for(const w of W){const mid=(w.start+w.end)/2;if(map(mid)==null)continue;
  let s=map(w.start),e=map(w.end);const mm=map(mid);
  if(s==null)s=mm-0.1; if(e==null)e=mm+0.1;
  words.push({text:w.text,start:s,end:Math.max(e,s+0.05)});}
// glossary fixes on the joined text, applied per phrase
const fixes=[
 [/\bodd ridies\b/gi,'order IDs'],[/\bodd ready\b/gi,'order ID'],[/\bodd writing\b/gi,'order ID'],
 [/\bmcp\b/g,'MCP'],[/\bMCP turtle\b/g,'MCP tool'],[/\bduck duck go\b/gi,'DuckDuckGo'],[/\bduck duck\b/gi,'DuckDuckGo'],
 [/\bdogs\b/g,'docs'],[/\be commerce\b/gi,'e-commerce'],[/\becommerce\b/gi,'e-commerce'],[/\bEcom\b/g,'ecom'],
 [/\bfreetire\b/gi,'free-tier'],[/\bchampion\b/gi,'Gemini'],[/\bv n v\b/gi,'venv'],[/\bv e n v\b/gi,'venv'],[/\bv and v\b/gi,'venv'],
 [/\bdot p y\b/gi,'.py'],[/\bp y\b/g,'py'],[/\biPhone iPhone\b/g,'--'],[/\bminus or\b/g,'-r'],[/\brequirement or txt\b/gi,'requirements.txt'],
 [/\brequirement dot txt\b/gi,'requirements.txt'],[/\brequirements dot txt\b/gi,'requirements.txt'],[/\bdot env\b/gi,'.env'],
 [/\bSTD IO\b/g,'stdio'],[/\bADK hyphen web\b/g,'adk web'],[/\bagentic development kit\b/gi,'Agent Development Kit'],
 [/\b127001\b/g,'127.0.0.1'],[/\bn8n hyphen gemini hyphen GB\b/gi,'n8n-gemini-gv'],[/\bsupport hyphen age and\b/gi,'support-agent-'],
 [/\bdata back\b/g,'data'],[/\ba agent\b/g,'an agent'],[/\bA agent\b/g,'AI agent'],[/\ban hands-on\b/g,'a hands-on'],
 [/\bNottingham\b/g,'Nottingham'],[/\bunder 11\b/g,'unrelated'],[/\bgenerate order status\b/g,'get_order_status'],
];
const fix=s=>fixes.reduce((a,[r,v])=>a.replace(r,v),s);
// group into cues
const cues=[];let cur=[];
const text=a=>a.map(w=>w.text).join(' ');
const flush=()=>{if(cur.length){cues.push({start:cur[0].start,end:cur[cur.length-1].end,text:fix(text(cur))});cur=[];}};
for(let i=0;i<words.length;i++){
  const w=words[i],prev=cur[cur.length-1];
  if(prev){const len=text(cur).length+1+w.text.length;
    const gap=w.start-prev.end, dur=w.end-cur[0].start;
    const ends=/[.?!]$/.test(w.text);
    if(gap>0.7||dur>6||(len>42&&!(ends&&len<=50))) flush();}
  cur.push(w);
  const L=text(cur).length;
  if(/[.?!]$/.test(w.text)&&L>=12) flush();
  else if(/,$/.test(w.text)&&L>=30) flush();
}
flush();
// merge 1-2 word orphans into previous cue if close
const out=[];for(const c of cues){const p=out[out.length-1];
  if(p&&c.text.split(' ').length<=2&&c.start-p.end<0.3&&(p.text+' '+c.text).length<=52){p.text+=' '+c.text;p.end=c.end;}else out.push({...c});}
// no overlaps, min duration
for(let i=0;i<out.length;i++){const n=out[i+1];if(n&&out[i].end>n.start)out[i].end=n.start;if(out[i].end-out[i].start<0.6)out[i].end=Math.min(out[i].start+0.6,n?n.start:out[i].start+0.6);}
const ts=t=>{const ms=Math.round(t*1000),h=Math.floor(ms/3600000),m=Math.floor(ms%3600000/60000),s=Math.floor(ms%60000/1000);return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`};
fs.writeFileSync('../renders/0927-tight.srt',out.map((c,i)=>`${i+1}\n${ts(c.start)} --> ${ts(c.end)}\n${c.text}\n`).join('\n'));
console.log('cues',out.length,'words',words.length,'last',ts(out[out.length-1].end));
