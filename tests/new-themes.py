"""Seven new themes: persistence, distinct art, game colors and responsive tools."""
import base64,json,os,re,runpy,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
ORIGIN='http://127.0.0.1';themes=['aero','milady','terminal','dark-souls','kitty-cat','pikachu','garfield']
r=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(r,timeout=30))).group()
with sync_playwright() as p:
 browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':720});assert context.request.post(ORIGIN+'/~/login',form={'password':code}).ok
 current=context.request.get(ORIGIN+'/apps/ursketch/play').text();ship=re.search(r"window.URSKETCH_SHIP='([^']+)'",current).group(1)
 html=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship))
 for route in (() if os.environ.get('URSKETCH_INSTALLED')=='1' else ('play','connect')):context.route('**/apps/ursketch/'+route,lambda r:r.fulfill(status=200,content_type='text/html',body=html))
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));palettes=[]
 for theme in themes:
  page.goto(ORIGIN+'/apps/ursketch/play');page.wait_for_function('connectionReady')
  page.locator('#browser-settings').click();page.locator('#theme-select').select_option(theme);page.locator('#sound-volume').evaluate("e=>{e.value=25;e.dispatchEvent(new Event('input'))}");page.locator('#sound-muted').check();page.locator('#settings-close').click()
  page.reload();page.wait_for_function('connectionReady');assert page.evaluate('(theme)=>preferences.values.theme===theme && preferences.values.volume===25 && preferences.values.muted && document.body.classList.contains("extra-theme")',theme)
  assert page.locator('#room-list').evaluate('e=>{const probe=document.createElement("i");probe.style.background="var(--theme-sheet)";document.body.append(probe);const same=getComputedStyle(e).backgroundColor===getComputedStyle(probe).backgroundColor;probe.remove();return same;}')
  palettes.append(page.locator('body').evaluate('e=>getComputedStyle(e).getPropertyValue("--theme-bg")'))
  page.screenshot(path=str(ROOT/f'artifacts/theme-{theme}-lobby.png'))
  page.evaluate("""()=>{
   window.originalPoke=api.poke;window.testCommands=[];api.poke=async(action,data)=>{if(action==='draw')testCommands.push(...data.lines);};
   host=SELF;roomId='theme-preview';$('lobby').hidden=true;$('game').hidden=false;document.body.classList.add('playing');
   const make=(kind,color,x1,y1,x2,y2,filled=true)=>({kind,color,x1,y1,x2,y2,filled,width:8,opacity:100,seed:0,id:'theme-'+x1+'-'+y1+'-'+kind});
   window.seedLines=[make('rectangle','#8cbaee',70,70,930,620),make('rectangle','#02a005',70,510,930,620),make('ellipse','#f5f229',710,95,850,235),make('rectangle','#883e31',175,260,225,530),make('ellipse','#20712c',90,100,310,350),make('rectangle','#e0ba96',400,325,690,550),make('stroke','#f50c08',365,325,545,190),make('stroke','#f50c08',545,190,725,325),make('rectangle','#883e31',505,430,575,550),make('rectangle','#139cec',605,370,660,425)];
   window.fixture={kind:'room',title:'Drawing room',owner:SELF,phase:'drawing',turn:3,token:99,remainingMs:120000,seconds:120,duration:120,started:true,answer:'treehouse',choices:[],hint:'',hintCount:0,value:10,artistValue:10,celebrating:false,winner:null,finishing:false,lines:seedLines,players:Array.from({length:10},(_,i)=>({ship:i?'~theme-'+i:SELF,name:i?'Player '+(i+1):'You',score:13+i,solved:i===2,avatar:{body:CHARACTER_CATALOG.parts.body[i%6].id,face:CHARACTER_CATALOG.parts.face[i%9].id,hat:CHARACTER_CATALOG.parts.hat[i%11].id}})),messages:[{who:'',text:'You drawing round 4',kind:'round'},{who:'Player 2',text:'cabin',kind:'guess'},{who:'Player 3',text:'Great drawing!',kind:'chat'}]};renderRoom(fixture);
  }""")
  page.wait_for_timeout(80);baseline=page.locator('#canvas').evaluate('c=>c.toDataURL()')
  for switch in ['classic',theme]:
   page.locator('#theme-select').evaluate('(e,value)=>{e.value=value;e.dispatchEvent(new Event("change"));}',switch);page.wait_for_timeout(60)
   assert page.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline,'Theme switch changed drawing pixels'
  assert page.locator('#players .player-name').evaluate_all("els=>els.every((e,i)=>getComputedStyle(e).color===(i===0?'rgb(0, 128, 0)':'rgb(0, 0, 0)'))")
  assert page.locator('#players .cat-character').evaluate_all('els=>els.every(e=>Math.abs(e.getCTM().a-e.getCTM().d)<1e-6)')
  selected=page.locator('#messages').evaluate('e=>getComputedStyle(e).backgroundColor');inactive=page.locator('#chat-messages').evaluate('e=>getComputedStyle(e).backgroundColor');assert selected!=inactive,(theme,selected,inactive)
  if theme=='terminal':assert 'monospace' in page.locator('#messages .message').first.evaluate('e=>getComputedStyle(e).fontFamily')
  for w,h in [(1280,720),(1024,600),(390,844)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(80)
   assert page.evaluate('document.documentElement.scrollHeight<=innerHeight && document.documentElement.scrollWidth<=innerWidth'),theme
   c=page.locator('#canvas').bounding_box();box=page.locator('.canvas-wrap').bounding_box();assert all(abs(c[k]-box[k])<2 for k in ['x','y','width','height']),(theme,c,box)
   assert page.locator('#canvas').evaluate('c=>c.toDataURL()')==baseline,'Theme/resize changed drawing pixels'
   assert page.locator('#canvas').evaluate("c=>getComputedStyle(c).filter==='none' && getComputedStyle(c).backgroundColor==='rgb(255, 255, 255)'")
   if w==1280:page.screenshot(path=str(ROOT/f'artifacts/theme-{theme}-game.png'))
  page.set_viewport_size({'width':1280,'height':720});page.wait_for_timeout(60);box=page.locator('#canvas').bounding_box()
  for y in [box['y']+5,box['y']+box['height']-5]:
   page.mouse.move(box['x']+box['width']*.4,y);page.mouse.down();page.mouse.move(box['x']+box['width']*.6,y,steps=3);page.mouse.up()
  page.wait_for_function('testCommands.length>=8');assert page.evaluate('testCommands.some(c=>c.y1<15) && testCommands.some(c=>c.y2>685)')
  assert page.locator('#tool-grid [aria-pressed=true]').count()==1
  page.evaluate("()=>{state=null;roomId='';api.poke=originalPoke;localStorage.removeItem(recoveryKey);}")
  page.goto(ORIGIN+'/apps/ursketch/connect');page.evaluate('characterReady');assert page.evaluate('(theme)=>preferences.values.theme===theme',theme)
  for w,h in [(1280,720),(320,568)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(60);assert page.locator('#connect-page').evaluate('e=>e.scrollHeight<=e.clientHeight+1'),theme
  page.set_viewport_size({'width':1280,'height':720})
 assert len(set(palettes))==7
 assert not errors,errors
 # A standalone visual contact sheet of the actual game renders.
 gallery=browser.new_page(viewport={'width':1320,'height':1700})
 cards=''.join('<figure><figcaption>'+theme+'</figcaption><img src="data:image/png;base64,'+base64.b64encode((ROOT/f'artifacts/theme-{theme}-game.png').read_bytes()).decode()+'"></figure>' for theme in themes)
 gallery.set_content('<style>body{background:#20242b;color:white;display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:16px;font:18px Arial}figure{margin:0}figcaption{padding:8px}img{width:100%}</style>'+cards);gallery.screenshot(path=str(ROOT/'artifacts/theme-gallery.png'),full_page=True)
 (ROOT/'artifacts/new-themes-verification.json').write_text(json.dumps({'installed':os.environ.get('URSKETCH_INSTALLED')=='1','themes':themes,'savedSelectionAndAudioPrefs':True,'distinctPalettes':True,'canvasPixelsPreserved':True,'fullCanvasEdgeDrawing':True,'rosterColorsAndProportions':True,'chatSelection':True,'terminalMonospace':True,'laptopAndPhoneFit':True,'browserOnlyFixtures':True},indent=2)+'\n')
 browser.close();print('PASS: seven distinct saved themes, unchanged drawing pixels, full canvas edges, chat selection, roster colors/proportions, Terminal font and laptop/phone fit')
