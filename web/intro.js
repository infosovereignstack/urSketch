/* Source footage supplies the animation; the theme song starts independently. */
'use strict';
(() => {
  const $=id=>document.getElementById(id),video=$('intro-video'),play=$('intro-play');
  const track=URSKETCH_INTRO_MOTION,settingsKey='ursketch.settings.v1',themeUrl='URSKETCH_INTRO_AUDIO_URL';
  const music=new Audio();music.preload='auto';music.loop=true;
  let prefs={},unlocked=false,pendingMusic=null,loading=null,videoUrl=null,poster=null,visualPaused=false,framePending=false,leaving=false,lastPosition=null;
  const systemMotion=matchMedia('(prefers-reduced-motion: reduce)');
  // Render the decoded footage and the repaired background in one sRGB surface.
  // A video compositor can display different blue values from drawImage samples.
  const scene=$('intro-scene'),context=scene.getContext('2d',{alpha:false,willReadFrequently:true});
  const status=text=>$('intro-status').textContent=text;
  const themeEnabled=()=>!prefs.themeDisabled&&!prefs.muted&&prefs.volume>0;
  function paintFrame(source){
    if(!source)return;
    context.drawImage(source,0,0,track.width,track.height);
    const image=context.getImageData(0,0,track.width,track.height),d=image.data;
    const at=(x,y)=>Array.from(d.slice((y*track.width+x)*4,(y*track.width+x)*4+3));
    const sky=at(1590,10),circle=[45,100,154].map((v,i)=>Math.round(v*sky[i]/[159,193,224][i])),tolerance=Math.max(1,Math.round(8*sky[2]/224));
    // The original sample at (738,70) is occluded by the exclamation and bulb.
    // Use the measured circle palette, scaled only by the unobstructed sky fade.
    // Flatten compression noise in both solid blues. The canvas edge and page
    // then contain identical pixels, including during the source's fade to black.
    for(let i=0;i<d.length;i+=4){
      let colour=null;
      if(Math.abs(d[i]-sky[0])<=tolerance&&Math.abs(d[i+1]-sky[1])<=tolerance&&Math.abs(d[i+2]-sky[2])<=tolerance)colour=sky;
      else if(Math.abs(d[i]-circle[0])<=tolerance&&Math.abs(d[i+1]-circle[1])<=tolerance&&Math.abs(d[i+2]-circle[2])<=tolerance)colour=circle;
      if(colour){d[i]=colour[0];d[i+1]=colour[1];d[i+2]=colour[2];}
    }
    context.putImageData(image,0,0);
    const css=c=>`rgb(${c.join(',')})`;
    // Replace the COMPLETE original-logo rectangle, including black outlines,
    // white interiors and codec ringing; no letter-shaped mask is involved.
    context.save();context.beginPath();context.rect(940,0,680,280);context.clip();
    context.fillStyle=css(sky);context.fillRect(940,0,680,280);
    context.fillStyle=css(circle);context.beginPath();context.arc(738,532,511,0,Math.PI*2);context.fill();context.restore();
    document.documentElement.style.setProperty('--intro-sky',css(sky));
  }
  function align(){
    // Use the media element's local playhead for every replay, independently
    // of callback presentation timestamps that may belong to another timeline.
    const time=video.readyState>=2?video.currentTime:0;
    const wrapped=lastPosition!==null&&time<lastPosition-.5;lastPosition=time;
    const n=Math.max(0,Math.min(track.frames.length-1,Math.floor(time*track.fps+.001))),[x,y,w,h]=track.frames[n];
    play.style.left=`${x/track.width*100}%`;play.style.top=`${y/track.height*100}%`;play.style.width=`${w/track.width*100}%`;play.style.height=`${h/track.height*100}%`;
    paintFrame(video.readyState>=2?video:poster);$('intro-wordmark').style.filter=`url(#logo-alpha-cleanup) brightness(${track.brightness[n]??1})`;
    if(!video.paused&&!visualPaused&&unlocked&&themeEnabled()){
      // The MP3 and video have slightly different durations. Explicitly reset
      // audio on every visual wrap, including recovery from an ended song.
      if(wrapped||(!music.paused&&Math.abs(music.currentTime-time)>.18)){try{music.currentTime=time;}catch{}}
      if(wrapped&&music.paused)void startMusic();
    }
  }
  function frames(){
    if(framePending||video.paused||document.hidden)return;framePending=true;
    if(video.requestVideoFrameCallback)video.requestVideoFrameCallback(()=>{framePending=false;align();frames();});
    else requestAnimationFrame(()=>{framePending=false;align();frames();});
  }
  async function output(){
    if(music.setSinkId&&music.sinkId!==prefs.output){try{await music.setSinkId(prefs.output||'');}catch{try{await music.setSinkId('');}catch{}}}
  }
  function startMusic(){
    if(!themeEnabled()||document.hidden||leaving)return Promise.resolve();
    if(pendingMusic)return pendingMusic;
    if(!music.src)music.src=themeUrl;
    if(!music.paused){void output();return Promise.resolve();}
    if(!video.paused&&video.readyState>=2){try{music.currentTime=video.currentTime;}catch{}}
    // Call play synchronously so a real pointer/key event can unlock browser audio.
    pendingMusic=music.play().then(()=>{unlocked=true;if(!themeEnabled()||document.hidden||leaving)music.pause();else status('');})
      .catch(()=>{status('Theme music will start after your first interaction if your browser blocks autoplay.');})
      .finally(()=>{pendingMusic=null;});
    void output();return pendingMusic;
  }
  async function load(){
    if(loading)return loading;
    loading=(async()=>{try{
      const response=await fetch('URSKETCH_INTRO_VIDEO_URL',{cache:'force-cache'});if(!response.ok)throw new Error('Video unavailable');
      videoUrl=URL.createObjectURL(await response.blob());
      const metadata=new Promise((resolve,reject)=>{video.addEventListener('loadedmetadata',resolve,{once:true});video.addEventListener('error',reject,{once:true});});
      video.src=videoUrl;video.load();await metadata;
      if(!visualPaused&&!document.hidden&&!leaving){if(!music.paused&&Number.isFinite(video.duration))video.currentTime=music.currentTime%video.duration;await video.play();}
    }catch{loading=null;status('Animation unavailable. Use Play now to continue.');$('intro-fallback').hidden=false;}})();
    return loading;
  }
  async function setVisualPaused(value){
    visualPaused=value;if(value){video.pause();if((prefs.reduceMotion||systemMotion.matches)&&video.readyState>=1)video.currentTime=1/12;paintFrame(video.readyState>=2?video:poster);return;}
    await load();if(!visualPaused&&!document.hidden&&!leaving)try{if(!music.paused&&Number.isFinite(video.duration))video.currentTime=music.currentTime%video.duration;await video.play();}catch{status('Use Settings to change Reduce motion, or choose Play now.');}
  }
  function applyPrefs(next){
    prefs=next;music.volume=(prefs.volume/100)*(prefs.themeQuiet ? .25 : 1);music.muted=!!prefs.muted;
    if(!themeEnabled())music.pause();else void startMusic();
    const reduced=!!prefs.reduceMotion||systemMotion.matches;
    if(reduced!==visualPaused)void setVisualPaused(reduced);
  }
  const preferences=createSettings({notify:status,onChange:applyPrefs});
  function refreshPrefs(){preferences.refresh();}
  function interaction(event){if(event.isTrusted&&(!unlocked||music.paused))void startMusic();}
  document.addEventListener('pointerdown',interaction,{capture:true});document.addEventListener('keydown',interaction,{capture:true});
  video.addEventListener('playing',frames);video.addEventListener('seeked',()=>align());
  video.addEventListener('error',()=>{status('Animation unavailable. Use Play now to continue.');$('intro-fallback').hidden=false;});
  let resumeHelp=false;
  $('intro-instructions').onclick=()=>{resumeHelp=!visualPaused;void setVisualPaused(true);$('intro-help').showModal();};
  $('intro-help').addEventListener('close',()=>{if(resumeHelp)void setVisualPaused(!!prefs.reduceMotion||systemMotion.matches);});
  function leave(){leaving=true;video.pause();music.pause();}
  play.addEventListener('click',leave);$('intro-fallback').addEventListener('click',leave);
  document.addEventListener('visibilitychange',async()=>{if(document.hidden){video.pause();music.pause();}else{if(pendingMusic)await pendingMusic;refreshPrefs();if(!visualPaused)void setVisualPaused(false);}});
  window.addEventListener('storage',event=>{if(event.key===settingsKey)refreshPrefs();});
  window.addEventListener('pagehide',event=>{leave();if(!event.persisted&&videoUrl)URL.revokeObjectURL(videoUrl);});
  window.addEventListener('pageshow',event=>{if(event.persisted){leaving=false;refreshPrefs();if(!visualPaused)void setVisualPaused(false);}});
  systemMotion.addEventListener?.('change',()=>void setVisualPaused(!!prefs.reduceMotion||systemMotion.matches));
  const image=src=>new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=src;});
  Promise.all([image('URSKETCH_INTRO_POSTER_URL').then(img=>{poster=img;paintFrame(img);}),image('URSKETCH_INTRO_WORDMARK_URL')])
    .then(()=>document.body.classList.add('art-ready')).catch(()=>{status('Artwork unavailable. Use Play now to continue.');$('intro-fallback').hidden=false;});
  align();if(!visualPaused)void load();
})();
