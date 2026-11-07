"""Classic/Blingee laptop geometry, controls, privacy and default-host regression."""
import json,re,urllib.request,time,sys,traceback,os,runpy
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
preview=None
if os.environ.get('URSKETCH_PREVIEW')=='1':
 sys.path.insert(0,str(ROOT/'scripts'));preview=runpy.run_path(str(ROOT/'scripts/build.py'))['html']

sys.excepthook=lambda kind,error,tb:sys.stderr.write(''.join(line for line in traceback.format_exception(kind,error,tb) if 'cookie:' not in line.lower()))
def dojo(port,command):
 req=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=60))
lenses={dojo(port,'our').strip():port for port in [12322,12323]};assert set(lenses)=={'~zod','~nec'}
def fits(page):
 result=page.evaluate('''()=>{const c=document.querySelector('#canvas').getBoundingClientRect(),w=document.querySelector('.canvas-wrap').getBoundingClientRect();return {inside:c.left>=w.left-.5&&c.top>=w.top-.5&&c.right<=w.right+.5&&c.bottom<=w.bottom+.5,ratio:c.width/c.height,dimensions:[c.width,c.height],scroll:document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight}}''')
 assert result['inside'] and result['scroll'] and abs(result['ratio']-10/7)<.001,result
 assert result['dimensions'][0]>100 and result['dimensions'][1]>100,result
with sync_playwright() as p:
 browser=p.chromium.launch();contexts=[browser.new_context(viewport={'width':1280,'height':720}) for _ in range(2)];pages=[];errors=[]
 for context,ship,origin in zip(contexts,['~zod','~nec'],['http://127.0.0.1:18080','http://127.0.0.1:18081']):
  code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lenses[ship],'+code')).group();assert context.request.post(origin+'/~/login',form={'password':code}).ok
  if preview:
   body=preview.replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
   for path in ['play','connect']:context.route('**/apps/ursketch/'+path+'**',lambda route,request,body=body:route.fulfill(status=200,content_type='text/html',body=body))
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(origin+'/apps/ursketch/connect')
  # Old saved Default is migrated; Classic is also the fresh default.
  page.evaluate("localStorage.setItem('ursketch.settings.v1',JSON.stringify({theme:'default'}))");page.reload();assert page.evaluate("preferences.values.theme==='classic'")
  assert page.locator('#theme-select option[value=default]').count()==0
  page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
  assert page.evaluate("host===GLOBAL_CHAT_HOST && host==='~zod'")
  assert page.locator('#create-open').is_enabled(),'Creating on your ship was disabled while browsing the publisher'
  assert page.locator('link[rel=icon]').get_attribute('type')=='image/png';pages.append(page)
 h,g=pages
 h.locator('#create-open').click();assert h.locator('#create-dialog').evaluate("e=>getComputedStyle(e).borderRadius")=='0px'
 h.screenshot(path=str(ROOT/'artifacts/classic-create-room.png'));h.locator('#title').fill('Theme QA '+str(time.time_ns()));h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
 rid=h.evaluate('roomId');g.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=rid);expect(g.locator('#game')).to_be_visible(timeout=30000)
 assert h.locator('.game-logo').evaluate('e=>e.complete&&e.naturalWidth>0')
 h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3);expect(h.locator('#classic-round')).to_contain_text('Round 1 of 10')
 assert h.locator('#choices button').first.evaluate('e=>getComputedStyle(e).borderRadius')=='0px'
 h.screenshot(path=str(ROOT/'artifacts/classic-word-choice.png'));h.locator('#choices button').first.click();g.wait_for_function("state.phase==='drawing'")
 assert h.evaluate("drawing.color==='#000000'&&drawing.selected==='pen'")
 for theme in ['classic','blingee','classic']:
  h.locator('#settings-open').click();h.locator('#theme-select').select_option(theme);h.locator('#settings-close').click()
  for width,height in [(1280,720),(1366,768),(1024,600),(960,560)]:
   for page in pages:page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100);fits(page)
  assert h.evaluate('drawing.zoom===1')
  if theme=='blingee':h.screenshot(path=str(ROOT/'artifacts/blingee-game.png'))
 # All four corners are reachable and replay into the guest's identical board.
 h.set_viewport_size({'width':1280,'height':720});h.wait_for_timeout(100)
 h.evaluate("drawing.setWidth(8)");box=h.locator('#canvas').bounding_box()
 for x,y in [(20,20),(960,20),(20,660),(960,660)]:
  h.mouse.move(box['x']+x/1000*box['width'],box['y']+y/700*box['height']);h.mouse.down();h.mouse.move(box['x']+(x+20)/1000*box['width'],box['y']+(y+20)/700*box['height'],steps=2);h.mouse.up()
 h.evaluate('drawing.flushAll()');g.wait_for_function('state.lines.length>=12')
 assert g.evaluate("()=>{const c=document.querySelector('#canvas').getContext('2d');return [[25,25],[965,25],[25,665],[965,665]].every(([x,y])=>c.getImageData(x,y,1,1).data[0]<30)}")
 # Theme switching while zoomed must restore the complete board without losing strokes.
 h.locator('#zoom').click();h.locator('#canvas').click();assert h.evaluate('drawing.zoom')==2
 h.locator('#settings-open').click();h.locator('#theme-select').select_option('blingee');h.locator('#settings-close').click();h.wait_for_timeout(100);fits(h);assert h.evaluate('drawing.zoom')==1
 h.locator('#select-chat-chat').click();assert h.evaluate("selectedChat==='chat'")
 assert h.locator('#chat-messages').evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(255, 255, 220)'
 assert h.locator('#messages').evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(255, 255, 255)'
 h.locator('#select-game-chat').click();assert h.locator('#messages').evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(255, 255, 220)'
 # Chat message rows share one line height/margin regardless of red/black styling.
 h.evaluate("renderMessages('chat-messages',[{who:'A',text:'red',kind:'warning'},{who:'B',text:'black',kind:'chat'},{who:'C',text:'red',kind:'system'}])")
 assert h.locator('#chat-messages .message').evaluate_all("rows=>new Set(rows.map(e=>getComputedStyle(e).lineHeight+' '+getComputedStyle(e).marginTop+' '+getComputedStyle(e).marginBottom)).size") == 1
 h.evaluate("drawing.setColor('#f50c08');drawing.select('brush')");h.locator('#skip').click();g.wait_for_function("state.phase==='choosing' && state.players[0].ship==='~nec'",timeout=15000)
 g.locator('#choices button').first.click();g.wait_for_function("state.phase==='drawing'");g.locator('#skip').click();h.wait_for_function("state.phase==='choosing' && state.players[0].ship==='~zod'",timeout=15000)
 h.locator('#choices button').first.click();h.wait_for_function("state.phase==='drawing'");assert h.evaluate("drawing.color==='#000000'&&drawing.selected==='pen'")
 h.reload();expect(h.locator('#game')).to_be_visible(timeout=30000);assert h.evaluate("preferences.values.theme==='blingee'")
 # HTTP signal timeouts are translated without retrying potentially accepted mutations.
 result=h.evaluate("""async()=>{const original=window.fetch;window.fetch=async()=>{throw new DOMException('signal timed out','TimeoutError')};try{await api.send({action:'ack'});return ''}catch(e){return e.message}finally{window.fetch=original}}""")
 assert '30 seconds' in result and 'may still have arrived' in result
 assert 'Only the artist' in g.evaluate("api.poke('hint').then(()=>'',e=>e.message)")
 for page in [g,h]:page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 # Creating on your own ship while browsing the publisher also handles failure.
 g.locator('#create-open').click();g.locator('#title').fill('Guest-owned room')
 g.evaluate("()=>{window.originalPoke=api.poke;api.poke=(action,...args)=>action==='create'?Promise.reject(new Error('Simulated create failure')):originalPoke.call(api,action,...args)}")
 g.locator('#create-form button.primary').click();expect(g.locator('#create-error')).to_have_text('Simulated create failure');expect(g.locator('#create-error')).to_be_visible();assert g.evaluate("host==='~zod' && !roomId")
 g.evaluate('()=>{api.poke=originalPoke;}');g.locator('#create-form button.primary').click();expect(g.locator('#game')).to_be_visible(timeout=30000)
 assert g.evaluate("host==='~nec' && state.owner==='~nec'")
 g.locator('#leave').click();expect(g.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/themes-and-gameplay-verification.json').write_text(json.dumps({'defaultClassicAndMigration':True,'hiddenOldTheme':True,'publisherDefaultRooms':True,'createWhileBrowsingPublisher':True,'classicDialogs':True,'currentGameLogo':True,'tileFavicon':True,'themes':['classic','blingee'],'canvasAllCornersAndFullAspect':True,'themeSwitchResetsZoom':True,'chatSelectionAndUniformRows':True,'artistResetsPenAndBlack':True,'friendlyTimeoutAndRejection':True},indent=2)+'\n')
 browser.close();print('PASS: Classic migration, publisher rooms, classic dialogs, both themes, uncropped corner-to-corner drawing, chat selection/spacing, artist reset, logos and error explanations')
