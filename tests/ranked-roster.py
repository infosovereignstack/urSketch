"""Browser-only score/color fixtures across every theme; no real room actions."""
import json,re,runpy,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));render=runpy.run_path(str(ROOT/'scripts/build.py'))
r=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(r,timeout=30))).group()
with sync_playwright() as p:
 browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':720});assert context.request.post('http://127.0.0.1/~/login',form={'password':code}).ok
 current=context.request.get('http://127.0.0.1/apps/ursketch/play').text();ship=re.search(r"window.URSKETCH_SHIP='([^']+)'",current).group(1);html=render['html'].replace('URSKETCH_SHIP_VALUE',json.dumps(ship));context.route('**/apps/ursketch/play',lambda r:r.fulfill(status=200,content_type='text/html',body=html))
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1/apps/ursketch/play');page.wait_for_function('connectionReady')
 page.evaluate("""()=>{window.realPoke=api.poke;api.poke=async()=>{};host=SELF;roomId='roster-fixture';$('lobby').hidden=true;$('game').hidden=false;document.body.classList.add('playing');window.fixture={kind:'room',title:'Ranked roster',owner:SELF,phase:'drawing',turn:0,token:200,remainingMs:120000,seconds:120,duration:120,started:true,answer:'treehouse',choices:[],hint:'',hintCount:0,value:10,artistValue:10,celebrating:false,winner:null,finishing:false,lines:[],messages:[],players:[{ship:SELF,name:'You',score:2,solved:false},{ship:'~zod',name:'High score',score:30,solved:false},{ship:'~nec',name:'Tied player',score:10,solved:false},{ship:'~bud',name:'First guesser',score:5,solved:false}]};}""")
 themes=page.locator('#theme-select option:not([disabled])').evaluate_all('els=>els.map(e=>e.value)')
 for theme in themes:
  page.locator('#theme-select').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("change"));}',theme)
  page.evaluate('()=>{rosterOrder=[];renderRoom(structuredClone(fixture));}')
  assert page.locator('#players li').evaluate_all('els=>els.map(e=>e.dataset.ship)')==['~zod','~nec','~bud',ship]
  assert page.locator('#players .player-name').evaluate_all("els=>els.every(e=>getComputedStyle(e).color===(e.closest('li').classList.contains('me')?'rgb(0, 128, 0)':'rgb(0, 0, 0)'))"),theme
  # A correct guess moves that player up and highlights them, regardless of artist position.
  page.evaluate("()=>{fixture.players[3].score=30;fixture.players[3].solved=true;renderRoom(structuredClone(fixture));}")
  assert page.locator('#players li').evaluate_all('els=>els.map(e=>e.dataset.ship)')==['~zod','~bud','~nec',ship]
  assert page.locator('#players li[data-ship="~bud"] .player-name').evaluate("e=>getComputedStyle(e).color==='rgb(0, 128, 0)'")
  assert page.locator('#players li.me .artist-pencil').count()==1
  # Backend turn rotation must not alter tied score order or move the pencil to the leader.
  page.evaluate("()=>{const r=structuredClone(fixture);r.players=[...r.players.slice(1),r.players[0]];r.token++;renderRoom(r);}")
  assert page.locator('#players li').evaluate_all('els=>els.map(e=>e.dataset.ship)')==['~zod','~bud','~nec',ship]
  assert page.locator('#players li[data-ship="~zod"] .artist-pencil').count()==1
  page.evaluate("()=>{renderRoom({...structuredClone(fixture),phase:'finished',remainingMs:0,seconds:0});}")
  assert page.locator('#players li:not(.me) .player-name').evaluate_all("els=>els.every(e=>getComputedStyle(e).color==='rgb(0, 0, 0)')"),theme
  page.evaluate("()=>{fixture.players[3].score=5;fixture.players[3].solved=false;renderRoom(structuredClone(fixture));}")
  assert page.locator('#players li.solved').count()==0
  if theme=='classic':page.screenshot(path=str(ROOT/'artifacts/score-ranked-roster.png'))
 page.evaluate("()=>{state=null;roomId='';localStorage.removeItem(recoveryKey);api.poke=realPoke;}");assert not errors,errors;browser.close()
 (ROOT/'artifacts/ranked-roster-verification.json').write_text(json.dumps({'themes':themes,'descendingScores':True,'stableTies':True,'selfGreen':True,'otherNamesBlackUntilSolved':True,'correctGuessGreen':True,'greenClearsAtRoundEnd':True,'artistMarkerTracksShip':True,'browserOnlyFixture':True},indent=2)+'\n');print('PASS: ranking, stable ties, baseline/solved/end-round name colors and artist marker across',len(themes),'themes')
