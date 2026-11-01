/* Browser-local preferences and the audio output used by game sounds. */
function createSettings({notify,onChange}) {
  const $=id=>document.getElementById(id),key='ursketch.settings.v1';
  const defaults={theme:'classic',volume:70,muted:false,output:'',reduceMotion:false,largeChat:false,themeQuiet:false,themeDisabled:false};
  function readPrefs(){
    const next={...defaults};
    try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(saved){
      next.theme=['classic','blingee'].includes(saved.theme)?saved.theme:'classic';
      next.volume=Number.isFinite(saved.volume)?Math.max(0,Math.min(100,saved.volume)):70;
      for(const name of ['muted','reduceMotion','largeChat','themeQuiet','themeDisabled'])next[name]=saved[name]===true;
      next.output=typeof saved.output==='string'?saved.output:'';
    }}catch{}
    return next;
  }
  let prefs=readPrefs();
  const audio=new Audio();audio.preload='auto';
  let toneUrl=null;
  function apply(){
    document.body.dataset.theme=prefs.theme;document.body.dataset.layout='classic';
    document.body.classList.toggle('reduce-motion',prefs.reduceMotion);
    document.body.classList.toggle('large-chat',prefs.largeChat);
    audio.volume=prefs.volume/100;audio.muted=prefs.muted;
    $('theme-select').value=prefs.theme;$('sound-volume').value=prefs.volume;$('volume-value').value=prefs.volume+'%';
    $('sound-muted').checked=prefs.muted;$('reduce-motion').checked=prefs.reduceMotion;$('large-chat').checked=prefs.largeChat;
    $('theme-song-quarter').checked=prefs.themeQuiet;$('theme-song-disabled').checked=prefs.themeDisabled;
    onChange?.({...prefs});
  }
  function save(){try{localStorage.setItem(key,JSON.stringify(prefs));}catch{}apply();}
  function message(text){$('audio-status').textContent=text;}
  async function outputs(){
    const select=$('audio-output');select.replaceChildren(new Option('System default',''));
    if(!audio.setSinkId||!navigator.mediaDevices?.enumerateDevices){select.disabled=true;$('choose-output').disabled=true;message('This browser uses your system audio output. Change the device in your browser or system settings.');return;}
    select.disabled=false;$('choose-output').disabled=false;
    try{
      const devices=await navigator.mediaDevices.enumerateDevices();
      for(const device of devices.filter(d=>d.kind==='audiooutput'&&d.deviceId&&d.deviceId!=='default'))select.append(new Option(device.label||`Audio output ${select.options.length}`,device.deviceId));
      if(prefs.output&&[...select.options].some(o=>o.value===prefs.output))select.value=prefs.output;
      else if(prefs.output)message('Your saved output is unavailable. Choose a device or use system default.');
      else message(navigator.mediaDevices.selectAudioOutput?'Choose an output device, or use the system default.':'Showing permitted audio outputs. Use system settings if your device is not listed.');
      $('choose-output').textContent=navigator.mediaDevices.selectAudioOutput?'Choose output…':'Refresh devices';
    }catch{message('Audio outputs could not be listed. System default is available.');}
  }
  async function setOutput(id){
    if(!audio.setSinkId){prefs.output='';save();return;}
    await audio.setSinkId(id);prefs.output=id;save();$('audio-output').value=id;message('Audio output selected. Use Test sound to check it.');
  }
  $('settings-open').onclick=()=>{$('settings-dialog').showModal();void outputs();};
  $('settings-close').onclick=()=>$('settings-dialog').close();
  $('theme-select').onchange=e=>{prefs.theme=e.target.value;save();};
  $('sound-volume').oninput=e=>{prefs.volume=Number(e.target.value);save();};
  for(const [id,name] of [['sound-muted','muted'],['reduce-motion','reduceMotion'],['large-chat','largeChat'],['theme-song-quarter','themeQuiet'],['theme-song-disabled','themeDisabled']])$(id).onchange=e=>{prefs[name]=e.target.checked;save();};
  $('audio-output').onchange=e=>{const id=e.target.value;setOutput(id).catch(()=>{$('audio-output').value=prefs.output;message('Could not switch to that output. Choose another device or system default.');});};
  $('choose-output').onclick=async()=>{
    try{
      if(navigator.mediaDevices?.selectAudioOutput){const device=await navigator.mediaDevices.selectAudioOutput(prefs.output?{deviceId:prefs.output}:{});await setOutput(device.deviceId);await outputs();}
      else await outputs();
    }catch(e){message(e.name==='NotAllowedError'?'Output selection was cancelled or not permitted. System default is available.':'The device could not be selected. Try again or use system default.');}
  };
  function tone(){
    if(toneUrl)return toneUrl;
    const rate=22050,count=Math.floor(rate*.24),buffer=new ArrayBuffer(44+count*2),v=new DataView(buffer);
    const text=(at,s)=>{for(let i=0;i<s.length;i++)v.setUint8(at+i,s.charCodeAt(i));};
    text(0,'RIFF');v.setUint32(4,36+count*2,true);text(8,'WAVE');text(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);text(36,'data');v.setUint32(40,count*2,true);
    for(let i=0;i<count;i++){const envelope=Math.min(1,i/200,(count-i)/800);v.setInt16(44+i*2,Math.sin(i/rate*Math.PI*2*523.25)*envelope*9000,true);}
    toneUrl=URL.createObjectURL(new Blob([buffer],{type:'audio/wav'}));return toneUrl;
  }
  async function play(url){
    if(audio.setSinkId&&audio.sinkId!==prefs.output){try{await audio.setSinkId(prefs.output);}catch{await audio.setSinkId('');message('Saved output unavailable; using system default.');}}
    audio.src=url;await audio.play();
  }
  $('test-sound').onclick=()=>{if(prefs.muted||prefs.volume===0){message('Unmute and raise the volume to hear the test sound.');return;}play(tone()).catch(()=>message('Sound could not play. Check your browser audio permissions.'));};
  $('settings-reset').onclick=()=>{prefs={...defaults};save();void setOutput('').catch(()=>{});void outputs();};
  navigator.mediaDevices?.addEventListener?.('devicechange',()=>{if($('settings-dialog').open)void outputs();});
  window.addEventListener('storage',e=>{if(e.key===key)notify('Settings changed in another tab. Reload to use those preferences here.');});
  apply();
  return {play,refresh(){prefs=readPrefs();apply();},get values(){return {...prefs};},get audio(){return audio;}};
}
