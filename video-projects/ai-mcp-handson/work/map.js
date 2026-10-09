const K=require('./keep.json');
const map=t=>{let o=0;for(const[s,e]of K){if(t<s)return o;if(t<=e)return o+(t-s);o+=e-s;}return o;};
const pts=[143.00,179.04,317.44,443.72,643.68,945.40,1015.20,1037.28,1175.56,1314.96,1507.16,1553.56,1659.92,1756.12,1794.52,2035.68,2127.44,2353.24,2781.80,2915.44,3009.80,3066.04,3127.44,3146.96,3611.28];
const f=s=>Math.floor(s/60)+':'+(s%60).toFixed(1).padStart(4,'0');
console.log(pts.map((p,i)=>`${i+1} src ${f(p)} -> out ${f(map(p))}`).join('\n'));
console.log('chapters:',[0,128,464,1060,1377,1898,2136,2649,3426,3738].map(t=>f(map(t))).join(' '));
