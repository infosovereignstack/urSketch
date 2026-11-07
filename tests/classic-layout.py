"""Compare Classic geometry with the user's drawer and guesser references."""
import getpass,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
codes=json.loads(getpass.getpass('Fake ship codes JSON (hidden input): '))
ART=Path(__file__).resolve().parents[1]/'artifacts'
def cog(page):
    h=page.locator('#help').bounding_box();s=page.locator('#settings-open').bounding_box()
    assert h and s and h['x']+h['width']<=s['x'],(h,s)
    assert s['x']+s['width']>=page.viewport_size['width']-40 and s['y']<25,s

def theme(page,value):
    page.locator('#browser-settings' if page.locator('#lobby').is_visible() else '#settings-open').click();page.locator('#theme-select').select_option(value);page.locator('#settings-close').click()

def rect(page,selector):return page.locator(selector).bounding_box()
with sync_playwright() as p:
    browser=p.chromium.launch();contexts=[browser.new_context(viewport={'width':960,'height':560}) for _ in range(2)]
    pages=[];errors=[]
    for context,origin,code,name in zip(contexts,['http://127.0.0.1:18080','http://127.0.0.1:18081'],[codes['host'],codes['guest']],['Badspot','Rotondo']):
        assert context.request.post(origin+'/~/login',form={'password':code}).ok
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(origin+'/apps/ursketch/connect')
        page.locator('#player-name').fill(name);page.locator('#profile-form button').click();expect(page.locator('#host-search')).to_be_enabled(timeout=30000);theme(page,'classic');pages.append(page)
    h,g=pages
    h.locator('#create-open').click();h.locator('#title').fill("Badspot's room");h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
    room=h.evaluate('roomId');g.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=room);expect(g.locator('#game')).to_be_visible(timeout=30000)
    h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3);h.locator('#choices button').first.click()
    for page in pages:page.wait_for_function("state.phase==='drawing'")
    h.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#000000',width:3,x1:160,y1:140,x2:650,y2:500,opacity:100,filled:false,seed:0,id:'classic-proof'}]})")
    for page in pages:page.wait_for_function('state.lines.length===1')
    # The supplied drawer image is 960×560: canvas begins at (468,66), chat at y388.
    canvas=rect(h,'.studio');chat=rect(h,'.chat .message-log');tools=rect(h,'.drawing-panel')
    assert abs(canvas['x']-468)<5 and abs(canvas['y']-66)<4,canvas
    assert abs(chat['y']-388)<8,chat
    assert abs(tools['x']-395)<5 and abs(tools['y']-40)<2,tools
    cog(h);h.evaluate("$('toast').hidden=true");h.screenshot(path=str(ART/'classic-drawer-reference.png'))
    # The supplied guesser image is 600×350: canvas begins at (304,54), chat at y241.
    g.set_viewport_size({'width':600,'height':350});g.wait_for_timeout(150)
    canvas=rect(g,'.studio');chat=rect(g,'.chat .message-log');guess=rect(g,'#guess')
    assert abs(canvas['x']-304)<6 and abs(canvas['y']-54)<4,canvas
    assert abs(chat['y']-241)<8,chat
    assert guess['width']>275 and guess['y']>200,guess
    cog(g);g.evaluate("$('toast').hidden=true");g.screenshot(path=str(ART/'classic-guesser-reference.png'))
    # The blue rail supports arrows, keys, and dragging; its old-style thumb is fixed-size.
    g.evaluate("renderMessages('messages',Array.from({length:100},(_,i)=>({who:'Player',text:'Scroll check '+i,kind:'guess'})))")
    g.wait_for_function("$('messages').scrollHeight>$('messages').clientHeight")
    g.locator('#messages').evaluate('el=>el.scrollTop=0')
    bar=g.locator('.game-log .classic-scrollbar');bar.locator('.scroll-down').click()
    assert g.locator('#messages').evaluate('el=>el.scrollTop')>0
    thumb=bar.locator('.scroll-thumb');assert abs(thumb.bounding_box()['height']-23)<1
    thumb.focus();g.keyboard.press('End')
    assert g.locator('#messages').evaluate('el=>Math.abs(el.scrollHeight-el.clientHeight-el.scrollTop)<2')
    g.wait_for_function("parseFloat(document.querySelector('.game-log .scroll-thumb').style.top)>40")
    t=thumb.bounding_box();track=bar.locator('.scroll-track').bounding_box()
    g.mouse.move(t['x']+t['width']/2,t['y']+t['height']/2);g.mouse.down();g.mouse.move(t['x']+t['width']/2,track['y']+4,steps=6);g.mouse.up()
    assert g.locator('#messages').evaluate('el=>el.scrollTop<100'),g.locator('#messages').evaluate('el=>({top:el.scrollTop,max:el.scrollHeight-el.clientHeight})')
    g.evaluate('renderRoom(state)')
    # Classic palette docking/rotation is independent of Default and persists on reload.
    grip=h.locator('.drawing-panel .palette-grip');grip.dblclick()
    assert 'classic-rotated' in h.locator('.drawing-panel').get_attribute('class')
    grip.dblclick();start=grip.bounding_box()
    h.mouse.move(start['x']+3,start['y']+4);h.mouse.down();h.mouse.move(220,240,steps=12);h.mouse.up()
    docked=h.locator('.drawing-panel').bounding_box()
    assert docked['x']<300 and docked['y']>150,docked
    h.reload();expect(h.locator('#game')).to_be_visible(timeout=30000);h.wait_for_timeout(150)
    restored=h.locator('.drawing-panel').bounding_box();assert abs(restored['x']-docked['x'])<3 and abs(restored['y']-docked['y'])<3,(docked,restored)
    # Theme switches retain forms, drafts, strokes, and control handlers.
    g.locator('#guess').fill('unsubmitted draft');theme(g,'default')
    expect(g.locator('.game-log #guess')).to_have_value('unsubmitted draft')
    theme(g,'classic');expect(g.locator('#classic-left-controls #guess')).to_have_value('unsubmitted draft')
    assert g.evaluate('state.lines.length')==1
    for page in pages:
        for width,height in [(1280,720),(1024,600),(960,560)]:
            page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100);cog(page)
            assert page.evaluate('document.documentElement.scrollHeight<=innerHeight && document.documentElement.scrollWidth<=innerWidth')
    h.locator('#zoom').click();h.locator('#canvas').click();assert h.evaluate('drawing.zoom')==2
    h.locator('#zoom').dblclick();assert h.evaluate('drawing.zoom')==1
    h.locator('#give-hint').click();g.wait_for_function('state.hintCount===1');expect(g.locator('#hint-display')).to_be_visible()
    theme(h,'default');expect(h.locator('.studio-toolbar #give-hint')).to_be_visible()
    # Header cog remains next to help on the Default landing page and mobile view.
    for width,height in [(1366,768),(390,844)]:
        h.set_viewport_size({'width':width,'height':height});h.wait_for_timeout(100);cog(h)
        assert h.evaluate('document.documentElement.scrollWidth<=innerWidth')
    for page in [g,h]:page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible();cog(page)
    assert not errors,errors
    print('PASS: drawer/guesser reference geometry, header cog placement, forms/drafts and ink across theme switches, Classic tool and hint interactions, and laptop fit.')
    browser.close()
