/* Friend requests survive closed tabs; native urSketch/Pals own their state. */
function createSocial({self,coordinator,perform,subscribe,unsubscribe,profile,inspect,notify,join}){
  const $=id=>document.getElementById(id);
  let data={peers:[]},sub=null,opening=null,inspected=null,signature='',presenceAt=0,presenceKey='',slateNonce=null,slateTimer=null,joiningSlate=false;
  function endSlate(){clearTimeout(slateTimer);slateTimer=null;slateNonce=null;$('clean-slate-join').disabled=false;$('clean-slate-join').classList.remove('friend-pulse');}
  const busy=p=>['checking','installing','pals','delivering','confirming'].includes(p?.stage);
  const node=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;};
  const peer=ship=>data.peers.find(p=>p.ship===ship);
  function profileButton(p){const b=node('button','friend-name',p.name||p.ship);b.type='button';b.title='Inspect player profile';b.onclick=()=>{$('friends-dialog').close();inspect(p);};return b;}
  function actionButton(text,action,p){const b=node('button','',text);b.type='button';b.disabled=busy(p);if(busy(p)){b.classList.add('friend-pulse');b.setAttribute('aria-busy','true');}b.onclick=()=>act(action,p);return b;}
  async function act(action,p){
    if(busy(peer(p.ship)))return;
    const optimistic={...p,stage:'checking',mode:action==='accept'?'accept':'request',error:''};data.peers=data.peers.filter(v=>v.ship!==p.ship).concat(optimistic);render();
    try{await perform(action,{ship:p.ship,peerName:p.name||p.ship,peerAvatar:p.avatar||null,...profile()});}
    catch(error){optimistic.stage='error';optimistic.error=error.message;render();notify(error.message);}
  }
  function renderProfile(){
    const b=$('request-friendship');b.hidden=!inspected||inspected.ship===self;if(b.hidden)return;
    const p=peer(inspected.ship);b.disabled=busy(p)||p?.stage==='pending'||p?.stage==='friend';
    b.classList.toggle('friend-pulse',busy(p));b.setAttribute('aria-busy',String(busy(p)));
    b.textContent=busy(p)?'Requesting friendship…':p?.stage==='friend'?'Friends':p?.stage==='pending'?'Friendship requested. Pending their approval':'Request friendship';
    b.title=p?.error||'';b.onclick=()=>act('request',inspected);
  }
  function render(){
    renderProfile();const pending=data.peers.filter(p=>p.incoming&&p.stage!=='friend'&&p.stage!=='denied');
    for(const dot of document.querySelectorAll('.friend-dot'))dot.hidden=!pending.length;
    for(const id of ['friends-open','browser-friends'])$(id).setAttribute('aria-label',pending.length?`Friends and DMs — ${pending.length} friend requests`:'Friends and DMs');
    if(!$('friends-dialog').open)return;
    const next=JSON.stringify(data.peers.map(p=>({...p,presence:undefined})));if(signature!==next){
      signature=next;const requests=$('friend-requests');requests.replaceChildren();
      for(const p of pending){const row=node('div','friend-request');row.append(profileButton(p));const controls=node('div','friend-request-actions');controls.append(actionButton(busy(p)?'Friendship…':'Become Friends','accept',p),actionButton('Deny Friendship','deny',p));row.append(controls);if(p.error)row.append(node('p','friend-error',p.error));requests.append(row);}
      if(!pending.length)requests.append(node('p','friends-empty','No friend requests.'));
      const list=$('friend-list');list.replaceChildren();
      for(const p of data.peers.filter(p=>p.stage==='friend')){const row=node('div','friend-row');row.dataset.ship=p.ship;const avatar=node('div','friend-avatar');avatar.append(createCharacter(p.avatar));const name=profileButton(p);name.prepend(avatar);const status=node('span','friend-presence');status.dataset.peer=p.ship;const dm=node('a','friend-dm','DM');dm.href='/apps/groups/dm/'+encodeURIComponent(p.ship);dm.target='_blank';dm.rel='noopener';dm.setAttribute('aria-label',`DM ${p.name||p.ship} in Groups`);row.append(name,status,dm);list.append(row);}
      if(!list.children.length)list.append(node('p','friends-empty','Your friends will appear here.'));
      const outgoing=data.peers.filter(p=>p.outgoing&&p.stage!=='friend'&&!p.incoming&&p.stage!=='denied');$('outgoing-section').hidden=!outgoing.length;$('friend-outgoing').replaceChildren(...outgoing.map(p=>{const row=node('div','friend-request');row.append(profileButton(p),node('span',busy(p)?'friend-pulse':'',p.stage==='pending'?'Friendship requested. Pending their approval':busy(p)?'Requesting friendship…':p.error||'Request not completed.'));if(p.stage==='error')row.append(actionButton('Retry','request',p));return row;}));
    }
    for(const e of document.querySelectorAll('[data-peer]')){const p=peer(e.dataset.peer),present=p?.presence; e.textContent=present?.title&&(!present.expires||present.expires>Date.now())?present.title:'Not in-game';}
  }
  async function receive(next){
    if(next.kind!=='friends')return;data={...next,peers:next.peers||[]};render();
    const room=next.slate;$('clean-slate-status').textContent=room?.ready?`${room.count||0}/25 players · Round ${room.round||1}/${room.rounds||10}`:'Join the shared drawing room';
    const destination=next.destination;if(!slateNonce||destination?.nonce!==slateNonce||joiningSlate)return;
    if(destination.error){notify(destination.error);endSlate();return;}
    if(!destination.host||!destination.room)return;
    joiningSlate=true;
    clearTimeout(slateTimer);
    try{await join(destination);}catch(error){notify(error.message);}finally{joiningSlate=false;endSlate();}
  }
  async function start(){
    if(sub!==null)return;if(opening)return opening;
    opening=(async()=>{try{sub=await subscribe(next=>{void receive(next);});$('friends-status').textContent='';await perform('profile',profile());}catch(error){$('friends-status').textContent='Friends are unavailable. Close and reopen this menu to retry.';throw error;}finally{opening=null;}})();return opening;
  }
  async function reconnect(){const old=sub;sub=null;if(old!==null)void unsubscribe(old).catch(()=>{});try{await start();}catch{}}
  async function open(){signature='';$('friends-dialog').showModal();render();try{await start();}catch{}}
  for(const id of ['friends-open','browser-friends'])$(id).onclick=open;
  $('friends-close').onclick=()=>$('friends-dialog').close();
  $('clean-slate-join').onclick=async()=>{if(slateNonce)return;slateNonce=crypto.randomUUID();$('clean-slate-join').disabled=true;$('clean-slate-join').classList.add('friend-pulse');$('clean-slate-status').textContent='Opening A Clean Slate…';slateTimer=setTimeout(()=>{if(joiningSlate)return;endSlate();notify('The shared room is taking too long to respond. Please retry.');},125000);try{await start();await perform('clean-slate',{nonce:slateNonce,...profile()});}catch(error){endSlate();notify(error.message);}};
  setInterval(()=>{if($('friends-dialog').open)render();},10000);
  return{start:()=>start().catch(()=>{}),reconnect,inspect:p=>{inspected=p;renderProfile();},presence:async room=>{const key=JSON.stringify([room,profile()]);if(key===presenceKey&&Date.now()-presenceAt<30000)return;presenceKey=key;presenceAt=Date.now();try{await perform('presence',{...profile(),...(room||{title:'',room:'',host:self})});}catch{presenceAt=0;}},get state(){return data;}};
}
