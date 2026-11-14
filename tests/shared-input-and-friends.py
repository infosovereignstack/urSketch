"""Shared composer routing and compact tagged Friends UI; never sends real messages."""
import json,os,re,runpy,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));build=runpy.run_path(str(ROOT/'scripts/build.py'))
installed=os.environ.get('URSKETCH_INSTALLED')=='1'
r=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(r,timeout=30))).group()
with sync_playwright() as p:
 b=p.chromium.launch();c=b.new_context(viewport={'width':1280,'height':720});assert c.request.post('http://127.0.0.1/~/login',form={'password':code}).ok;code=None
 current=c.request.get('http://127.0.0.1/apps/ursketch/play').text();ship=re.search(r"window.URSKETCH_SHIP='([^']+)'",current).group(1)
 if not installed:c.route('**/apps/ursketch/play',lambda route:route.fulfill(content_type='text/html',body=build['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship))))
 else:assert (ROOT/'web/social.js').read_text() in current
 def media(route):
  a=next(a for a in build['assets'].values() if route.request.url.endswith(a['url']));route.fulfill(content_type=a['mime'],body=a['data'])
 if not installed:c.route('**/apps/ursketch/media/**',media)
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1/apps/ursketch/play');page.wait_for_function("connectionReady && social.state.kind==='friends'")
 page.evaluate("""async()=>{await social.start();for(const [id,handler] of api.handlers)api.handlers.set(id,data=>data.kind==='friends'?undefined:handler(data));window.friendJoins=[];window.uiSocial=createSocial({self:SELF,perform:async()=>{},unsubscribe:async()=>{},profile:()=>({name:SELF,avatar:null}),inspect:inspectPlayer,notify:toast,join:async room=>friendJoins.push(room),subscribe:async receive=>{window.friendsReceive=receive;receive({kind:'friends',palsReady:true,peers:[{ship:'~zod',name:'W'.repeat(30),stage:'friend',tags:['urSketch','other'],avatar:{body:'orange',face:'excited',hat:'bow'},presence:{title:'A friend’s room',host:'~nec',room:'test-room',expires:Date.now()+120000}},{ship:'~bud',name:'External friend',stage:'friend',tags:['other']},{ship:'~nec',name:'Offline friend',stage:'friend',tags:['urSketch']},{ship:'~wes',name:'Expired room',stage:'friend',tags:['urSketch'],presence:{title:'Old room',host:'~wes',room:'old',expires:Date.now()-1000}}]});return 999999;}});await uiSocial.start();}""")
 page.locator('#browser-friends').click();expect(page.locator('#friends-ursketch')).to_have_attribute('aria-pressed','true');assert page.locator('.friend-row').count()==3
 expect(page.locator('.friend-row[data-ship="~bud"]')).to_have_count(0);assert page.locator('#friend-list svg').count()==0
 assert 'Not in-game' not in page.locator('#friends-dialog').inner_text();expect(page.locator('#incoming-section')).to_be_hidden()
 expect(page.locator('[data-join-peer="~zod"]')).to_be_visible();expect(page.locator('[data-join-peer="~nec"]')).to_be_hidden();expect(page.locator('[data-join-peer="~wes"]')).to_be_hidden()
 page.locator('#friends-all').click();assert page.locator('.friend-row').count()==4
 expect(page.locator('#ursketch-lounge')).to_have_attribute('href','https://invite.tlon.io/0vt7ss0.t4r7h.feu82.7jjj2.8g565');expect(page.locator('#ursketch-lounge')).to_have_attribute('target','_blank')
 assert page.locator('.friend-dm .external-arrow').first.evaluate('e=>getComputedStyle(e).color')=='rgb(0, 0, 0)'
 page.locator('#friends-dialog summary').click();expect(page.locator('.pals-open').first).to_have_text('Open Pals app');expect(page.locator('.pals-open').first).to_have_attribute('href','/pals');page.locator('#friends-dialog summary').click()
 checks=0
 for theme in page.locator('#theme-select option:not([disabled])').evaluate_all('es=>es.map(e=>e.value)'):
  page.locator('#theme-select').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("change"));}',theme)
  for w,h in [(1280,720),(800,600),(390,844),(320,568)]:
   page.set_viewport_size({'width':w,'height':h})
   assert page.locator('.friend-row[data-ship="~zod"] .friend-name').evaluate('e=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().width<=e.clientWidth-8;}'),(theme,w,'30-char name clipped',page.locator('.friend-row[data-ship="~zod"] .friend-name').evaluate('e=>({font:getComputedStyle(e).font,width:e.clientWidth,scroll:e.scrollWidth,grid:getComputedStyle(e.parentElement).gridTemplateColumns})'))
   assert page.locator('#friends-dialog').evaluate('e=>e.scrollWidth<=e.clientWidth'),(theme,w,'horizontal scrolling')
   checks+=1
 page.set_viewport_size({'width':1280,'height':720});page.locator('#theme-select').evaluate('e=>{e.value="classic";e.dispatchEvent(new Event("change"));}')
 page.screenshot(path=str(ROOT/'artifacts/compact-friends.png'))
 page.locator('.friend-row[data-ship="~zod"] .friend-name').click();expect(page.locator('#player-profile-avatar svg')).to_be_visible();assert page.locator('#player-profile-avatar [data-part=body]').get_attribute('data-part-id')=='orange';page.locator('#player-profile-dialog form button').click()
 page.locator('#browser-friends').click();page.locator('[data-join-peer="~zod"]').click();expect(page.locator('#friends-dialog')).not_to_be_visible();assert page.evaluate('friendJoins[0]')=={'host':'~nec','room':'test-room','title':'A friend’s room'}
 page.evaluate("""()=>{api.poke=async(action,data)=>{sent.push({action,...data});};window.sent=[];gameAudio?.stop();gameAudio=null;host=SELF;roomId='shared-input-fixture';$('lobby').hidden=true;$('game').hidden=false;document.body.classList.add('playing');window.view={kind:'room',title:'Shared composer',owner:SELF,phase:'drawing',turn:1,rounds:10,token:1,remainingMs:120000,seconds:120,duration:120,started:true,answer:'',choices:[],hint:'',hintCount:0,value:10,artistValue:10,celebrating:false,winner:null,finishing:false,lines:[],messages:[],players:[{ship:'~zod',name:'Artist',score:0,solved:false},{ship:SELF,name:'Me',score:0,solved:false}],admin:{seconds:120,difficulty:'default',enabled:['default'],individual:[],custom:[]}};renderRoom(view);selectChat('game',true);}""")
 expect(page.locator('#guess')).to_be_focused();assert page.locator('#chat-form,#chat-input').count()==0;box=page.locator('#guess').bounding_box()
 page.locator('#guess').fill('game draft');page.locator('#chat-messages').click();expect(page.locator('#guess')).to_be_focused();expect(page.locator('#guess')).to_have_value('');assert page.locator('#guess').bounding_box()==box
 assert page.locator('[data-chat=chat]').evaluate('e=>e.classList.contains("chat-selected")');page.locator('#guess').fill('chat only');page.locator('#guess').press('Enter');expect(page.locator('#guess')).to_have_value('');assert page.evaluate('sent.pop()')=={'action':'chat','text':'chat only'}
 page.keyboard.press('Tab');expect(page.locator('#guess')).to_have_value('game draft');page.locator('#guess').press('Enter');expect(page.locator('#guess')).to_have_value('');assert page.evaluate('sent.pop()')=={'action':'guess','text':'game draft'}
 page.evaluate('renderRoom({...view,players:[view.players[1],view.players[0]]})');expect(page.locator('#guess')).to_be_disabled();page.locator('#select-chat-chat').click();expect(page.locator('#guess')).to_be_enabled();page.locator('#guess').fill('artist chat');page.locator('#guess').press('Enter');expect(page.locator('#guess')).to_have_value('');assert page.evaluate('sent.pop().action')=='chat'
 assert page.locator('#guess').evaluate('e=>{const a=e.getBoundingClientRect(),b=document.getElementById("round-controls").getBoundingClientRect();return a.right<=b.left;}')
 page.screenshot(path=str(ROOT/'artifacts/shared-room-input.png'))
 page.evaluate('state=null;roomId="";localStorage.removeItem(recoveryKey)');assert not errors,errors
 result={'version':build['VERSION'],'installed':installed,'oneComposer':True,'separateDrafts':True,'selectedChannelRoutesSubmission':True,'artistCanChat':True,'tagsFilterDefaultsToUrSketch':True,'profileAvatarOnlyInProfile':True,'presenceJoinAndExpiry':True,'loungeInviteAndExternalArrows':True,'thirtyCharacterThemeViewportChecks':checks}
 (ROOT/'artifacts/shared-input-friends-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS:',result);b.close()
