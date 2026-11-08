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
AudioBufferSourceNode.prototype.start=function(...args){scheduled.push({cue:this.urSketchCue,when:args[0],gain:this.urSketchGain});nodes.push(this);return start.apply(this,args);};
AudioBufferSourceNode.prototype.stop=function(...args){this.testStopAt=args[0];stopped.push(this.urSketchCue);return stop.apply(this,args);};
const engine=createGameAudio({urls:URLS,getPrefs:()=>prefs,notify:message=>{throw new Error(message);}});
</script>'''.replace('URLS',json.dumps(urls))
with sync_playwright() as p:
 browser=getattr(p,os.environ.get('URSKETCH_AUDIO_BROWSER','chromium')).launch();page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
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
 # The supplied MP3 is expanded to one finite 20-second track. The native
 # source never loops, including on interruption/resume near the clip end.
 page.evaluate("()=>{scheduled.length=nodes.length=0;engine.fireworks({key:'finale',elapsed:7,remaining:3000});}")
 assert page.evaluate("nodes.length===1 && !nodes[0].loop && Math.abs(nodes[0].buffer.duration-20)<.001")
 # Check actual decoded samples, including the original clip's repeat boundary
 # and silence at the very end, rather than just inspecting scheduling calls.
 assert page.evaluate("""async()=>{const response=await fetch(URLS.Fireworks);const original=await engine.context.decodeAudioData(await response.arrayBuffer());const a=original.getChannelData(0),b=nodes[0].buffer.getChannelData(0);return [100,10000,a.length+100,a.length*2+100].every(i=>Math.abs(b[i]-a[i%a.length])<1e-6)&&b.at(-1)===0;}""".replace('URLS',json.dumps(urls)))
 page.wait_for_function('()=>{const pcm=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(pcm);return pcm.some(x=>Math.abs(x)>.001);}')
 page.evaluate("()=>{prefs.muted=true;engine.settings();}");page.wait_for_timeout(100)
 before=page.evaluate('nodes.length');page.evaluate("()=>{prefs.muted=false;engine.settings();}");assert page.evaluate('nodes.length')==before+1
 page.evaluate('engine.stopFireworks()');before=page.evaluate('scheduled.length');page.wait_for_timeout(150);assert page.evaluate('scheduled.length')==before
 # The 40-second visuals keep running; only the first 20 seconds have audio.
 page.evaluate("()=>{engine.stop();nodes.length=0;engine.fireworks({key:'half',elapsed:0,remaining:40000});}")
 assert page.evaluate("nodes.length===1 && nodes[0].urSketchGain===.5 && Math.abs(nodes[0].testStopAt-scheduled.at(-1).when-20)<.05")
 page.evaluate("()=>{engine.stopFireworks();nodes.length=0;engine.fireworks({key:'late',elapsed:21,remaining:19000});engine.settings();}")
 assert page.evaluate('nodes.length')==0,'Late rejoin restarted fireworks after the audio window'
 # A stalled device audio clock cannot keep fireworks alive past wall time.
 page.evaluate("""()=>{engine.stop();nodes.length=0;engine.countdown(1000,'finishing');engine.fireworks({key:'wall-bound',elapsed:0,remaining:350});window.ticksBefore=scheduled.filter(s=>s.cue==='TickingNoise').length;engine.countdown(1000,'illegal-during-finale');}""")
 page.wait_for_function("nodes.some(n=>n.urSketchCue==='Fireworks')")
 page.evaluate("window.fireworksTest=nodes.find(n=>n.urSketchCue==='Fireworks')")
 assert page.evaluate("nodes.filter(n=>n.urSketchCue==='TickingNoise').every(n=>n.cancelled) && scheduled.filter(s=>s.cue==='TickingNoise').length===ticksBefore")
 page.wait_for_function("fireworksTest.cancelled && engine.context.state==='suspended'")
 # An early ended notification is final; do not create rapid replacement loops.
 page.evaluate("()=>{engine.stop();nodes.length=0;engine.fireworks({key:'ended-once',elapsed:0,remaining:2000});}")
 page.wait_for_function('nodes.length===1')
 page.evaluate("()=>{const v=nodes[0];v.onended?.();stop.call(v);}")
 page.wait_for_function("engine.context.state==='suspended'")
 page.evaluate("()=>{for(let i=0;i<40;i++){engine.fireworks({key:'ended-once',elapsed:0,remaining:40000});engine.settings();}}")
 assert page.evaluate('nodes.length')==1,'Room updates resurrected an ended finale'
 # A suspended mobile page can leave performance/audio clocks behind wall time.
 # Expiration must still silence the source and remain final after resume.
 page.evaluate("()=>{engine.stop();nodes.length=0;engine.fireworks({key:'suspended-clock',elapsed:0,remaining:40000});}")
 page.wait_for_function('nodes.length===1')
 page.evaluate("""()=>{window.realNow=performance.now.bind(performance);window.realDateNow=Date.now;const frozen=performance.now();performance.now=()=>frozen;window.interruptedVoice=nodes[0];Date.now=()=>realDateNow()+30000;engine.settings();Date.now=realDateNow;performance.now=realNow;engine.fireworks({key:'suspended-clock',elapsed:0,remaining:40000});}""")
 assert page.evaluate('interruptedVoice.cancelled && nodes.length===1'), 'Suspension kept or restarted fireworks'
 page.wait_for_function("engine.context.state==='suspended'")
 # New game cues wake the rested output, including background drawing alerts.
 page.evaluate("()=>{engine.play('NewRound');engine.play('YourTurnToDraw');}")
 page.wait_for_function("nodes.some(n=>n.urSketchCue==='NewRound') && nodes.some(n=>n.urSketchCue==='YourTurnToDraw')")
 page.wait_for_function('()=>{const pcm=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(pcm);return pcm.some(x=>Math.abs(x)>.001);}')
 assert page.evaluate("engine.context.state==='running' && nodes.filter(n=>n.urSketchCue==='Fireworks').every(n=>n.cancelled)")
 # An actual interrupted/resumed context creates at most one remaining finite
 # voice; regular state updates cannot start another source beside it.
 page.evaluate("()=>{engine.stop();nodes.length=0;engine.fireworks({key:'resume',elapsed:4,remaining:36000});}")
 page.wait_for_function('nodes.length===1')
 page.evaluate('engine.context.suspend()')
 page.wait_for_timeout(100)
 page.evaluate('engine.context.resume()')
 page.wait_for_function('nodes.length===2')
 page.evaluate("()=>{for(let i=0;i<40;i++)engine.fireworks({key:'resume',elapsed:4.2,remaining:35800});}")
 assert page.evaluate('nodes.length===2 && nodes[0].cancelled && !nodes[1].loop && nodes[1].testStopAt-nodes[1].context.currentTime<=16'), 'Resume overlapped or looped fireworks'
 page.evaluate('engine.stop()')
 # Exercise the full, real 20-second output window while the same room sends
 # frequent updates. Then leave its silent second half running with no voices.
 page.evaluate("""()=>{nodes.length=0;window.fullStart=Date.now();engine.fireworks({key:'full-window',elapsed:0,remaining:40000});window.fullUpdates=setInterval(()=>{const elapsed=Date.now()-fullStart;engine.fireworks({key:'full-window',elapsed:elapsed/1000,remaining:40000-elapsed});},50);}""")
 page.wait_for_function('nodes.length===1')
 page.wait_for_function("engine.context.state==='suspended'",timeout=25000)
 assert page.evaluate("Date.now()-fullStart>=19500 && Date.now()-fullStart<24000 && nodes.length===1 && !nodes[0].loop && nodes[0].cancelled"), 'Full fireworks playback did not stop once at 20 seconds'
 page.wait_for_timeout(500)
 assert page.evaluate("nodes.length===1 && engine.context.state==='suspended'")
 page.evaluate('clearInterval(fullUpdates)')
 page.locator('button').click();page.wait_for_timeout(100)
 assert page.evaluate("engine.context.state==='suspended' && nodes.length===1"), 'An unrelated click woke silent finale output'
 # A room-join cue overlapping the deadline may finish, then output must rest.
 page.evaluate("()=>{engine.stop();nodes.length=0;engine.fireworks({key:'overlap-cue',elapsed:0,remaining:200});engine.play('YourTurnToDraw');}")
 page.wait_for_function("nodes.some(n=>n.urSketchCue==='YourTurnToDraw')")
 page.wait_for_function("engine.context.state==='suspended'",timeout=10000)
 assert page.evaluate("nodes.filter(n=>n.urSketchCue==='Fireworks').every(n=>n.cancelled)")
 page.evaluate('engine.stop()')

 assert not errors,errors
 (ROOT/('artifacts/audio-clock-verification'+('-webkit' if os.environ.get('URSKETCH_AUDIO_BROWSER')=='webkit' else '')+'.json')).write_text(json.dumps({'decodedCues':len(urls),'suppliedFireworksPCMAndFinitePlayback':True,'fireworksDurationSeconds':20,'nativeAudioLoops':False,'repeatedRoomUpdatesCannotRestartEndedFinale':True,'suspendedPerformanceClockStillExpires':True,'contextResumeHasOneFiniteVoice':True,'silentFinaleSuspendsOutput':True,'nextGameCuesWakeOutput':True,'unrelatedClicksKeepSilentOutputSuspended':True,'fullTwentySecondPlaybackAndSilentUpdates':True,'overlappingCueThenSilentOutput':True,'fireworksHalfGain':True,'fireworksTwentySecondAudioWindow':True,'lateFinaleRemainsSilent':True,'wallClockCutsOffFireworks':True,'ticksCannotOverlapFinale':True,'earlyEndedFireworksCannotRestart':True,'fireworksMuteAndStop':True,'nonzeroPCM':True,'backgroundCue':True,'wholeWindowScheduledAhead':True,'twoSecondTicks':8,'intervalSeconds':.25,'muteCancelsScheduledSources':True,'leavingStopsScheduler':True,'clockDivergenceCannotReplayFinishedSlots':True,'completedRoundCannotRestart':True},indent=2)+'\n')
 browser.close();print('PASS: finite fireworks PCM, interruption/resume and ended-finale guards; background cues and bounded 4 Hz ticks')
