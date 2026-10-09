const fs=require('fs');
const file=process.argv[2], meta=fs.readFileSync(process.argv[3],'utf8');
const ch=[...meta.matchAll(/START=(\d+)[\s\S]*?title=(.*)/g)].map(m=>({start:+m[1],title:m[2].trim()}));
const fd=fs.openSync(file,'r+');const size=fs.fstatSync(fd).size;
let off=0,moov=null;const h=Buffer.alloc(16);
while(off<size){fs.readSync(fd,h,0,16,off);let s=h.readUInt32BE(0);const t=h.toString('latin1',4,8);if(s===1)s=Number(h.readBigUInt64BE(8));if(s===0)s=size-off;if(t==='moov')moov={off,s};off+=s;}
if(!moov||moov.off+moov.s!==size)throw new Error('moov must be last box');
const mb=Buffer.alloc(moov.s);fs.readSync(fd,mb,0,moov.s,moov.off);
// build chpl
const parts=[];for(const c of ch){const tb=Buffer.from(c.title,'utf8').subarray(0,255);const b=Buffer.alloc(9+tb.length);b.writeBigUInt64BE(BigInt(c.start)*10000n,0);b.writeUInt8(tb.length,8);tb.copy(b,9);parts.push(b);}
const body=Buffer.concat([Buffer.from([1,0,0,0, 0,0,0,0, ch.length]),...parts]);
const chpl=Buffer.alloc(8);chpl.writeUInt32BE(8+body.length,0);chpl.write('chpl',4,'latin1');const chplBox=Buffer.concat([chpl,body]);
// find udta directly under moov
let p=8,udta=null;while(p<mb.length){const s=mb.readUInt32BE(p),t=mb.toString('latin1',p+4,p+8);if(t==='udta')udta={p,s};p+=s;}
let out;
if(udta){const u=Buffer.concat([mb.subarray(udta.p,udta.p+udta.s),chplBox]);u.writeUInt32BE(u.length,0);out=Buffer.concat([mb.subarray(0,udta.p),u,mb.subarray(udta.p+udta.s)]);}
else{const u=Buffer.alloc(8);u.writeUInt32BE(8+chplBox.length,0);u.write('udta',4,'latin1');out=Buffer.concat([mb,u,chplBox]);}
out.writeUInt32BE(out.length,0);
fs.ftruncateSync(fd,moov.off);fs.writeSync(fd,out,0,out.length,moov.off);fs.closeSync(fd);
console.log('wrote',ch.length,'chapters');
