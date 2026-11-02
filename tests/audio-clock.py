"""Real browser audio decoding, background cues and cancellable scheduled ticks."""
import json,os,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
urls={p.stem:'https://audio-test.invalid/'+p.name for p in (ROOT/'desk/media/audio/cues').glob('*.mp3')}
audio_source=subprocess.check_output(['git','show','ursketch-v0.13.0:web/audio.js'],cwd=ROOT,text=True) if os.environ.get('URSKETCH_AUDIO_BASELINE')=='1' else (ROOT/'web/audio.js').read_text()
html='<button>Enable audio</button><script>'+audio_source+'''
const prefs={volume:70,muted:false,output:''};window.scheduled=[];window.stopped=[];window.nodes=[];
const start=AudioBufferSourceNode.prototype.start,stop=AudioBufferSourceNode.prototype.stop;
AudioBufferSourceNode.prototype.start=function(...args){scheduled.push({cue:this.urSketchCue,when:args[0]});nodes.push(this);return start.apply(this,args);};
AudioBufferSourceNode.prototype.stop=function(...args){stopped.push(this.urSketchCue);return stop.apply(this,args);};
const engine=createGameAudio({urls:URLS,getPrefs:()=>prefs,notify:message=>{throw new Error(message);}});
</script>'''.replace('URLS',json.dumps(urls))
with sync_playwright() as p:
 browser=p.chromium.launch();page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def route(request):
  name=request.request.url.rsplit('/',1)[-1]
  if name.endswith('.mp3'):request.fulfill(status=200,content_type='audio/mpeg',body=(ROOT/'desk/media/audio/cues'/name).read_bytes())
  else:request.fulfill(status=200,content_type='text/html',body=html)
 page.route('https://audio-test.invalid/**',route);page.goto('https://audio-test.invalid/');page.locator('button').click();page.wait_for_function('(n)=>engine.loaded.length===n',arg=len(urls))
 # Verify a decoded file produces nonzero PCM at the actual gain output.
 page.evaluate("()=>{window.analyser=engine.context.createAnalyser();engine.master.connect(analyser);engine.play('JoinRoom');}")
 page.wait_for_function('()=>{const pcm=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(pcm);return pcm.some(x=>Math.abs(x)>.001);}')
 page.evaluate("()=>{engine.stop();scheduled.length=0;stopped.length=0;Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});engine.countdown(2000);}")
 ticks=page.evaluate("scheduled.filter(s=>s.cue==='TickingNoise').map(s=>s.when)")
 assert len(ticks)==8 and all(abs(b-a-.25)<1e-9 for a,b in zip(ticks,ticks[1:])),ticks
 assert abs(ticks[-1]-ticks[0]-1.75)<1e-9
 page.evaluate("()=>{prefs.muted=true;engine.settings();}")
 assert page.evaluate("stopped.filter(c=>c==='TickingNoise').length")==8
 page.evaluate("()=>{prefs.muted=false;engine.settings();engine.play('YourTurnToDraw');}")
 page.wait_for_function("scheduled.some(s=>s.cue==='YourTurnToDraw')")
 page.evaluate('engine.stop()');n=page.evaluate('scheduled.length');page.wait_for_timeout(400);assert page.evaluate('scheduled.length')==n
 # Reproduce an exhausted queue plus disagreement between the two clocks.
 # Simulate early audio-ended callbacks and an advanced audio playhead. Old
 # code resets its scheduling cursor and queues a second countdown repeatedly.
 page.evaluate("""()=>{engine.stop();scheduled.length=nodes.length=0;engine.countdown(2000,'bounded');for(const node of [...nodes]){node.onended?.();stop.call(node);}window.fakeClock=engine.context.currentTime+3;Object.defineProperty(engine.context,'currentTime',{configurable:true,get:()=>fakeClock});for(let i=0;i<40;i++)engine.countdown(2000,'bounded');delete engine.context.currentTime;}""")
 total=page.evaluate("scheduled.filter(s=>s.cue==='TickingNoise').length")
 if os.environ.get('URSKETCH_AUDIO_BASELINE')=='1':
  assert total>8,total;print('REPRODUCED old scheduler: one eight-tick window queued',total,'ticks after clock divergence');browser.close();sys.exit(0)
 assert total==8,total
 page.evaluate("engine.countdown(0,'bounded');engine.countdown(2000,'bounded')");assert page.evaluate('scheduled.length')==8
 page.evaluate("()=>{engine.stop();scheduled.length=0;engine.countdown(null,'idle');}");page.wait_for_timeout(80);page.evaluate("engine.countdown(1000,'idle')");assert page.evaluate('scheduled.length')==4;page.evaluate('engine.stop()')
 # The supplied MP3 loops once through native Web Audio, with timeline-aware
 # resume and the same master gain/output as other game audio.
 page.evaluate("()=>{scheduled.length=nodes.length=0;engine.fireworks({key:'finale',elapsed:7,remaining:3000});}")
 assert page.evaluate("nodes.length===1 && nodes[0].loop && nodes[0].buffer.duration>5 && nodes[0].buffer.duration<6")
 page.wait_for_function('()=>{const pcm=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(pcm);return pcm.some(x=>Math.abs(x)>.001);}')
 page.evaluate("()=>{prefs.muted=true;engine.settings();}");page.wait_for_timeout(100)
 before=page.evaluate('nodes.length');page.evaluate("()=>{prefs.muted=false;engine.settings();}");assert page.evaluate('nodes.length')==before+1
 page.evaluate('engine.stopFireworks()');before=page.evaluate('scheduled.length');page.wait_for_timeout(150);assert page.evaluate('scheduled.length')==before
 assert not errors,errors
 (ROOT/'artifacts/audio-clock-verification.json').write_text(json.dumps({'decodedCues':len(urls),'suppliedFireworksPCMAndLoop':True,'fireworksMuteAndStop':True,'nonzeroPCM':True,'backgroundCue':True,'wholeWindowScheduledAhead':True,'twoSecondTicks':8,'intervalSeconds':.25,'muteCancelsScheduledSources':True,'leavingStopsScheduler':True,'clockDivergenceCannotReplayFinishedSlots':True,'completedRoundCannotRestart':True},indent=2)+'\n')
 browser.close();print('PASS: real decoded PCM, background turn alerts, ahead-scheduled 4 Hz ticks, mute cancellation and stopped scheduler')
