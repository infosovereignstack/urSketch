"""Unified search and four distinct ships staying in one room."""
import getpass
import json
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

codes = json.loads(getpass.getpass('Fake ship codes JSON (zod/nec/bud/wes, hidden): '))
art = Path(__file__).resolve().parents[1] / 'artifacts'
ships = ['zod', 'nec', 'bud', 'wes']

with sync_playwright() as p:
    browser = p.chromium.launch()
    contexts = [browser.new_context(viewport={'width':1280,'height':720}) for _ in ships]
    pages = []
    errors = []
    for index, (ship, context) in enumerate(zip(ships, contexts)):
        origin = f'http://127.0.0.1:{18080+index}'
        assert context.request.post(origin+'/~/login',form={'password':codes[ship]}).ok
        page = context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(origin+'/apps/ursketch/play')
        expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
        pages.append(page)
    h = pages[0]
    # The landing page uses the original flowing layout.
    assert h.locator('#host-form').count()==1
    assert h.locator('#invite-form').count()==0
    title=f'Four ships {time.time_ns()}'
    h.locator('#create-open').click();h.locator('#title').fill(title);h.locator('#create-form button.primary').click()
    expect(h.locator('#game')).to_be_visible(timeout=30000)
    room=h.evaluate('roomId')
    for index,page in enumerate(pages[1:],start=2):
        page.locator('#host').fill('~zod');page.locator('#host-search').click()
        expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
        page.locator('.room-name', has_text=h.locator('#room-title').inner_text()).click()
        expect(page.locator('#game')).to_be_visible(timeout=30000)
        for active in pages[:index]:expect(active.locator('#player-count')).to_have_text(f'{index}/12',timeout=30000)
        print(f'{index} distinct ships joined; all prior players remain.',flush=True)
    # An abandoned lobby tab must never leave an active room in another tab.
    stale=contexts[-1].new_page()
    stale.goto('http://127.0.0.1:18083/apps/ursketch/play')
    expect(stale.locator('#host-search')).to_be_enabled(timeout=30000)
    expect(stale.locator('#room-recovery')).to_be_visible()
    stale.evaluate('saveRecovery({...savedRoom,expiresAt:Date.now()-1})')
    h.wait_for_timeout(3000)
    for page in pages:expect(page.locator('#player-count')).to_have_text('4/12',timeout=3000)
    stale.close()
    print('Expired recovery in an old lobby tab did not remove an active player.',flush=True)
    # A single delayed/missing heartbeat must not return a player to the lobby.
    pages[-1].evaluate("""()=>{const original=api.poke.bind(api);window.missedHeartbeat=false;api.poke=(action,...args)=>{if(action==='heartbeat'&&!window.missedHeartbeat){window.missedHeartbeat=true;return Promise.reject(new Error('Simulated delayed acknowledgement'));}return original(action,...args);};}""")
    h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3)
    h.locator('#choices button').first.click()
    for page in pages:page.wait_for_function("state.phase==='drawing'")
    assert all(page.evaluate('roomStream') for page in pages)
    h.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#883e31',width:4,x1:10,y1:20,x2:300,y2:400,opacity:100,filled:false,seed:0,id:'four-ships'}]})")
    for page in pages:page.wait_for_function('state.lines.length===1')
    pixels=[page.evaluate("async()=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',ctx.getImageData(0,0,1000,700).data))].join(',')") for page in pages]
    assert len(set(pixels))==1,'Four-ship drawing replay differs'
    expected={f'~{s}' for s in ships}
    print('Checking four-player membership across heartbeat/expiry windows and turn changes…',flush=True)
    for tick in range(int(os.environ.get("QA_HOLD_SECONDS","160"))//10):
        h.wait_for_timeout(10000)
        for page in pages:
            actual=page.evaluate("({players:state?.players.map(p=>p.ship),roomId,connectionReady,status:$('join-status').textContent})")
            assert actual['roomId']==room and set(actual['players'] or [])==expected,actual
        if tick%3==2:print(f'{(tick+1)*10}s: all four still present.',flush=True)
    assert pages[-1].evaluate('window.missedHeartbeat'), 'Heartbeat failure was not exercised'
    assert pages[-1].evaluate('!heartbeatWarning'), 'Heartbeat did not recover'
    h.screenshot(path=str(art/'four-players.png'))
    # Every ship can act without displacing another subscriber.
    for ship,page in zip(ships,pages):
        page.locator('#select-chat-chat').click();page.locator('#guess').fill(f'Hello from {ship}');page.locator('#guess').press('Enter')
        for recipient in pages:expect(recipient.locator('#chat-messages')).to_contain_text(f'Hello from {ship}',timeout=30000)
    for page in reversed(pages):
        page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible(timeout=30000)
    assert not errors,errors
    print('PASS: unified search and four-ship membership/chat/turns for 160 seconds.')
    browser.close()
