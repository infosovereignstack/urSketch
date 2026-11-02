/* The host owns the 40-second deadline; local particles never travel over Ames. */
function createFinale({surface,layer,getAudio,getPrefs,onEnd}){
  const sky=layer.querySelector('canvas'),ctx=sky.getContext('2d',{alpha:false});
  let key=null,start=0,end=0,frame=null,live=false,bursts=[];
  const completed=new Set();
  const colours=['#fff7d1','#ffffff','#e7d5ff','#ffcb68','#adceff','#ffb9cc'];
  function random(seed){return()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};}
  function stop(){live=false;key=null;cancelAnimationFrame(frame);frame=null;layer.hidden=true;getAudio()?.stopFireworks();}
  function paint(now){
    frame=null;if(!live)return;if(now>=end){completed.add(key);if(completed.size>64)completed.delete(completed.values().next().value);stop();onEnd?.();return;}
    const box=surface.getBoundingClientRect(),ratio=Math.min(2,devicePixelRatio||1),w=Math.max(1,Math.round(box.width*ratio)),h=Math.max(1,Math.round(box.height*ratio));
    if(sky.width!==w||sky.height!==h){sky.width=w;sky.height=h;}
    ctx.fillStyle='#000';ctx.fillRect(0,0,w,h);
    const seconds=(now-start)/1000,reduced=getPrefs().reduceMotion;
    for(const burst of bursts){
      const age=seconds-burst.time;if(age<0||age>3.5)continue;
      if(reduced)continue;
      for(const particle of burst.particles){
        const life=Math.max(0,1-age/particle.life);if(!life)continue;
        const drag=(1-Math.exp(-age*1.15))/1.15;
        const x=(burst.x+particle.vx*drag)*w,y=(burst.y+particle.vy*drag+age*age*.026)*h;
        ctx.globalAlpha=Math.pow(life,1.3)*(.8+.2*Math.sin(age*31+particle.twinkle));ctx.strokeStyle=particle.colour;ctx.lineWidth=Math.max(.8,ratio*.9);
        ctx.beginPath();ctx.moveTo(x-particle.vx*w*.025*life,y-(particle.vy+age*.052)*h*.025*life);ctx.lineTo(x,y);ctx.stroke();ctx.fillStyle=particle.colour;ctx.fillRect(x,y,Math.max(1,ratio*.8),Math.max(1,ratio*.8));
      }
    }
    ctx.globalAlpha=1;frame=requestAnimationFrame(paint);
  }
  function update(data,identity){
    if(completed.has(identity))return;
    if(!data?.celebrating||!data.winner){if(live)stop();return;}
    const remaining=Math.min(40000,Math.max(0,data.remainingMs??data.seconds*1000));
    if(!remaining){if(live)stop();return;}
    if(identity!==key){
      stop();key=identity;live=true;end=performance.now()+remaining;start=end-40000;
      const rand=random(0x63757273);bursts=[];
      for(let i=0;i<32;i++){
        const time=.15+i*1.22+(i%5===3?.2:0),x=.13+rand()*.74,y=.16+rand()*.47,colour=colours[i%colours.length];
        const particles=Array.from({length:200},()=>{const angle=rand()*Math.PI*2,speed=.07+rand()*.19;return{vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,life:1.9+rand()*1.6,twinkle:rand()*Math.PI*2,colour:rand()<.7?'#fff8e9':colour};});
        bursts.push({id:i,time,x,y,particles});
      }
    }else end=Math.min(end,performance.now()+remaining);
    getAudio()?.fireworks({key:identity,elapsed:(performance.now()-start)/1000,remaining:Math.max(0,end-performance.now())});
    layer.hidden=false;layer.querySelector('.finale-winner').textContent=data.winner.name;
    layer.querySelector('.finale-score').textContent=`with ${data.winner.score} points!`;
    layer.querySelector('.finale-winner').classList.toggle('long-name',data.winner.name.length>20);
    if(frame===null)frame=requestAnimationFrame(paint);
  }
  document.addEventListener('visibilitychange',()=>{if(live&&frame===null)frame=requestAnimationFrame(paint);});
  window.addEventListener('pagehide',stop);
  return{update,stop,get active(){return live;}};
}
