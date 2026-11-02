"""Native three-ship immediate turns, private outcomes, focus and tab-close regression."""
import json,re,time,urllib.request,sys,runpy
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
manifest=json.loads((ROOT/'artifacts/media-manifest.json').read_text())
def dojo(port,command):
 request=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(request,timeout=60))
lenses={dojo(port,'our').strip():port for port in (12322,12323,12324)}
assert set(lenses)=={'~zod','~nec','~bud'},'Only isolated fake ships allowed'
with sync_playwright() as p:
 browser=p.chromium.launch();pages=[];errors=[]
 for ship,name,port in [('~zod','Alice',18080),('~nec','Zoe',18081),('~bud','Bob',18082)]:
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
 h,g,b=pages
 h.locator('#create-open').click();h.locator('#title').fill(f'Round QA {time.time_ns()}');h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
 rid=h.evaluate('roomId')
 for page in (g,b):
  page.evaluate("setSearchMode('invite')");page.locator('#host').fill(f'~zod/{rid}');page.locator('#host-search').click();expect(page.locator('#game')).to_be_visible(timeout=30000);expect(page.locator('#guess')).to_be_focused()
 h.wait_for_function('state.players.length===3');h.locator('#start').click()
 for page in pages:page.wait_for_function("state.phase==='drawing' && state.players[0].name==='Alice'")
 answer=h.evaluate('state.answer');token=h.evaluate('state.token')
 assert h.evaluate('state.duration===120 && state.remainingMs>117000 && !state.choices.length')
 expect(h.locator('#artist-banner')).to_be_visible();expect(h.locator('#banner-word')).to_have_text(answer)
 expect(h.locator('#messages')).to_contain_text("You're up next to draw! Your word is: "+answer)
 for page in (g,b):
  assert page.evaluate("state.answer==='' && !state.messages.some(m=>m.kind==='artist-word')")
  expect(page.locator('#artist-banner')).to_be_hidden()
 for page in pages:
  expect(page.locator('#messages')).to_contain_text('Alice drawing round 1');assert page.locator('#overlay,#choices').count()==0
 canvas=h.locator('#canvas').bounding_box();h.mouse.move(canvas['x']+40,canvas['y']+80);h.mouse.down();h.mouse.move(canvas['x']+100,canvas['y']+120,steps=5);h.mouse.up();expect(h.locator('#artist-banner')).to_be_hidden()
 g.locator('#guess').fill(answer);started=time.monotonic();g.locator('#guess').press('Enter')
 for page in pages:expect(page.locator('#messages')).to_contain_text('The word has been found! The round will end in 20 seconds!')
 expect(g.locator('#messages .found-word strong')).to_have_text(answer+'!');expect(g.locator('#messages .reward')).to_have_text("You found Alice's word and get 10 points!")
 for page in (h,b):assert page.locator('#messages .found-word,#messages .reward').count()==0
 assert h.evaluate('state.finishing && state.duration===20')
 g.wait_for_function("state.players[0].name==='Zoe' && state.phase==='drawing'",timeout=25000);elapsed=time.monotonic()-started;assert 19.5<elapsed<24,elapsed
 expected=f'Time has lapsed since the first correct guess. 1 players (Zoe) found Alice\'s word: "{answer}"'
 for page in pages:expect(page.locator('#messages .round-result')).to_have_text(expected)
 expect(h.locator('#guess')).to_be_focused();expect(g.locator('#artist-banner')).to_be_visible()
 assert g.evaluate('state.lines.length===0')
 ticks=b.evaluate("heard.filter(e=>e.cue==='TickingNoise').map(e=>e.when)");assert 76<=len(ticks)<=80,len(ticks);assert all(abs(y-x-.25)<1e-5 for x,y in zip(ticks,ticks[1:])),ticks
 answer=g.evaluate('state.answer')
 h.locator('#guess').fill(answer);h.locator('#guess').press('Enter');expect(h.locator('#messages .reward')).to_have_text("You found Zoe's word and get 10 points!")
 b.locator('#guess').fill(answer);started=time.monotonic();b.locator('#guess').press('Enter');b.wait_for_function("state.players[0].name==='Bob' && state.turn===2");assert time.monotonic()-started<3
 for page in pages:
  expect(page.locator('#messages .round-result').last).to_have_text(f'All 2 players found Zoe\'s word: "{answer}"');assert page.evaluate("state.phase==='drawing'")
 expect(b.locator('#messages .reward')).to_have_text("You found Zoe's word and get 9 points!");expect(b.locator('#messages .found-word strong')).to_have_text(answer+'!')
 expect(g.locator('#guess')).to_be_focused();expect(b.locator('#artist-banner')).to_be_visible()
 b.screenshot(path=str(ROOT/'artifacts/artist-banner.png'))
 # Closing a normal browser tab delivers leave; remaining ships see membership change.
 b.close(run_before_unload=True);h.wait_for_function("state.players.length===2 && !state.players.some(p=>p.ship==='~bud')",timeout=10000)
 for page in (g,h):page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/round-flow-verification.json').write_text(json.dumps({'ships':list(lenses),'immediateAssignedWords':True,'yellowBannerDismissesOnDrawing':True,'privateSolverAndArtistMessages':True,'partialSolveSeconds':round(elapsed,3),'tickCount':len(ticks),'allSolvedImmediate':True,'guessFocus':True,'tabCloseDisconnects':True},indent=2)+'\n')
 browser.close();print('PASS: three-ship immediate turns, private exact messages, 20-second partial finish, all-solved transition, banner/focus and tab-close leave')
