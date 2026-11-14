"""Intro fidelity, clean presentation, immediate/blocked audio, and shared settings."""
import base64,hashlib,json,os,re,runpy,sys,traceback,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
sys.excepthook=lambda kind,error,tb:sys.stderr.write(''.join(line for line in traceback.format_exception(kind,error,tb) if 'cookie:' not in line.lower()))
ROOT=Path(__file__).resolve().parents[1]
ORIGIN=os.environ.get('URSKETCH_ORIGIN','http://127.0.0.1:18080')
LENS=os.environ.get('URSKETCH_LENS_URL','http://127.0.0.1:12322')
PREVIEW=os.environ.get('URSKETCH_PREVIEW')=='1'
req=urllib.request.Request(LENS,data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
def code():return re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(req,timeout=30))).group()
manifest=json.loads((ROOT/'artifacts/media-manifest.json').read_text());track=json.loads((ROOT/'web/intro-motion.json').read_text())
render=None
if PREVIEW:
 sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
def authenticate(context):assert context.request.post(ORIGIN+'/~/login',form={'password':code()}).ok
def prepare(context):
 authenticate(context)
 if render:
  current=context.request.get(ORIGIN+'/apps/ursketch/play').text();ship=re.search(r"window.URSKETCH_SHIP='([^']+)'",current).group(1)
  context.route('**/apps/ursketch',lambda route:route.fulfill(status=200,content_type='text/html',body=render['intro']))
  for path in ('play','connect'):
   context.route('**/apps/ursketch/'+path,lambda route:route.fulfill(status=200,content_type='text/html',body=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship))))
 context.add_init_script("window.testAudios=[];window.OriginalAudio=Audio;window.Audio=class extends OriginalAudio{constructor(...args){super(...args);testAudios.push(this);}}")
def song(page,expression):return page.evaluate('()=>{const music=testAudios[0];return '+expression+';}')
def slider(page,value):page.locator('#sound-volume').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input"));}',value)
def seek(page,time):
 page.locator('video').evaluate('(v,t)=>new Promise(resolve=>{v.addEventListener("seeked",resolve,{once:true});v.currentTime=t})',time)
 page.wait_for_timeout(80)
def fit(page,width,height):
 page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(80)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
 old=min(width-(8 if width<=600 else 16),1620,(height-(110 if width<=600 else 78))*1.5)
 assert abs(page.locator('#intro-stage').bounding_box()['width']-old*.72)<1
def clean_background(page):
 # Inspect the logo's main band. The original hair beneath it is intentionally
 # preserved; intro-hair.py checks that lower edge across every source frame.
 assert page.evaluate("""()=>{
  const c=document.querySelector('#intro-scene'),x=c.getContext('2d'),d=x.getImageData(0,0,c.width,c.height).data;
  const pixel=(a,b)=>Array.from(d.slice((b*c.width+a)*4,(b*c.width+a)*4+3));
  const sky=pixel(1590,10),circle=pixel(1000,200);
  for(let y=0;y<225;y++)for(let a=940;a<1620;a++){
   const radius=Math.hypot(a+.5-738,y+.5-532);if(Math.abs(radius-511)<2)continue;
   const expected=radius<511?circle:sky,actual=pixel(a,y);
   if(actual.some((v,i)=>v!==expected[i]))return false;
  }return true;
 }""")
 # Check screenshot pixels, rather than merely comparing CSS to decoded video.
 # This catches differences introduced by the browser's video compositor.
 stage=page.locator('#intro-stage').bounding_box()
 pairs=[]
 for right in (False,True):
  for bottom in (False,True):
   x=stage['x']+stage['width'] if right else stage['x']
   y=stage['y']+stage['height'] if bottom else stage['y']
   pairs.append([round(x+(-8 if right else 8)),round(y+(-8 if bottom else 8)),round(x+(8 if right else -8)),round(y+(-8 if bottom else 8))])
 shot=base64.b64encode(page.screenshot()).decode()
 assert page.evaluate("""async({shot,pairs})=>{
  const image=new Image();image.src='data:image/png;base64,'+shot;await image.decode();
  const c=document.createElement('canvas');c.width=image.width;c.height=image.height;
  const x=c.getContext('2d');x.drawImage(image,0,0);
  return pairs.every(([a,b,c,d])=>{const inside=x.getImageData(a,b,1,1).data,outside=x.getImageData(c,d,1,1).data;return inside.every((v,i)=>v===outside[i]);});
 }""",{'shot':shot,'pairs':pairs})
with sync_playwright() as p:
 browser=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']);context=browser.new_context(viewport={'width':1280,'height':900})
 denied=context.request.get(ORIGIN+'/apps/ursketch',max_redirects=0);assert denied.status==303
 denied=context.request.get(ORIGIN+manifest['audio/music/theme_song.mp3']['url'],max_redirects=0);assert denied.status==303 and len(denied.body())<1000
 prepare(context)
 for name,asset in manifest.items():
  response=context.request.get(ORIGIN+asset['url']);assert response.status==200,(name,response.status)
  assert response.headers['content-type']==asset['mime'];assert len(response.body())==asset['bytes']
  assert hashlib.sha256(response.body()).hexdigest()==asset['sha256'];assert 'immutable' in response.headers['cache-control']
 assert context.request.get(ORIGIN+'/apps/ursketch/media/missing.mp3').status==404
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 held=[];page.route('**/video/intro.mp4',lambda route:held.append(route))
 page.goto(ORIGIN+'/apps/ursketch',wait_until='domcontentloaded');expect(page).to_have_title('urSketch · Play now')
 # Audio starts while the video request is deliberately held: it does not wait for animation.
 page.wait_for_function('testAudios[0].currentTime>.1 && !testAudios[0].paused',timeout=15000)
 assert page.locator('video').evaluate('v=>v.readyState===0')
 assert page.locator('.intro-controls').count()==0
 assert page.locator('#intro-motion,#intro-sound,#intro-volume').count()==0
 assert page.locator('#settings-open').is_visible()
 assert held;held[0].continue_();page.unroute('**/video/intro.mp4')
 page.wait_for_function("document.body.classList.contains('art-ready') && document.querySelector('video').readyState>=2",timeout=30000)
 page.locator('video').evaluate('v=>v.pause()')
 sizes=[]
 for frame in [0,1,24,60,72,84,96,144,156,180,300,420,441]:
  seek(page,frame/24+.002)
  stage=page.locator('#intro-stage').bounding_box();box=page.locator('#intro-play').bounding_box();x,y,w,h=track['frames'][frame]
  assert abs((box['x']+box['width']/2-stage['x'])/stage['width']*1620-x)<3
  assert abs((box['y']+box['height']/2-stage['y'])/stage['height']*1080-y)<3
  sizes.append(box['width']);clean_background(page)
 for time in [3.002,3.502,6.002,6.502]:
  seek(page,time)
  pixel=page.evaluate("()=>Array.from(document.querySelector('#intro-scene').getContext('2d').getImageData(1000,200,1,1).data).slice(0,3)");assert all(abs(a-b)<=3 for a,b in zip(pixel,[45,100,154])),(time,pixel)
 assert max(sizes)>min(sizes)*2
 seek(page,4)
 # The page's colour follows the decoded video, including fade-out colour changes.
 assert page.evaluate("()=>{const v=document.querySelector('video'),c=document.createElement('canvas');c.width=c.height=1;const x=c.getContext('2d');x.drawImage(v,1590,10,1,1,0,0,1,1);const d=x.getImageData(0,0,1,1).data;return getComputedStyle(document.body).backgroundColor===`rgb(${d[0]}, ${d[1]}, ${d[2]})`;}")
 fit(page,1280,900);page.screenshot(path=str(ROOT/'artifacts/intro-desktop.png'))
 page.locator('#intro-instructions').click();expect(page.locator('#intro-help')).to_be_visible();page.locator('#intro-help button').click()
 page.locator('#settings-open').click();slider(page,100)
 assert abs(song(page,'music.volume')-1)<.01
 page.locator('#theme-song-quarter').check();assert abs(song(page,'music.volume')-.25)<.01
 page.locator('#theme-song-disabled').check();assert song(page,'music.paused')
 assert page.evaluate("JSON.parse(localStorage.getItem('ursketch.settings.v1')).themeDisabled")
 page.screenshot(path=str(ROOT/'artifacts/intro-settings.png'))
 page.locator('#settings-close').click()
 for width,height in [(1024,600),(390,844),(320,568)]:fit(page,width,height)
 page.screenshot(path=str(ROOT/'artifacts/intro-mobile.png'))
 page.locator('#intro-play').click();page.wait_for_url('**/apps/ursketch/connect');page.evaluate('characterReady');expect(page.locator('#player-name')).to_have_value(page.evaluate('activeName'));page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
 page.locator('#browser-settings').click();expect(page.locator('#theme-song-quarter')).to_be_checked();expect(page.locator('#theme-song-disabled')).to_be_checked()
 page.locator('#theme-song-disabled').uncheck();page.locator('#settings-close').click()
 page.goto(ORIGIN+'/apps/ursketch');page.wait_for_function('!testAudios[0].paused && testAudios[0].currentTime>0')
 assert abs(song(page,'music.volume')-.25)<.01
 # Preferences changed in the game must be re-applied after back/forward-cache restoration.
 page.evaluate("()=>{const s=JSON.parse(localStorage.getItem('ursketch.settings.v1'));s.themeDisabled=true;localStorage.setItem('ursketch.settings.v1',JSON.stringify(s));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}));}")
 assert song(page,'music.paused');page.locator('#settings-open').click();expect(page.locator('#theme-song-disabled')).to_be_checked();page.locator('#settings-close').click()
 # Disable means no automatic music request, including on a fresh intro page.
 disabled=browser.new_context();prepare(disabled);disabled.add_init_script("localStorage.setItem('ursketch.settings.v1',JSON.stringify({themeDisabled:true}))")
 dp=disabled.new_page();requested=[];dp.on('request',lambda r:requested.append(r.url));dp.goto(ORIGIN+'/apps/ursketch');dp.wait_for_function("document.body.classList.contains('art-ready')")
 assert song(dp,'music.paused && !music.getAttribute("src")');assert not any('theme_song.mp3' in url for url in requested)
 # Reduced motion affects visuals; music remains a separately controlled preference.
 reduced=browser.new_context(reduced_motion='reduce');prepare(reduced)
 rp=reduced.new_page();rp.goto(ORIGIN+'/apps/ursketch');rp.wait_for_function("document.body.classList.contains('art-ready')")
 assert rp.locator('video').evaluate('v=>v.paused&&!v.getAttribute("src")')
 rp.wait_for_function('testAudios[0].currentTime>0');rp.locator('#intro-play').click();expect(rp.locator('#connect-page')).to_be_visible();rp.locator('#connect-submit').click();expect(rp.locator('#lobby')).to_be_visible()
 # Let three passes play naturally. Simulate a callback clock that continues
 # across loops; the media element's playhead still resets normally. The old
 # client used that unbounded clock to darken the logo and seek audio to EOF.
 loops=browser.new_context(viewport={'width':1280,'height':900});prepare(loops)
 loops.add_init_script("""(()=>{
  const original=HTMLVideoElement.prototype.requestVideoFrameCallback,clocks=new WeakMap();
  HTMLVideoElement.prototype.requestVideoFrameCallback=function(callback){
   return original.call(this,(now,data)=>{
    const clock=clocks.get(this)||{last:0,offset:0};
    if(data.mediaTime<clock.last-.5)clock.offset+=this.duration;
    clock.last=data.mediaTime;clocks.set(this,clock);
    window.testCallbackTime=data.mediaTime+clock.offset;
    callback(now,{...data,mediaTime:window.testCallbackTime});
   });
  };
 })();""")
 lp=loops.new_page();lp.on('pageerror',lambda e:errors.append(str(e)));lp.goto(ORIGIN+'/apps/ursketch')
 lp.wait_for_function('document.querySelector("video").readyState>=2 && !testAudios[0].paused')
 lp.evaluate("""async()=>{
  const audio=testAudios[0],video=document.querySelector('video');
  const ac=new AudioContext(),source=ac.createMediaElementSource(audio),analyser=ac.createAnalyser();
  source.connect(analyser);analyser.connect(ac.destination);await ac.resume();
  window.loopAudioContext=ac;const data=new Float32Array(analyser.fftSize);
  const probe=window.introLoopProbe={cycle:0,last:video.currentTime,passes:[]};
  window.loopProbeTimer=setInterval(()=>{
   const time=video.currentTime;if(time<probe.last-.5)probe.cycle++;probe.last=time;
   if(time<2||time>3)return;
   const pass=probe.passes[probe.cycle]||={samples:0,peakRms:0,maxDrift:0,minBrightness:1,paused:false};
   analyser.getFloatTimeDomainData(data);const rms=Math.sqrt(data.reduce((sum,v)=>sum+v*v,0)/data.length);
   const brightness=Number(document.querySelector('#intro-wordmark').style.filter.match(/brightness\(([^)]+)\)/)[1]);
   pass.samples++;pass.peakRms=Math.max(pass.peakRms,rms);pass.maxDrift=Math.max(pass.maxDrift,Math.abs(audio.currentTime-time));
   pass.minBrightness=Math.min(pass.minBrightness,brightness);pass.paused||=audio.paused||audio.ended;
  },50);
 }""")
 lp.wait_for_function('introLoopProbe.passes[2]?.samples>=8',timeout=55000)
 result=lp.evaluate("()=>{clearInterval(loopProbeTimer);return {passes:introLoopProbe.passes,callbackTime:testCallbackTime,videoTime:document.querySelector('video').currentTime};}")
 assert result['callbackTime']>36 and result['videoTime']<4,result
 for playback in result['passes'][:3]:
  assert playback['samples']>=8 and playback['peakRms']>.001,playback
  assert playback['maxDrift']<.35 and playback['minBrightness']==1 and not playback['paused'],playback
 (ROOT/'artifacts/intro-loops.json').write_text(json.dumps(result,indent=2)+'\n')
 loops.close()
 assert not errors,errors
 browser.close()
 # A denied autoplay attempt retries on a genuine first interaction, with no control bar.
 blocked=p.chromium.launch(args=['--autoplay-policy=user-gesture-required']);bc=blocked.new_context();prepare(bc)
 bc.add_init_script("""window.soundGesture=false;window.addEventListener('pointerdown',e=>{if(e.isTrusted)soundGesture=true},true);const originalPlay=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){if(this instanceof HTMLAudioElement&&!soundGesture)return Promise.reject(new DOMException('Gesture required','NotAllowedError'));return originalPlay.call(this);};""")
 bp=bc.new_page();bp.goto(ORIGIN+'/apps/ursketch');bp.wait_for_function("document.body.classList.contains('art-ready')")
 assert song(bp,'music.paused');assert bp.locator('.intro-controls').count()==0
 bp.mouse.click(15,300);bp.wait_for_function('!testAudios[0].paused && testAudios[0].currentTime>0',timeout=15000)
 blocked.close()
 print('PASS: exact media; audio starts before video load; quarter/off settings shared with game; blocked-autoplay interaction fallback; no bottom controls; pixel-verified seam-free background and complete original-logo removal; 72% sizing; hit targets; reduced motion and navigation; three audible passes with logo reset and unbounded callback timestamps.')
