"""Authoritative game events and real decoded audio on isolated ~zod / ~nec."""
import json,re,time,urllib.request,sys,traceback,os,runpy
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
preview=None
if os.environ.get('URSKETCH_PREVIEW')=='1':
 sys.path.insert(0,str(ROOT/'scripts'));preview=runpy.run_path(str(ROOT/'scripts/build.py'))['html']

sys.excepthook=lambda kind,error,tb:sys.stderr.write(''.join(line for line in traceback.format_exception(kind,error,tb) if 'cookie:' not in line.lower()))
def dojo(port,command):
 request=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(request,timeout=60))
lenses={dojo(port,'our').strip():port for port in (12322,12323)}
assert set(lenses)=={'~zod','~nec'},'Only isolated fake ships are allowed'
def cue(page,name,count=1):
 page.wait_for_function('([name,count])=>name==="TickingNoise"?heard.some(e=>e.cue===name):heard.filter(e=>e.cue===name).length===count',arg=[name,count],timeout=15000)
with sync_playwright() as p:
 browser=p.chromium.launch();contexts=[browser.new_context(viewport={'width':1280,'height':720}) for _ in range(2)];pages=[];errors=[]
 for context,ship,origin in zip(contexts,['~zod','~nec'],['http://127.0.0.1:18080','http://127.0.0.1:18081']):
  code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lenses[ship],'+code')).group()
  assert context.request.post(origin+'/~/login',form={'password':code}).ok
  if preview:
   body=preview.replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
   for path in ['play','connect']:context.route('**/apps/ursketch/'+path+'**',lambda route,request,body=body:route.fulfill(status=200,content_type='text/html',body=body))
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("window.heard=[];window.addEventListener('ursketch:sound',e=>heard.push(e.detail));")
  page.goto(origin+'/apps/ursketch/play');expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
  assert page.evaluate('GLOBAL_CHAT_HOST')=='~zod'
  page.locator('#browser-settings').click();page.locator('#settings-reset').click();page.locator('#settings-close').click()
  page.wait_for_function('gameAudio.loaded.length===9',timeout=30000)
  assert page.evaluate("gameAudio.context.state==='running' && gameAudio.master.gain.value>.69")
  pages.append(page)
 h,g=pages
 h.locator('#create-open').click();h.locator('#title').fill(f'Sound QA {time.time_ns()}');h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
 cue(h,'JoinRoom');rid=h.evaluate('roomId')
 g.evaluate("setSearchMode('invite')");g.locator('#host').fill(f'~zod/{rid}');g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000)
 cue(h,'JoinRoom',2);cue(g,'JoinRoom')
 h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3);cue(h,'YourTurnToDraw')
 for page in pages:cue(page,'NewRound')
 assert g.evaluate("!heard.some(e=>e.cue==='YourTurnToDraw')")
 h.locator('#choices button').first.click()
 for page in pages:
  page.wait_for_function("state.phase==='drawing'");cue(page,'NewRound');assert page.evaluate('state.duration===120 && state.remainingMs>115000 && !state.finishing')
 answer=h.evaluate('state.answer');assert g.evaluate("state.answer==='' && !state.choices.length")
 assert g.evaluate("api.poke('hint').then(()=>false,()=>true)")
 h.locator('#give-hint').click()
 for page in pages:cue(page,'HintNoise')
 # Ordinary wrong guesses stay public; close guesses are private.
 g.locator('#guess').fill('zzzxq');g.locator('#guess').press('Enter');expect(h.locator('#messages')).to_contain_text('zzzxq')
 # A typo is detected privately by the host; only its sender gets the cue/message.
 near=answer[:-1] if len(answer)>3 else answer[0]+answer[-1]
 g.locator('#guess').fill(near);g.locator('#guess').press('Enter');cue(g,'CloseGuess')
 expect(g.locator('#messages .close')).to_have_text(near+' is close!')
 assert h.locator('#messages .close').count()==0
 assert not h.evaluate('(near)=>state.messages.some(m=>m.text===near)',near)
 assert not g.evaluate('(near)=>state.messages.some(m=>m.text===near)',near)
 assert h.evaluate("!heard.some(e=>e.cue==='CloseGuess')")
 h.evaluate("api.poke('chat',{text:'Keep drawing'})")
 expect(g.locator('#chat-messages')).to_contain_text('Keep drawing');expect(g.locator('#messages .close')).to_have_text(near+' is close!')
 # The player-name menu writes an authoritative warning to bottom Chat.
 g.locator('#players .player-name').filter(has_text='~zod').click();expect(g.locator('#warn-player')).to_be_visible();g.locator('#warn-player').click()
 for page in pages:
  expect(page.locator('#chat-messages')).to_contain_text('reminds ~zod not to violate drawing rules.');cue(page,'RemindsRules')
 assert g.evaluate("api.poke('warn',{player:'~bud'}).then(()=>false,()=>true)")
 assert g.evaluate("api.poke('warn',{player:'~nec'}).then(()=>false,()=>true)")
 g.locator('#guess').fill(answer);started=time.monotonic();g.locator('#guess').press('Enter')
 cue(g,'YouGotTheWord');cue(h,'SomeoneElseGotTheWord')
 for page in pages:
  assert page.evaluate("state.phase==='drawing' && state.finishing && state.duration===20 && state.remainingMs>19000")
  cue(page,'TickingNoise',1);expect(page.locator('#give-hint')).to_be_disabled()
 assert h.evaluate("api.poke('hint').then(()=>false,()=>true)")
 # Repeated snapshots must not replay any one-shot cues or erase private feedback.
 g.evaluate("api.poke('sync')");g.wait_for_timeout(1100)
 assert g.evaluate("heard.filter(e=>e.cue==='YouGotTheWord').length===1")
 expect(g.locator('#messages .close')).to_have_text(near+' is close!')
 # Mute and volume control the actual Web Audio gain, independent of theme toggles.
 h.locator('#settings-open').click();h.locator('#sound-volume').evaluate("el=>{el.value=25;el.dispatchEvent(new Event('input'));}")
 h.wait_for_function('Math.abs(gameAudio.master.gain.value-.25)<1e-6')
 h.locator('#theme-song-disabled').check();h.wait_for_function('Math.abs(gameAudio.master.gain.value-.25)<1e-6')
 h.locator('#sound-muted').check();h.wait_for_function('gameAudio.master.gain.value===0')
 h.wait_for_timeout(300);n=h.evaluate("heard.filter(e=>e.cue==='TickingNoise').length");h.wait_for_timeout(600);assert h.evaluate("heard.filter(e=>e.cue==='TickingNoise').length")==n
 h.locator('#sound-muted').uncheck();h.locator('#settings-close').click()
 # No premature all-solved reveal; native deadline ends the turn at 20 seconds.
 assert h.evaluate("state.phase==='drawing'")
 g.wait_for_function("state.phase==='reveal'",timeout=25000);elapsed=time.monotonic()-started
 assert 19.5<elapsed<24,elapsed
 g.wait_for_timeout(350)
 ticks=g.evaluate("heard.filter(e=>e.cue==='TickingNoise').map(e=>e.when)")
 assert 77<=len(ticks)<=81,len(ticks)
 assert all(abs(b-a-.25)<1e-6 for a,b in zip(ticks,ticks[1:])),ticks
 for page in pages:
  assert page.evaluate("heard.filter(e=>e.cue==='HintNoise').length===1")
  n=page.evaluate("heard.filter(e=>e.cue==='TickingNoise').length");page.wait_for_timeout(400);assert page.evaluate("heard.filter(e=>e.cue==='TickingNoise').length")==n
 scores=h.evaluate('Object.fromEntries(state.players.map(p=>[p.ship,p.score]))');assert scores=={'~zod':5,'~nec':10},scores
 # Rotation gives the next artist their own cue. Historical state on refresh stays quiet.
 g.wait_for_function("state.phase==='choosing'",timeout=10000);cue(g,'YourTurnToDraw')
 g.reload();expect(g.locator('#game')).to_be_visible(timeout=30000);assert g.evaluate('heard.length')==0
 h.screenshot(path=str(ROOT/'artifacts/game-sounds.png'))
 for page in [g,h]:page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/game-sounds-verification.json').write_text(json.dumps({'isolatedShips':['~zod','~nec'],'decodedCues':9,'privateCloseGuess':True,'publicWarningAndValidation':True,'correctCueRouting':True,'hintsAndDeduplication':True,'drawingSeconds':120,'finishSeconds':20,'measuredFinishSeconds':round(elapsed,3),'tickCount':len(ticks),'tickIntervalSeconds':.25,'masterGainMuteAndThemeIndependence':True,'refreshDoesNotReplay':True},indent=2)+'\n')
 browser.close();print('PASS: nine decoded cues, private close guesses, warning permissions, correct cue routing, 120/20-second timing, 4 Hz audio clock, mute/volume, deduplication and silent historical snapshots')
