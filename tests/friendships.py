"""Native Pals installation/consent tests on isolated ~zod and ~nec only."""
import json, re, runpy, sys, time, urllib.request
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
    browser=p.chromium.launch(); pages=[]; errors=[]
    for ship,port,lens in [('~zod',18080,12322),('~nec',18081,12323)]:
        context=browser.new_context(viewport={'width':1280,'height':720})
        code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lens,'+code')).group()
        origin=f'http://127.0.0.1:{port}'; assert context.request.post(origin+'/~/login',form={'password':code}).ok; code=None
        html=build['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
        context.route('**/apps/ursketch/play**',lambda route,request,html=html:route.fulfill(status=200,content_type='text/html',body=html))
        def media(route):
            asset=next(a for a in build['assets'].values() if route.request.url.endswith(a['url']))
            route.fulfill(status=200,content_type=asset['mime'],body=asset['data'])
        context.route('**/apps/ursketch/media/**',media)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(origin+'/apps/ursketch/play');page.wait_for_function("connectionReady && social.state.kind==='friends'")
        pages.append(page)
    z,n=pages
    # Reset only this fake pair so the consent check is repeatable.
    for page,target in [(z,'~nec'),(n,'~zod')]:
        if page.evaluate('social.state.palsReady'):
            dojo(12322 if page is z else 12323,f'[%part {target} ~]',{'app':'pals'})
    for page,target in [(z,'~nec'),(n,'~zod')]:
        page.wait_for_function("ship=>!social.state.peers.some(p=>p.ship===ship && p.stage==='friend')",arg=target,timeout=15000)
    # The first click alone installs Pals; an offline recipient is not claimed sent.
    z.evaluate("social.inspect({ship:'~bud',name:'Offline test ship',avatar:null});$('request-friendship').click()")
    z.wait_for_function("social.state.palsReady===true && social.state.peers.some(p=>p.ship==='~bud')",timeout=180000)
    assert z.evaluate("social.state.peers.find(p=>p.ship==='~bud')?.stage")!='pending'
    print('PASS: request makes native Pals ready; offline target is not falsely marked sent',flush=True)
    # Remove Pals only on the fake recipient, to exercise notification before install.
    dojo(12322,'+hood/uninstall %pals',{'app':'hood'})
    deadline=time.monotonic()+30
    while '%.y' in dojo(12322,'.^(? %gu /~zod/pals/[(scot %da now)]/$)'):
        assert time.monotonic()<deadline,'Fake Pals desk was not uninstalled for recipient test'
        z.wait_for_timeout(1000)
    n.evaluate("social.inspect({ship:'~zod',name:'Friend Alpha',avatar:null});$('request-friendship').click()")
    z.wait_for_function("social.state.peers.some(p=>p.ship==='~nec' && p.incoming)",timeout=30000)
    n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod' && p.stage==='pending')",timeout=30000)
    assert '%.n' in dojo(12322,'.^(? %gu /~zod/pals/[(scot %da now)]/$)')
    expect(z.locator('#browser-friends .friend-dot')).to_be_visible()
    z.reload();z.wait_for_function("social.state.peers.some(p=>p.ship==='~nec' && p.incoming)")
    z.locator('#browser-friends').click();expect(z.locator('#friend-requests')).to_contain_text('Friend Beta')
    z.get_by_role('button',name='Deny Friendship',exact=True).click()
    n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod' && p.stage==='denied')")
    expect(z.locator('#browser-friends .friend-dot')).to_be_hidden()
    # A later request can be accepted, installing Pals and replaying the missed hey.
    n.evaluate("$('request-friendship').click()")
    z.wait_for_function("social.state.peers.some(p=>p.ship==='~nec' && p.incoming && p.stage!=='denied')")
    z.get_by_role('button',name='Become Friends',exact=True).click()
    z.wait_for_function("social.state.peers.some(p=>p.ship==='~nec' && p.stage==='friend')",timeout=180000)
    n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod' && p.stage==='friend')",timeout=30000)
    expect(z.locator('#friend-list')).to_contain_text('Friend Beta')
    expect(z.locator('#friend-list .friend-presence')).to_have_text('Not in-game')
    expect(z.locator('#friend-list .friend-dm')).to_have_attribute('href','/apps/groups/dm/~nec')
    expect(z.locator('#friend-list .friend-dm')).to_have_attribute('target','_blank')
    n.locator('#clean-slate-join').click();expect(n.locator('#game')).to_be_visible(timeout=30000)
    expect(z.locator('#friend-list .friend-presence')).to_have_text('A Clean Slate',timeout=15000)
    n.locator('#leave').click();expect(z.locator('#friend-list .friend-presence')).to_have_text('Not in-game',timeout=15000)
    assert not errors,errors
    z.screenshot(path=str(ROOT/'artifacts/friends-dialog.png'))
    (ROOT/'artifacts/friendship-verification.json').write_text(json.dumps({'nativePalsReadyAfterRequest':True,'offlineNotFalselyConfirmed':True,'notificationWithoutPals':True,'notificationSurvivesReload':True,'denyAndRequestAgain':True,'nativePalsReadyAfterAccept':True,'nativeMutualFriendship':True,'displayNamesAndRoomPresence':True,'groupsDmDeepLink':True},indent=2)+'\n')
    browser.close();print('PASS: persisted requests without Pals, consent, native mutual friendship, profile names, room presence and DM links')
