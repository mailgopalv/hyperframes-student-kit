const K=require('./keep.json');const fs=require('fs');
const terms=K.map(([s,e])=>'between(t,'+(s-1/60).toFixed(4)+','+(e-1/60).toFixed(4)+')');
const bal=a=>a.length==1?a[0]:'('+bal(a.slice(0,a.length>>1))+'+'+bal(a.slice(a.length>>1))+')';
fs.writeFileSync('vselect.txt',"fps=30,select='"+bal(terms)+"',setpts=N/30/TB");
