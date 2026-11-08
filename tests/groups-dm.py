"""Open real Groups composers from urSketch without sending any messages."""
import hashlib,json,os,re,runpy,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
build=runpy.run_path(str(ROOT/'scripts/build.py'))
req=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(req,timeout=30))).group()
with sync_playwright() as p:
    engine=os.environ.get('URSKETCH_DM_BROWSER','chromium');mobile=os.environ.get('URSKETCH_DM_MOBILE')=='1'
    browser=getattr(p,engine).launch();context=browser.new_context(**(p.devices['iPhone 13'] if mobile else {'viewport':{'width':1280,'height':720}}))
    assert context.request.post('http://127.0.0.1/~/login',form={'password':code}).ok;code=None
    current=context.request.get('http://127.0.0.1/apps/ursketch/play').text()
    ship=re.search(r"window.URSKETCH_SHIP='([^']+)'",current).group(1)
    html=build['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship))
    installed=os.environ.get('URSKETCH_INSTALLED')=='1'
    if installed:assert (ROOT/'web/social.js').read_text() in current,'Installed DM client differs from source'
    else:context.route('**/apps/ursketch/play',lambda route:route.fulfill(content_type='text/html',body=html))
    def media(route):
        a=next(a for a in build['assets'].values() if route.request.url.endswith(a['url']))
        route.fulfill(content_type=a['mime'],body=a['data'])
    if not installed:context.route('**/apps/ursketch/media/**',media)
    sent=[]
    def guard(route):
        if route.request.method=='PUT':
            for action in route.request.post_data_json or []:
                if action.get('action')=='poke' and action.get('app')=='chat' and action.get('mark','').startswith(('chat-dm-action','chat-club-action','chat-dm-rsvp')):
                    sent.append(action['mark']);route.abort();return
        route.continue_()
    context.route('**/~/channel/**',guard)
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1/apps/ursketch/play');page.wait_for_function("social.state.kind==='friends'")
    # Friends are a local UI fixture, not a change to the comet's Pals records.
    page.evaluate("""async()=>{
      await social.start();
      for(const [id,handler] of api.handlers)api.handlers.set(id,data=>data.kind==='friends'?undefined:handler(data));
      window.dmFixture=createSocial({self:SELF,perform:async()=>{},unsubscribe:async()=>{},profile:()=>({name:SELF,avatar:null}),inspect:()=>{},notify:toast,join:async()=>{},subscribe:async receive=>{receive({kind:'friends',peers:['~nec','~bud'].map(ship=>({ship,name:ship,stage:'friend',avatar:null}))});return 999999;}});
      await dmFixture.start();
    }""")
    page.locator('#browser-friends').click();results=[]
    for target in ['~nec','~bud','~nec']:
        button=page.locator(f'.friend-row[data-ship="{target}"] .friend-dm')
        with page.expect_popup() as opening:button.click()
        tab=opening.value
        for attempt in range(6):
            try:
                tab.locator('[data-testid="MessageInput"]').wait_for(state='visible',timeout=10000)
                break
            except Exception:
                print('DM opening diagnostic:',target,tab.url,page.locator('#toast').text_content(),tab.locator('input').evaluate_all("es=>es.map(e=>({placeholder:e.placeholder,value:e.value}))"),flush=True)
        else:raise AssertionError('Target DM composer did not open')
        expect(button).to_be_enabled(timeout=10000)
        assert tab.url.split('?')[0]=='http://127.0.0.1/apps/groups/dm/'+target
        expect(tab.locator('[data-testid="ScreenHeaderTitle"]').filter(has_text=target)).to_be_visible()
        expect(tab.locator('[data-testid="MessageInput"]')).to_have_value('')
        assert tab.evaluate('window.opener===null'),'Groups retains access to the game tab'
        results.append({'target':target,'composerReady':True,'emptyDraft':True})
        print('Opened empty composer for',target,flush=True)
        tab.close();page.bring_to_front()
    # Popup blocking must give feedback and leave the control usable.
    page.evaluate('window.originalOpen=window.open;window.open=()=>null')
    page.locator('.friend-row[data-ship="~nec"] .friend-dm').click()
    expect(page.locator('#toast')).to_contain_text('Allow pop-ups')
    expect(page.locator('.friend-row[data-ship="~nec"] .friend-dm')).to_be_enabled()
    page.evaluate('window.open=originalOpen')
    published=None
    if installed:
        published=page.evaluate("""()=>new Promise(async(resolve,reject)=>{
          const id=api.next,timer=setTimeout(()=>reject(new Error('Publication check timed out')),20000);
          api.handlers.set(id,data=>{clearTimeout(timer);resolve(data);});
          await api.send({action:'subscribe',ship:SELF.slice(1),app:'treaty',path:`/treaty/${SELF}/ursketch`});
        })""")
        assert published['title']=='urSketch' and published['version']==build['VERSION']
    assert not sent,sent
    assert not errors,errors
    (ROOT/f'artifacts/groups-dm-verification-{engine}{"-mobile" if mobile else ""}.json').write_text(json.dumps({'realInstalledGroups':True,'installedUrSketch':installed,'version':build['VERSION'],'publishedVersion':published['version'] if published else None,'clientSha256':hashlib.sha256((ROOT/'web/social.js').read_bytes()).hexdigest(),'browser':engine,'mobile':mobile,'newAndExistingRecipients':results,'messagePokes':0,'noOpenerAccess':True,'blockedPopupRecovery':True},indent=2)+'\n')
    browser.close();print('PASS: actual Groups composers for new/repeated/switched recipients, no messages sent, isolated opener and popup recovery')
