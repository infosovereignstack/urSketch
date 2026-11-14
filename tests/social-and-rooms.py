"""Native two-ship social, room, privacy and saved-profile integration checks."""
import json, os, re, runpy, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
build=runpy.run_path(str(ROOT/'scripts/build.py'))

def dojo(port,command,sink=None):
 request=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':command},'sink':sink or {'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(request,timeout=60))
assert dojo(12322,'our').strip()=='~zod' and dojo(12323,'our').strip()=='~nec'
with sync_playwright() as p:
 browser=p.chromium.launch();pages=[];errors=[]
 for ship,name,port,lens in [('~zod','Friend Alpha',18080,12322),('~nec','Friend Beta',18081,12323)]:
  context=browser.new_context(viewport={'width':1280,'height':720})
  code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lens,'+code')).group()
  origin=f'http://127.0.0.1:{port}';assert context.request.post(origin+'/~/login',form={'password':code}).ok;code=None
  html=build['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
  for path in ['play','connect']:context.route('**/apps/ursketch/'+path+'**',lambda route,request,html=html:route.fulfill(status=200,content_type='text/html',body=html))
  def media(route):
   asset=next(a for a in build['assets'].values() if route.request.url.endswith(a['url']))
   route.fulfill(status=200,content_type=asset['mime'],body=asset['data'])
  context.route('**/apps/ursketch/media/**',media)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("window.heard=[];window.addEventListener('ursketch:sound',e=>heard.push(e.detail))")
  page.goto(origin+'/apps/ursketch/connect');page.evaluate('characterReady');page.locator('#player-name').fill(name)
  page.locator('[data-character-part=hat][data-step="1"]').click();page.locator('[data-character-part=face][data-step="1"]').click()
  character=page.evaluate('characterBuilder.value')
  page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');page.wait_for_function('connectionReady && social.state.kind===\'friends\'')
  assert page.evaluate('listedRooms.length===0 && !roomId'),'The browser searched or joined automatically'
  page.goto(origin+'/apps/ursketch/connect');page.evaluate('characterReady')
  expect(page.locator('#player-name')).to_have_value(name);assert page.evaluate('characterBuilder.value')==character
  page.evaluate('localStorage.clear()');page.reload();page.evaluate('characterReady')
  expect(page.locator('#player-name')).to_have_value(name);assert page.evaluate('characterBuilder.value')==character
  page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');page.wait_for_function("social.state.kind==='friends'")
  pages.append(page)
 z,n=pages
 friend_join=os.environ.get('URSKETCH_FRIEND_JOIN')=='1'
 if friend_join:
  # An existing Pals friend can join the owner's live room from the compact menu.
  n.locator('#create-open').click();n.locator('#title').fill('Friends Join QA');n.locator('#create-form button.primary').click();expect(n.locator('#game')).to_be_visible(timeout=30000)
  z.locator('#browser-friends').click();expect(z.locator('[data-join-peer="~nec"]')).to_be_visible(timeout=20000);z.locator('[data-join-peer="~nec"]').click();expect(z.locator('#game')).to_be_visible(timeout=30000)
 else:
  n.locator('#clean-slate-join').click();expect(n.locator('#game')).to_be_visible(timeout=30000)
  z.locator('#clean-slate-join').click();expect(z.locator('#game')).to_be_visible(timeout=30000)
 assert z.evaluate('host')==n.evaluate('host')=='~nec'
 assert z.evaluate('roomId')==n.evaluate('roomId')
 n.wait_for_function('state.players.length===2')
 expect(n.locator('#player-count')).to_have_text('2/25');expect(n.locator('#start')).to_be_enabled()
 # Avatar and name are one keyboard-accessible player inspection target.
 z.locator('#players .player-avatar').first.click();expect(z.locator('#player-profile-dialog')).to_be_visible()
 expect(z.locator('#request-friendship')).to_be_visible();z.locator('#player-profile-dialog form button').click()
 # Header order and laptop/phone geometry.
 for page in pages:
  assert page.locator('.header-actions').evaluate("e=>[...e.children].map(x=>x.id)")==['friends-open','help','settings-open','timer-dial']
  assert page.evaluate('document.documentElement.scrollHeight<=innerHeight && document.documentElement.scrollWidth<=innerWidth')
 n.locator('#start').click();n.wait_for_function("state.phase==='drawing'");z.wait_for_function("state.phase==='drawing'")
 answer=n.evaluate('state.answer');assert answer
 # Bottom chat is usable, independent of scoring, and protects close/exact answers.
 z.locator('#chat-messages').click();expect(z.locator('#guess')).to_be_focused()
 z.locator('#guess').fill(answer);z.locator('#guess').press('Enter')
 expect(z.locator('#chat-messages')).to_contain_text('Enter guesses in the Game box')
 assert z.evaluate("state.phase==='drawing' && state.players.every(p=>p.score===0 && !p.solved)")
 assert n.evaluate("!roomTimeline.some(m=>m.kind==='chat-close')")
 assert not n.locator('#chat-messages').inner_text().find('Enter guesses in the Game box')>=0
 z.locator('#guess').fill('hello everyone');z.locator('#guess').press('Enter')
 expect(n.locator('#chat-messages')).to_contain_text('hello everyone')
 n_before=n.evaluate("heard.filter(e=>e.cue==='NewRound').length")
 close_before=z.evaluate("heard.filter(e=>e.cue==='CloseGuess').length")
 z.locator('#select-game-chat').click();z.locator('#guess').fill(answer);z.locator('#guess').press('Enter')
 n.wait_for_function("state.phase==='reveal'")
 assert z.evaluate("heard.filter(e=>e.cue==='CloseGuess').length")==close_before,'Correct Game guesses must not play the close-guess warning'
 n.wait_for_function('(n)=>heard.filter(e=>e.cue===\'NewRound\').length===n+1',arg=n_before)
 after=n.evaluate("heard.filter(e=>e.cue==='NewRound').length")
 n.wait_for_function("state.phase==='drawing' && state.turn===1")
 assert n.evaluate("heard.filter(e=>e.cue==='NewRound').length")==after
 # Selected name/character remain after the normal game navigation as well.
 for page in pages:
  page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 if not friend_join:
  z.wait_for_function('social.state.slate===null')
  # Two claims arriving together must resolve to the same host and room.
  z.evaluate("$('clean-slate-join').click()");n.evaluate("$('clean-slate-join').click()")
  for page in pages:expect(page.locator('#game')).to_be_visible(timeout=30000)
  assert z.evaluate('[host,roomId]')==n.evaluate('[host,roomId]')
  for page in pages:page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts'/('friend-room-join-verification.json' if friend_join else 'social-room-verification.json')).write_text(json.dumps({'savedNameAndCharacterLocalAndShip':True,'noAutomaticSearch':True,'firstJoinerHostsSharedRoom':not friend_join,'concurrentClaimsUseOneRoom':not friend_join,'joinFriendsLiveRoom':friend_join,'capacity':25,'wholePlayerRowInspection':True,'headerOrder':True,'chatInputWorks':True,'chatExactAnswerPrivateAndNoPoints':True,'normalChatSeparate':True,'newRoundCueAtDrawingEnd':True},indent=2)+'\n')
 browser.close();print('PASS: saved profiles, friend Join or shared room path, 25-player UI, private conversation answers and end-of-drawing audio')
