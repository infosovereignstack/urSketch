"""Local room recovery and a navigation band clear of the artist's palettes."""
import json,os,re,runpy,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
build=runpy.run_path(str(ROOT/'scripts/build.py'));preview=os.environ.get('URSKETCH_PREVIEW')=='1'
req=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(req,timeout=30))).group()
with sync_playwright() as p:
    browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':720})
    assert context.request.post('http://127.0.0.1/~/login',form={'password':code}).ok;code=None
    current=context.request.get('http://127.0.0.1/apps/ursketch/play').text();ship=re.search(r"window.URSKETCH_SHIP='([^']+)'",current).group(1)
    if preview:
        html=build['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship))
        context.route('**/apps/ursketch/play**',lambda route:route.fulfill(content_type='text/html',body=html))
    else:
        source=(ROOT/'web/app.js').read_text().replace('URSKETCH_PENCIL_URL',build['assets']['images/pencil.svg']['url']).replace('URSKETCH_GLOBAL_CHAT_HOST',json.dumps(build['chat_host'])).replace('URSKETCH_CUE_URLS',json.dumps(build['cue_urls']))
        assert source in current and (ROOT/'web/social.css').read_text() in current
    def media(route):
        a=next(a for a in build['assets'].values() if route.request.url.endswith(a['url']))
        route.fulfill(content_type=a['mime'],body=a['data'])
    if preview:context.route('**/apps/ursketch/media/**',media)
    context.add_init_script("localStorage.setItem("+json.dumps(f'ursketch.palettes.{ship}.classic')+",JSON.stringify({color:{x:.65,y:0},stroke:{x:.35,y:0},drawing:{x:.48,y:0}}))")
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1/apps/ursketch/play');page.wait_for_function("connectionReady && social.state.kind==='friends'")
    report={'version':build['VERSION'],'installed':not preview}
    if not preview:
        # Unavailable remote services cannot hold up an own-ship room.
        isolate="""()=>{const sub=api.subscribe.bind(api);api.subscribe=(path,...args)=>path==='/global-chat'||args[2]&&args[2]!==SELF?new Promise(()=>{}):sub(path,...args);globalChatSub=null;void connectGlobalChat();void social.reconnect();host='~zod';}"""
        page.evaluate(isolate)
        # Deliver create locally but lose its HTTP/SSE confirmation, as on an
        # interrupted connection. Retry after reload must reuse the same ID.
        page.evaluate("""()=>{window.realFetch=fetch;window.lostRoom=null;window.lostPoke=null;const receive=api.events.onmessage;
          api.events.onmessage=e=>{const d=JSON.parse(e.data);if(d.response==='poke'&&d.id===lostPoke){void api.send({action:'ack','event-id':Number(e.lastEventId)});return;}receive(e);};
          window.fetch=async(url,options)=>{const actions=options?.body&&typeof options.body==='string'?JSON.parse(options.body):[];const create=Array.isArray(actions)&&actions.find(a=>a.json?.action==='create');if(create&&!lostRoom){lostRoom=create.json.room;lostPoke=create.id;await realFetch(url,options);throw new DOMException('Lost local response','TimeoutError');}return realFetch(url,options);};}""")
        page.locator('#create-open').click();title='Local retry QA '+str(time.time_ns());page.locator('#title').fill(title);page.locator('#create-form button.primary').click()
        expect(page.locator('#create-error')).to_contain_text('local room request',timeout=30000)
        rid=page.evaluate('pendingCreation.id');assert rid==page.evaluate('lostRoom')
        page.reload();page.wait_for_function('connectionReady');assert page.evaluate('state===null && !roomId')
        page.evaluate(isolate);page.locator('#create-open').click();expect(page.locator('#title')).to_have_value(title)
        page.locator('#create-form button.primary').click();expect(page.locator('#game')).to_be_visible(timeout=30000)
        assert page.evaluate('[host,roomId]')==[ship,rid]
        assert page.evaluate('pendingCreation===null && state.players.length===1')
        page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
        # A real >30-second delay shows progress and then completes locally.
        page.evaluate("""()=>{window.baseFetch=fetch;window.releaseCreate=null;window.createTarget=null;window.fetch=async(url,options)=>{const actions=options?.body&&typeof options.body==='string'?JSON.parse(options.body):[];const create=Array.isArray(actions)&&actions.find(a=>a.json?.action==='create');if(create){createTarget=create.json.host;await new Promise(resolve=>releaseCreate=resolve);}return baseFetch(url,options);};}""")
        page.locator('#create-open').click();page.locator('#title').fill('Slow local QA '+str(time.time_ns()));page.locator('#create-form button.primary').click();page.wait_for_function('releaseCreate!==null')
        expect(page.locator('#create-status')).to_contain_text('taking longer than usual',timeout=35000)
        page.evaluate('releaseCreate()');expect(page.locator('#game')).to_be_visible(timeout=30000)
        assert page.evaluate('createTarget')==ship
        page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
        assert page.evaluate("api.poke('create',{title:'Blocked'},{host:'~zod',room:'blocked'}).then(()=>false,()=>true)")
        report.update({'lostReplyRetrySameRoom':True,'pendingRoomSurvivesReloadWithoutJoining':True,'remoteServicesNotRequired':True,'slowCreateBeyond30Seconds':True,'foreignCreateBlocked':True})
    # Fixture-only profile/room views; no messages or Pals requests are sent.
    page.evaluate("""async()=>{await social.start();for(const [id,receive] of api.handlers)api.handlers.set(id,d=>d.kind==='friends'?undefined:receive(d));window.palsFixture=createSocial({self:SELF,profile:()=>({name:SELF,avatar:null}),perform:async()=>{},unsubscribe:async()=>{},inspect:()=>{},notify:toast,join:async()=>{},subscribe:async cb=>{window.palsReceive=cb;cb({kind:'friends',palsReady:false,peers:[]});return 99999;}});await palsFixture.start();}""")
    page.locator('#browser-friends').click();page.locator('#friends-dialog summary').click()
    expect(page.locator('#friends-dialog .pals-open')).to_be_hidden();expect(page.locator('#friends-dialog .pals-install-note')).to_be_visible()
    page.evaluate("palsReceive({kind:'friends',palsReady:true,peers:[]})")
    expect(page.locator('#friends-dialog .pals-open')).to_be_visible();expect(page.locator('#friends-dialog .pals-open')).to_have_attribute('href','/pals');page.locator('#friends-close').click()
    page.evaluate("""()=>{api.poke=async()=>{};gameAudio?.stop();gameAudio=null;host=SELF;roomId='layout-fixture';$('lobby').hidden=true;$('game').hidden=false;document.body.classList.add('playing');window.fixture={kind:'room',title:'Header QA',owner:SELF,phase:'drawing',turn:1,rounds:10,token:1,remainingMs:120000,seconds:120,duration:120,started:true,answer:'lighthouse',choices:[],hint:'',hintCount:0,value:10,artistValue:10,celebrating:false,winner:null,finishing:false,lines:[],messages:[],players:[{ship:SELF,name:'Artist',score:0,solved:false},{ship:'~zod',name:'Guesser',score:0,solved:false}],admin:{seconds:120,difficulty:'default',enabled:['default'],individual:[],custom:[]}};}""")
    checks=0
    for theme in page.locator('#theme-select option:not([disabled])').evaluate_all('es=>es.map(e=>e.value)'):
        page.locator('#theme-select').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("change"));}',theme)
        for width,height,mobile in [(1440,900,False),(1280,720,False),(1024,600,False),(960,560,False),(800,600,False),(390,844,True),(320,568,True),(844,390,True)]:
            page.set_viewport_size({'width':width,'height':height});page.locator('#mobile-layout').evaluate('(e,m)=>{e.value=m?"mobile":"desktop";e.dispatchEvent(new Event("change"));}',mobile)
            for artist in [True,False]:
                page.evaluate("artist=>{const r=structuredClone(fixture);if(!artist)r.players.reverse();r.token=++fixture.token;renderRoom(r);requestAnimationFrame(fitCanvas);}",artist);page.wait_for_timeout(45)
                result=page.evaluate("""()=>{const visible=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';const rect=e=>e.getBoundingClientRect();const intersects=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1;const nav=[...document.querySelectorAll('.header-actions button')].filter(visible),panels=[...document.querySelectorAll('.palette-panel')].filter(visible);return{clear:nav.every(b=>panels.every(p=>!intersects(rect(b),rect(p)))),fit:nav.every(b=>{const r=rect(b);return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight}),scroll:document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight};}""")
                assert all(result.values()),(theme,width,height,artist,result);checks+=1
    page.set_viewport_size({'width':1280,'height':720});page.locator('#theme-select').evaluate('e=>{e.value="classic";e.dispatchEvent(new Event("change"));}');page.locator('#mobile-layout').evaluate('e=>{e.value="desktop";e.dispatchEvent(new Event("change"));}');page.evaluate('renderRoom({...fixture,token:++fixture.token})');page.wait_for_timeout(100)
    page.locator('#settings-open').click();expect(page.locator('#settings-dialog')).to_be_visible();page.locator('#settings-close').click()
    page.drag_and_drop('.color-panel .palette-grip','#friends-open')
    assert page.locator('.color-panel').bounding_box()['y']>=page.locator('#timer-dial').bounding_box()['y']+page.locator('#timer-dial').bounding_box()['height']+7
    page.screenshot(path=str(ROOT/'artifacts/header-navigation-safe.png'))
    report.update({'palsLocalRoute':'/pals','absentPalsShowsInstallGuidance':True,'headerRoleThemeViewportChecks':checks,'savedAndDraggedPalettesClearNavigation':True})
    page.evaluate("state=null;roomId='';localStorage.removeItem(recoveryKey)");assert not errors,errors
    (ROOT/'artifacts/local-room-header-verification.json').write_text(json.dumps(report,indent=2)+'\n');browser.close();print('PASS:',report)
