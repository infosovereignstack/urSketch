"""Ten native rounds, authoritative 40-second finale, winner persistence and sounds."""
import json,re,time,urllib.request,sys,runpy
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
manifest=json.loads((ROOT/'artifacts/media-manifest.json').read_text())
def dojo(port,command):
 request=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(request,timeout=60))
lenses={dojo(port,'our').strip():port for port in (12322,12323)}
assert set(lenses)=={'~zod','~nec'},'Only isolated fake ships allowed'
with sync_playwright() as p:
 browser=p.chromium.launch();pages=[];errors=[]
 for ship,name,port in [('~zod','Alice',18080),('~nec','Zoe',18081)]:
  context=browser.new_context(viewport={'width':1280,'height':720});origin=f'http://127.0.0.1:{port}'
  code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lenses[ship],'+code')).group()
  assert context.request.post(origin+'/~/login',form={'password':code}).ok
  body=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
  for path in ('play','connect'):context.route('**/apps/ursketch/'+path+'**',lambda route,request,body=body:route.fulfill(status=200,content_type='text/html',body=body))
  def media(route):
   asset=next((name for name,a in manifest.items() if route.request.url.endswith(a['url'])),None)
   assert asset,route.request.url
   route.fulfill(status=200,content_type=manifest[asset]['mime'],body=(ROOT/'desk/media'/asset).read_bytes())
  context.route('**/apps/ursketch/media/**',media)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script("window.heard=[];window.addEventListener('ursketch:sound',e=>heard.push(e.detail))")
  page.goto(origin+'/apps/ursketch/connect');page.locator('#player-name').fill(name);page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
  page.locator('#browser-settings').click();page.locator('#settings-reset').click();page.locator('#settings-close').click()
  page.wait_for_function('gameAudio?.loaded.length===9',timeout=30000);pages.append(page)
 h,g=pages
 h.locator('#create-open').click();h.locator('#title').fill(f'Finale QA {time.time_ns()}');h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
 rid=h.evaluate('roomId');g.evaluate("setSearchMode('invite')");g.locator('#host').fill(f'~zod/{rid}');g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000)
 h.wait_for_function('state.players.length===2');h.locator('#start').click();h.wait_for_function("state.phase==='drawing'")
 h.locator('#give-hint').click();h.wait_for_function('state.hintCount===1');answer=h.evaluate('state.answer');g.locator('#guess').fill(answer);g.locator('#guess').press('Enter')
 for turn in range(1,9):
  h.wait_for_function('(turn)=>state.turn===turn',arg=turn);g.wait_for_function('(turn)=>state.turn===turn',arg=turn)
  artist=h if turn%2==0 else g;artist.evaluate("api.poke('skip')")
 for page in pages:page.wait_for_function('state.turn===9')
 g.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#ff0000',width:10,x1:100,y1:100,x2:900,y2:600,opacity:100,filled:false,seed:0,id:'final-drawing'}]})")
 answer=g.evaluate('state.answer');h.locator('#guess').fill(answer);began=time.monotonic();h.locator('#guess').press('Enter')
 for page in pages:
  page.wait_for_function("state.phase==='finished' && state.celebrating && state.winner?.name==='Zoe' && state.winner.score===20")
  assert page.evaluate('state.remainingMs>38500 && state.remainingMs<=40000')
  expect(page.locator('#game-finale')).to_be_visible();expect(page.locator('.finale-winner')).to_have_text('Zoe');expect(page.locator('.finale-score')).to_have_text('with 20 points!')
  expect(page.locator('#messages .game-result strong')).to_have_text('That was the last round. The winner is Zoe with a score of 20 points!')
  assert page.locator('#messages .game-result').evaluate("el=>getComputedStyle(el).color==='rgb(255, 0, 0)' && Number(getComputedStyle(el).fontWeight)>=700")
  assert page.locator('#timer-dial').get_attribute('aria-valuetext')==''
  expect(page.locator('#start')).to_be_hidden();assert page.locator('#game-finale button,#game-finale a').count()==0
 assert h.evaluate("api.poke('start').then(()=>false,()=>true)"),'Host allowed restart during celebration'
 h.evaluate("()=>{window.finaleAnalyser=gameAudio.context.createAnalyser();gameAudio.master.connect(finaleAnalyser)}")
 h.wait_for_function("heard.filter(e=>e.cue==='Fireworks').length>=2",timeout=10000)
 h.wait_for_function("()=>{const a=new Float32Array(finaleAnalyser.fftSize);finaleAnalyser.getFloatTimeDomainData(a);return a.some(v=>Math.abs(v)>.001)}")
 assert h.locator('#game-finale>canvas').evaluate("c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let dark=0,light=0;for(let i=0;i<d.length;i+=4){if(d[i]+d[i+1]+d[i+2]===0)dark++;else light++;}return dark>light*10 && light>0}")
 h.screenshot(path=str(ROOT/'artifacts/game-finale.png'))
 # Shared settings affect synthesized fireworks; refreshing a winner cannot erase the result.
 h.locator('#settings-open').click();h.locator('#sound-muted').check();h.locator('#settings-close').click();n=h.evaluate("heard.filter(e=>e.cue==='Fireworks').length");h.wait_for_timeout(1500);assert h.evaluate("heard.filter(e=>e.cue==='Fireworks').length")==n
 h.locator('#settings-open').click();h.locator('#sound-muted').uncheck();h.locator('#settings-close').click()
 g.reload();expect(g.locator('#game')).to_be_visible(timeout=30000);g.wait_for_function("state.celebrating && state.winner.name==='Zoe' && state.winner.score===20")
 assert g.evaluate('state.remainingMs<38000'), 'Refresh restarted 40 seconds'
 assert g.evaluate("heard.filter(e=>e.cue==='Fireworks').length===0"), 'Refreshed browser replayed missed fireworks'
 h.wait_for_function("state.phase==='finished' && !state.celebrating",timeout=42000);elapsed=time.monotonic()-began;assert 39.5<elapsed<43,elapsed
 for page in pages:expect(page.locator('#game-finale')).to_be_hidden()
 assert h.evaluate("state.lines.some(l=>l.id==='final-drawing')"),'Finale destroyed final drawing'
 assert h.locator('#messages .game-result').count()==1
 expect(h.locator('#start')).to_be_visible();h.locator('#start').click();h.wait_for_function("state.phase==='drawing' && state.turn===0 && state.winner===null")
 for page in (g,h):page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/finale-verification.json').write_text(json.dumps({'nativeRounds':10,'winner':'Zoe','points':20,'durationSeconds':round(elapsed,3),'restartBlocked':True,'blankTimer':True,'boldRedFinalMessage':True,'rejoinPreservesWinnerAndDeadline':True,'fireworksPCM':True,'mute':True,'finalDrawingRetained':True},indent=2)+'\n')
 browser.close();print('PASS: ten native rounds, final scoring, 40-second finale, blank timer, fireworks PCM/mute, exact bold red result, refresh persistence and restart lockout')
