const fs=require('fs');
const DUR=3778.149, FPS=30;
// Tier 2: [cutStart, cutEnd] — from first removed word to first kept word
const T2=[
 [143.00,156.76,'1 install-software repeat'],
 [179.04,196.28,'2 start menu / open VS Code'],
 [317.44,333.80,'3 recap no-code-yet'],
 [443.72,463.84,'4 recap two folders'],
 [643.68,653.32,'5 importing repeat'],
 [945.40,956.12,'6 no way of testing repeat'],
 [1015.20,1031.50,'7a why inspector repeat'],
 [1037.28,1044.96,'7b new tool aside'],
 [1175.56,1184.08,'8 already built aside'],
 [1314.96,1325.87,'9 re-run get_order_status'],
 [1507.16,1514.92,'10 __init__ repeat'],
 [1553.56,1565.40,'11 free-tier repeat'],
 [1659.92,1667.12,'12 parent-of-parent repeat'],
 [1756.12,1776.48,'13a never guess repeat'],
 [1794.52,1822.32,'13b precise instruction repeat'],
 [2035.68,2050.70,'14 moving .env'],
 [2127.44,2136.04,'15 port 8001 fumble'],
 [2353.24,2382.36,'16 no-access 3rd explanation'],
 [2781.80,2820.72,'17 inspector restart repeat'],
 [2915.44,2926.94,'18 beauty-of-it repeat'],
 [3009.80,3025.16,'19 google aside'],
 [3066.04,3087.08,'20 servers recap'],
 [3127.44,3134.20,'21a harnessing restate'],
 [3146.96,3201.56,'21b+22 rules restate + early wrap'],
 [3611.28,3621.60,'23 ecommerce-website repeat'],
];
// Tier 1: pauses >=1.0s at -40dB -> keep 0.25s each side
const sil=fs.readFileSync('sil40_06.txt','utf8').trim().split('\n').map(l=>l.split(' ').map(Number)).filter(r=>r[2]>=1.0).map(([s,e])=>[s+0.25,e-0.25]);
let cuts=[...T2.map(c=>[c[0]-0.05,c[1]-0.05]),...sil].sort((a,b)=>a[0]-b[0]);
const m=[];for(const c of cuts){if(m.length&&c[0]<=m[m.length-1][1])m[m.length-1][1]=Math.max(m[m.length-1][1],c[1]);else m.push([...c]);}
// keep segments snapped to frame grid
const keep=[];let t=0;
for(const [s,e] of m){keep.push([t,s]);t=e;}keep.push([t,DUR]);
const K=keep.map(([s,e])=>[Math.ceil(s*FPS)/FPS,Math.floor(e*FPS)/FPS]).filter(([s,e])=>e-s>=2/FPS);
const total=K.reduce((a,[s,e])=>a+e-s,0);
fs.writeFileSync('keep.json',JSON.stringify(K));
fs.writeFileSync('vselect.txt',"fps=30,select='"+K.map(([s,e])=>`between(t,${s.toFixed(4)},${(e-0.5/FPS).toFixed(4)})`).join('+')+"',setpts=N/30/TB");
const t2=T2.reduce((a,c)=>a+c[1]-c[0],0);
console.log('segments',K.length,'tier2 removes',t2.toFixed(0)+'s','output',(total/60).toFixed(2),'min','removed',((DUR-total)/60).toFixed(2),'min');
