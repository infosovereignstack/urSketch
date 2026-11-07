"""Lossless vector deltas, payload measurement, recovery, and rolling compatibility."""
import getpass
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
codes=json.loads(getpass.getpass('Fake ship codes JSON (hidden input): '))
H='http://127.0.0.1:18080';G='http://127.0.0.1:18081'
HASH="""async()=>{const data=ctx.getImageData(0,0,1000,700).data;return [...new Uint8Array(await crypto.subtle.digest('SHA-256',data))].join(',');}"""

def same_board(a,b):
    assert a.evaluate(HASH)==b.evaluate(HASH),'Canvas replay pixels differ'

def send_lines(page,start,count):
    page.evaluate("""async([start,count])=>{const lines=Array.from({length:count},(_,j)=>{const i=start+j;return {kind:'stroke',color:['#00000f','#883e31','#f50c08'][Math.floor(i/40)%3],width:3,x1:(i*17)%990,y1:(i*11)%690,x2:(i*17)%990+9,y2:(i*11)%690+9,opacity:100,filled:false,seed:0,id:'load-'+i};});await api.poke('draw',{encoding:1,lines:lines.map(l=>UrSketchWire.pack(l))});}""",[start,count])

with sync_playwright() as p:
    browser=p.chromium.launch()
    contexts=[browser.new_context(viewport={'width':1280,'height':720}) for _ in range(2)]
    pages=[];errors=[]
    for ctx_,origin,code in zip(contexts,[H,G],[codes['host'],codes['guest']]):
        assert ctx_.request.post(origin+'/~/login',form={'password':code}).ok
        ctx_.add_init_script("""window.wireEvents=[];const Original=EventSource;window.EventSource=class extends Original{constructor(...args){super(...args);this.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.response==='diff')window.wireEvents.push(m.json);});}};""")
        page=ctx_.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(origin+'/apps/ursketch/play')
        expect(page.locator('#host-search')).to_be_enabled(timeout=30000);pages.append(page)
    h,g=pages
    h.locator('#create-open').click();h.locator('#title').fill(f'Vector load {time.time_ns()}');h.locator('#create-form button.primary').click()
    expect(h.locator('#game')).to_be_visible(timeout=30000);room=h.evaluate('roomId')
    g.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=room)
    expect(g.locator('#game')).to_be_visible(timeout=30000)
    assert h.evaluate('roomStream') and g.evaluate('roomStream')
    h.locator('#start').click();expect(h.locator('#choices button')).to_have_count(3);h.locator('#choices button').first.click()
    for page in pages:page.wait_for_function("state.phase==='drawing'")
    assert g.evaluate("state.answer==='' && state.choices.length===0")
    g.evaluate('window.wireEvents=[];window.measureTemplate={...state}')
    # 1,600 commands, sent as forty equally sized vector batches.
    for start in range(0,1600,40):send_lines(h,start,40)
    for page in pages:page.wait_for_function('state.lines.length===1600',timeout=30000)
    same_board(h,g)
    metrics=g.evaluate("""()=>{const batches=wireEvents.filter(e=>e.kind==='draw'),bytes=x=>new TextEncoder().encode(JSON.stringify(x)).length;
      if(batches.length!==40)throw new Error('Unexpected draw batch count: '+batches.length);
      const baseline={...measureTemplate};delete baseline.encoding;delete baseline.count;
      let oldBytes=0,history=[];
      for(const e of batches){if(e.lines.length!==40||!e.lines.every(Array.isArray))throw new Error('Non-compact delta');history.push(...e.lines.map(l=>UrSketchWire.unpack(l)));oldBytes+=bytes({...baseline,seconds:e.seconds,lines:history});}
      const newBytes=batches.reduce((n,e)=>n+bytes(e),0);
      const full=bytes({...baseline,lines:history}),compact=bytes({...baseline,encoding:1,lines:history.map(l=>UrSketchWire.pack(l))});
      return {commands:history.length,batches:batches.length,oldRepeatedSnapshotJsonBytes:oldBytes,newDeltaJsonBytes:newBytes,reductionPercent:100*(1-newBytes/oldBytes),fullObjectSnapshotJsonBytes:full,compactSnapshotJsonBytes:compact,snapshotReductionPercent:100*(1-compact/full),firstDeltaJsonBytes:bytes(batches[0]),lastDeltaJsonBytes:bytes(batches.at(-1))};}""")
    assert metrics['reductionPercent']>95,metrics
    assert metrics['snapshotReductionPercent']>50,metrics
    assert metrics['lastDeltaJsonBytes']<1.2*metrics['firstDeltaJsonBytes'],metrics
    print(json.dumps(metrics,indent=2),flush=True)
    # Metadata never carries the drawing history; draw patches carry no secret answer.
    h.locator('#chat-input').fill('Vector stream check');h.locator('#chat-form button').click()
    expect(g.locator('#chat-messages')).to_contain_text('Vector stream check')
    assert g.evaluate("wireEvents.filter(e=>e.kind==='state').every(e=>e.lines.length===0)")
    assert g.evaluate("wireEvents.filter(e=>e.kind==='draw').every(e=>!('answer' in e)&&!('choices' in e))")
    same_board(h,g)
    # Duplicate patches are ignored, while a dropped browser update requests a snapshot.
    g.evaluate("roomEvent(wireEvents.findLast(e=>e.kind==='draw'))")
    assert g.evaluate('state.lines.length')==1600
    g.evaluate("""()=>{const receive=api.handlers.get(roomSub);window.droppedPatch=false;api.handlers.set(roomSub,event=>{if(event.kind==='draw'&&!window.droppedPatch){window.droppedPatch=true;return;}return receive(event);});window.wireEvents=[];}""")
    send_lines(h,1600,40);send_lines(h,1640,40)
    g.wait_for_function('state.lines.length===1680',timeout=30000)
    assert g.evaluate("droppedPatch && wireEvents.some(e=>e.kind==='room'&&e.count===1680)")
    same_board(h,g)
    # A new local browser gets a complete snapshot from the existing remote proxy.
    extra=contexts[1].new_page();extra.goto(G+f'/apps/ursketch/play?host=~zod&room={room}')
    expect(extra.locator('#game')).to_be_visible(timeout=30000);extra.wait_for_function('state.lines.length===1680')
    same_board(h,extra);extra.evaluate('api.unsubscribe(roomSub)');extra.close()
    # Reload also rebuilds all commands and preserves the private view.
    g.reload();expect(g.locator('#game')).to_be_visible(timeout=30000);g.wait_for_function('state.lines.length===1680')
    same_board(h,g);assert g.evaluate("state.answer==='' && state.choices.length===0")
    # A full-view client keeps receiving complete room snapshots.
    legacy_context=browser.new_context(viewport={'width':1280,'height':720})
    assert legacy_context.request.post(G+'/~/login',form={'password':codes['guest']}).ok
    legacy=legacy_context.new_page()
    legacy.goto(G+'/apps/ursketch/play');expect(legacy.locator('#host-search')).to_be_enabled(timeout=30000)
    legacy.evaluate("""()=>{const subscribe=api.subscribe.bind(api);api.subscribe=(path,...args)=>path.startsWith('/stream/')?Promise.reject(new Error('The host could not open that room or room list.')):subscribe(path,...args);}""")
    legacy.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=room)
    expect(legacy.locator('#game')).to_be_visible(timeout=30000)
    legacy.wait_for_function('state.lines.length===1680');same_board(h,legacy)
    send_lines(h,1680,10);legacy.wait_for_function('state.lines.length===1690');g.wait_for_function('state.lines.length===1690')
    same_board(h,legacy);same_board(h,g)
    # Rotate to the guest: both compact remote writes and old object writes remain valid.
    h.locator('#skip').click();g.wait_for_function("state.phase==='choosing' && state.players[0].ship==='~nec'",timeout=15000)
    g.locator('#choices button').first.click()
    for page in [h,g]:page.wait_for_function("state.phase==='drawing'")
    send_lines(g,0,10)
    for page in [h,g]:page.wait_for_function('state.lines.length===10')
    same_board(h,g)
    legacy.wait_for_function("state.phase==='drawing'&&state.lines.length===10")
    legacy.evaluate("api.poke('draw',{lines:[{kind:'stroke',color:'#883e31',width:4,x1:10,y1:20,x2:200,y2:220,opacity:100,filled:false,seed:0,id:'legacy-write'}]})")
    for page in [h,g,legacy]:page.wait_for_function('state.lines.length===11')
    same_board(h,g);same_board(h,legacy)
    # New clients fall back cleanly when a host rejects the stream subscription.
    fallback=contexts[1].new_page();fallback.goto(G+'/apps/ursketch/play');expect(fallback.locator('#host-search')).to_be_enabled(timeout=30000)
    fallback.evaluate("""()=>{const subscribe=api.subscribe.bind(api);api.subscribe=(path,...args)=>path.startsWith('/stream/')?Promise.reject(new Error('The host could not open that room or room list.')):subscribe(path,...args);}""")
    fallback.evaluate("async room=>{await browse('~zod');await joinRoom(room)}",arg=room)
    expect(fallback.locator('#game')).to_be_visible(timeout=30000);assert not fallback.evaluate('roomStream');same_board(h,fallback)
    for page in [legacy,fallback]:page.evaluate('api.unsubscribe(roomSub)')
    legacy_context.close();fallback.close()
    g.locator('#leave').click();expect(g.locator('#lobby')).to_be_visible();h.locator('#leave').click();expect(h.locator('#lobby')).to_be_visible()
    assert not errors,errors
    (ROOT/'artifacts/vector-stream-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print('PASS: bounded compact deltas, exact pixels, metadata separation, duplicate/gap recovery, proxy/reload replay, remote artist, and full-view fallback.')
    browser.close()
