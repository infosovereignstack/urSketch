"""Read-only social UI smoke check on the installed comet; send no requests."""
import json,re,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
req=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(req,timeout=30))).group()
with sync_playwright() as p:
    browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':720})
    assert context.request.post('http://127.0.0.1/~/login',form={'password':code}).ok;code=None
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1/apps/ursketch/play');page.wait_for_function("connectionReady && social.state.kind==='friends'")
    assert page.evaluate('!roomId && listedRooms.length===0')
    before=page.evaluate('social.state.palsReady')
    assert page.locator('.browser-actions').evaluate("e=>[...e.children].map(c=>c.id)").index('browser-friends')<page.locator('.browser-actions').evaluate("e=>[...e.children].map(c=>c.id)").index('browser-help')
    page.locator('#browser-friends').click();expect(page.locator('#friends-dialog')).to_be_visible()
    expect(page.locator('#ursketch-lounge')).to_have_attribute('href','https://invite.tlon.io/0vt7ss0.t4r7h.feu82.7jjj2.8g565')
    page.locator('#friends-dialog summary').click()
    expect(page.locator('#friends-dialog .pals-explainer')).to_contain_text('Other Urbit applications use')
    link=page.locator('#friends-dialog a[href="/pals"]')
    if before:expect(link).to_be_visible()
    else:
        expect(link).to_be_hidden()
        expect(page.locator('#friends-dialog .pals-install-note')).to_be_visible()
    for width,height in [(1280,720),(390,844),(320,568)]:
        page.set_viewport_size({'width':width,'height':height})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
        box=page.locator('#friends-dialog').bounding_box();assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width and box['y']+box['height']<=height
    assert page.evaluate('social.state.palsReady')==before
    assert not errors,errors
    (ROOT/'artifacts/live-social-verification.json').write_text(json.dumps({'installedNativeSocialReady':True,'noAutomaticSearchOrJoin':True,'friendsBeforeInstructions':True,'loungeInvite':True,'palsExplainerAndLocalLink':True,'laptopAndPhoneDialogFit':True,'menuDoesNotInstallPals':True},indent=2)+'\n')
    browser.close();print('PASS: installed native Friends menu, manual shared-room entry, Pals explainer, phone/laptop fit and no unsolicited Pals installation')
