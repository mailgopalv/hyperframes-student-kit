const W=require('./transcript.json'),K=require('./keep.json');
const map=t=>{let o=0;for(const[s,e]of K){if(t<s)return o;if(t<=e)return o+(t-s);o+=e-s;}return o;};
const norm=s=>s.toLowerCase().replace(/[^a-z0-9 ]/g,'');
function find(phrase,after){const p=norm(phrase).split(' ');for(let i=0;i<W.length;i++){if(W[i].start<after)continue;let ok=true;for(let j=0;j<p.length;j++){if(!W[i+j]||norm(W[i+j].text)!==p[j]){ok=false;break;}}if(ok)return W[i].start;}return null;}
const C=[
 ['Intro',0,null],
 ['Prerequisites',120,'All right, let\'s go through the prerequisites'],
 ['Project setup & virtual environment',150,'So the next thing I\'m going to ask you'],
 ['Building the MCP server',460,'So I\'m all set to do my coding'],
 ['Testing with MCP Inspector',950,'That\'s where MCP inspector'],
 ['Adding more tools',1150,'Before we move on'],
 ['Building the AI agent with Google ADK',1360,'The next thing we\'re going to look at'],
 ['Creating a Gemini API key',1890,'We haven\'t created'],
 ['Running the agent in ADK Web',2075,'So I have dot environment'],
 ['Exploring the ADK Web UI',2400,'And this tool, the ADK'],
 ['Public MCP servers: filesystem',2640,'okay, this is all good and going back'],
 ['Web search with DuckDuckGo MCP',2980,'before we go beyond'],
 ['Testing the upgraded agent',3215,'Right now I have done this'],
 ['Streamable HTTP MCP server',3420,'Just in case if you decided'],
 ['Wrap-up',3730,'So I just wanted to show you'],
];
const f=s=>{s=Math.floor(s);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')};
const res=C.map(([n,a,p])=>{const src=p?find(p,a):0;return [n,src,src==null?null:map(src)]});
res.forEach(r=>console.log(r[0].padEnd(40),r[1]==null?'NOT FOUND':f(r[1])+' -> '+f(r[2])));
require('fs').writeFileSync('chapters.json',JSON.stringify(res));
