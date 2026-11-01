/* Game cues use decoded buffers: overlapping voices and an audio-clock ticker. */
function createGameAudio({urls,getPrefs,notify}) {
  let context=null,master=null,bridge=null,output=null,loading=null,disposed=false;
  let deadline=0,ticker=null,outputRevision=0,tickKey=null,tickOrigin=0,tickLimit=0,tickDone=false;
  const tickVoices=new Map(),tickFinished=new Set();
  const buffers=new Map(),voices=new Set();
  const audible=()=>!disposed&&!getPrefs().muted&&getPrefs().volume>0&&context?.state==='running';
  function stopVoice(voice){voice.cancelled=true;if(tickVoices.get(voice.urSketchTickIndex)===voice)tickVoices.delete(voice.urSketchTickIndex);if(voice.urSketchTickIndex!=null&&performance.now()>=tickOrigin+voice.urSketchTickIndex*250-5)tickFinished.add(voice.urSketchTickIndex);try{voice.stop();}catch{}voices.delete(voice);}
  function stopTicks(){for(const voice of tickVoices.values())stopVoice(voice);tickVoices.clear();}
  function source(cue,when=context?.currentTime,index=null,buffer=buffers.get(cue)){
    if(!audible()||!buffer)return;
    const voice=context.createBufferSource();voice.buffer=buffer;voice.urSketchCue=cue;
    voice.connect(master);voices.add(voice);voice.urSketchTickIndex=index;const sourceKey=tickKey;voice.onended=()=>{voices.delete(voice);if(index!==null&&!voice.cancelled&&sourceKey===tickKey)tickFinished.add(index);if(index!==null&&tickVoices.get(index)===voice)tickVoices.delete(index);voice.disconnect();};voice.start(when);
    if(index!==null)tickVoices.set(index,voice);
    window.dispatchEvent(new CustomEvent('ursketch:sound',{detail:{cue,when,index,key:tickKey}}));
  }
  async function routeOutput(){
    if(!context)return;
    const revision=++outputRevision,id=getPrefs().output||'';
    try{
      if(context.setSinkId)await context.setSinkId(id);
      else if(output?.setSinkId){await output.setSinkId(id);if(revision===outputRevision)await output.play();}
    }catch{
      if(revision!==outputRevision)return;
      try{if(context.setSinkId)await context.setSinkId('');else if(output?.setSinkId){await output.setSinkId('');await output.play();}}catch{}
      notify?.('Saved audio output unavailable; using system default.');
    }
  }
  function settings(){
    if(!master)return;
    master.gain.setValueAtTime(getPrefs().muted?0:getPrefs().volume/100,context.currentTime);
    if(!audible())for(const voice of [...voices])stopVoice(voice);
    if(context.urSketchOutput!==getPrefs().output){context.urSketchOutput=getPrefs().output;void routeOutput();}
    schedule();
  }
  async function unlock(event){
    if(disposed||event&&!event.isTrusted)return;
    if(!context){
      const AudioContextClass=window.AudioContext||window.webkitAudioContext;if(!AudioContextClass)return;
      context=new AudioContextClass();master=context.createGain();
      // Firefox supports output selection on HTMLAudioElement, but not AudioContext.
      if(!context.setSinkId&&HTMLMediaElement.prototype.setSinkId){
        bridge=context.createMediaStreamDestination();output=new Audio();output.srcObject=bridge.stream;master.connect(bridge);void output.play().catch(()=>{});
      }else master.connect(context.destination);
      context.addEventListener('statechange',()=>{if(context.state!=='running')stopTicks();else schedule();});
      settings();
    }
    try{await context.resume();if(output)await output.play();}catch{return;}
    if(!loading)loading=Promise.all(Object.entries(urls).map(async([cue,url])=>{
      try{const response=await fetch(url);if(!response.ok)throw new Error('Audio unavailable');const bytes=await response.arrayBuffer();buffers.set(cue,await context.decodeAudioData(bytes));}
      catch{notify?.(`Could not load ${cue}. Reopen the app to retry.`);}
    })).then(()=>schedule());
    await loading;settings();
  }
  async function play(cue){
    const received=performance.now();if(!audible())return;
    await loading;if(disposed||performance.now()-received>1500)return;source(cue);
  }
  function schedule(){
    if(tickKey===null||tickDone||!deadline)return;
    const now=performance.now();
    if(now>=deadline){tickDone=true;stopTicks();return;}
    if(!audible()||!buffers.has('TickingNoise')){stopTicks();return;}
    // Each slot belongs to one round and one wall-clock instant. Never reset a
    // cursor when its queued ticks finish, and never play an overdue slot.
    for(const [index,voice] of tickVoices){if(tickOrigin+index*250>=deadline){stopVoice(voice);tickVoices.delete(index);}}
    const first=Math.max(0,Math.ceil((now+5-tickOrigin)/250)),clockBase=context.currentTime-now/1000;
    for(let index=first;index<tickLimit;index++){
      const time=tickOrigin+index*250;if(time>=deadline)break;
      if(tickVoices.has(index)||tickFinished.has(index))continue;
      const delay=(time-performance.now())/1000;if(delay<.003)continue;
      const when=clockBase+time/1000;if(when<context.currentTime+.003)continue;
      source('TickingNoise',when,index);
    }
  }
  function countdown(ms,key='round'){
    if(key!==tickKey){stopTicks();tickKey=key;tickFinished.clear();tickDone=false;deadline=0;tickLimit=0;}
    if(ms==null||ms<=0){if(deadline){tickDone=true;stopTicks();}return;}
    if(tickDone)return;
    if(!deadline){tickOrigin=performance.now()+15;deadline=performance.now()+Math.min(20000,ms);tickLimit=Math.min(80,Math.ceil(ms/250));}
    else deadline=Math.min(deadline,performance.now()+ms);
    schedule();
  }
  let fireworkBuffers=[];
  function firework(index){
    if(!audible())return;
    if(!fireworkBuffers.length){
      for(let variant=0;variant<3;variant++){
        const rate=context.sampleRate,buffer=context.createBuffer(2,Math.ceil(rate*2.4),rate);
        let seed=12371+variant*8123;const noise=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2147483648-1;};
        for(let channel=0;channel<2;channel++){
          const pcm=buffer.getChannelData(channel);let low=0;
          for(let i=0;i<pcm.length;i++){
            const t=i/rate,n=noise();low=low*.96+n*.04;
            const boom=low*Math.exp(-t*5)*(1-Math.exp(-t*180))*2;
            const crackle=n*Math.pow(Math.max(0,1-t/2.4),2)*(Math.sin(t*(91+variant*13))>.88?.13:.012);
            pcm[i]=Math.max(-.7,Math.min(.7,boom+crackle));
          }
        }
        fireworkBuffers.push(buffer);
      }
    }
    source('Fireworks',undefined,null,fireworkBuffers[index%fireworkBuffers.length]);
  }
  function stopFireworks(){for(const voice of [...voices])if(voice.urSketchCue==='Fireworks')stopVoice(voice);}
  function stop(){deadline=0;tickKey=null;tickDone=true;stopTicks();for(const voice of [...voices])stopVoice(voice);}
  document.addEventListener('pointerdown',unlock,{passive:true});document.addEventListener('keydown',unlock);
  window.addEventListener('pagehide',()=>{stop();disposed=true;clearInterval(ticker);void context?.close();output?.pause();});
  ticker=setInterval(schedule,25);
  return {play,countdown,settings,stop,firework,stopFireworks,get context(){return context;},get master(){return master;},get ready(){return loading;},get loaded(){return [...buffers.keys()];}};
}
