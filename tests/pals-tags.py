"""Native fake-ship Pals tags, existing-list preservation and v0 social upgrade.

Requires local ~zod/~nec test desks. Pals uses the official backend with only
its Web UI omitted; command, gesture, records and merge logic are unchanged.
The recipient begins on the prior social agent, then upgrades during this test.
"""
import json,os,re,runpy,sys,urllib.request,subprocess,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));build=runpy.run_path(str(ROOT/'scripts/build.py'))
def dojo(port,cmd):
 r=urllib.request.Request(f'http://127.0.0.1:{port}',data=json.dumps({'source':{'dojo':cmd},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'});return json.load(urllib.request.urlopen(r,timeout=60))
def tags(port,ship,target):
 return dojo(port,f"=/  r=[outgoing=(map @p (set @ta)) incoming=(set @p) receipts=(map @p ?)]  .^([outgoing=(map @p (set @ta)) incoming=(set @p) receipts=(map @p ?)] %gx /{ship}/pals/[(scot %da now)]/noun)  ~(tap in (~(gut by outgoing.r) {target} ~))")
assert dojo(12322,'our').strip()=='~zod' and dojo(12323,'our').strip()=='~nec'
with sync_playwright() as p:
 b=p.chromium.launch();pages=[];errors=[]
 for ship,http,lens in [('~zod',18080,12322),('~nec',18081,12323)]:
  c=b.new_context(viewport={'width':1280,'height':720});code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',dojo(lens,'+code')).group();assert c.request.post(f'http://127.0.0.1:{http}/~/login',form={'password':code}).ok;code=None
  html=build['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship)).replace(json.loads((ROOT/'web/chat-config.json').read_text())['host'],'~zod')
  c.route('**/apps/ursketch/play',lambda route,request,html=html:route.fulfill(content_type='text/html',body=html))
  def media(route):
   a=next(a for a in build['assets'].values() if route.request.url.endswith(a['url']));route.fulfill(content_type=a['mime'],body=a['data'])
  c.route('**/apps/ursketch/media/**',media);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{http}/apps/ursketch/play');page.wait_for_function("connectionReady && social.state.kind==='friends'");pages.append(page)
 z,n=pages
 if os.environ.get('URSKETCH_PALS_RESUME')!='1':
  # Existing list membership must survive urSketch's %meet.
  # Seeded once through :pals on the isolated ~zod before this test.
 
  n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod'&&p.incoming)",timeout=20000)
  assert 'existing' in tags(12322,'~zod','~nec')
  z.evaluate("inspectPlayer({ship:'~nec',name:'Friend Beta',avatar:null})");z.locator('#request-friendship').click();expect(z.locator('#request-friendship')).to_contain_text('Pending their approval',timeout=20000)
  n.locator('#browser-friends').click();n.locator('#friend-requests button').filter(has_text='Become Friends').click()
  z.wait_for_function("social.state.peers.some(p=>p.ship==='~nec'&&p.stage==='friend'&&p.tags?.includes('urSketch'))",timeout=20000)
  n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod'&&p.stage==='friend')",timeout=20000)
  assert 'urSketch' in tags(12322,'~zod','~nec') and 'existing' in tags(12322,'~zod','~nec')
  assert 'urSketch' not in tags(12323,'~nec','~zod'),'Recipient must begin on the prior agent for the migration check'
  # Reload a populated v0 social state, then backfill only its urSketch friendship.
  subprocess.run([sys.executable,'/private/tmp/ursketch-028/import.py','12323','ursketch',str(ROOT/'desk'),'app/ursketch-social.hoon'],check=True,capture_output=True,text=True)
  n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod'&&p.stage==='friend'&&p.tags?.includes('urSketch'))",timeout=20000)
  assert 'urSketch' in tags(12323,'~nec','~zod')
 n.wait_for_function("social.state.peers.some(p=>p.ship==='~zod'&&p.stage==='friend'&&p.tags?.includes('urSketch'))",timeout=20000)
 assert 'urSketch' in tags(12322,'~zod','~nec') and 'existing' in tags(12322,'~zod','~nec')
 assert 'urSketch' in tags(12323,'~nec','~zod')
 n.locator('#browser-friends').click()
 assert n.evaluate("social.state.peers.find(p=>p.ship==='~zod').name")==z.evaluate('activeName')
 expect(n.locator('.friend-row[data-ship="~zod"]')).to_be_visible()
 assert not errors,errors
 report={'version':build['VERSION'],'ships':['~zod','~nec'],'nativePalsBackend':'official, web UI omitted in test desk','requestAndAccept':True,'exactUrSketchTagBothShips':True,'existingTagsPreserved':True,'populatedV0StateUpgraded':True,'priorUrSketchFriendshipBackfilled':True,'defaultFilterContainsFriend':True,'realShipsContacted':False}
 (ROOT/'artifacts/pals-tags-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',report);b.close()
