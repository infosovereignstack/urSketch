"""Two-ship hints, zoom reset, themes, and browser audio settings."""
import getpass,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
codes=json.loads(getpass.getpass('Fake ship codes JSON (hidden input): '))
ART=Path(__file__).resolve().parents[1]/'artifacts'
with sync_playwright() as p:
    browser=p.chromium.launch()
    contexts=[browser.new_context(viewport={'width':1366,'height':768}) for _ in range(2)]
    pages=[];errors=[]
    for context,origin,code in zip(contexts,['http://127.0.0.1:18080','http://127.0.0.1:18081'],[codes['host'],codes['guest']]):
        assert context.request.post(origin+'/~/login',form={'password':code}).ok
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(origin+'/apps/ursketch/play');expect(page.locator('#host-search')).to_be_enabled(timeout=30000);pages.append(page)
    h,g=pages
    h.locator('#create-open').click();h.locator('#title').fill(f'Hints {time.time_ns()}');h.locator('#create-form button.primary').click();expect(h.locator('#game')).to_be_visible(timeout=30000)
    room=h.evaluate('roomId');g.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=room);expect(g.locator('#game')).to_be_visible(timeout=30000)
    h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3);h.locator('#choices button').first.click()
    for page in pages:page.wait_for_function("state.phase==='drawing'")
    answer=h.evaluate('state.answer')
    assert g.evaluate("state.hint==='' && state.answer==='' && state.hintCount===0")
    assert g.evaluate("api.poke('hint').then(()=>false,()=>true)"),'Guesser was allowed to give hints'
    expect(h.locator('#zoom')).to_have_attribute('title','Zoom (Z, +/-)')
    h.locator('#zoom').click();h.locator('#canvas').click();assert h.evaluate('drawing.zoom')==2
    h.locator('#zoom').dblclick();assert h.evaluate('drawing.zoom')==1
    assert h.locator('#canvas').evaluate("el=>el.style.transform")=='translate(0px, 0px) scale(1)'
    h.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#883e31',width:4,x1:100,y1:120,x2:600,y2:500,opacity:100,filled:false,seed:0,id:'hint-stroke'}]})")
    g.wait_for_function('state.lines.length===1')
    previous=''
    for count in [1,2,3]:
        h.locator('#give-hint').click();g.wait_for_function('(n)=>state.hintCount===n',arg=count)
        mask=g.evaluate('state.hint')
        assert len(mask.replace(' ',''))==len(answer.replace(' ',''))
        assert sum(c not in '_ ' for c in mask)==max(0,count-1),(answer,mask)
        for i,c in enumerate(mask):assert c=='_' or c==answer[i]
        for i,c in enumerate(previous):assert c=='_' or c==mask[i]
        assert g.evaluate("state.answer==='' && state.choices.length===0")
        assert h.evaluate('state.artistValue')==6-count
        if count==2:
            h.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#0b02f1',width:5,x1:200,y1:400,x2:800,y2:200,opacity:100,filled:false,seed:0,id:'hint-stroke-2'}]})")
            g.wait_for_function('state.lines.length===2')
        previous=mask
    expect(h.locator('#give-hint')).to_be_disabled()
    assert h.evaluate("api.poke('hint').then(()=>false,()=>true)"),'Fourth hint was accepted'
    g.reload();expect(g.locator('#game')).to_be_visible(timeout=30000)
    assert g.evaluate('state.hint')==previous
    assert g.evaluate('state.lines.length')==2
    expect(g.locator('#hint-display')).to_be_visible()
    # All controls remain available on laptop-sized screens in both themes.
    h.locator('#settings-open').click();expect(h.locator('#settings-dialog')).to_be_visible()
    assert h.locator('#theme-select option[value=grubbery]').is_disabled()
    h.locator('#theme-select').select_option('classic')
    h.locator('#sound-volume').evaluate("el=>{el.value=25;el.dispatchEvent(new Event('input'));}")
    h.locator('#sound-muted').check();h.locator('#reduce-motion').check();h.locator('#large-chat').check()
    assert h.evaluate("preferences.audio.volume===.25 && preferences.audio.muted")
    h.locator('#test-sound').click();expect(h.locator('#audio-status')).to_contain_text('Unmute')
    # Exercise the output selector without requesting a microphone or real hardware.
    h.evaluate("""()=>{window.testSink='';Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{enumerateDevices:async()=>[{kind:'audiooutput',deviceId:'speakers',label:'Desk speakers'},{kind:'audiooutput',deviceId:'headphones',label:'Headphones'}],selectAudioOutput:async()=>({kind:'audiooutput',deviceId:'headphones',label:'Headphones'})}});preferences.audio.setSinkId=async id=>{window.testSink=id;};Object.defineProperty(preferences.audio,'sinkId',{get:()=>window.testSink});}""")
    h.locator('#choose-output').click();expect(h.locator('#audio-output')).to_have_value('headphones');assert h.evaluate('window.testSink')=='headphones'
    h.locator('#audio-output').select_option('speakers');h.wait_for_function("window.testSink==='speakers'")
    h.locator('#sound-muted').uncheck();h.locator('#test-sound').click();h.wait_for_function('preferences.audio.currentTime>0 || preferences.audio.ended')
    h.locator('#settings-close').click()
    for width,height in [(1280,720),(1024,600),(1366,768)]:
        h.set_viewport_size({'width':width,'height':height});h.wait_for_timeout(150)
        assert h.evaluate('document.documentElement.scrollHeight<=innerHeight && document.documentElement.scrollWidth<=innerWidth')
        for selector in ['#give-hint','#zoom','#guess','#settings-open']:
            box=h.locator(selector).bounding_box();assert box and box['y']+box['height']<=height,(selector,box)
    h.screenshot(path=str(ART/'classic-hints.png'))
    h.reload();expect(h.locator('#game')).to_be_visible(timeout=30000)
    assert h.evaluate("document.body.dataset.theme==='classic' && preferences.values.volume===25 && preferences.values.reduceMotion && preferences.values.largeChat")
    h.locator('#settings-open').click();h.screenshot(path=str(ART/'settings.png'))
    h.locator('#settings-reset').click();assert h.evaluate("preferences.values.theme==='default' && preferences.values.volume===70 && !preferences.values.muted")
    h.locator('#settings-close').click();h.screenshot(path=str(ART/'default-hints.png'))
    # Unsupported browsers retain system-default output and useful feedback.
    g.evaluate('preferences.audio.setSinkId=undefined');g.locator('#settings-open').click();expect(g.locator('#audio-output')).to_be_disabled();expect(g.locator('#audio-status')).to_contain_text('system audio output');g.locator('#settings-close').click()
    g.locator('#guess').fill(answer);g.locator('#guess-form button').click()
    for page in pages:page.wait_for_function("state.phase==='reveal'")
    scores=h.evaluate('Object.fromEntries(state.players.map(p=>[p.ship,p.score]))');assert scores=={'~zod':3,'~nec':10},scores
    g.wait_for_function("state.phase==='choosing' && state.players[0].ship==='~nec'",timeout=15000);g.locator('#choices button').first.click()
    for page in pages:page.wait_for_function("state.phase==='drawing'")
    assert all(page.evaluate("state.hintCount===0 && state.hint==='' && state.artistValue===10") for page in pages)
    for page in [g,h]:page.locator('#leave').click();expect(page.locator('#lobby')).to_be_visible()
    assert not errors,errors
    print('PASS: three persistent private hints, limits/roles/scoring/reset, zoom reset, Classic/default themes, saved preferences, audio controls/device branches, and laptop fit.')
    browser.close()
