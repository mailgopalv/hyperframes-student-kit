const {execFileSync}=require('child_process');const fs=require('fs');
const SRC='../ai-mcp-handson/renders/0927-tight-16x9.mp4', VO='../ai-mcp-handson/assets/mcp-handson-shorts1.m4a';
const CROP={chat:'crop=1260:1260:1216:180,scale=1080:1080:flags=lanczos',
            rules:'crop=900:900:690:100,scale=1080:1080:flags=lanczos',
            fs:'crop=900:900:690:250,scale=1080:1080:flags=lanczos'};
// [label, videoStart, crop, audio: 'clip' | [voStart, voEnd]]
const S=[
 ['s1-vo-hook',   1974.90,'chat',[0.85,6.95]],
 ['s2-no-access', 1981.25,'chat','clip',1992.35],
 ['s3-harness',   1996.70,'chat','clip',2001.40],
 ['s4-rules',     2007.40,'rules','clip',2015.12],
 ['s5-vo-docs',   2516.00,'fs',[9.75,16.55]],
 ['s6-payoff',    2713.12,'chat','clip',2720.05],
 ['s7-vo-outro',  2716.70,'chat',[19.20,23.45],'freeze'],
];
const snap=d=>Math.round(d*30)/30;let t=0;const list=[],meta=[];
for(const [lab,vs,crop,a,ve] of S){const freeze=ve==='freeze';
  const dur=snap(a==='clip'?ve-vs:a[1]-a[0]);if(freeze)execFileSync('ffmpeg',['-y','-v','error','-ss',vs.toFixed(3),'-i',SRC,'-frames:v','1','work/freeze.png']);const out=`work/${lab}.mp4`;
  const aIn=a==='clip'?['-ss',vs.toFixed(3),'-t',dur.toFixed(4),'-i',SRC]:['-ss',a[0].toFixed(3),'-t',dur.toFixed(4),'-i',VO];
  const vIn=freeze?['-loop','1','-framerate','30','-t',dur.toFixed(4),'-i','work/freeze.png']:['-ss',vs.toFixed(3),'-t',dur.toFixed(4),'-i',SRC];execFileSync('ffmpeg',['-y','-v','error',...vIn,...aIn,
    '-filter_complex',`[0:v]${CROP[crop]},fps=30,setsar=1[v];[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.02,afade=t=out:st=${(dur-0.03).toFixed(3)}:d=0.03,apad,atrim=0:${dur.toFixed(4)}[a]`,
    '-map','[v]','-map','[a]','-frames:v',String(Math.round(dur*30)),'-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',out]);
  list.push(`file '${lab}.mp4'`);meta.push({lab,start:+t.toFixed(4),dur});t+=dur;}
fs.writeFileSync('work/list.txt',list.join('\n'));fs.writeFileSync('work/segments.json',JSON.stringify(meta,null,1));
console.log(meta.map(m=>`${m.lab.padEnd(14)} start ${m.start.toFixed(2)} dur ${m.dur.toFixed(2)}`).join('\n'),'\nTOTAL',t.toFixed(3));
