/* Friend requests survive closed tabs; native urSketch/Pals own their state. */
async function openGroupsDm(ship){
  if(!/^~[a-z-]+$/.test(ship))throw new Error('This player does not have a valid Urbit ID.');
  const path='/apps/groups/dm/'+encodeURIComponent(ship),tab=window.open('/apps/groups/','_blank');
  if(!tab)throw new Error('Allow pop-ups for your ship to open a Groups DM.');
  // Keep the same-origin handle while preparing the composer, without giving
  // the Groups tab access to its opener. Never click a message Send control.
  tab.opener=null;
  const deadline=Date.now()+90000;
  const visible=e=>e&&e.getClientRects().length&&!e.disabled;
  const wait=async find=>{
    while(Date.now()<deadline){
      if(tab.closed)throw new Error('The Groups tab was closed before the DM opened.');
      if(tab.location.href==='about:blank'){await new Promise(resolve=>setTimeout(resolve,350));continue;}
      if(tab.location.origin!==location.origin)throw new Error('Log into Groups on your ship, then try DM again.');
      if(tab.location.pathname.includes('/group/')||tab.location.pathname.includes('/dm/')&&tab.location.pathname!==path)throw new Error('The Groups tab moved to another conversation. Click DM to try again.');
      const value=find(tab.document);if(value)return value;
      await new Promise(resolve=>setTimeout(resolve,350));
    }
    throw new Error('Groups did not finish opening the DM. Try again after Groups has loaded.');
  };
  const exact=(root,text)=>[...root.querySelectorAll('button,[role=button],span')].find(e=>visible(e)&&e.textContent.trim()===text);
  const composer=doc=>visible(doc.querySelector('[data-testid="MessageInput"]'));
  const trigger=await wait(doc=>visible(doc.querySelector('[data-testid="CreateChatSheetTrigger"]'))&&doc.querySelector('[data-testid="CreateChatSheetTrigger"]'));
  trigger.click();
  (await wait(doc=>exact(doc,'New Message'))).click();
  // A bare DM URL does not create Groups' local pending conversation. Use its
  // own New Message flow so both existing and first-time recipients work.
  const field=await wait(doc=>[...doc.querySelectorAll('input')].find(e=>visible(e)&&e.placeholder==='Filter by nickname or id'));
  Object.getOwnPropertyDescriptor(tab.HTMLInputElement.prototype,'value').set.call(field,ship);
  field.dispatchEvent(new tab.Event('input',{bubbles:true}));
  field.dispatchEvent(new tab.Event('change',{bubbles:true}));
  (await wait(doc=>{
    const input=[...doc.querySelectorAll('input')].find(e=>visible(e)&&e.placeholder==='Filter by nickname or id');
    return input&&input.value===ship&&exact(input.closest('[role=dialog]')||doc,ship);
  })).click();
  await wait(doc=>tab.location.pathname===path&&composer(doc));
  return tab;
}
function createSocial({self,coordinator,perform,subscribe,unsubscribe,profile,inspect,notify,join}){
  const $=id=>document.getElementById(id);
  let data={peers:[]},sub=null,opening=null,inspected=null,signature='',presenceAt=0,presenceKey='',slateNonce=null,slateTimer=null,joiningSlate=false;
  function endSlate(){clearTimeout(slateTimer);slateTimer=null;slateNonce=null;$('clean-slate-join').disabled=false;$('clean-slate-join').classList.remove('friend-pulse');}
  const busy=p=>['checking','installing','pals','delivering','confirming'].includes(p?.stage);
  const node=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;};
  const peer=ship=>data.peers.find(p=>p.ship===ship);
  let friendsFilter='ursketch';
  const openingDms=new Set(),joiningFriends=new Set();
  const arrow=()=>node('span','external-arrow','↗');
  function dmButton(p){
    const b=node('button','friend-dm',openingDms.has(p.ship)?'Opening DM…':'DM');b.type='button';if(!openingDms.has(p.ship))b.append(' ',arrow());b.disabled=openingDms.has(p.ship);b.classList.toggle('friend-pulse',b.disabled);b.setAttribute('aria-label',`DM ${p.name||p.ship} in Groups`);
    b.onclick=async()=>{if(openingDms.has(p.ship))return;openingDms.add(p.ship);b.disabled=true;b.textContent='Opening DM…';b.classList.add('friend-pulse');try{await openGroupsDm(p.ship);}catch(error){notify(error.message);}finally{openingDms.delete(p.ship);signature='';render();}};
    return b;
  }
  function profileButton(p){const b=node('button','friend-name',p.name||p.ship);b.type='button';b.title='View profile: '+(p.name||p.ship);b.setAttribute('aria-label','View profile: '+(p.name||p.ship));b.onclick=()=>{$('friends-dialog').close();inspect(p);};return b;}
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
    for(const link of document.querySelectorAll('.pals-open'))link.parentElement.hidden=data.palsReady!==true;
    for(const note of document.querySelectorAll('.pals-install-note'))note.hidden=data.palsReady===true;
    for(const dot of document.querySelectorAll('.friend-dot'))dot.hidden=!pending.length;
    for(const id of ['friends-open','browser-friends'])$(id).setAttribute('aria-label',pending.length?`Friends and DMs — ${pending.length} friend requests`:'Friends and DMs');
    if(!$('friends-dialog').open)return;
    const next=JSON.stringify([friendsFilter,data.peers.map(p=>({...p,presence:undefined}))]);if(signature!==next){
      signature=next;$('incoming-section').hidden=!pending.length;const requests=$('friend-requests');requests.replaceChildren();
      for(const p of pending){const row=node('div','friend-request');row.append(profileButton(p));const controls=node('div','friend-request-actions');controls.append(actionButton(busy(p)?'Friendship…':'Become Friends','accept',p),actionButton('Deny Friendship','deny',p));row.append(controls);if(p.error)row.append(node('p','friend-error',p.error));requests.append(row);}
      if(!pending.length)requests.append(node('p','friends-empty','No friend requests.'));
      const list=$('friend-list');list.replaceChildren();
      for(const p of data.peers.filter(p=>p.stage==='friend'&&(friendsFilter==='all'||p.tags?.includes('urSketch')))){
        const row=node('div','friend-row');row.dataset.ship=p.ship;const status=node('span','friend-presence');status.dataset.peer=p.ship;
        const enter=node('button','friend-join','Join');enter.type='button';enter.dataset.joinPeer=p.ship;
        enter.onclick=async()=>{
          const current=peer(p.ship)?.presence;if(!livePresence(current)||joiningFriends.has(p.ship))return;
          joiningFriends.add(p.ship);enter.disabled=true;enter.textContent='Joining…';enter.classList.add('friend-pulse');
          try{await join({host:current.host,room:current.room,title:current.title});$('friends-dialog').close();}catch(error){notify(error.message);}finally{joiningFriends.delete(p.ship);enter.textContent='Join';enter.disabled=false;enter.classList.remove('friend-pulse');render();}
        };
        row.append(profileButton(p),status,enter,dmButton(p));list.append(row);
      }
      if(!list.children.length)list.append(node('p','friends-empty',friendsFilter==='ursketch'?'No urSketch friends yet. Select All Friends to see your other pals.':'Your friends will appear here.'));
      const outgoing=data.peers.filter(p=>p.outgoing&&p.stage!=='friend'&&!p.incoming&&p.stage!=='denied');$('outgoing-section').hidden=!outgoing.length;$('friend-outgoing').replaceChildren(...outgoing.map(p=>{const row=node('div','friend-request');row.append(profileButton(p),node('span',busy(p)?'friend-pulse':'',p.stage==='pending'?'Friendship requested. Pending their approval':busy(p)?'Requesting friendship…':p.error||'Request not completed.'));if(p.stage==='error')row.append(actionButton('Retry','request',p));return row;}));
    }
    for(const e of $('friend-list').querySelectorAll('[data-peer]')){const present=peer(e.dataset.peer)?.presence;e.textContent=livePresence(present)?present.title:'';e.title=e.textContent;}
    for(const e of $('friend-list').querySelectorAll('[data-join-peer]'))e.hidden=!livePresence(peer(e.dataset.joinPeer)?.presence);
  }
  function livePresence(p){return p?.title&&p?.host&&p?.room&&p.expires>Date.now();}
  for(const [id,filter] of [['friends-ursketch','ursketch'],['friends-all','all']])$(id).onclick=()=>{
    friendsFilter=filter;for(const [id,value] of [['friends-ursketch','ursketch'],['friends-all','all']])$(id).setAttribute('aria-pressed',String(filter===value));render();
  };
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
