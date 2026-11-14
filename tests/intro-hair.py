"""Compare the intro's hair with decoded source pixels across all 442 frames."""
import base64,json,os,re,runpy,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PREVIEW=os.environ.get('URSKETCH_PREVIEW')=='1'
SELECTED=os.environ.get('URSKETCH_HAIR_FRAMES')
FRAMES=[int(n) for n in SELECTED.split(',')] if SELECTED else range(442)
sys.path.insert(0,str(ROOT/'scripts'));build=runpy.run_path(str(ROOT/'scripts/build.py'))
r=urllib.request.Request('http://127.0.0.1:12321',data=json.dumps({'source':{'dojo':'+code'},'sink':{'stdout':None}}).encode(),headers={'Content-Type':'application/json'})
code=re.search(r'[a-z]{6}(?:-[a-z]{6}){3}',json.load(urllib.request.urlopen(r,timeout=30))).group()
with sync_playwright() as p:
 b=p.chromium.launch();c=b.new_context(viewport={'width':1280,'height':900})
 assert c.request.post('http://127.0.0.1/~/login',form={'password':code}).ok;code=None
 if PREVIEW:c.route('**/apps/ursketch',lambda route:route.fulfill(content_type='text/html',body=build['intro']))
 c.add_init_script("localStorage.setItem('ursketch.settings.v1',JSON.stringify({themeDisabled:true}))")
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 response=page.goto('http://127.0.0.1/apps/ursketch');assert "context.rect(1072,264,112,8)" in response.text()
 if not PREVIEW:
  assert response.text()==build['intro'], 'Installed intro differs from the verified build'
  assert 'id="app-version">'+build['VERSION']+'<' in c.request.get('http://127.0.0.1/apps/ursketch/play').text()
 page.wait_for_function("document.querySelector('video').readyState>=2 && document.body.classList.contains('art-ready')")
 page.locator('video').evaluate('v=>v.pause()')
 page.evaluate("""()=>{window.original=document.createElement('canvas');original.width=1620;original.height=1080;window.ox=original.getContext('2d',{willReadFrequently:true});}""")
 report={'version':build['VERSION'],'installed':not PREVIEW,'frames':0,'hairFrames':0,'hairPixels':0,'outlinePixels':0,'hairMismatches':0,'logoRemnantPixels':0}
 for frame in FRAMES:
  page.locator('video').evaluate('(v,t)=>new Promise(r=>{v.addEventListener("seeked",r,{once:true});v.currentTime=t})',frame/24+.002)
  result=page.evaluate("""()=>{
   ox.drawImage(document.querySelector('video'),0,0);
   const rendered=document.querySelector('#intro-scene').getContext('2d'),a=ox.getImageData(940,0,680,280).data,d=rendered.getImageData(940,0,680,280).data;
   const red=i=>a[i]>100&&a[i]>a[i+1]+75&&a[i]>a[i+2]+75;
   const near=(x,y,r=4)=>{for(let b=Math.max(0,y-r);b<=Math.min(279,y+r);b++)for(let c=Math.max(0,x-r);c<=Math.min(679,x+r);c++)if(red((b*680+c)*4))return true;return false;};
   const sky=[d[4*(10*680+650)],d[4*(10*680+650)+1],d[4*(10*680+650)+2]],circle=[45,100,154].map((v,i)=>Math.round(v*sky[i]/[159,193,224][i]));
   let hair=0,outline=0,mismatch=0,remnants=0,examples=[];
   for(let y=0;y<280;y++)for(let x=0;x<680;x++){
    const i=(y*680+x)*4,rawRed=red(i),black=a[i]<65&&a[i+1]<65&&a[i+2]<65;
    if(rawRed||(y>=225&&black&&near(x,y))){if(rawRed)hair++;else outline++;if(a[i]!==d[i]||a[i+1]!==d[i+1]||a[i+2]!==d[i+2])mismatch++;}
    const radius=Math.hypot(x+940+.5-738,y+.5-532);if(Math.abs(radius-511)<2)continue;
    const colour=radius<511?circle:sky;
    if(colour.some((v,j)=>Math.abs(d[i+j]-v)>8)&&!(y>=225&&near(x,y,16)&&[0,1,2].every(j=>a[i+j]===d[i+j]))){remnants++;if(examples.length<12)examples.push([x+940,y,...d.slice(i,i+3),...colour]);}
   }
   return{hair,outline,mismatch,remnants,examples};
  }""")
  assert result['mismatch']==0 and result['remnants']==0,(frame,result)
  report['frames']+=1;report['hairFrames']+=int(result['hair']>0);report['hairPixels']+=result['hair'];report['outlinePixels']+=result['outline'];report['hairMismatches']+=result['mismatch'];report['logoRemnantPixels']+=result['remnants']
 assert report['hairFrames']>(1 if SELECTED else 20) and report['outlinePixels']>100,report
 page.locator('video').evaluate('(v)=>new Promise(r=>{v.addEventListener("seeked",r,{once:true});v.currentTime=7.002})')
 data=page.evaluate("""()=>{ox.drawImage(document.querySelector('video'),0,0);const c=document.createElement('canvas');c.width=960;c.height=340;const x=c.getContext('2d');x.fillStyle='#eef3f8';x.fillRect(0,0,960,340);x.fillStyle='#111';x.font='18px sans-serif';x.fillText('Original footage',18,28);x.fillText('Restored animation',498,28);x.drawImage(original,890,225,270,160,0,44,480,284);x.drawImage(document.querySelector('#intro-scene'),890,225,270,160,480,44,480,284);return c.toDataURL()}""")
 (ROOT/'artifacts/intro-hair-comparison.png').write_bytes(base64.b64decode(data.split(',')[1]))
 page.screenshot(path=str(ROOT/'artifacts/intro-hair-restored.png'))
 assert not errors,errors
 (ROOT/'artifacts'/('intro-hair-installed.json' if SELECTED else 'intro-hair-verification.json')).write_text(json.dumps(report,indent=2)+'\n');b.close();print('PASS:',report)
