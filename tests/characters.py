"""Stable layered characters, ship persistence and an idle room browser."""
import json,re,runpy,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'));manifest=json.loads((ROOT/'artifacts/media-manifest.json').read_text())
def dojo(port,cmd):
 r=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':cmd},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(r,timeout=60))
assert dojo(12322,'our').strip()=='~zod'
with sync_playwright() as p:
 browser=p.chromium.launch();errors=[]
 def prepare(ship='~zod',http=18080,lens=12322):
  context=browser.new_context(viewport={'width':1920,'height':1080});origin=f'http://127.0.0.1:{http}';code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lens,'+code')).group();assert context.request.post(origin+'/~/login',form={'password':code}).ok
  body=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
  for path in ('connect','play'):context.route('**/apps/ursketch/'+path+'**',lambda r,request,body=body:r.fulfill(status=200,content_type='text/html',body=body))
  def media(route):
   name=next(k for k,v in manifest.items() if route.request.url.endswith(v['url']));route.fulfill(status=200,content_type=manifest[name]['mime'],body=(ROOT/'desk/media'/name).read_bytes())
  context.route('**/apps/ursketch/media/**',media)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script("window.roomQueries=[];const nativeFetch=fetch;window.fetch=(input,init)=>{if(init?.method==='PUT'){try{for(const a of JSON.parse(init.body)){if(a.action==='subscribe'&&a.path?.endsWith('/lobby'))roomQueries.push(a.path);}}catch{}}return nativeFetch(input,init);}")
  return context,page,origin
 context,page,origin=prepare();page.goto(origin+'/apps/ursketch/connect');page.evaluate('characterReady');expect(page.locator('#character-preview svg')).to_be_visible();expect(page.locator('#player-name')).to_have_value('~zod');assert not page.evaluate('connectionReady')
 assert page.locator('#character-preview image').evaluate_all("items=>items.map(e=>e.dataset.part).join(',')==='body,face,hat'")
 for part,target in [('body','calico'),('face','sad'),('hat','propellor-hat')]:
  for i in range(27):
   if page.evaluate('(part)=>characterBuilder.value[part]',part)==target:break
   page.locator(f'[data-character-part={part}][data-step="1"]').click()
 page.wait_for_timeout(200);page.screenshot(path=str(ROOT/'artifacts/character-connect-reference.png'))
 # Every supplied layer is browser-decodable and cycles back to the same stable ID.
 for part,count in [('body',6),('face',9),('hat',11)]:
  before=page.evaluate('(part)=>characterBuilder.value[part]',part)
  for i in range(count):
   page.locator(f'[data-character-part={part}][data-step="1"]').click()
   assert page.evaluate("()=>Promise.all([...document.querySelectorAll('#character-preview image')].map(i=>new Promise(resolve=>{const im=new Image();im.onload=()=>resolve(true);im.onerror=()=>resolve(false);im.src=i.href.baseVal;}))).then(v=>v.every(Boolean))")
  assert page.evaluate('(part)=>characterBuilder.value[part]',part)==before
 for part in ('body','face','hat'):page.locator(f'[data-character-part={part}][data-step="1"]').click()
 expected=page.evaluate('characterBuilder.value');page.reload();page.evaluate('characterReady');assert page.evaluate('characterBuilder.value')==expected
 for w,h in [(1280,720),(1024,600),(960,560),(390,844),(320,568)]:
  page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(60)
  assert page.evaluate('document.documentElement.scrollHeight<=innerHeight && document.documentElement.scrollWidth<=innerWidth')
  for sel in ['#connect-logo','#character-builder','.connect-copy','#player-name','#connect-submit']:
   b=page.locator(sel).bounding_box();assert b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w+1 and b['y']+b['height']<=h+1,(w,h,sel,b)
  assert page.locator('#connect-page').evaluate('e=>e.scrollHeight<=e.clientHeight+1'),(w,h)
 page.screenshot(path=str(ROOT/'artifacts/character-connect-mobile.png'));page.set_viewport_size({'width':1280,'height':720})
 page.locator('#player-name').fill('Cat Tester');page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play');page.wait_for_function('connectionReady');page.wait_for_timeout(1000)
 assert context.request.get(origin+'/apps/ursketch/character').json()==expected
 assert page.evaluate('roomQueries.length===0 && listedRooms.length===0 && [...knownHosts.values()].every(v=>v.id===null && v.pending===null)'),'Room discovery ran on arrival'
 expect(page.locator('#browse-status')).to_have_text('Search a ship to view its rooms.')
 # A different browser has no local draft; the ship restores exactly the saved IDs.
 fresh,other,other_origin=prepare();other.goto(other_origin+'/apps/ursketch/connect');other.evaluate('characterReady');assert other.evaluate('characterBuilder.value')==expected
 # Inserting a new menu entry never changes a saved choice by index.
 other.evaluate("()=>{CHARACTER_CATALOG.parts.body.unshift({...CHARACTER_CATALOG.parts.body[0],id:'new-body',label:'New body'});characterBuilder.restore(activeCharacter)}")
 assert other.evaluate('characterBuilder.value')==expected
 # Unknown future part IDs survive older clients without silently overwriting them.
 page.evaluate("api.poke('profile',{avatar:{body:'calico',face:'future-face',hat:'future-hat'}},{host:SELF,room:''})")
 newer,newpage,neworigin=prepare();newpage.goto(neworigin+'/apps/ursketch/connect');newpage.evaluate('characterReady');assert newpage.evaluate("characterBuilder.value.face==='future-face' && characterBuilder.value.hat==='future-hat'")
 expect(newpage.locator('#character-face-value')).to_have_text('Saved option (unavailable)')
 # Restore the selected character before cross-ship room propagation.
 page.evaluate('(avatar)=>api.poke("profile",{avatar},{host:SELF,room:""})',expected)
 page.locator('#host').fill('~zod');page.locator('#host-search').click();page.wait_for_function('roomQueries.length===1')
 guest,g,go=prepare('~nec',18081,12323);g.goto(go+'/apps/ursketch/connect');g.evaluate('characterReady');g.locator('#player-name').fill('Guest Cat');g.locator('#connect-submit').click();g.wait_for_url('**/apps/ursketch/play');g.wait_for_function('connectionReady')
 page.locator('#create-open').click();page.locator('#title').fill('Character QA');page.locator('#create-form button.primary').click();expect(page.locator('#game')).to_be_visible(timeout=30000);rid=page.evaluate('roomId')
 g.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=rid);expect(g.locator('#game')).to_be_visible(timeout=30000);g.wait_for_function("(avatar)=>state.players.some(p=>p.name==='Cat Tester' && JSON.stringify(p.avatar)===JSON.stringify(avatar))",arg=expected)
 for q in (g,page):q.locator('#leave').click();expect(q.locator('#lobby')).to_be_visible()
 assert not errors,errors
 (ROOT/'artifacts/character-verification.json').write_text(json.dumps({'bodyCount':6,'faceCount':9,'hatCount':10,'noHatOption':True,'allSVGsDecode':True,'stableIDs':True,'shipPersistenceAcrossBrowsers':True,'futureIDsPreserved':True,'noAutomaticRoomSearch':True,'peerAvatarPropagation':True,'laptopAndPhoneFit':True},indent=2)+'\n')
 browser.close();print('PASS: layered SVGs, all parts, stable/future IDs, ship persistence across browsers, no automatic room discovery, peer propagation and screen fit')
