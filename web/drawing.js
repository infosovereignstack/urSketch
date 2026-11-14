/* Stable, lossless wire tuples; rendering still uses the full command model. */
const UrSketchWire={
  kinds:['stroke','brush','eraser','spray','rectangle','ellipse','fill','clear'],
  pack(l){return [this.kinds.indexOf(l.kind||'stroke'),parseInt(l.color.slice(1),16),l.width,l.x1,l.y1,l.x2,l.y2,l.opacity??100,!!l.filled,l.seed||0,l.id||''];},
  unpack(l){
    if(!Array.isArray(l))return l;
    if(l.length!==11||!this.kinds[l[0]])throw new Error('Unsupported drawing command.');
    return {kind:this.kinds[l[0]],color:'#'+l[1].toString(16).padStart(6,'0'),width:l[2],x1:l[3],y1:l[4],x2:l[5],y2:l[6],opacity:l[7],filled:l[8],seed:l[9],id:l[10]};
  }
};
/* Replayable drawing tools. The host stores commands; every viewer renders them. */
function createDrawing({canvas, colors, canDraw, send, error, storageKey,onDraw,onSwitchChat=()=>{}}) {
  const ctx=canvas.getContext('2d'), board=document.createElement('canvas');
  board.width=1000;board.height=700;
  const base=board.getContext('2d',{willReadFrequently:true});
  let selected='pen', color='#000000', filled=true, gesture=null, space=false;
  let pending=[],optimistic=new Map(),sending=null,sequence=0,action=0,undoing=false,serverCount=0,serverLast='',serverToken=null;
  let zoom=1,panX=0,panY=0;
  const uid=crypto.randomUUID(), sizes=[1,2,3,4,5,6,7,8,16,32];
  const $=id=>document.getElementById(id);
  const paths={
    undo:'<path d="M8 6 3 11l5 5M3 11h10a7 7 0 0 1 7 7" fill="none" stroke-width="2"/>',
    eraser:'<path d="m4 15 8-10 8 7-8 9H9z" fill="#e99b9b"/><path d="m4 15 5 6h5l3-4-8-7z" fill="#fff"/>',
    rectangle:'<rect x="4" y="5" width="16" height="14" fill="currentColor"/>',
    fill:'<path d="m5 10 7-7 8 8-8 8-9-7z"/><path d="m5 10 8 1 7 0"/><path d="M20 14q5 6 0 6-3-1 0-6" fill="currentColor"/>',
    spray:'<path d="m6 13 7-4 5 9-7 4zM11 5l4-2 2 3-4 2"/><path d="m9 8-3-1M8 10H4M8 6 6 3"/><circle cx="3" cy="4" r=".5"/><circle cx="3" cy="9" r=".5"/>',
    pen:'<path d="m5 20 3-8L18 2l4 4-10 10z" fill="#e9bd7e"/><path d="m5 20 6-3-3-4z" fill="currentColor"/><path d="m16 4 4 4"/>',
    clear:'<path d="M6 3h9l4 5v13H6z" fill="#fff"/><path d="M15 3v5h4M9 12h7M9 16h7"/>',
    circle:'<circle cx="12" cy="12" r="8" fill="currentColor"/>',
    zoom:'<circle cx="10" cy="10" r="7" fill="#fff"/><path d="m15 15 7 7M6 10h8M10 6v8"/>',
    line:'<path d="M3 21 21 3" stroke-width="2.5"/>',
    brush:'<path d="m10 14 8-11 4 3-9 10z" fill="#a9bdd3"/><path d="M12 14Q5 13 5 19q0 3-3 3 10 1 12-6" fill="currentColor"/>'
  };
  const definitions=[['eraser','Eraser','E'],['rectangle','Rectangle','S'],['fill','Fill',''],['spray','Spray','Y'],['pen','Pen','P'],['clear','Clear','Shift: current color'],['circle','Circle','C'],['zoom','Zoom','Z'],['line','Line','L'],['brush','Brush','B'],['undo','Undo last action','Ctrl/⌘+Z']];
  function select(next,{toggle=true}={}) {
    if(next==='clear'||next==='undo')return;
    if(toggle&&next===selected&&['rectangle','circle'].includes(next))filled=!filled;
    if(next==='eraser'&&selected!=='eraser')setColor('#ffffff');
    gesture=null;space=false;
    selected=next;
    document.querySelectorAll('#tool-grid button').forEach(b=>{const active=b.dataset.tool===selected;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));});
    const name=definitions.find(d=>d[0]===next)?.[1]||next;
    $('tool-status').textContent=name+(['rectangle','circle'].includes(next)?(filled?' — filled':' — outline'):'');
    for(const name of ['rectangle','circle']){const svg=$(name)?.querySelector('svg');if(svg)svg.classList.toggle('outline',!filled);}
    canvas.dataset.tool=selected;preview();repaint();
    if(document.activeElement?.closest('#tool-grid'))$(next)?.focus({preventScroll:true});
  }
  for(const [id,name,key] of definitions){
    const b=document.createElement('button');b.id=id;b.type='button';b.className='tool';b.dataset.tool=id;b.title=id==='zoom'?'Zoom (Z, +/-)':name+(key?` (${key})`:'');b.setAttribute('aria-label',name);b.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true">${paths[id]}</svg>`;
    b.onclick=e=>id==='undo'?undo().catch(error):id==='clear'?clear(e.shiftKey).catch(error):select(id);
    if(id==='zoom')b.ondblclick=()=>setZoom(1);
    $('tool-grid').append(b);
  }
  for(const [value,name] of colors){const b=document.createElement('button');b.type='button';b.className='swatch';b.style.background=value;b.title=name;b.dataset.color=value;b.setAttribute('aria-label',name);b.onclick=()=>setColor(value);$('palette').append(b);}
  function setColor(next){color=next.toLowerCase();for(const b of $('palette').children){const active=b.dataset.color===color;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));}$('custom-color').value=color;$('color-preview').firstElementChild.style.background=color;preview();}
  function brighten(step){const rgb=color.slice(1).match(/../g).map(v=>Math.max(0,Math.min(255,parseInt(v,16)+step)));setColor('#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join(''));}
  function setWidth(value){$('width').value=Math.max(1,Math.min(40,value));preview();}
  function preview(){const size=Number($('width').value);$('width-value').value=String(size);const dot=$('brush-preview').firstElementChild;dot.style.width=`${Math.min(26,size)}px`;dot.style.height=`${Math.min(26,size)}px`;dot.style.borderRadius=selected==='eraser'?'0':'50%';dot.style.background=color;dot.style.opacity=selected==='brush'?'.35':'1';}
  $('width').oninput=preview;$('lighter').onclick=()=>brighten(16);$('darker').onclick=()=>brighten(-16);
  $('color-preview').onclick=()=>{$('advanced-palette').hidden=!$('advanced-palette').hidden;};
  $('custom-color').oninput=e=>setColor(e.target.value);
  function flood(target,x,y,hex){
    const image=target.getImageData(0,0,1000,700),d=image.data,start=(y*1000+x)*4;
    const old=[d[start],d[start+1],d[start+2],d[start+3]],rgb=hex.slice(1).match(/../g).map(v=>parseInt(v,16));
    if(old[0]===rgb[0]&&old[1]===rgb[1]&&old[2]===rgb[2]&&old[3]===255)return;
    const match=p=>p>=0&&p<700000&&!(d[p*4]===rgb[0]&&d[p*4+1]===rgb[1]&&d[p*4+2]===rgb[2]&&d[p*4+3]===255)&&Math.abs(d[p*4]-old[0])+Math.abs(d[p*4+1]-old[1])+Math.abs(d[p*4+2]-old[2])+Math.abs(d[p*4+3]-old[3])<=24;
    const stack=[y*1000+x];
    while(stack.length){let p=stack.pop();if(!match(p))continue;const row=Math.floor(p/1000),left=row*1000,right=left+1000;while(p>left&&match(p-1))p--;let above=false,below=false;for(;p<right&&match(p);p++){const i=p*4;d[i]=rgb[0];d[i+1]=rgb[1];d[i+2]=rgb[2];d[i+3]=255;const a=row>0&&match(p-1000),b=row<699&&match(p+1000);if(a&&!above)stack.push(p-1000);if(b&&!below)stack.push(p+1000);above=a;below=b;}}
    target.putImageData(image,0,0);
  }
  function paint(target,l){
    const kind=l.kind||'stroke';
    if(kind==='fill'){flood(target,Math.min(999,l.x2),Math.min(699,l.y2),l.color);return;}
    target.save();target.globalAlpha=(l.opacity??100)/100;target.strokeStyle=l.color;target.fillStyle=l.color;target.lineWidth=l.width;target.lineCap=kind==='eraser'?'square':'round';target.lineJoin='round';
    const x=Math.min(l.x1,l.x2),y=Math.min(l.y1,l.y2),w=Math.max(1,Math.abs(l.x2-l.x1)),h=Math.max(1,Math.abs(l.y2-l.y1));
    if(kind==='clear'){target.globalAlpha=1;target.fillRect(0,0,1000,700);}
    else if(kind==='rectangle'){if(l.filled)target.fillRect(x,y,w,h);else target.strokeRect(x,y,w,h);}
    else if(kind==='ellipse'){target.beginPath();target.ellipse(x+w/2,y+h/2,w/2,h/2,0,0,Math.PI*2);l.filled?target.fill():target.stroke();}
    else if(kind==='spray'){let seed=l.seed>>>0;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};for(let i=0;i<Math.max(12,l.width*3);i++){const angle=random()*Math.PI*2,r=Math.sqrt(random())*l.width/2;target.fillRect(Math.round(l.x2+Math.cos(angle)*r),Math.round(l.y2+Math.sin(angle)*r),1,1);}}
    else {target.beginPath();target.moveTo(l.x1,l.y1);target.lineTo(l.x2,l.y2);target.stroke();}
    target.restore();
  }
  function resetBase(){base.globalAlpha=1;base.fillStyle='#ffffff';base.fillRect(0,0,1000,700);serverCount=0;serverLast='';}
  function repaint(){ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.clearRect(0,0,1000,700);ctx.drawImage(board,0,0);for(const l of optimistic.values())paint(ctx,l);if(gesture?.shape)paint(ctx,gesture.shape);}
  function render(lines,token){
    if(token!==serverToken){pending=[];optimistic.clear();gesture=null;serverToken=token;resetBase();setZoom(1);}
    if(lines.length<serverCount||(serverCount&&JSON.stringify(lines[serverCount-1])!==serverLast))resetBase();
    for(let i=serverCount;i<lines.length;i++){paint(base,lines[i]);if(lines[i].id)optimistic.delete(lines[i].id);}
    serverCount=lines.length;serverLast=lines.length?JSON.stringify(lines.at(-1)):'';
    repaint();
  }
  function command(kind,a,b){return {kind,color,width:Number($('width').value),x1:a.x,y1:a.y,x2:b.x,y2:b.y,opacity:kind==='brush'?25:100,filled,seed:kind==='spray'?crypto.getRandomValues(new Uint32Array(1))[0]:0,id:`${uid}-${action}:${++sequence}`};}
  function queue(l){if(l.kind!=='clear')onDraw?.();optimistic.set(l.id,l);pending.push(l);repaint();}
  function point(event){const r=canvas.getBoundingClientRect();return{x:Math.max(0,Math.min(1000,Math.round((event.clientX-r.left)*1000/r.width))),y:Math.max(0,Math.min(700,Math.round((event.clientY-r.top)*700/r.height)))};}
  function clampedEnd(a,b,event){if(event.shiftKey&&['rectangle','circle'].includes(selected)){const n=Math.max(Math.abs(b.x-a.x),Math.abs(b.y-a.y));return{x:Math.max(0,Math.min(1000,a.x+Math.sign(b.x-a.x||1)*n)),y:Math.max(0,Math.min(700,a.y+Math.sign(b.y-a.y||1)*n))};}return b;}
  function transform(){const wrap=canvas.parentElement;const mx=Math.max(0,(canvas.clientWidth*zoom-wrap.clientWidth)/2),my=Math.max(0,(canvas.clientHeight*zoom-wrap.clientHeight)/2);panX=Math.max(-mx,Math.min(mx,panX));panY=Math.max(-my,Math.min(my,panY));canvas.style.transform=`translate(${panX}px,${panY}px) scale(${zoom})`;canvas.dataset.zoom=String(zoom);}
  function setZoom(value,event){const next=Math.max(1,Math.min(16,value)),r=canvas.parentElement.getBoundingClientRect(),ax=event?event.clientX-r.left-r.width/2:0,ay=event?event.clientY-r.top-r.height/2:0;panX=ax-(ax-panX)*next/zoom;panY=ay-(ay-panY)*next/zoom;zoom=next;if(zoom===1){panX=0;panY=0;}transform();}
  canvas.onpointerdown=event=>{
    if(!canDraw())return;event.preventDefault();canvas.focus({preventScroll:true});
    if(space&&event.metaKey){setZoom(zoom/2,event);return;}
    if(space&&event.altKey){setZoom(zoom*2,event);return;}
    if(space){gesture={pan:true,startX:event.clientX,startY:event.clientY,panX,panY};canvas.setPointerCapture(event.pointerId);return;}
    if(event.altKey){const p=point(event),v=ctx.getImageData(Math.min(999,p.x),Math.min(699,p.y),1,1).data;setColor('#'+Array.from(v).slice(0,3).map(n=>n.toString(16).padStart(2,'0')).join(''));return;}
    if(selected==='zoom'){setZoom(event.shiftKey?zoom/2:zoom*2,event);return;}
    action++;const p=point(event);if(selected==='fill'){queue(command('fill',p,p));return;}
    canvas.setPointerCapture(event.pointerId);gesture={start:p,last:p,tool:selected,token:serverToken};
    if(['rectangle','circle','line'].includes(selected)){gesture.shape=command(selected==='circle'?'ellipse':selected==='line'?'stroke':'rectangle',p,p);repaint();}
    else queue(command(selected==='pen'?'stroke':selected,p,{x:Math.min(1000,p.x+1),y:p.y}));
  };
  canvas.onpointermove=event=>{if(!gesture||!canDraw())return;if(gesture.pan){panX=gesture.panX+event.clientX-gesture.startX;panY=gesture.panY+event.clientY-gesture.startY;transform();return;}const p=point(event);if(gesture.shape){const end=clampedEnd(gesture.start,p,event);gesture.shape={...gesture.shape,x2:end.x,y2:end.y};repaint();}else {queue(command(gesture.tool==='pen'?'stroke':gesture.tool,gesture.last,p));gesture.last=p;}};
  function finish(event){if(!gesture)return;const ended=gesture;gesture=null;if(event.type==='pointerup'&&ended.shape&&canDraw()&&ended.token===serverToken)queue(ended.shape);repaint();}
  for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,finish);
  window.addEventListener('blur',()=>{gesture=null;space=false;repaint();});
  canvas.ondblclick=()=>{if(selected==='zoom')setZoom(1);};
  setInterval(()=>{if(gesture?.tool==='spray'&&canDraw())queue(command('spray',gesture.last,gesture.last));},80);
  function flush(){if(sending)return sending;if(!pending.length)return Promise.resolve();if(!canDraw()){pending=[];optimistic.clear();repaint();return Promise.resolve();}const batch=pending.splice(0,80);sending=send('draw',{lines:batch}).catch(e=>{pending=[];optimistic.clear();repaint();error(e);}).finally(()=>{sending=null;});return sending;}
  async function flushAll(){while(pending.length||sending)await flush();}
  async function clear(useColor){if(!canDraw())return;action++;await flushAll();const l=command('clear',{x:0,y:0},{x:1000,y:700});l.color=useColor?color:'#ffffff';queue(l);await flushAll();}
  async function undo(){if(!canDraw()||undoing)return;undoing=true;gesture=null;try{await flushAll();await send('undo',{});}finally{undoing=false;}}
  setInterval(()=>{void flush();},100);
  function keydown(event){
    if(event.key==='Tab'&&!event.ctrlKey&&!event.metaKey&&document.body.classList.contains('playing')&&document.activeElement?.id==='guess'){event.preventDefault();if(document.body.dataset.mobile!=='true')onSwitchChat();return;}
    if(event.target.closest('input,textarea,select,[contenteditable=true]')||document.querySelector('dialog[open]')||!canDraw())return;
    if(event.code==='Space'){space=true;event.preventDefault();return;}
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='z'&&!event.shiftKey){event.preventDefault();void undo().catch(error);return;}
    if(event.ctrlKey||event.metaKey)return;
    const key=event.key.toLowerCase(),map={s:'rectangle',c:'circle',b:'brush',p:'pen',y:'spray',e:'eraser',l:'line',z:'zoom'};
    if(map[key]){event.preventDefault();if(!event.repeat)select(map[key]);return;}
    if(key==='+'||key==='='){event.preventDefault();setZoom(zoom*2);}
    else if(key==='-'){event.preventDefault();setZoom(zoom/2);}
    else if(key==='d'){event.preventDefault();setColor(color==='#000000'?'#ffffff':'#000000');}
    else if(key==='arrowup'||key==='arrowdown'){event.preventDefault();brighten(key==='arrowup'?16:-16);}
    else if(key==='arrowleft'||key==='arrowright'){event.preventDefault();setWidth(Number($('width').value)+(key==='arrowright'?1:-1));}
    else if(/^[0-9]$/.test(key)){event.preventDefault();setWidth(key==='0'?32:key==='9'?16:Number(key));}
    else if(key==='alt')event.preventDefault();
  }
  document.addEventListener('keydown',keydown);document.addEventListener('keyup',e=>{if(e.code==='Space')space=false;});window.addEventListener('blur',()=>{space=false;gesture=null;repaint();});
  let dragged=null,dragOffset={x:0,y:0},classicLayout={};
  const palettes=$('drawing-palettes');
  try{classicLayout=JSON.parse(localStorage.getItem(storageKey+'.classic')||'{}')||{};}catch{}
  const isClassic=()=>document.body.dataset.layout==='classic';
  function placeClassic(panel,x,y){
    const box=panel.getBoundingClientRect(),board=canvas.parentElement.getBoundingClientRect();
    const navigation=document.querySelector('.header-actions'),timer=document.getElementById('timer-dial');
    const reservedTop=Math.max(2,navigation?.getBoundingClientRect().bottom+8||0,timer?.getBoundingClientRect().bottom+8||0);
    x=Math.max(2,Math.min(innerWidth-box.width-2,x));y=Math.max(reservedTop,Math.min(innerHeight-box.height-2,y));
    if(x+box.width>board.left&&x<board.right&&y+box.height>board.top&&y<board.bottom)x=Math.max(2,board.left-box.width-4);
    panel.classList.add('classic-positioned');panel.style.setProperty('--classic-x',x+'px');panel.style.setProperty('--classic-y',y+'px');
    return {x:x/innerWidth,y:y/innerHeight,rotated:panel.classList.contains('classic-rotated')};
  }
  function saveClassic(){try{localStorage.setItem(storageKey+'.classic',JSON.stringify(classicLayout));}catch{}}
  function fitClassic(){if(!isClassic())return;for(const panel of palettes.children){const saved=classicLayout[panel.dataset.palette];if(saved&&Number.isFinite(saved.x)&&Number.isFinite(saved.y)){panel.classList.toggle('classic-rotated',saved.rotated===true);placeClassic(panel,saved.x*innerWidth,saved.y*innerHeight);}}}
  document.addEventListener('dragover',e=>{if(isClassic()&&dragged)e.preventDefault();});
  document.addEventListener('drop',e=>{if(!isClassic()||!dragged)return;e.preventDefault();classicLayout[dragged.dataset.palette]=placeClassic(dragged,e.clientX-dragOffset.x,e.clientY-dragOffset.y);saveClassic();});
  function saveLayout(){try{localStorage.setItem(storageKey,JSON.stringify([...palettes.children].map(p=>({name:p.dataset.palette,rotated:p.classList.contains('rotated')}))));}catch{}}
  for(const panel of palettes.children){const grip=panel.querySelector('.palette-grip');grip.ondblclick=()=>{if(isClassic()){const box=panel.getBoundingClientRect();panel.classList.toggle('classic-rotated');classicLayout[panel.dataset.palette]=placeClassic(panel,box.x,box.y);saveClassic();}else{panel.classList.toggle('rotated');saveLayout();}};grip.ondragstart=e=>{dragged=panel;const box=panel.getBoundingClientRect();dragOffset={x:e.clientX-box.left,y:e.clientY-box.top};e.dataTransfer.setData('text/plain',panel.dataset.palette);};grip.ondragend=()=>{dragged=null;if(!isClassic())saveLayout();};panel.ondragover=e=>{e.preventDefault();if(!isClassic()&&dragged&&dragged!==panel){const r=panel.getBoundingClientRect();palettes.insertBefore(dragged,e.clientX<r.left+r.width/2?panel:panel.nextSibling);}};}
  try{for(const entry of JSON.parse(localStorage.getItem(storageKey)||'[]')){const panel=[...palettes.children].find(p=>p.dataset.palette===entry.name);if(panel){panel.classList.toggle('rotated',!!entry.rotated);palettes.append(panel);}}}catch{}
  canvas.tabIndex=0;resetBase();repaint();setColor(color);select('pen',{toggle:false});
  return {render,flushAll,clear,resetView(){setZoom(1);},resetTools(){setColor('#000000');select('pen',{toggle:false});setZoom(1);},fit(){transform();fitClassic();},cancel(){gesture=null;pending=[];optimistic.clear();setZoom(1);repaint();},undo,get selected(){return selected;},get color(){return color;},get zoom(){return zoom;},select,setColor,setWidth};
}
