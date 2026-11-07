"""Mobile input/layout and DOM reuse; browser-only fixtures on an isolated ship."""
import json,re,runpy,sys,urllib.request,subprocess,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
ORIGIN=os.environ.get('URSKETCH_TEST_ORIGIN','http://127.0.0.1:18080');LENS=os.environ.get('URSKETCH_TEST_LENS','http://127.0.0.1:12322')
r=urllib.request.Request(LENS,data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'});code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(r,timeout=30))).group()
r=urllib.request.Request(LENS,data=json.dumps({'source':{'dojo':'our'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'});ship=json.load(urllib.request.urlopen(r,timeout=30)).strip()
old=subprocess.check_output(['git','show','ursketch-v0.25.1:web/app.js'],cwd=ROOT,text=True);old=old[old.index('function renderRoom(data) {'):old.index('function renderMessages(')]
fixture="""()=>{api.poke=async(action,data)=>{testPokes.push({action,data});};window.testPokes=[];host=SELF;roomId='mobile-fixture';$('lobby').hidden=true;$('game').hidden=false;document.body.classList.add('playing');window.fixture={kind:'room',title:'Mobile QA',owner:SELF,phase:'drawing',turn:2,token:51,remainingMs:120000,seconds:120,duration:120,started:true,answer:'treehouse',choices:[],hint:'',hintCount:0,value:10,artistValue:10,celebrating:false,winner:null,finishing:false,lines:[],messages:[{who:'',text:'Bob drawing round 3',kind:'round'}],players:Array.from({length:10},(_,i)=>({ship:i===1?SELF:i===0?'~nec':'~fixture-'+i,name:i===1?'You':'Player '+i,score:20-i,solved:false,avatar:{body:CHARACTER_CATALOG.parts.body[i%6].id,face:CHARACTER_CATALOG.parts.face[i%9].id,hat:CHARACTER_CATALOG.parts.hat[i%11].id}})),admin:{seconds:120,difficulty:'default',enabled:['default'],individual:[],custom:[]}};renderRoom(structuredClone(fixture));}"""
with sync_playwright() as p:
 browser=p.chromium.launch();errors=[];measurements={}
 for mobile in [False,True]:
  context=browser.new_context(**(p.devices['Pixel 7'] if mobile else {'viewport':{'width':1280,'height':720}}));assert context.request.post(ORIGIN+'/~/login',form={'password':code}).ok
  html=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],ship)
  if os.environ.get('URSKETCH_INSTALLED')!='1':context.route('**/apps/ursketch/play',lambda route:route.fulfill(status=200,content_type='text/html',body=html))
  def media(route):
   a=next(a for a in render['assets'].values() if route.request.url.endswith(a['url']));route.fulfill(status=200,content_type=a['mime'],body=a['data'])
  context.route('**/apps/ursketch/media/**',media);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(ORIGIN+'/apps/ursketch/play');page.wait_for_function('connectionReady');page.evaluate(fixture);page.wait_for_timeout(150)
  assert page.evaluate('document.body.dataset.mobile')==str(mobile).lower()
  if mobile:
   for w,h in [(393,851),(320,568),(844,390)]:
    page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(80)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
    expect(page.locator('.game-grid>.chat')).to_be_hidden();expect(page.locator('#guess-form button')).to_be_visible();expect(page.locator('#guess-form button')).to_have_text('Send')
    users=page.locator('.players').bounding_box();guesses=page.locator('.game-log').bounding_box();canvas=page.locator('#canvas').bounding_box();guess=page.locator('#guess-form').bounding_box()
    assert guesses['x']>=users['x']+users['width'] and canvas['y']>=users['y']+users['height'] and guess['y']>=canvas['y']+canvas['height']-1,(users,guesses,canvas,guess)
    assert canvas['height']>75
   page.set_viewport_size({'width':393,'height':851});page.locator('#guess').fill('house');page.locator('#guess-form button').click();assert page.evaluate("testPokes.some(p=>p.action==='guess'&&p.data.text==='house')")
   page.screenshot(path=str(ROOT/'artifacts/mobile-guesser.png'))
   page.evaluate("()=>{const r=structuredClone(fixture);r.players=[r.players[1],r.players[0],...r.players.slice(2)];r.token++;renderRoom(r);}");page.wait_for_timeout(100)
   c=page.locator('#canvas').bounding_box();box=page.locator('.canvas-wrap').bounding_box();assert c['height']>120 and all(abs(c[k]-box[k])<2 for k in ['x','y','width','height'])
   assert page.locator('#tool-grid').evaluate('e=>e.getBoundingClientRect().bottom<=document.querySelector("#canvas").getBoundingClientRect().top')
   icon=page.locator('#admin-open').bounding_box();guess=page.locator('#guess-form').bounding_box();assert icon['y']>=guess['y'] and icon['y']+icon['height']<=guess['y']+guess['height']
   page.screenshot(path=str(ROOT/'artifacts/mobile-artist.png'))
   page.locator('#settings-open').click();page.locator('#mobile-layout').select_option('desktop');page.locator('#settings-close').click();expect(page.locator('#guess-form button')).to_be_hidden();assert page.evaluate("preferences.values.layout==='desktop'")
  else:
   expect(page.locator('#guess-form button')).to_be_hidden();page.evaluate('(source)=>{window.oldRender=eval("("+source+")");}',old)
   for theme in ['classic','blingee','aero','spider-man']:
    page.locator('#theme-select').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("change"));}',theme)
    result=page.evaluate("""()=>{const loop=fn=>{const start=performance.now();for(let i=0;i<60;i++)fn(structuredClone(fixture));return performance.now()-start;};renderRoom(structuredClone(fixture));const before=$('players').firstElementChild;const optimized=loop(renderRoom);const reused=before===$('players').firstElementChild;const original=loop(oldRender);const replaced=before!==$('players').firstElementChild;return {optimizedMs:optimized,previousMs:original,rosterReused:reused,previousRebuilt:replaced};}""")
    assert result['rosterReused'] and result['previousRebuilt'];measurements[theme]=result
   page.locator('#settings-open').click();page.locator('#mobile-layout').select_option('mobile');page.locator('#settings-close').click();expect(page.locator('#guess-form button')).to_be_visible();assert page.evaluate("document.body.dataset.mobile==='true'")
  page.evaluate("()=>{state=null;roomId='';localStorage.removeItem(recoveryKey);}");context.close()
 assert not errors,errors
 (ROOT/'artifacts/mobile-performance-verification.json').write_text(json.dumps({'automaticMobileDetection':True,'mobileOnlySend':True,'manualLayoutChoice':True,'playersAndGuessesAboveCanvas':True,'noMobileChat':True,'phoneAndLandscapeFit':True,'fullCanvas':True,'adminIconOutsideCanvas':True,'installed':os.environ.get('URSKETCH_INSTALLED')=='1','metadataUpdates':60,'themeDOMReuse':measurements},indent=2)+'\n')
 browser.close();print('PASS: automatic/mobile-only Send, manual layout selection, phone/landscape canvas and themed DOM reuse',measurements)
