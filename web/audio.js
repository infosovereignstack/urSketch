/* Game cues use decoded buffers: overlapping voices and an audio-clock ticker. */
function createGameAudio({urls,getPrefs,notify}) {
  let context=null,master=null,bridge=null,output=null,loading=null,disposed=false;
  let deadline=0,ticker=null,outputRevision=0,tickKey=null,tickOrigin=0,tickLimit=0,tickDone=false;
  const tickVoices=new Map(),tickFinished=new Set();
  const buffers=new Map(),voices=new Set();
  let fireworksState=null,fireworksVoice=null;
  const audible=()=>!disposed&&!getPrefs().muted&&getPrefs().volume>0&&context?.state==='running';
  function stopVoice(voice){voice.cancelled=true;if(tickVoices.get(voice.urSketchTickIndex)===voice)tickVoices.delete(voice.urSketchTickIndex);if(voice.urSketchTickIndex!=null&&performance.now()>=tickOrigin+voice.urSketchTickIndex*250-5)tickFinished.add(voice.urSketchTickIndex);try{voice.stop();}catch{}try{voice.disconnect();voice.urSketchGainNode?.disconnect();}catch{}voices.delete(voice);}
  function stopTicks(){for(const voice of tickVoices.values())stopVoice(voice);tickVoices.clear();}
  function source(cue,when=context?.currentTime,index=null,buffer=buffers.get(cue),options={}){
    if(!audible()||!buffer||cue==='TickingNoise'&&fireworksState)return;
    const voice=context.createBufferSource();voice.buffer=buffer;voice.urSketchCue=cue;
    voice.loop=!!options.loop;voice.urSketchGain=options.gain??1;const gain=context.createGain();voice.urSketchGainNode=gain;gain.gain.value=voice.urSketchGain;voice.connect(gain);gain.connect(master);voices.add(voice);voice.urSketchTickIndex=index;const sourceKey=tickKey;voice.onended=()=>{voices.delete(voice);if(index!==null&&!voice.cancelled&&sourceKey===tickKey)tickFinished.add(index);if(index!==null&&tickVoices.get(index)===voice)tickVoices.delete(index);voice.disconnect();gain.disconnect();};voice.start(when,options.offset||0);if(options.duration)voice.stop(when+options.duration);
    if(index!==null)tickVoices.set(index,voice);
    window.dispatchEvent(new CustomEvent('ursketch:sound',{detail:{cue,when,index,key:tickKey,loop:voice.loop,offset:options.offset||0}}));
    return voice;
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
    schedule();syncFireworks();
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
      context.addEventListener('statechange',()=>{if(context.state!=='running'){stopTicks();if(fireworksVoice)stopVoice(fireworksVoice);fireworksVoice=null;}else{schedule();syncFireworks();}});
      settings();
    }
    try{await context.resume();if(output)await output.play();}catch{return;}
    if(!loading)loading=Promise.all(Object.entries(urls).map(async([cue,url])=>{
      try{const response=await fetch(url);if(!response.ok)throw new Error('Audio unavailable');const bytes=await response.arrayBuffer();let decoded=await context.decodeAudioData(bytes);
        // A tick is a short transient, not overlapping copies of a long MP3.
        if(cue==='TickingNoise'){
          const samples=decoded.getChannelData(0);let peak=0;for(let i=1;i<samples.length;i++)if(Math.abs(samples[i])>Math.abs(samples[peak]))peak=i;
          const start=Math.max(0,peak-Math.round(decoded.sampleRate*.02)),length=Math.min(decoded.length-start,Math.round(decoded.sampleRate*.2));
          const clipped=context.createBuffer(decoded.numberOfChannels,length,decoded.sampleRate);
          for(let c=0;c<decoded.numberOfChannels;c++){const out=clipped.getChannelData(c),input=decoded.getChannelData(c);for(let i=0;i<length;i++)out[i]=input[start+i]*Math.min(1,i/(decoded.sampleRate*.001),(length-1-i)/(decoded.sampleRate*.005));}
          decoded=clipped;
        }
        buffers.set(cue,decoded);}
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
    if(fireworksState&&ms>0)return;
    if(ms==null||ms<=0){if(deadline){tickDone=true;stopTicks();}return;}
    if(tickDone)return;
    if(!deadline){tickOrigin=performance.now()+15;deadline=performance.now()+Math.min(20000,ms);tickLimit=Math.min(80,Math.ceil(ms/250));}
    else deadline=Math.min(deadline,performance.now()+ms);
    schedule();
  }
  function syncFireworks(){
    if(!fireworksState||!audible()||!buffers.has('Fireworks'))return;
    const now=performance.now(),remaining=(fireworksState.end-now)/1000;
    if(remaining<=0){stopFireworks();return;}
    // A naturally ended voice must not restart just because the clocks disagree.
    if(fireworksVoice&&!fireworksVoice.cancelled)return;
    const buffer=buffers.get('Fireworks'),offset=Math.max(0,(now-fireworksState.start)/1000)%buffer.duration;
    fireworksVoice=source('Fireworks',context.currentTime,null,buffer,{loop:true,offset,duration:remaining,gain:.5});
  }
  function fireworks({key,elapsed,remaining}){
    stopTicks();tickDone=true;deadline=0;
    const now=performance.now();
    if(fireworksState?.key!==key){stopFireworks();fireworksState={key,start:now-elapsed*1000,end:Math.min(now+remaining,now-elapsed*1000+20000)};}
    else fireworksState.end=Math.min(fireworksState.end,now+remaining);
    syncFireworks();
  }
  function stopFireworks(){fireworksState=null;if(fireworksVoice)stopVoice(fireworksVoice);fireworksVoice=null;}
  function stop(){stopFireworks();deadline=0;tickKey=null;tickDone=true;stopTicks();for(const voice of [...voices])stopVoice(voice);}
  document.addEventListener('pointerdown',unlock,{passive:true});document.addEventListener('keydown',unlock);
  window.addEventListener('pagehide',()=>{stop();disposed=true;clearInterval(ticker);void context?.close();output?.pause();});
  ticker=setInterval(()=>{schedule();syncFireworks();},25);
  return {play,countdown,settings,stop,fireworks,stopFireworks,get context(){return context;},get master(){return master;},get ready(){return loading;},get loaded(){return [...buffers.keys()];}};
}
