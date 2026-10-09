const {execFileSync}=require('child_process');const fs=require('fs');
const K=JSON.parse(fs.readFileSync('keep.json'));const list=[];
K.forEach(([s,e],i)=>{const d=(e-s).toFixed(6),f=`aseg/${String(i).padStart(3,'0')}.wav`;
 execFileSync('ffmpeg',['-y','-v','error','-i','src_audio.wav','-af',`atrim=start=${s.toFixed(6)}:end=${e.toFixed(6)},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=${(e-s-0.01).toFixed(6)}:d=0.01`,'-c:a','pcm_s16le',f]);
 list.push(`file '${f}'`);});
fs.writeFileSync('alist.txt',list.join('\n'));console.log('audio segs',K.length);
