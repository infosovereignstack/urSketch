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
  page.wait_for_function('gameAudio?.loaded.length===10',timeout=30000);pages.append(page)
 h,g=pages
 h.locator('#create-open').click();h.locator('#title').fill(f'Finale QA {time.time_ns()}');h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
 rid=h.evaluate('roomId');g.evaluate("setSearchMode('invite')");g.locator('#host').fill(f'~zod/{rid}');g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000)
 h.wait_for_function('state.players.length===2')
 # Removing players is owner-only; the removed client must stay out until it chooses to join.
 g.locator('#players .player-name').filter(has_text='Alice').click();expect(g.locator('#remove-player')).to_be_hidden();g.locator('#player-profile-dialog form button').click()
 assert g.evaluate("api.poke('kick',{player:'~zod'}).then(()=>false,()=>true)")
 h.locator('#players .player-name').filter(has_text='Zoe').click();expect(h.locator('#remove-player')).to_be_visible();h.locator('#remove-player').click()
 expect(g.locator('#lobby')).to_be_visible();h.wait_for_function('state.players.length===1');g.wait_for_timeout(1500);assert h.evaluate('state.players.length===1')
 g.evaluate("setSearchMode('invite')");g.locator('#host').fill(f'~zod/{rid}');g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000)
 h.wait_for_function('state.players.length===2');h.locator('#start').click();h.wait_for_function("state.phase==='drawing'")
 # Every tool has one selected button, with icon and hit box contained inside its rectangle.
 h.locator('#fill').click();assert h.evaluate("drawing.selected==='fill' && document.querySelectorAll('#tool-grid [aria-pressed=true]').length===1")
 h.keyboard.press('p');assert h.evaluate("drawing.selected==='pen' && document.activeElement.id==='pen' && document.querySelectorAll('#tool-grid [aria-pressed=true]').length===1")
 assert h.locator('#tool-grid button').evaluate_all("buttons=>buttons.every(b=>{const r=b.getBoundingClientRect(),s=b.querySelector('svg').getBoundingClientRect();return r.width===21&&r.height===22&&s.x>=r.x&&s.y>=r.y&&s.right<=r.right&&s.bottom<=r.bottom&&getComputedStyle(b).backgroundImage==='none';})")
 h.locator('#fill').click();h.evaluate("drawing.setColor('#ff0000')");c=h.locator('#canvas').bounding_box();h.mouse.click(c['x']+c['width']/2,c['y']+c['height']/2);h.wait_for_function("state.lines.some(l=>l.kind==='fill')")
 h.locator('#pen').click();h.evaluate("drawing.setColor('#000000')");h.mouse.move(c['x']+50,c['y']+100);h.mouse.down();h.mouse.move(c['x']+150,c['y']+150,steps=3);h.mouse.up();h.wait_for_function("state.lines.at(-1).kind==='stroke'")
 assert h.evaluate("drawing.selected==='pen' && document.querySelectorAll('#tool-grid .selected').length===1")
 h.screenshot(path=str(ROOT/'artifacts/tools-single-selection.png'))
 h.locator('#give-hint').click();h.wait_for_function('state.hintCount===1');answer=h.evaluate('state.answer');g.locator('#guess').fill(answer);g.locator('#guess').press('Enter')
 h.wait_for_function("state.players[0].ship==='~nec'")
 assert h.locator('#players li').evaluate_all("rows=>rows.map(r=>r.dataset.ship).join(',')==='~nec,~zod'")
 expect(h.locator('#players li[data-ship="~nec"] .artist-pencil')).to_have_count(1)
 assert h.locator('#players li[data-ship="~nec"] .player-name').evaluate("e=>getComputedStyle(e).color==='rgb(0, 0, 0)'")
 assert h.locator('#players li.me .player-name').evaluate("e=>getComputedStyle(e).color==='rgb(0, 128, 0)'")
 for turn in range(1,9):
  h.wait_for_function('(turn)=>state.turn===turn',arg=turn);g.wait_for_function('(turn)=>state.turn===turn',arg=turn)
  artist=h if turn%2==0 else g;artist.evaluate("api.poke('skip')")
 for page in pages:page.wait_for_function('state.turn===9')
 g.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#ff0000',width:10,x1:100,y1:100,x2:900,y2:600,opacity:100,filled:false,seed:0,id:'final-drawing'}]})")
 answer=g.evaluate('state.answer');h.locator('#guess').fill(answer);began=time.monotonic();h.locator('#guess').press('Enter')
 for page in pages:
  page.wait_for_function("state.phase==='finished' && state.celebrating && state.winner?.name==='Zoe' && state.winner.score===20")
  assert page.evaluate('state.remainingMs>38500 && state.remainingMs<=40000 && state.lines.length===0'), 'Final canvas was not cleared before fireworks'
  expect(page.locator('#game-finale')).to_be_visible();expect(page.locator('.finale-winner')).to_have_text('Zoe');expect(page.locator('.finale-score')).to_have_text('with 20 points!')
  expect(page.locator('#messages .game-result strong')).to_have_text('That was the last round. The winner is Zoe with a score of 20 points!')
  assert page.locator('#messages .game-result').evaluate("el=>getComputedStyle(el).color==='rgb(255, 0, 0)' && Number(getComputedStyle(el).fontWeight)>=700")
  assert page.locator('#timer-dial').get_attribute('aria-valuetext')==''
  expect(page.locator('#start')).to_be_hidden();assert page.locator('#game-finale button,#game-finale a').count()==0
 assert h.evaluate("api.poke('start').then(()=>false,()=>true)"),'Host allowed restart during celebration'
 h.evaluate("()=>{window.finaleAnalyser=gameAudio.context.createAnalyser();gameAudio.master.connect(finaleAnalyser)}")
 h.wait_for_function("heard.filter(e=>e.cue==='Fireworks').length>=1",timeout=10000)
 h.wait_for_timeout(6000);assert h.evaluate("heard.filter(e=>e.cue==='Fireworks').length===1 && heard.find(e=>e.cue==='Fireworks').loop"), 'Fireworks track restarted instead of looping'
 h.wait_for_function("()=>{const a=new Float32Array(finaleAnalyser.fftSize);finaleAnalyser.getFloatTimeDomainData(a);return a.some(v=>Math.abs(v)>.001)}")
 assert h.locator('#game-finale>canvas').evaluate("c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let dark=0,light=0;for(let i=0;i<d.length;i+=4){if(d[i]+d[i+1]+d[i+2]===0)dark++;else light++;}return dark>light*10 && light>0}")
 h.screenshot(path=str(ROOT/'artifacts/game-finale.png'))
 # Shared settings affect synthesized fireworks; refreshing a winner cannot erase the result.
 h.locator('#settings-open').click();h.locator('#sound-muted').check();h.locator('#settings-close').click();n=h.evaluate("heard.filter(e=>e.cue==='Fireworks').length");h.wait_for_timeout(1500);assert h.evaluate("heard.filter(e=>e.cue==='Fireworks').length")==n
 h.locator('#settings-open').click();h.locator('#sound-muted').uncheck();h.locator('#settings-close').click()
 g.reload();expect(g.locator('#lobby')).to_be_visible();expect(g.locator('#room-recovery')).to_be_visible(timeout=30000);g.wait_for_timeout(1000);assert g.evaluate('state===null'), 'Restored tab ghost-rejoined';g.locator('#rejoin-room').click();expect(g.locator('#game')).to_be_visible(timeout=30000);g.wait_for_function("state.celebrating && state.winner.name==='Zoe' && state.winner.score===20")
 assert g.evaluate('state.remainingMs<38000'), 'Refresh restarted 40 seconds'
 g.wait_for_function("heard.some(e=>e.cue==='Fireworks')");assert g.evaluate("heard.filter(e=>e.cue==='Fireworks').every(e=>e.loop && e.offset>0)"), 'Refreshed fireworks did not resume at their offset'
 h.wait_for_function("state.phase==='drawing' && state.turn===0 && state.winner===null",timeout=42000);elapsed=time.monotonic()-began;assert 39.5<elapsed<43,elapsed
 for page in pages:expect(page.locator('#game-finale')).to_be_hidden()
 assert h.evaluate("state.started && state.lines.length===0 && state.players.every(p=>p.score===0)"),'Automatic next game did not reset scores/canvas'
 assert h.locator('#messages .game-result').count()==1
 expect(h.locator('#start')).to_be_hidden()
 # A started room waits/resumes automatically after a removal drops it below two players.
 h.locator('#players .player-name').filter(has_text='Zoe').click();h.locator('#remove-player').click();expect(g.locator('#lobby')).to_be_visible();h.wait_for_function("state.phase==='waiting' && state.started");expect(h.locator('#start')).to_be_hidden()
 g.evaluate("setSearchMode('invite')");g.locator('#host').fill(f'~zod/{rid}');g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000);h.wait_for_function("state.phase==='drawing' && state.started");expect(h.locator('#start')).to_be_hidden()
 for page in (g,h):page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/finale-verification.json').write_text(json.dumps({'nativeRounds':10,'winner':'Zoe','points':20,'durationSeconds':round(elapsed,3),'restartBlocked':True,'blankTimer':True,'boldRedFinalMessage':True,'rejoinPreservesWinnerAndDeadline':True,'fireworksPCM':True,'mute':True,'canvasClearedBeforeFinale':True,'automaticNewGame':True,'ownerRemoval':True,'explicitRejoinOnReload':True,'singleToolSelection':True,'suppliedFireworksLoop':True,'fireworksRejoinOffset':True,'scoreRankedRosterAndPencil':True},indent=2)+'\n')
 browser.close();print('PASS: ten native rounds, final scoring, 40-second finale, blank timer, fireworks PCM/mute, exact bold red result, explicit refresh rejoin, owner removal, single tool state, cleared canvas and automatic next game')
