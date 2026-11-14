"""Exercise the reference tools and room recovery on two isolated fake ships."""
import getpass
import json
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

codes=json.loads(getpass.getpass('Fake ship codes JSON (hidden input): '))
HOST=os.environ.get('URSKETCH_HOST_URL','http://127.0.0.1:18080')
GUEST=os.environ.get('URSKETCH_GUEST_URL','http://127.0.0.1:18081')
ART=Path(__file__).resolve().parents[1]/'artifacts'
TITLE=f'Tools and recovery {time.time_ns()}'

def inject_delay(page):
    page.evaluate("""()=>{const original=window.fetch;window.fetch=async(url,options={})=>{
      let actions=[];try{actions=JSON.parse(options.body||'[]');}catch{}
      if(window.testDelay&&actions.some(a=>a.action==='subscribe'&&(a.path?.includes('/'+window.testDelay)||(window.testDelay==='room'&&a.path?.includes('/stream/'))))){window.testDelay='';await new Promise(r=>setTimeout(r,1200));}
      return original(url,options);
    };}""")

def drag(page,a,b):
    box=page.locator('#canvas').bounding_box()
    def position(p):return(box['x']+p[0]*box['width']/1000,box['y']+p[1]*box['height']/700)
    page.mouse.move(*position(a));page.mouse.down();page.mouse.move(*position(b),steps=6);page.mouse.up()
    page.evaluate('drawing.flushAll()')

def click_point(page,p,modifiers=None):
    box=page.locator('#canvas').bounding_box()
    options={'position':{'x':p[0]*box['width']/1000,'y':p[1]*box['height']/700}}
    if modifiers is not None:options['modifiers']=modifiers
    page.locator('#canvas').click(**options)
    page.evaluate('drawing.flushAll()')

def equal_board(a,b):
    a.evaluate('drawing.flushAll()')
    count=a.evaluate('state.lines.length')
    b.wait_for_function('(n)=>state.lines.length===n',arg=count)
    expression="""async()=>{const b=$('canvas').getContext('2d').getImageData(0,0,1000,700).data;const hash=await crypto.subtle.digest('SHA-256',b);return [...new Uint8Array(hash)].map(n=>n.toString(16).padStart(2,'0')).join('');}"""
    assert a.evaluate(expression)==b.evaluate(expression),'Drawing replay pixels differ'

with sync_playwright() as p:
    browser=p.chromium.launch()
    contexts=[browser.new_context(viewport={'width':1366,'height':768}) for _ in range(2)]
    for context,origin,code in zip(contexts,[HOST,GUEST],[codes['host'],codes['guest']]):
        assert context.request.post(origin+'/~/login',form={'password':code}).ok
    h,g=[context.new_page() for context in contexts]
    errors=[]
    for page in (h,g):page.on('pageerror',lambda e:errors.append(str(e)))
    h.goto(HOST+'/apps/ursketch/play');g.goto(GUEST+'/apps/ursketch/play')
    for page in (h,g):expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
    expect(g.locator('#host-search')).to_have_text('Search →')
    assert 'Draw a little closer.' not in h.locator('body').inner_text()
    inject_delay(g);g.evaluate("window.testDelay='lobby'")
    g.locator('#host').fill('~zod');g.locator('#host-search').click()
    expect(g.locator('#browse-status')).to_contain_text('Searching')
    expect(g.locator('#host-search')).to_be_disabled()
    expect(g.locator('#host-search')).to_be_enabled(timeout=30000)
    h.locator('#create-open').click();h.locator('#title').fill(TITLE);h.locator('#create-form button.primary').click()
    expect(h.locator('#game')).to_be_visible(timeout=30000)
    room=h.evaluate('roomId')
    expect(g.locator('#room-list')).to_contain_text(TITLE,timeout=30000)
    g.evaluate("window.testDelay='room'")
    g.locator('#room-list article').filter(has_text=TITLE).get_by_role('button').click()
    expect(g.locator('#join-status')).to_contain_text('Joining')
    expect(g.locator('#lobby')).to_be_visible()
    expect(g.locator('#game')).to_be_visible(timeout=30000)
    h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3)
    h.locator('#choices button').first.click();h.wait_for_function("state.phase==='drawing'")
    g.wait_for_function("state.phase==='drawing'")
    assert h.locator('#tool-grid button').count()==10
    assert h.locator('#pen').get_attribute('title')=='Pen (P)'
    assert h.locator('#brush').get_attribute('title')=='Brush (B)'
    assert h.evaluate("getComputedStyle($('timer-dial')).getPropertyValue('--timer-ink').trim()")=='#a7aaa4'
    h.evaluate('clockSeconds=21;clockAt=performance.now();updateDial()');assert 'urgent' not in h.locator('#timer-dial').get_attribute('class')
    h.evaluate('clockSeconds=20;clockAt=performance.now();updateDial()');assert 'urgent' in h.locator('#timer-dial').get_attribute('class')
    assert h.evaluate("getComputedStyle($('timer-dial')).getPropertyValue('--timer-ink').trim()")=='#df5650'
    h.evaluate('clockSeconds=state.seconds;clockAt=performance.now();updateDial()')
    h.locator('#pen').click()
    for key,width in [('1',1),('8',8),('9',16),('0',32),('ArrowLeft',31),('ArrowRight',32)]:
        h.keyboard.press(key);assert h.locator('#width').input_value()==str(width)
    h.keyboard.press('3')
    h.keyboard.press('d');assert h.evaluate('drawing.color')=='#ffffff'
    h.keyboard.press('d');assert h.evaluate('drawing.color')=='#000000'
    h.keyboard.press('ArrowUp');assert h.evaluate('drawing.color')=='#101010'
    h.keyboard.press('ArrowDown');assert h.evaluate('drawing.color')=='#000000'
    for key,tool in [('p','pen'),('b','brush'),('y','spray'),('e','eraser'),('l','line'),('z','zoom'),('s','rectangle'),('c','circle')]:
        h.keyboard.press(key);assert h.evaluate('drawing.selected')==tool
    h.locator('#rectangle').click()
    if h.locator('#rectangle svg').get_attribute('class')=='outline':h.keyboard.press('s')
    h.get_by_role('button',name='Black',exact=True).click()
    drag(h,(100,100),(300,300));assert h.evaluate('state.lines.at(-1).kind')=='rectangle';assert h.evaluate('state.lines.at(-1).filled')
    h.keyboard.press('s');drag(h,(350,100),(450,200));assert not h.evaluate('state.lines.at(-1).filled')
    h.keyboard.press('c');drag(h,(500,100),(600,200));assert h.evaluate('state.lines.at(-1).kind')=='ellipse'
    h.keyboard.press('c');drag(h,(650,100),(750,200));assert h.evaluate('state.lines.at(-1).filled')
    h.keyboard.press('l');drag(h,(100,400),(300,450));assert h.evaluate('state.lines.at(-1).kind')=='stroke'
    h.keyboard.press('p');drag(h,(100,500),(300,500))
    h.keyboard.press('b');drag(h,(350,500),(550,500));assert h.evaluate('state.lines.at(-1).kind')=='brush';assert h.evaluate('state.lines.at(-1).opacity')==25
    h.keyboard.press('y');drag(h,(650,500),(750,500));assert h.evaluate('state.lines.at(-1).kind')=='spray'
    h.keyboard.press('e');drag(h,(140,500),(180,500));assert h.evaluate('state.lines.at(-1).kind')=='eraser'
    h.locator('#fill').click();h.get_by_role('button',name='Blue',exact=True).click();click_point(h,(200,200))
    assert h.evaluate('state.lines.at(-1).kind')=='fill'
    assert h.evaluate("[...ctx.getImageData(200,200,1,1).data].slice(0,3)")==[11,2,241]
    equal_board(h,g)
    h.locator('#pen').click();h.get_by_role('button',name='Black',exact=True).click();click_point(h,(200,200),['Alt'])
    assert h.evaluate('drawing.color')=='#0b02f1'
    assert h.evaluate('drawing.selected')=='pen'
    before=h.evaluate('state.lines.length')
    h.keyboard.press('z');h.keyboard.press('+');assert h.evaluate('drawing.zoom')==2
    click_point(h,(500,350),['Shift']);assert h.evaluate('drawing.zoom')==1
    h.keyboard.press('+');h.locator('#zoom').dblclick();assert h.evaluate('drawing.zoom')==1
    h.keyboard.down('Space');h.keyboard.down('Alt');click_point(h,(500,350));h.keyboard.up('Alt');h.keyboard.up('Space');assert h.evaluate('drawing.zoom')==2
    h.keyboard.down('Space');h.keyboard.down('Meta');click_point(h,(500,350));h.keyboard.up('Meta');h.keyboard.up('Space');assert h.evaluate('drawing.zoom')==1
    assert h.evaluate('state.lines.length')==before
    g.locator('#guess').focus();g.keyboard.press('Tab');expect(g.locator('#guess')).to_be_focused();assert g.evaluate('selectedChat')=='chat';g.keyboard.press('Tab');expect(g.locator('#guess')).to_be_focused()
    h.locator('#color-preview').click();expect(h.locator('#advanced-palette')).to_be_visible();h.locator('#color-preview').click()
    grip=h.locator('.drawing-panel .palette-grip');grip.dblclick();assert 'rotated' in h.locator('.drawing-panel').get_attribute('class');grip.dblclick()
    selected=h.evaluate('drawing.selected');h.locator('#clear').click();h.evaluate('drawing.flushAll()');assert h.evaluate('drawing.selected')==selected
    assert h.evaluate("[...ctx.getImageData(200,200,1,1).data].slice(0,3)")==[255,255,255]
    h.get_by_role('button',name='Brown',exact=True).click();h.locator('#clear').click(modifiers=['Shift']);h.evaluate('drawing.flushAll()')
    assert h.evaluate("[...ctx.getImageData(200,200,1,1).data].slice(0,3)")==[136,62,49]
    equal_board(h,g)
    h.screenshot(path=str(ART/'tools-laptop.png'),full_page=True)
    # A refresh with a failed room subscription must preserve a usable recovery card.
    block={'once':True}
    def fail_room(route):
        try:actions=route.request.post_data_json or []
        except Exception:actions=[]
        if block['once'] and any(a.get('action')=='subscribe' and any(part in a.get('path','') for part in ['/room/','/stream/']) for a in actions):
            block['once']=False;route.fulfill(status=503,body='test subscription failure')
        else:route.continue_()
    g.route('**/~/channel/**',fail_room);g.reload()
    expect(g.locator('#join-status')).to_contain_text('Could not join:',timeout=30000)
    expect(g.locator('#room-recovery')).to_be_visible(timeout=30000)
    expect(g.locator('#rejoin-room')).to_be_enabled(timeout=30000)
    assert g.evaluate('roomId')==''
    g.unroute('**/~/channel/**',fail_room)
    g.screenshot(path=str(ART/'rejoin-lobby.png'),full_page=True)
    g.locator('#rejoin-room').click();expect(g.locator('#game')).to_be_visible(timeout=30000)
    assert g.evaluate('roomId')==room
    equal_board(h,g)
    # Server-side lease expiry: no client is allowed to send an explicit leave.
    g.locator('#leave').click();expect(g.locator('#lobby')).to_be_visible()
    h.locator('#leave').click();expect(h.locator('#lobby')).to_be_visible()
    h.locator('#create-open').click();h.locator('#title').fill('Expiry probe');h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible()
    h.goto(HOST+'/apps/ursketch/play');expect(h.locator('#room-recovery')).to_be_visible()
    expect(h.locator('#room-list')).to_contain_text('Expiry probe')
    h.evaluate('localStorage.removeItem(recoveryKey);savedRoom=null;renderRecovery()')
    print('Tools, progress, timer, replay, and refresh/rejoin passed. Waiting for host-side two-minute expiry…',flush=True)
    expect(h.locator('#room-list')).not_to_contain_text('Expiry probe',timeout=130000)
    assert not errors,errors
    print('PASS: all reference tools/shortcuts, replay pixels, progress, refresh recovery, and authoritative two-minute expiry')
    browser.close()
