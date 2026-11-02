"""Two native test ships: recover watches without rejoining, bounded settings and lobby traffic."""
import json,re,runpy,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'));manifest=json.loads((ROOT/'artifacts/media-manifest.json').read_text())
def dojo(port,command):
 r=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(r,timeout=60))
assert dojo(12322,'our').strip()=='~zod' and dojo(12323,'our').strip()=='~nec','Isolated fake ships only'
with sync_playwright() as p:
 browser=p.chromium.launch();pages=[];errors=[]
 for ship,port,lens in [('~zod',18080,12322),('~nec',18081,12323)]:
  context=browser.new_context(viewport={'width':1280,'height':720});origin=f'http://127.0.0.1:{port}';code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lens,'+code')).group();assert context.request.post(origin+'/~/login',form={'password':code}).ok
  html=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
  for route in ('play','connect'):context.route('**/apps/ursketch/'+route+'**',lambda r,request,html=html:r.fulfill(status=200,content_type='text/html',body=html))
  context.route('**/apps/ursketch',lambda r:r.fulfill(status=200,content_type='text/html',body=render['intro']))
  def media(r):
   name=next(name for name,a in manifest.items() if r.request.url.endswith(a['url']));r.fulfill(status=200,content_type=manifest[name]['mime'],body=(ROOT/'desk/media'/name).read_bytes())
  context.route('**/apps/ursketch/media/**',media)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(origin+'/apps/ursketch/play');page.wait_for_function('connectionReady');pages.append(page)
 h,g=pages
 # The same shared dialog fits intro, lobby, every theme and smaller screens.
 for theme in ['classic','blingee','terminal','m1a1-abrams','mountain-dew']:
  h.locator('#browser-settings').click();h.locator('#theme-select').select_option(theme)
  for w,ht in [(1280,720),(1024,600),(390,844),(320,568)]:
   h.set_viewport_size({'width':w,'height':ht});b=h.locator('#settings-dialog').bounding_box();assert abs(b['width']-w*.85)<2 and abs(b['height']-ht*.85)<2
   assert b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w and b['y']+b['height']<=ht
   if w>600:assert h.locator('.settings-sound').bounding_box()['x']<h.locator('.settings-appearance').bounding_box()['x']
  h.set_viewport_size({'width':1280,'height':720});h.locator('#settings-close').click()
 h.locator('#browser-settings').click();h.locator('#theme-select').select_option('classic');h.screenshot(path=str(ROOT/'artifacts/settings-wide.png'));h.locator('#settings-close').click()
 h.goto('http://127.0.0.1:18080/apps/ursketch');h.locator('#settings-open').click();assert abs(h.locator('#settings-dialog').bounding_box()['width']-1088)<2;h.locator('#settings-close').click();h.goto('http://127.0.0.1:18080/apps/ursketch/play');h.wait_for_function('connectionReady')
 h.locator('#create-open').click();h.locator('#title').fill('Stability QA '+str(time.time_ns()));h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible();rid=h.evaluate('roomId')
 g.evaluate("setSearchMode('invite')");g.locator('#host').fill('~zod/'+rid);g.locator('#host-search').click();expect(g.locator('#game')).to_be_visible();h.wait_for_function('state.players.length===2')
 h.locator('#start').click();g.wait_for_function("state.phase==='drawing'");h.wait_for_function("state.phase==='drawing'")
 g.evaluate("()=>{window.lobbyEvents=0;const id=knownHosts.get('~zod').id,receive=api.handlers.get(id);api.handlers.set(id,d=>{lobbyEvents++;return receive(d);});window.actions=[];window.realPoke=api.poke;api.poke=function(action,...args){actions.push(action);return realPoke.call(this,action,...args);};}")
 g.evaluate("api.poke('guess',{text:'zzzzzzzzzzzzzzzzzz'})");h.evaluate("api.poke('chat',{text:'zzzzzzzzzzzzzzzzzz'})");h.evaluate("api.poke('hint')");g.wait_for_function('state.hintCount===1');g.wait_for_timeout(500);assert g.evaluate('lobbyEvents')==0,'Chat/guess/hint broadcast unrelated lobby snapshots'
 h.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#000000',width:3,x1:0,y1:0,x2:1000,y2:700,opacity:100,filled:false,seed:0,id:'recovery-edge'}]})");g.wait_for_function('state.lines.length===1');before=g.locator('#canvas').evaluate('c=>c.toDataURL()')
 # Lose one watch; two resubscription failures must preserve the room and pixels.
 g.evaluate("()=>{window.realSubscribe=api.subscribe;window.failedWatches=0;api.subscribe=function(path,...args){if(path.startsWith('/stream/')&&failedWatches++<2)return Promise.reject(new Error('Simulated outage'));return realSubscribe.call(this,path,...args);};window.clockBeforeRecovery=clockAt;subscriptionLost(roomSub,new Error('Simulated quit'));}")
 expect(g.locator('#game')).to_be_visible();assert g.evaluate('clockAt===clockBeforeRecovery');assert g.locator('#canvas').evaluate('c=>c.toDataURL()')==before
 g.wait_for_function('!roomRecovering && roomSub!==null',timeout=20000);assert g.evaluate('failedWatches')==3;assert g.evaluate("!actions.includes('join')");assert g.locator('#canvas').evaluate('c=>c.toDataURL()')==before
 # A timeout beyond the local grace estimate must not decide host membership.
 g.evaluate("""async()=>{api.subscribe=realSubscribe;hostPresenceUntil=0;api.poke=function(action,...args){if(action==='heartbeat')return Promise.reject(new Error('Simulated slow heartbeat'));return realPoke.call(this,action,...args);};await maintainPresence();api.poke=function(action,...args){actions.push(action);return realPoke.call(this,action,...args);};}""")
 expect(g.locator('#game')).to_be_visible();g.wait_for_function('!roomRecovering',timeout=10000);assert g.evaluate('state.players.some(p=>p.ship===SELF)')
 # A transport reconnect re-requests current state without issuing join.
 g.evaluate("()=>{api.events.onopen();}");g.wait_for_function('!roomRecovering',timeout=10000)
 # Delete the actual Eyre channel: reopen transport and all watches, never join.
 g.evaluate("()=>{window.oldRoomSub=roomSub;window.oldChatSub=globalChatSub;window.originalEvents=api.events;void api.send({action:'delete'}).then(()=>{originalEvents.close();originalEvents.onerror();});}")
 g.wait_for_function('api.events!==originalEvents && connectionReady && roomSub!==oldRoomSub && !roomRecovering && globalChatSub!==oldChatSub && globalChatReady',timeout=30000)
 assert g.locator('#canvas').evaluate('c=>c.toDataURL()')==before
 assert g.evaluate("!actions.includes('join')")
 # Authoritative removal still works and cannot be undone by a queued retry.
 h.evaluate("api.poke('kick',{player:'~nec'})");expect(g.locator('#game')).to_be_hidden(timeout=10000);g.wait_for_timeout(2500);assert g.evaluate('state===null && roomId===\"\" && roomRecoveryTimer===null');h.wait_for_function('state.players.length===1');g.wait_for_function('(id)=>knownHosts.get("~zod").data.rooms.find(r=>r.id===id)?.count===1',arg=rid)
 h.locator('#leave').click();expect(h.locator('#game')).to_be_hidden();assert not errors,errors
 (ROOT/'artifacts/stability-verification.json').write_text(json.dumps({'nativeShips':2,'settings85Percent':True,'soundLeftAppearanceRight':True,'introSettingsShared':True,'phoneFit':True,'roomRetainedDuringWatchOutage':True,'twoFailedRetriesRecover':True,'canvasPixelsPreserved':True,'recoveryDoesNotJoin':True,'slowHeartbeatDoesNotEvict':True,'sseReconnectResnapshots':True,'deletedEyreChannelRecovers':True,'chatAndLobbyWatchesRestored':True,'ownerRemovalStillAuthoritative':True,'noLobbyBroadcastForChatGuessHint':True,'membershipStillUpdatesLobby':True},indent=2)+'\n');browser.close();print('PASS: two native ships; 85% settings; room/canvas recovery without join; slow-heartbeat tolerance; authoritative removal; reduced lobby fanout')
