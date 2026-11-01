"""Verify the live local comet without saving or displaying its login code."""
import json
import os
import re
import runpy
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

RELEASE = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/release.py'))
VERSION = RELEASE['VERSION']

request = urllib.request.Request('http://127.0.0.1:12321',
    data=json.dumps({'source': {'dojo': '+code'}, 'sink': {'stdout': None}}).encode(),
    headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(request, timeout=30) as response:
    output = json.load(response)
code = re.search(r'[a-z]{6}(?:-[a-z]{6}){3}', output).group()
artifacts = Path(__file__).resolve().parents[1] / 'artifacts'
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    login = context.request.post('http://127.0.0.1/~/login', form={'password': code})
    assert login.ok
    code = None
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    preview = os.environ.get('URSKETCH_PREVIEW') == '1'
    if preview:
        current = context.request.get('http://127.0.0.1/apps/ursketch/play').text()
        ship_name = re.search(r"window.URSKETCH_SHIP='([^']+)'", current).group(1)
        import sys
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0,str(root/'scripts'))
        render=runpy.run_path(str(root/'scripts/build.py'))
        html=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship_name))
        for path in ('play','connect'):
            page.route('**/apps/ursketch/'+path,lambda route:route.fulfill(status=200,content_type='text/html',body=html))
    page.set_viewport_size({'width':1280,'height':720})
    response = page.goto('http://127.0.0.1/apps/ursketch/connect')
    expect(page.locator('#connect-page')).to_be_visible()
    expect(page.locator('#lobby')).not_to_be_visible()
    expect(page.locator('#player-name')).to_have_value(page.evaluate('SELF'))
    assert not page.evaluate('connectionReady'), 'Connect page opened a channel before Connect'
    assert page.locator('#connect-page input').count()==1
    assert page.locator('input[type=password]').count()==0
    expect(page.locator('label[for=player-name]')).to_have_text('Name:')
    assert page.locator('#player-name').get_attribute('name')=='name'
    assert page.locator('#connect-submit').inner_text()=='Connect'
    assert page.locator('.connect-copy p').all_text_contents()==[
        "Welcome to urSketch, the net's premier sketching game!",
        'Enter your display name in the box to the right and click the Connect button to connect to the game.',
        'Your Urbit ID is your permanent name. You can choose to change your in-game display name, or leave your display name as your Urbit ID.']
    page.wait_for_function("Array.from(document.querySelectorAll('#connect-logo image')).every(i=>i.href.baseVal.includes('/media/'))")
    page.wait_for_timeout(350)
    copy=page.locator('.connect-copy').bounding_box();form=page.locator('#profile-form').bounding_box()
    assert abs(copy['x']-153)<3 and abs(copy['y']-229)<3,copy
    assert abs(form['x']-862)<3 and abs(form['y']-313)<4,form
    page.screenshot(path=str(artifacts/'connect-desktop.png'))
    for width,height in [(1024,600),(390,844),(320,568)]:
        page.set_viewport_size({'width':width,'height':height})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
        assert page.locator('#connect-page').evaluate('el=>el.scrollHeight<=el.clientHeight+1'), (width,height)
        for selector in ('.connect-copy','#player-name','#connect-submit'):
            box=page.locator(selector).bounding_box();assert box['y']>=0 and box['y']+box['height']<=height,(selector,box)
    page.screenshot(path=str(artifacts/'connect-mobile.png'))
    page.set_viewport_size({'width':1280,'height':720})
    # A failed connection must preserve the field and allow retry.
    page.evaluate("()=>{window.originalEnsure=api.ensure;api.ensure=async()=>{throw new Error('Connection test failure')}}")
    page.locator('#connect-submit').click();expect(page.locator('#connect-error')).to_have_text('Connection test failure')
    expect(page.locator('#connect-submit')).to_be_enabled()
    page.evaluate('()=>{api.ensure=window.originalEnsure}')
    # The full ship ID is valid, including a comet longer than the old 24-char limit.
    page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play')
    expect(page.locator('#profile-current')).to_have_text('Playing as '+page.evaluate('SELF'))
    page.locator('.player-summary a').click();page.wait_for_url('**/apps/ursketch/connect')
    expect(page.locator('#player-name')).to_have_value(page.evaluate('SELF'))
    page.locator('#player-name').fill('Sketch Player')
    page.locator('#connect-submit').click();page.wait_for_url('**/apps/ursketch/play')
    expect(page.locator('#profile-current')).to_have_text('Playing as Sketch Player')
    assert page.locator('#profile-form').is_hidden()
    page.set_viewport_size({'width':1440,'height':1000})
    assert response.status == 200
    favicon=page.locator('link[rel="icon"]').get_attribute('href')
    assert favicon == RELEASE['FAVICON_URL'], 'Browser tab logo is missing'
    expect(page.locator('#status')).to_contain_text('Connected as', timeout=30000)
    expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
    expect(page.locator('#host-search')).to_have_text('Search →')
    assert 'Draw a little closer.' not in page.locator('body').inner_text()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert page.locator('#tool-grid button').count() == 10
    assert page.locator('#pen').get_attribute('title') == 'Pen (P)'
    assert page.locator('#brush').get_attribute('title') == 'Brush (B)'
    assert page.locator('#host-form').count() == 1
    assert page.locator('#invite-form').count() == 0
    assert page.locator('#search-invite-mode').is_hidden()
    assert page.locator('#search-host-mode').is_hidden()
    assert page.locator('#app-version').inner_text()==VERSION
    expect(page.locator('.browser-version')).to_have_text('v '+VERSION)
    expect(page.locator('.browser-panel-label>span').first).to_have_text('Global Chat')
    assert page.locator('#browser-hosts').count()==0
    assert page.locator('#host-form').evaluate('el=>!!el.closest(".browser-room-controls")')
    assert page.locator('#global-chat-form #host').count()==0
    if not preview:expect(page.locator('#global-chat-input')).to_be_enabled(timeout=30000)
    page.set_viewport_size({'width':1280,'height':720})
    left=page.locator('.browser-left>.classic-scroll-shell').bounding_box();right=page.locator('#room-browser').bounding_box()
    assert abs(left['x']-30)<3 and abs(left['y']-126)<3 and abs(left['width']-859)<4,left
    assert abs(right['x']-904)<4 and abs(right['y']-5)<3,right
    assert page.locator('#browser-logo').bounding_box()['width']==180
    assert page.locator('#app-version').bounding_box()['y']>page.locator('#browser-logo').bounding_box()['y']+60
    assert page.evaluate('document.documentElement.scrollHeight<=innerHeight')
    assert page.locator('#browser-player-total').inner_text().startswith('Rooms (')
    page.locator('#browser-settings').click();expect(page.locator('#settings-dialog')).to_be_visible();page.locator('#theme-select').select_option('classic');page.locator('#settings-close').click()
    assert page.locator('#hide-full-rooms').evaluate('el=>getComputedStyle(el).borderRadius')=='50%'
    assert page.locator('.browser-version').evaluate('el=>getComputedStyle(el).color')=='rgb(0, 0, 0)'
    page.locator('#browser-settings').click();page.locator('#theme-select').select_option('classic');page.locator('#settings-close').click()
    page.locator('#browser-help').click();expect(page.locator('#help-dialog')).to_be_visible();page.locator('#close-help').click()
    host_draft = page.locator('#host').input_value()
    page.evaluate("setSearchMode(\'invite\')")
    expect(page.locator('#host')).to_have_attribute('placeholder','Paste your room invite code or link')
    page.locator('#host').fill('invalid invite')
    page.locator('#host-search').click()
    expect(page.locator('#toast')).to_contain_text('Paste a room invite link')
    page.evaluate("setSearchMode(\'host\')")
    expect(page.locator('#host')).to_have_value(host_draft)
    page.locator('#host').fill(page.evaluate('SELF'))
    page.locator('#host-search').click()
    expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
    expect(page.locator('#host')).to_have_value('')
    assert page.evaluate('SELF') not in page.locator('#browse-status').inner_text()
    page.evaluate("$('toast').hidden=true")
    page.screenshot(path=str(artifacts / 'comet-lobby.png'), full_page=True)
    # Use normal subscription callbacks for two simulated known hosts. This
    # checks distinct-ID aggregation, updates, filter independence and reuse.
    result=page.evaluate('''async()=>{
      window.savedSubscribe=api.subscribe;window.remoteFeeds={};window.actualKnownHost=knownHosts.get(SELF);knownHosts.delete(SELF);let next=900000;
      api.subscribe=(path,handler,initial,target)=>{
        if(!['~zod','~nec'].includes(target))return savedSubscribe.call(api,path,handler,initial,target);
        remoteFeeds[target]=handler;
        handler({kind:'lobby',rooms:[]});return Promise.resolve(++next);
      };
      await watchHost('~zod');await watchHost('~nec');
      const room=(id,count,ships)=>({id,title:id,phase:'waiting',count,players:ships.map(ship=>({ship,name:ship}))});
      remoteFeeds['~zod']({kind:'lobby',rooms:[room('shared',2,['~zod','~bud']),room('empty',0,[])]});
      remoteFeeds['~nec']({kind:'lobby',rooms:[room('other',2,['~bud','~wes'])]});
      await browse('~zod');
      return {total:$('browser-player-total').textContent,subscriptions:next};
    }''')
    assert result['total']=='Rooms (3 players)' and result['subscriptions']==900002,result
    page.evaluate("remoteFeeds['~nec']({kind:'lobby',rooms:[{id:'other',title:'Other',phase:'waiting',count:1,players:[{ship:'~bud',name:'Bud'}]}]})")
    expect(page.locator('#browser-player-total')).to_have_text('Rooms (2 players)')
    page.evaluate('''()=>{const players=Array.from({length:10},(_,i)=>({ship:'~fixture-'+i,name:'Player '+i}));remoteFeeds['~zod']({kind:'lobby',rooms:[{id:'full',title:'Full room',phase:'drawing',count:10,players},{id:'empty',title:'Empty room',phase:'waiting',count:0,players:[]},{id:'open',title:'Open room',phase:'choosing',count:1,players:[{ship:'~bud',name:'Bud'}]}]});}''')
    before=page.locator('#browser-player-total').inner_text()
    assert page.locator('#room-list article').count()==3
    page.locator('#hide-full-rooms').check();assert page.locator('#room-list article').count()==2
    page.locator('#hide-empty-rooms').check();assert page.locator('#room-list article').count()==1
    expect(page.locator('#room-list')).to_contain_text('Open room')
    assert page.locator('#browser-player-total').inner_text()==before
    page.locator('#hide-full-rooms').uncheck();page.locator('#hide-empty-rooms').uncheck()
    page.screenshot(path=str(artifacts/'room-browser-reference.png'))
    # The reference scroll rails must scroll real content by keyboard/arrows.
    page.evaluate('''()=>{remoteFeeds['~zod']({kind:'lobby',rooms:Array.from({length:50},(_,i)=>({id:'scroll-'+i,title:'Drawing room '+i,phase:'waiting',count:0,players:[]}))});}''')
    rail=page.locator('#room-browser .classic-scrollbar')
    rail.locator('.scroll-down').click();assert page.locator('#room-list').evaluate('el=>el.scrollTop')>0
    rail.locator('.scroll-thumb').focus();page.keyboard.press('End')
    assert page.locator('#room-list').evaluate('el=>el.scrollTop+el.clientHeight>=el.scrollHeight-1')
    # Remove simulated hosts without sending anything to remote ships.
    page.evaluate('''async()=>{api.subscribe=savedSubscribe;knownHosts.delete('~zod');knownHosts.delete('~nec');knownHosts.set(SELF,actualKnownHost);await browse(SELF);renderPlayerTotal();}''')
    for width,height in [(1280,720),(1024,600),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#host-form').scroll_into_view_if_needed()
        assert page.locator('#host-search').bounding_box()['width'] > 0
        assert page.evaluate('document.documentElement.scrollHeight<=innerHeight')
        page.screenshot(path=str(artifacts/('room-browser-mobile.png' if width==390 else 'room-browser-laptop.png')))
    page.set_viewport_size({'width':1440,'height':1000})
    page.evaluate("()=>{window.cachedLobbyProbe=true;window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}));}")
    page.wait_for_function('!window.cachedLobbyProbe && connectionReady')
    expect(page.locator('#host-search')).to_be_enabled(timeout=30000)
    page.locator('#create-open').click()
    page.locator('#title').fill('Installation check')
    page.locator('#create-form button.primary').click()
    expect(page.locator('#game')).to_be_visible(timeout=30000)
    page.wait_for_function("state && state.phase === 'waiting'")
    assert page.evaluate('roomStream'), 'The installed app did not use vector streaming'
    page.set_viewport_size({'width':1280,'height':720})
    page.wait_for_timeout(150)
    assert page.evaluate('document.documentElement.scrollHeight <= innerHeight')
    assert page.locator('#timer-dial').is_visible()
    assert page.locator('#chat-form').bounding_box()['y'] < 720
    expect(page.locator('#player-count')).to_have_text('1/10')
    if not preview:
        page.wait_for_function('knownHosts.get(SELF)?.data?.rooms.find(r=>r.id===roomId)?.players?.some(p=>p.ship===SELF)')
        roster=page.evaluate('knownHosts.get(SELF).data.rooms.find(r=>r.id===roomId).players')
        assert any(player['ship']==page.evaluate('SELF') for player in roster),roster
    page.locator('#players .player-name').first.click()
    expect(page.locator('#player-profile-name')).to_have_text('Sketch Player')
    expect(page.locator('#player-profile-ship')).to_have_text(page.evaluate('SELF'))
    page.locator('#player-profile-dialog form button').click()
    page.screenshot(path=str(artifacts / 'comet-room.png'), full_page=True)
    # Browser-only artist fixture: real pointer strokes must reach the panel's
    # former letterbox areas. Draw commands stay in this browser and never poke
    # the live room; the native waiting-room snapshot is restored afterwards.
    page.evaluate("""()=>{window.waitingSnapshot=structuredClone(state);window.savedPoke=api.poke;window.edgeCommands=[];api.poke=(action,data,...args)=>action==='draw'?(edgeCommands.push(...data.lines.map(l=>UrSketchWire.unpack(l))),Promise.resolve()):savedPoke.call(api,action,data,...args);renderRoom({...state,phase:'drawing',token:state.token+1000,answer:'edge test',duration:120,remainingMs:120000,players:[{...state.players[0],ship:SELF,solved:false},{ship:'~zod',name:'Canvas fixture',score:0,solved:false}],lines:[]});}""")
    for theme,width,height in [('classic',1280,720),('classic',1024,600),('blingee',1280,720),('classic',960,560)]:
        page.locator('#settings-open').click();page.locator('#theme-select').select_option(theme);page.locator('#settings-close').click()
        page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100)
        canvas=page.locator('#canvas').bounding_box();panel=page.locator('.canvas-wrap').bounding_box()
        assert all(abs(canvas[key]-panel[key])<2 for key in ('x','y','width','height')),(theme,canvas,panel)
        # Two strokes near opposite edges of the entire visible drawing panel.
        before=page.evaluate('edgeCommands.length')
        for y in (panel['y']+5,panel['y']+panel['height']-5):
            page.mouse.move(panel['x']+panel['width']*.4,y);page.mouse.down();page.mouse.move(panel['x']+panel['width']*.6,y,steps=3);page.mouse.up()
        page.wait_for_function('(before)=>edgeCommands.length>=before+8',arg=before)
        commands=page.evaluate('(before)=>edgeCommands.slice(before)',before)
        assert any(min(c['y1'],c['y2'])<15 for c in commands),commands
        assert any(max(c['y1'],c['y2'])>685 for c in commands),commands
        assert page.evaluate("""()=>{const x=canvas.getContext('2d'),d=x.getImageData(450,0,100,700).data;return [0,680].every(top=>{for(let y=top;y<top+20;y++)for(let a=0;a<100;a++){const i=(y*100+a)*4;if(d[i]<50&&d[i+1]<50&&d[i+2]<50)return true;}return false;});}"""),'Edge strokes did not paint the canvas'
        assert page.evaluate('document.documentElement.scrollHeight<=innerHeight')
    page.screenshot(path=str(artifacts/'canvas-full-panel.png'))
    page.evaluate("()=>{api.poke=savedPoke;renderRoom(waitingSnapshot);}")
    page.set_viewport_size({'width':1280,'height':720})
    ship = page.evaluate('SELF')
    page.locator('#leave').click()
    expect(page.locator('#lobby')).to_be_visible()
    tile = context.request.get('http://127.0.0.1/~/scry/docket/charges.json')
    assert tile.ok, f'Docket HTTP {tile.status}'
    charges = tile.json()
    assert 'urSketch' in json.dumps(charges), 'urSketch app tile is missing'
    assert '/apps/ursketch' in json.dumps(charges), 'urSketch tile route is missing'
    icon=runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/release.py'))['ICON_DATA_URL']
    assert icon in json.dumps(charges), 'urSketch logo is missing from the installed tile'
    ship = page.evaluate('SELF')
    treaty = page.evaluate("""() => new Promise(async (resolve, reject) => {
      const id=api.next;
      const timer=setTimeout(()=>reject(new Error('Publication subscription timed out')),20000);
      api.handlers.set(id,data=>{clearTimeout(timer);resolve(data);});
      await api.send({action:'subscribe',ship:SELF.slice(1),app:'treaty',path:`/treaty/${SELF}/ursketch`});
    })""")
    assert treaty['title'] == 'urSketch', 'urSketch publication is missing'
    assert treaty['image'] == icon, 'Published tile logo does not match the tile artwork'
    for label,src in [('Tile',icon),('Browser tab',favicon)]:
        assert page.evaluate("src=>new Promise(resolve=>{const image=new Image();image.onload=()=>resolve(image.naturalWidth>0);image.onerror=()=>resolve(false);image.src=src;})",src), label+' image did not decode'
    if not preview: assert treaty['version'] == VERSION
    assert treaty['href']['site'] == '/apps/ursketch'
    (artifacts / 'comet-publication.json').write_text(json.dumps(treaty, indent=2) + '\n')
    assert not errors, errors
    print(f'PASS on {ship}: Name screen wording, full-ship/custom profiles, profile inspection, full-panel edge drawing across themes/laptop sizes, reference room-browser layout, distinct known-host player counts, filters, hidden invite compatibility, search, tools, room lifecycle, room create/leave, Landscape tile, and Treaty publication')
    browser.close()
