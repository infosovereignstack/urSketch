"""Integration test against two already-running, installed fake Urbit ships.

Use isolated fake ships on localhost; no real ship credentials are needed or written.
"""
import os
import json
import getpass
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ARTIFACTS = Path(__file__).resolve().parents[1] / 'artifacts'
ARTIFACTS.mkdir(exist_ok=True)
HOST = os.environ.get('URSKETCH_HOST_URL', 'http://127.0.0.1:18080')
GUEST = os.environ.get('URSKETCH_GUEST_URL', 'http://127.0.0.1:18081')
codes = json.loads(getpass.getpass('Fake ship codes JSON (hidden input): '))

with sync_playwright() as p:
    browser = p.chromium.launch()
    first = browser.new_context(viewport={'width': 1440, 'height': 1000})
    second = browser.new_context(viewport={'width': 1440, 'height': 1000})
    anonymous = first.request.get(HOST + '/apps/ursketch/play', max_redirects=0)
    assert anonymous.status == 303
    assert anonymous.headers['location'] == '/~/login?redirect=/apps/ursketch'
    for context, origin, code in ((first, HOST, codes['host']), (second, GUEST, codes['guest'])):
        response = context.request.post(origin + '/~/login', form={'password': code})
        assert response.ok, 'Fake ship login failed'
    host, guest = first.new_page(), second.new_page()
    errors = []
    for page in (host, guest):
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.add_init_script("""window.urSketchEvents=[]; const ES=window.EventSource;
          window.EventSource=class extends ES {constructor(...args){super(...args);
            this.addEventListener('message',e=>window.urSketchEvents.push(JSON.parse(e.data)));}};""")
    host.goto(HOST + '/apps/ursketch/connect')
    host.locator('#player-name').fill('Alice')
    host.locator('#profile-form button').click()
    expect(host.locator('#profile-current')).to_have_text('Playing as Alice')
    host.locator('#create-open').click()
    host.locator('#title').fill('The questionable artists club')
    host.locator('#create-form button.primary').click()
    expect(host.locator('#game')).to_be_visible(timeout=30000)
    room = host.evaluate('roomId')
    host_ship = host.evaluate('SELF')
    guest.goto(GUEST + '/apps/ursketch/connect')
    guest.locator('#player-name').fill('Bob')
    guest.locator('#profile-form button').click()
    expect(guest.locator('#profile-current')).to_have_text('Playing as Bob')
    guest.locator('#host').fill(host_ship)
    guest.locator('#host-search').click()
    expect(guest.locator('#host-search')).to_be_enabled(timeout=30000)
    guest.locator('.room-name', has_text=host.locator('#room-title').inner_text()).click()
    expect(guest.locator('#game')).to_be_visible(timeout=60000)
    try:
        guest.wait_for_function('state !== null', timeout=15000)
    except Exception:
        print('GUEST EVENTS', guest.evaluate('window.urSketchEvents.slice(-12)'))
        print('GUEST TOAST', guest.locator('#toast').inner_text())
        raise
    expect(host.locator('#player-count')).to_have_text('2/12', timeout=30000)
    assert guest.evaluate('state.players[0].name') == 'Alice'
    assert host.evaluate('state.players[1].name') == 'Bob'
    host.locator('#start').click()
    expect(host.locator('#choices button')).to_have_count(3, timeout=30000)
    guest.wait_for_function("state.phase === 'choosing'", timeout=30000)
    assert guest.evaluate('state.choices.length') == 0, 'Secret word choices leaked'
    answer = host.locator('#choices button').first.text_content()
    host.locator('#choices button').first.click()
    expect(host.locator('#overlay')).to_be_hidden(timeout=30000)
    expect(guest.locator('#overlay')).to_be_hidden(timeout=30000)
    assert guest.evaluate('state.answer') != answer, 'Answer leaked before reveal'
    assert guest.evaluate('state.answer') == '', 'Word-length hint leaked'
    # Remote guest cannot draw and cannot claim to be the host.
    rejected = guest.evaluate("""async () => {
        try { await api.poke('draw', {token:state.token, lines:[]}); return false; }
        catch { return true; }
    }""")
    assert rejected, 'Non-artist drawing accepted'
    host.get_by_role('button', name='Brown', exact=True).click()
    host.locator('#width').evaluate("e=>e.value=12")
    host.locator('#width').dispatch_event('input')
    assert host.locator('#width-value').inner_text() == '12'
    assert guest.locator('#tools').is_hidden()
    assert host.locator('#timer-dial').evaluate("e=>[...e.childNodes].filter(n=>n.nodeType===3).every(n=>!n.textContent.trim())")
    assert host.locator('#artist-secret').is_visible()
    assert guest.locator('#artist-secret').is_hidden()
    for width, height in ((1280,720),(1366,768),(1440,900),(1024,600)):
        for page in (host, guest):
            page.set_viewport_size({'width':width,'height':height})
            page.wait_for_timeout(150)
            assert page.evaluate('document.documentElement.scrollHeight <= innerHeight'), (width,height)
            for selector in ('#guess-form','#timer-dial','#canvas'):
                box=page.locator(selector).bounding_box()
                assert box['y']+box['height'] <= height, (selector,width,height,box)
        box=host.locator('#palette').bounding_box()
        assert box['y']+box['height'] <= height
    host.set_viewport_size({'width':1366,'height':768})
    guest.set_viewport_size({'width':1366,'height':768})
    host.locator('#select-chat-chat').click();host.locator('#guess').fill('Have fun everyone')
    host.locator('#guess').press('Enter')
    expect(guest.locator('#chat-messages')).to_contain_text('Have fun everyone')
    expect(guest.locator('#messages')).not_to_contain_text('Have fun everyone')
    canvas = host.locator('#canvas').bounding_box()
    host.mouse.move(canvas['x']+100, canvas['y']+100)
    host.mouse.down()
    host.mouse.move(canvas['x']+200, canvas['y']+180, steps=15)
    host.mouse.up()
    guest.wait_for_function('state.lines.length > 5', timeout=30000)
    assert guest.evaluate('state.lines[0].color') == '#883e31'
    assert guest.evaluate('state.lines[0].width') == 12
    host.screenshot(path=str(ARTIFACTS / 'drawing.png'), full_page=True)
    # Resubscribing gives a complete replay, including the drawing.
    guest.screenshot(path=str(ARTIFACTS / 'guesser-laptop.png'), full_page=True)
    count = guest.evaluate('state.lines.length')
    guest.reload()
    expect(guest.locator('#game')).to_be_visible(timeout=30000)
    guest.wait_for_function('(n) => state && state.lines.length >= n', arg=count)
    guest.locator('#guess').fill('definitely not the answer')
    guest.locator('#guess-form button').click()
    expect(host.locator('#messages')).to_contain_text('definitely not the answer')
    guest.locator('#guess').fill(answer.upper())
    guest.locator('#guess-form button').click()
    host.wait_for_function("state.phase === 'reveal'")
    guest.wait_for_function("state.phase === 'reveal'")
    assert host.evaluate('state.players[0].score') == 10
    assert host.evaluate('state.players[1].score') == 10
    assert all(m['text'] != answer.upper() for m in guest.evaluate('state.messages'))
    host.wait_for_function("state.phase === 'choosing' && state.players[0].ship !== SELF", timeout=15000)
    guest.wait_for_function('state.choices.length === 3')
    assert host.evaluate('state.choices.length') == 0
    guest.screenshot(path=str(ARTIFACTS / 'room.png'), full_page=True)
    # Choosing timeout must begin drawing without a browser timer action.
    guest.wait_for_function("state.phase === 'drawing'", timeout=20000)
    assert host.evaluate('state.lines.length') == 0
    expect(guest.locator('#tools')).to_be_visible()
    expect(host.locator('#tools')).to_be_hidden()
    await_reject = guest.evaluate("""async () => {
      try { await api.poke('draw',{token:state.token-1,lines:[]}); return false; }
      catch { return true; }
    }""")
    assert await_reject
    guest.locator('#skip').click()
    guest.wait_for_function("state.phase === 'reveal'")
    # Responsive lobby and game checks.
    host.set_viewport_size({'width':390,'height':844})
    assert host.evaluate('document.documentElement.scrollWidth <= innerWidth')
    host.screenshot(path=str(ARTIFACTS / 'mobile.png'), full_page=True)
    guest.locator('#leave').click()
    expect(guest.locator('#lobby')).to_be_visible()
    expect(host.locator('#player-count')).to_have_text('1/12')
    host.wait_for_function("state.phase === 'waiting'")
    host.locator('#leave').click()
    expect(host.locator('#lobby')).to_be_visible()
    expect(host.locator('#profile-current')).to_have_text('Playing as Alice')
    host.reload()
    expect(host.locator('#profile-current')).to_have_text('Playing as Alice')
    assert not errors, errors
    print('PASS: cross-ship names, private word before hints, laptop layout, dial, palette, chat, replay, scoring, timers, profiles, leave')
    browser.close()
