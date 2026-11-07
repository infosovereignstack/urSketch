"""Two native ships: owner controls, grouped undo, hold, and durable rejoining."""
import json,re,time,urllib.request,runpy,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
from wordlists import read_bank

def dojo(port,command):
 r=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(r,timeout=30))
assert dojo(12322,'our').strip()=='~zod' and dojo(12323,'our').strip()=='~nec'
with sync_playwright() as p:
 browser=p.chromium.launch();pages=[];errors=[]
 for ship,name,port,lens in [('~zod','Alice',18080,12322),('~nec','Bob',18081,12323)]:
  context=browser.new_context(viewport={'width':1280,'height':720});origin=f'http://127.0.0.1:{port}'
  code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lens,'+code')).group();assert context.request.post(origin+'/~/login',form={'password':code}).ok
  body=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
  for path in ('play','connect'):context.route('**/apps/ursketch/'+path+'**',lambda route,request,body=body:route.fulfill(status=200,content_type='text/html',body=body))
  def media(route):
   asset=next(a for a in render['assets'].values() if route.request.url.endswith(a['url']));route.fulfill(status=200,content_type=asset['mime'],body=asset['data'])
  context.route('**/apps/ursketch/media/**',media)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(origin+'/apps/ursketch/connect');page.locator('#player-name').fill(name);page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');page.wait_for_function('connectionReady');pages.append(page)
 h,g=pages
 h.locator('#create-open').click();h.locator('#title').fill('Admin QA '+str(time.time_ns()));h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000);rid=h.evaluate('roomId')
 g.evaluate("setSearchMode('invite')");g.locator('#host').fill('~zod/'+rid);g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000);h.wait_for_function('state.players.length===2')
 expect(h.locator('#admin-open')).to_be_visible();expect(g.locator('#admin-open')).to_be_hidden()
 valid={'seconds':120,'difficulty':'default','enabled':['default'],'individual':[]}
 assert g.evaluate("data=>api.poke('admin',data).then(()=>false,()=>true)",valid),'Non-owner configured room'
 assert g.evaluate("api.poke('reset-timer').then(()=>false,()=>true)")
 h.locator('#start').click();h.wait_for_function("state.phase==='drawing'");g.wait_for_function("state.phase==='drawing'")
 h.locator('#admin-open').click();expect(h.locator('#admin-dialog')).to_be_visible();h.locator('#admin-length').select_option('150');h.locator('#admin-form button[type=submit]').click();h.wait_for_function('state.admin.seconds===150');h.locator('#admin-reset-timer').click();h.wait_for_function('state.remainingMs>149000');h.locator('#admin-close').click()
 for seconds in [0,601]:assert h.evaluate("data=>api.poke('admin',data).then(()=>false,()=>true)",{**valid,'seconds':seconds})
 assert g.evaluate("api.poke('undo').then(()=>false,()=>true)")
 # A gesture spans several transmitted segments and must undo atomically.
 c=h.locator('#canvas').bounding_box();h.mouse.move(c['x']+50,c['y']+60);h.mouse.down();h.mouse.move(c['x']+200,c['y']+150,steps=8);h.mouse.up();h.evaluate('drawing.flushAll()');h.wait_for_function('state.lines.length>=3');count=h.evaluate('state.lines.length');g.wait_for_function('(n)=>state.lines.length===n',arg=count)
 baseline=h.locator('#canvas').evaluate('c=>c.toDataURL()');assert g.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline
 h.locator('#fill').click();h.evaluate("drawing.setColor('#f50c08')");h.mouse.click(c['x']+c['width']-25,c['y']+25);h.wait_for_function("state.lines.at(-1).kind==='fill'");g.wait_for_function("state.lines.at(-1).kind==='fill'")
 h.locator('#undo').click();h.wait_for_function('(n)=>state.lines.length===n',arg=count);g.wait_for_function('(n)=>state.lines.length===n',arg=count)
 assert h.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline and g.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline
 h.locator('#clear').click();h.wait_for_function("state.lines.at(-1).kind==='clear'");h.locator('#undo').click();h.wait_for_function('(n)=>state.lines.length===n',arg=count);assert h.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline
 h.locator('#pen').click();h.keyboard.press('Control+z');h.wait_for_function('state.lines.length===0');g.wait_for_function('state.lines.length===0');assert h.locator('#tool-grid [aria-pressed=true]').count()==1
 # Configure future artists and upload a real Markdown bank.
 h.locator('#admin-open').click();h.locator('#admin-word-file').set_input_files({'name':'qa-easy.md','mimeType':'text/markdown','buffer':('# QA\n\n'+'\n'.join('- '+w for w in read_bank('easy')[:110])).encode()});h.wait_for_function('state.admin.custom.length===1');assert h.evaluate('state.admin.custom[0].count')==110
 h.locator('#admin-length').select_option('120');h.locator('#admin-difficulty').select_option('hard');h.locator('#admin-dialog summary').filter(has_text='Per-player difficulty').click();h.locator('#admin-players select[data-ship="~zod"]').select_option('easy');h.locator('#admin-form button[type=submit]').click();h.wait_for_function("state.admin.difficulty==='hard' && state.admin.individual[0].difficulty==='easy'");h.screenshot(path=str(ROOT/'artifacts/room-admin.png'));h.locator('#admin-close').click()
 # Final correct guess preserves the exact drawing for three seconds.
 h.mouse.move(c['x']+30,c['y']+30);h.mouse.down();h.mouse.move(c['x']+100,c['y']+70,steps=3);h.mouse.up();h.evaluate('drawing.flushAll()');h.wait_for_function('state.lines.length>1');baseline=h.locator('#canvas').evaluate('c=>c.toDataURL()');answer=h.evaluate('state.answer');g.locator('#guess').fill(answer);start=time.monotonic();g.locator('#guess').press('Enter');h.wait_for_function("state.phase==='reveal'");g.wait_for_function("state.phase==='reveal'")
 h.wait_for_timeout(2400);assert h.evaluate("state.phase==='reveal'");assert h.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline
 h.wait_for_function("state.phase==='drawing' && state.turn===1");elapsed=time.monotonic()-start;assert 2.9<elapsed<4.5,elapsed
 g.wait_for_function("state.phase==='drawing' && state.turn===1");assert g.evaluate('state.answer') in read_bank('hard');assert h.evaluate('document.activeElement.id')=='guess'
 scores=h.evaluate('Object.fromEntries(state.players.map(p=>[p.ship,p.score]))');assert scores=={'~nec':10,'~zod':10},scores
 # Leave, retain a no-expiry recovery record and reload without ghost-joining.
 title=h.evaluate('state.title');h.locator('#leave').click();expect(h.locator('#lobby')).to_be_visible();expect(h.locator('#room-recovery')).to_be_visible(timeout=30000)
 h.evaluate("()=>{savedRoom.expiresAt=Date.now()-86400000;localStorage.setItem(recoveryKey,JSON.stringify(savedRoom));}");h.reload();h.wait_for_function('connectionReady');expect(h.locator('#room-recovery')).to_be_visible();assert h.evaluate('state===null');g.wait_for_function("state.phase==='waiting' && state.turn===2",timeout=10000)
 h.wait_for_function('savedRoom.round===3');assert title in h.locator('#recovery-detail').inner_text();h.locator('#rejoin-room').click();expect(h.locator('#game')).to_be_visible(timeout=30000);h.wait_for_function("state.phase==='drawing' && state.turn===2");assert h.evaluate('state.players.find(p=>p.ship===SELF).score')==10;assert h.evaluate('state.players[0].ship')=='~zod';assert h.evaluate('state.answer') in read_bank('easy')
 # Owner transfer must also refresh permissions; returner's score is not zeroed.
 expect(h.locator('#admin-open')).to_be_hidden();expect(g.locator('#admin-open')).to_be_visible()
 # Only the most recently joined room may populate recovery.
 h.locator('#leave').click();expect(h.locator('#lobby')).to_be_visible();h.locator('#create-open').click();second='Most recent '+str(time.time_ns());h.locator('#title').fill(second);h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000);second_id=h.evaluate('roomId')
 g.locator('#leave').click();expect(g.locator('#lobby')).to_be_visible();g.evaluate("setSearchMode('invite')");g.locator('#host').fill('~zod/'+second_id);g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible(timeout=30000);h.wait_for_function('state.players.length===2')
 h.locator('#leave').click();expect(h.locator('#lobby')).to_be_visible();expect(h.locator('#room-recovery')).to_be_visible();h.wait_for_function('(id)=>savedRoom?.id===id',arg=second_id);assert second in h.locator('#recovery-detail').inner_text() and title not in h.locator('#recovery-detail').inner_text()
 g.locator('#leave').click();expect(g.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/room-admin-verification.json').write_text(json.dumps({'nativeShips':2,'ownerOnlyAdmin':True,'timerResetAndBounds':True,'markdownUpload':110,'globalAndArtistDifficulty':True,'wholeGestureUndo':True,'fillAndClearUndo':True,'peerCanvasIdentity':True,'artworkHoldSeconds':round(elapsed,3),'noExpiryReconnect':True,'restoredScore':10,'restoredDrawingSeat':True,'liveRecoveryRound':True,'noGhostRejoin':True,'ownerTransfer':True,'mostRecentRoomOnly':True},indent=2)+'\n')
 browser.close();print('PASS: native owner admin, timer/reset bounds, Markdown banks, artist difficulty, peer gesture/fill/clear undo, three-second artwork hold and durable score/seat rejoin')
