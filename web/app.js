/* urSketch: native Eyre channels, no JavaScript dependencies. */
'use strict';
const $ = id => document.getElementById(id);
const SELF = window.URSKETCH_SHIP;
const GLOBAL_CHAT_HOST=URSKETCH_GLOBAL_CHAT_HOST;
const connectPage = document.documentElement.classList.contains('connect-route');
$('connect-page').hidden=!connectPage;
if(connectPage)document.title='urSketch · Connect';else document.body.classList.add('browsing');
let activeName = SELF, profiles = [], hasLocalProfile=false, hasLocalCharacter=false;
const profileKey = `ursketch.players.${SELF}`;
const characterKey=`ursketch.character.${SELF}`;
let activeCharacter=normalizeCharacter(null),characterReady=Promise.resolve(),characterBuilder=null,characterDraft=false;
try{const saved=JSON.parse(localStorage.getItem(characterKey)||'null');if(saved){hasLocalCharacter=true;activeCharacter=normalizeCharacter(saved.value||saved);characterDraft=saved.pending===true;}}catch{}
function rememberCharacter(value,pending=false){activeCharacter=normalizeCharacter(value);characterDraft=pending;try{localStorage.setItem(characterKey,JSON.stringify({value:activeCharacter,pending}));}catch{}}
let host = SELF, roomId = '', state = null, lobbySub = null, roomSub = null;
let drawing,roomAdmin,social;let nameDraft=false;let rosterSignature='';const messageSignatures=new Map();
let rosterOrder=[];
const PENCIL_URL='URSKETCH_PENCIL_URL';
let finale=null,gameAudio=null,roomTimeline=[],serverMessages=[],feedbackSeen=new Set(),selectedChat='game',lastTheme='',bannerDismissed=null;
let clockAt = 0, clockSeconds = 0, connectionReady = false;
const ctx = $('canvas').getContext('2d');
// Swatch centers sampled from the supplied palette reference; black/white are exact.
const colors = [
  ['#0b02f1','Blue'],['#20712c','Dark green'],['#f5bb1c','Gold'],['#f50c08','Red'],['#6c1dd1','Violet'],['#7e043f','Maroon'],['#490007','Dark brown'],['#000000','Black'],
  ['#139cec','Azure'],['#02a005','Green'],['#f5f229','Yellow'],['#e53f29','Orange-red'],['#cb0069','Magenta'],['#e0ba96','Peach'],['#883e31','Brown'],['#828280','Gray'],
  ['#8cbaee','Light blue'],['#02f102','Lime'],['#fffa85','Light yellow'],['#fe9c3b','Orange'],['#e67287','Pink'],['#f3ccbd','Light peach'],['#ba7b58','Tan'],['#ffffff','White']
];
function toast(message) { $('toast').textContent = message; $('toast').hidden = false; clearTimeout(toast.timer); toast.timer = setTimeout(() => $('toast').hidden = true, 4500); }
function connection(text, good) { $('status').textContent = text; $('status-dot').classList.toggle('connected', good); connectionReady = good; renderPlayerTotal(); chatControls(); }
function element(tag, className, text) { const el = document.createElement(tag); if (className) el.className = className; if (text != null) el.textContent = text; return el; }
function rejectedAction(action){
  const detail={undo:'Only the current artist can undo an action in the active drawing turn.',admin:'Only the room owner can change settings. Choose 10–600 seconds and available word lists.', 'reset-timer':'Only the room owner can reset an active drawing round.', 'custom-words':'The owner can upload up to five lists with 101–5,000 unique plain-text entries each.',join:'The room may be full or no longer available.',guess:'The drawing turn may have changed, or you have already guessed correctly.',hint:'Only the artist can give hints, before the first correct guess and up to three times.',draw:'The drawing turn may have changed or its command limit was reached.',start:'The room owner can start the first game when at least two players are present. Later games start automatically.',skip:'Only the current artist can end this drawing turn.',chat:'The message may contain the secret word.',heartbeat:'Your membership may have expired. Use Rejoin to return.',warn:'Both players must still be in the room.',kick:'Only the room owner can remove another player who is still in the room.', 'global-chat':'Messages must be at most 240 bytes and at least one second apart.'};
  return new Error('The host could not accept this action. '+(detail[action]||'Check your room connection and try again.'));
}
class Eyre {
  constructor(){this.uid=`${Date.now()}-${crypto.randomUUID()}`;this.next=1;this.handlers=new Map();this.subscriptions=new Map();this.waiters=new Map();this.requests=new Map();this.url=`/~/channel/ursketch-${this.uid}`;this.opening=null;this.reconnectTimer=null;this.reconnectAttempt=0;this.closed=false;}
  async send(action){
    const id=this.next++;let response;
    try{response=await fetch(this.url,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify([{id,...action}]),signal:AbortSignal.timeout(30000)});}
    catch(error){if(error.name==='TimeoutError'||error.name==='AbortError')throw new Error('Your ship did not respond within 30 seconds. Check the connection and room before retrying; the action may still have arrived.');throw error;}
    if(!response.ok)throw new Error(response.status===403?'Log into your ship, then reload this page.':`Your ship returned HTTP ${response.status}.`);return id;
  }
  ensure(){if(this.events&&this.events.readyState!==EventSource.CLOSED)return Promise.resolve();if(this.opening)return this.opening;if(this.events?.readyState===EventSource.CLOSED)this.url=`/~/channel/ursketch-${this.uid}-${crypto.randomUUID()}`;this.opening=this.open().finally(()=>this.opening=null);return this.opening;}
  retryChannel(){
    if(this.closed||this.reconnectTimer!==null||this.events?.readyState!==EventSource.CLOSED)return;
    const delay=Math.min(30000,1000*2**Math.min(this.reconnectAttempt++,5))+Math.random()*1000;
    this.reconnectTimer=setTimeout(()=>{this.reconnectTimer=null;if(this.closed)return;void this.ensure().then(()=>this.retryChannel()).catch(()=>this.retryChannel());},delay);
  }
  async open(){
    await this.send({action:'poke',ship:SELF.slice(1),app:'hood',mark:'helm-hi',json:'urSketch connected'});
    this.events=new EventSource(this.url);
    this.events.onopen=()=>{
      const restored=this.connectedOnce;this.connectedOnce=true;this.reconnectAttempt=0;clearTimeout(this.reconnectTimer);this.reconnectTimer=null;connection(`Connected as ${SELF}`,true);
      if(restored){
        recoveryTarget='';recoverySub=null;if(savedRoom)void watchRecovery();
        if(state)restartRoomUpdates();
        if(globalChatSub!==null){const old=globalChatSub;globalChatSub=null;globalChatReady=false;chatControls();void this.unsubscribe(old).catch(()=>{});}
        void connectGlobalChat();void social?.reconnect();
        for(const [ship,entry] of knownHosts){if(entry.id===null)continue;const old=entry.id;entry.id=null;void this.unsubscribe(old).catch(()=>{});void watchHost(ship).catch(()=>{});}
      }
    };
    this.events.onerror=()=>{connection('Reconnecting to your ship…',false);this.retryChannel();};
    this.events.onmessage=event=>{
      const data=JSON.parse(event.data);
      this.send({action:'ack','event-id':Number(event.lastEventId)}).catch(()=>{});
      const subscription=this.subscriptions.get(data.id);
      if(data.response==='diff'){
        try{const ready=this.handlers.get(data.id)?.(data.json);if(ready!==false)subscription?.ready();}catch(e){subscription?.fail(e);}
      }
      if((data.response==='subscribe'&&data.err)||data.response==='quit'){
        const message=new Error(data.err?'The host could not open that room or room list.':'The host stopped sending updates.');
        subscription?.fail(message);
        if(subscription?.settled&&data.response==='quit')subscriptionLost(data.id,message);
      }
      const waiter=this.waiters.get(data.id);
      if(waiter&&data.response==='poke'){
        if(waiter.remote&&!data.err)return;
        this.finish(waiter,data.err?rejectedAction(waiter.action):null);
      }
    };
    if(this.relaySub!=null)await this.unsubscribe(this.relaySub).catch(()=>{});
    this.relaySub=await this.subscribe('/relay',data=>{const waiter=this.requests.get(data.request);if(waiter)this.finish(waiter,data.ok?null:rejectedAction(waiter.action));},false,SELF);
  }
  finish(waiter,error){clearTimeout(waiter.timer);this.waiters.delete(waiter.id);this.requests.delete(waiter.request);error?waiter.reject(error):waiter.resolve();}
  async poke(action,data={},target={host,room:roomId},app='ursketch'){
    const turnToken=state?.token||0;
    await characterReady;
    const id=this.next,request=`${this.uid}-${id}`;
    const result=new Promise((resolve,reject)=>{
      const waiter={id,request,action,resolve,reject,remote:target.host!==SELF};
      waiter.timer=setTimeout(()=>this.finish(waiter,new Error('The host has not acknowledged this action yet. It may still arrive; check the room before repeating it.')),60000);
      this.waiters.set(id,waiter);if(waiter.remote)this.requests.set(request,waiter);
      this.send({action:'poke',ship:SELF.slice(1),app,mark:'json',json:{action,room:target.room,host:target.host,request,name:activeName,avatar:activeCharacter,token:turnToken,...data}}).catch(e=>this.finish(waiter,e));
    });
    return result;
  }
  subscribe(path,handler,initial=false,targetHost=host,app='ursketch'){
    const id=this.next,localPath=targetHost===SELF?path:`/proxy/${targetHost}${path}`;
    let resolve,reject;
    const first=initial?new Promise((yes,no)=>{resolve=yes;reject=no;}):null;
    const meta={settled:!initial,ready:()=>{if(meta.settled)return;meta.settled=true;clearTimeout(meta.timer);resolve(id);},fail:e=>{if(meta.settled)return;meta.settled=true;clearTimeout(meta.timer);this.handlers.delete(id);this.subscriptions.delete(id);this.send({action:'unsubscribe',subscription:id}).catch(()=>{});reject(e);}};
    if(initial)meta.timer=setTimeout(()=>meta.fail(new Error('No room data arrived from the host. Please try again.')),60000);
    this.handlers.set(id,handler);this.subscriptions.set(id,meta);
    const sent=this.send({action:'subscribe',ship:SELF.slice(1),app,path:localPath});
    if(initial){sent.catch(meta.fail);return first;}
    return sent.then(()=>id).catch(e=>{this.handlers.delete(id);this.subscriptions.delete(id);throw e;});
  }
  async unsubscribe(id){if(id==null)return;const sub=this.subscriptions.get(id);if(sub&&!sub.settled)sub.fail(new Error('Search cancelled.'));this.handlers.delete(id);this.subscriptions.delete(id);await this.send({action:'unsubscribe',subscription:id});}
}
// A restored lobby must recreate subscriptions after pagehide closes its channel.
window.addEventListener('pageshow',event=>{if(event.persisted&&!connectPage)location.reload();});
const api=new Eyre();
const recoveryKey=`ursketch.room.${SELF}`,GRACE_MS=120000;
let savedRoom=null,browsing=false,joining=false,searchEpoch=0,roomEpoch=0;
let heartbeatInFlight=null,hostPresenceUntil=0,heartbeatWarning=false;
let roomStream=false,snapshotRequest=null,roomReceiver=null,roomRecovering=false,roomRecoveryTimer=null,roomRecoveryAttempt=0,roomRecoveryInFlight=null;
function operation(id,text,busy=false){const el=$(id);el.textContent=text;el.classList.toggle('is-busy',busy);el.setAttribute('aria-label',text+(busy?'…':''));}
function busyControls(){const busy=browsing||joining;$('host-search').disabled=busy;$('host').disabled=joining;$('create-open').disabled=busy;for(const b of $('room-list').querySelectorAll('button'))b.disabled=busy||b.dataset.full==='true';$('rejoin-room').disabled=busy;$('leave-saved-room').disabled=busy;}
function saveRecovery(record){savedRoom=record;try{record?localStorage.setItem(recoveryKey,JSON.stringify(record)):localStorage.removeItem(recoveryKey);}catch{}renderRecovery();}
let recoverySub=null,recoveryTarget='';
function rememberRoom(title){if(!roomId)return;saveRecovery({host,id:roomId,title:title||state?.title||savedRoom?.title||roomId,rounds:state?.rounds||savedRoom?.rounds||10,round:state?Math.min(state.rounds||10,state.turn+1):savedRoom?.host===host&&savedRoom?.id===roomId?savedRoom.round||1:1});}
function renderRecovery(){const visible=!!savedRoom&&!state;$('room-recovery').hidden=!visible;if(!visible)return;$('recovery-title').textContent='Reconnect to your previous game';$('recovery-detail').textContent=`${savedRoom.title} · Round ${savedRoom.round||1}/${savedRoom.rounds||10} · ${savedRoom.host}`;}
function restoreRecovery(){savedRoom=null;try{const r=JSON.parse(localStorage.getItem(recoveryKey)||'null');if(r&&/^~[a-z-]+$/.test(r.host)&&/^[a-z0-9-]{1,40}$/.test(r.id))savedRoom=r;}catch{}renderRecovery();if(savedRoom&&!connectPage)void watchRecovery();}
async function watchRecovery(){
  const record=savedRoom;if(!record||connectPage)return;const target=`${record.host}/${record.id}`;if(target===recoveryTarget)return;recoveryTarget=target;
  const old=recoverySub;recoverySub=null;if(old!==null)void api.unsubscribe(old).catch(()=>{});
  try{const id=await api.subscribe('/lobby',data=>{if(target!==recoveryTarget||!savedRoom||savedRoom.host!==record.host||savedRoom.id!==record.id)return;const room=data.rooms?.find(r=>r.id===record.id);if(!room){if(!state)saveRecovery(null);return;}savedRoom={...savedRoom,title:room.title,round:room.round||savedRoom.round||1,rounds:room.rounds||savedRoom.rounds||10};try{localStorage.setItem(recoveryKey,JSON.stringify(savedRoom));}catch{}renderRecovery();},true,record.host);if(target===recoveryTarget)recoverySub=id;else void api.unsubscribe(id);}catch{if(target===recoveryTarget)recoveryTarget='';}
}
function showLobby({keepRoom=true}={}){void social?.presence(null);const old=roomSub;roomEpoch++;clearTimeout(roomRecoveryTimer);roomRecoveryTimer=null;roomReceiver=null;roomRecovering=false;roomRecoveryAttempt=0;roomRecoveryInFlight=null;if(snapshotRequest){clearTimeout(snapshotRequest.timer);snapshotRequest=null;}roomId='';state=null;roomSub=null;rosterOrder=[];finale?.stop();gameAudio?.stop();roomAdmin?.render(null);roomTimeline=[];serverMessages=[];feedbackSeen.clear();if(old!=null)api.unsubscribe(old).catch(()=>{});drawing?.cancel();$('game').hidden=true;$('lobby').hidden=false;document.body.classList.remove('playing','is-artist','is-guesser');history.replaceState(null,'',location.pathname);if(!keepRoom)saveRecovery(null);renderRecovery();if(savedRoom)void watchRecovery();}
const knownHostsKey=`ursketch.hosts.${SELF}`,knownHosts=new Map();
let hideFull=false,hideEmpty=false;
try{const saved=JSON.parse(localStorage.getItem('ursketch.roomFilters')||'{}');hideFull=saved.full===true;hideEmpty=saved.empty===true;}catch{}
$('hide-full-rooms').checked=hideFull;$('hide-empty-rooms').checked=hideEmpty;
function saveRoomFilters(){hideFull=$('hide-full-rooms').checked;hideEmpty=$('hide-empty-rooms').checked;try{localStorage.setItem('ursketch.roomFilters',JSON.stringify({full:hideFull,empty:hideEmpty}));}catch{}renderRoomList();}
$('hide-full-rooms').onchange=$('hide-empty-rooms').onchange=saveRoomFilters;
function rememberHost(ship){
  if(!knownHosts.has(ship)){if(knownHosts.size>=20){const removable=[...knownHosts].find(([key])=>key!==SELF&&key!==host);if(removable){api.unsubscribe(removable[1].id).catch(()=>{});knownHosts.delete(removable[0]);}}knownHosts.set(ship,{id:null,data:null,pending:null});}
  try{localStorage.setItem(knownHostsKey,JSON.stringify([...knownHosts.keys()]));}catch{}
  return knownHosts.get(ship);
}
function renderPlayerTotal(){
  const ships=new Set();let reachable=0,legacy=0;
  for(const entry of knownHosts.values()){
    if(!entry.data)continue;reachable++;
    for(const room of entry.data.rooms){if(Array.isArray(room.players)){for(const player of room.players)ships.add(player.ship);}else legacy=Math.max(legacy,room.count);}
  }
  const total=Math.max(ships.size,legacy),label=$('browser-player-total');
  label.textContent=connectionReady&&reachable?`Rooms (${legacy?'≥':''}${total} players)`:'Rooms (… players)';
  label.title=`Distinct players across ${reachable} reachable known host ship${reachable===1?'':'s'} (${knownHosts.size} known).`+(legacy?' Some hosts do not provide player IDs, so this is a minimum.':'');
}
async function watchHost(ship){
  const entry=rememberHost(ship);if(entry.id!==null)return entry.id;if(entry.pending)return entry.pending;
  entry.pending=api.subscribe('/lobby',data=>{if(knownHosts.get(ship)!==entry)return;if(data.kind!=='lobby'||!Array.isArray(data.rooms))throw new Error('The host did not return a room list.');entry.data=data;renderPlayerTotal();if(host===ship)renderLobby(data);},true,ship)
    .then(id=>{if(knownHosts.get(ship)!==entry){void api.unsubscribe(id);return id;}entry.id=id;return id;}).catch(error=>{entry.data=null;renderPlayerTotal();throw error;}).finally(()=>entry.pending=null);
  return entry.pending;
}
function restoreKnownHosts(){
  let saved=[];try{saved=JSON.parse(localStorage.getItem(knownHostsKey)||'[]');}catch{}
  for(const ship of Array.isArray(saved)?saved.slice(-19):[])if(/^~[a-z-]+$/.test(ship))rememberHost(ship);
  rememberHost(SELF);
}
async function watchOtherHosts(){await Promise.allSettled([...knownHosts.keys()].filter(ship=>ship!==host).map(watchHost));}

function subscriptionLost(id,error){
  if(id===globalChatSub){globalChatSub=null;globalChatReady=false;chatStatus('Chat disconnected. Retry.',true);chatControls();}
  if(id===roomSub)restartRoomUpdates();
  for(const [ship,entry] of knownHosts){if(entry.id!==id)continue;entry.id=null;entry.data=null;renderPlayerTotal();if(ship===host)operation('browse-status','Room search disconnected. Search again to retry.');}
}
function restartRoomUpdates(){
  if(!state||!roomId||!roomReceiver||roomRecovering)return;
  const old=roomSub;roomSub=null;roomRecovering=true;
  if(old!==null)void api.unsubscribe(old).catch(()=>{});
  drawing?.cancel();const at=clockAt,seconds=clockSeconds;renderRoom(state);clockAt=at;clockSeconds=seconds;updateDial();toast('Room updates interrupted. Reconnecting…');scheduleRoomRecovery();
}
// Rewatch the existing membership; never send join during recovery.
function scheduleRoomRecovery(){
  if(!state||!roomId||!roomReceiver||roomRecoveryTimer!==null||roomRecoveryInFlight?.epoch===roomEpoch)return;
  const epoch=roomEpoch,receive=roomReceiver,target=host,path=`/${roomStream?'stream':'room'}/${roomId}/${SELF}`;
  const delay=Math.min(15000,1000*2**Math.min(roomRecoveryAttempt++,4))+Math.random()*500;
  roomRecoveryTimer=setTimeout(async()=>{
    roomRecoveryTimer=null;if(epoch!==roomEpoch)return;
    const attempt={epoch};roomRecoveryInFlight=attempt;let failed=false;
    try{
      await api.ensure();if(epoch!==roomEpoch)return;const id=await api.subscribe(path,receive,true,target);
      if(epoch!==roomEpoch){void api.unsubscribe(id).catch(()=>{});return;}
      roomSub=id;roomRecovering=false;roomRecoveryAttempt=0;renderRoom(state);toast('Room updates restored.');void maintainPresence();
    }catch{failed=true;}finally{if(roomRecoveryInFlight===attempt)roomRecoveryInFlight=null;if(failed&&epoch===roomEpoch)scheduleRoomRecovery();}
  },delay);
}
async function browse(ship){
  if(!/^~[a-z-]+$/.test(ship))throw new Error('Enter an Urbit ship name beginning with ~.');
  if(roomId)throw new Error('Leave your current room before searching another host.');
  const epoch=++searchEpoch;browsing=true;host=ship;
  operation('browse-status','Searching',true);operation('join-status','');listedRooms=[];renderRoomList();busyControls();
  try{
    await api.ensure();const id=await watchHost(ship);
    if(epoch!==searchEpoch)return;lobbySub=id;renderLobby(knownHosts.get(ship).data);void watchOtherHosts();$('host').value='';
  }catch(e){if(epoch===searchEpoch)operation('browse-status','Search failed. Please try again.');throw e;}
  finally{if(epoch===searchEpoch){browsing=false;busyControls();renderRoomList();}}
}
let listedRooms=[];
function renderRoomList(){renderRoomCards(listedRooms);}
function renderLobby(data){
  if(data?.kind!=='lobby')return;
  operation('browse-status','');
  $('browse-status').title=$('browse-status').textContent;listedRooms=data.rooms;renderRoomList();
}
function renderRoomCards(rooms){
  const list=$('room-list'),shown=rooms.filter(r=>!(hideFull&&r.count>=(r.capacity||25))&&!(hideEmpty&&r.count===0));list.hidden=false;
  if(!shown.length){list.replaceChildren(element('p','browser-empty',browsing?'Searching…':rooms.length?'No rooms match your filters.':'None found'));return;}
  list.replaceChildren(...shown.map(r=>{
    const row=element('article',`room-row${r.count?' occupied':''}`),rejoin=savedRoom?.host===host&&savedRoom?.id===r.id,full=r.count>=(r.capacity||25)&&!rejoin;
    const button=element('button','room-name',r.title);button.dataset.full=String(full);button.disabled=full||browsing||joining;button.onclick=()=>run(()=>joinRoom(r.id,r.title));button.title=`${r.title}\n${r.phase} · ${r.count}/${r.capacity||25} players\nHosted by ${host}`;
    const count=element('span','room-occupancy',`${r.count}/${r.capacity||25}`);count.tabIndex=0;count.title=Array.isArray(r.players)?r.players.map(p=>`${p.name||p.ship} (${p.ship})`).join('\n')||'No players yet':`${r.count} players`;
    const details=element('div','room-details');details.append(element('b','',r.title),element('p','',`Phase: ${r.phase}`),element('p','',`Players: ${r.count}/${r.capacity||25}`));
    row.append(button,count,details);return row;
  }));
}
let globalChatSub=null,globalChatOpening=null,globalChatReady=false,globalChatSending=false,globalMessages=[];
function chatStatus(text,retry=false){$('global-chat-status').textContent=text;$('global-chat-retry').hidden=!retry;}
function chatControls(){const disabled=!globalChatReady||globalChatSending||!connectionReady;$('global-chat-input').disabled=disabled;$('global-chat-send').disabled=disabled;}
function renderGlobalChat(data){
  if(data.kind!=='global-chat'||!Array.isArray(data.messages))throw new Error('Chat data unavailable.');
  const guide=$('browser-guide'),atBottom=guide.scrollHeight-guide.scrollTop-guide.clientHeight<60,first=globalMessages.length===0;
  globalMessages=data.messages;globalChatReady=true;chatStatus('');chatControls();
  $('global-messages').replaceChildren(...globalMessages.map(message=>{
    const row=element('p','global-message'),name=element('button','global-chat-name',message.name||message.ship);name.type='button';name.title=message.ship;name.onclick=()=>inspectPlayer(message);
    row.append(name,document.createTextNode(': '+message.text));return row;
  }));
  if(atBottom||first&&globalMessages.length)requestAnimationFrame(()=>guide.scrollTop=guide.scrollHeight);
}
async function connectGlobalChat(){
  if(globalChatOpening)return globalChatOpening;if(globalChatSub!==null)return;
  globalChatOpening=(async()=>{chatStatus('Connecting…');try{await api.ensure();globalChatSub=await api.subscribe('/global-chat',renderGlobalChat,true,GLOBAL_CHAT_HOST);}catch{globalChatReady=false;chatStatus('Chat unavailable. Retry.',true);chatControls();}finally{globalChatOpening=null;}})();
  return globalChatOpening;
}
$('global-chat-retry').onclick=()=>{void connectGlobalChat();};
$('global-chat-form').onsubmit=async event=>{
  event.preventDefault();const input=$('global-chat-input'),text=input.value.trim();if(!text||!globalChatReady||globalChatSending)return;
  if(new TextEncoder().encode(text).length>240||/[\u0000-\u001f\u007f]/.test(text)){chatStatus('Please shorten your message.');return;}
  globalChatSending=true;chatControls();
  try{await api.poke('global-chat',{text},{host:GLOBAL_CHAT_HOST,room:''});if(input.value.trim()===text)input.value='';chatStatus('');}
  catch{chatStatus('Message not sent. Please try again.');}
  finally{globalChatSending=false;chatControls();if(!input.disabled)input.focus();}
};
function requestDrawingSnapshot(){
  if(snapshotRequest?.epoch===roomEpoch)return;
  const epoch=roomEpoch;
  const request={epoch,timer:setTimeout(()=>{if(snapshotRequest===request){snapshotRequest=null;toast('Drawing updates are delayed. Rejoin if the connection does not recover.');}},20000)};
  snapshotRequest=request;
  api.poke('sync').catch(e=>{if(snapshotRequest===request){clearTimeout(request.timer);snapshotRequest=null;toast(e.message);}});
}
function roomEvent(data){
  if(state&&Number.isInteger(data.token)&&data.token<state.token)return null;
  if(data.kind==='feedback'){
    if(data.feedback==='close'&&state?.phase==='drawing'&&data.room===roomId&&data.token===state.token&&!feedbackSeen.has(data.id)){
      feedbackSeen.add(data.id);if(feedbackSeen.size>100)feedbackSeen.delete(feedbackSeen.values().next().value);
      roomTimeline.push({who:'',text:data.text,kind:data.channel==='chat'?'chat-close':'close'});roomTimeline=roomTimeline.slice(-160);renderRoomMessages();void gameAudio?.play('CloseGuess');
    }
    return null;
  }
  if(data.kind==='draw'){
    if(!state){requestDrawingSnapshot();return null;}
    if(data.token<state.token)return null;
    if(data.token!==state.token){requestDrawingSnapshot();return null;}
    if(state.phase!=='drawing')return null;
    if(data.count<=state.lines.length)return null;
    if(data.from!==state.lines.length||data.count!==data.from+data.lines.length){requestDrawingSnapshot();return null;}
    state.lines.push(...data.lines.map(l=>UrSketchWire.unpack(l)));state.count=data.count;state.seconds=data.seconds;state.remainingMs=data.remainingMs;
    clockSeconds=(data.remainingMs??data.seconds*1000)/1000;clockAt=performance.now();
    gameAudio?.countdown(state.phase==='drawing'&&state.finishing?clockSeconds*1000:null,`${host}/${roomId}/${state.token}`);
    drawing.render(state.lines,state.token);updateDial();
    return null;
  }
  if(data.kind==='state'){
    if(state&&data.token===state.token&&data.count===state.lines.length)return {...data,kind:'room',lines:state.lines};
    if(data.count===0)return {...data,kind:'room',lines:[]};
    requestDrawingSnapshot();return null;
  }
  if(data.kind==='room'){
    if(snapshotRequest){clearTimeout(snapshotRequest.timer);snapshotRequest=null;}
    return {...data,lines:data.encoding===1?data.lines.map(l=>UrSketchWire.unpack(l)):data.lines};
  }
  return data;
}
async function joinRoom(id,title=''){
  if(joining)throw new Error('A room is already opening.');
  const recovering=savedRoom?.id===id&&savedRoom?.host===host;
  const epoch=++roomEpoch;let firstView=true;
  finale?.stop();gameAudio?.stop();roomTimeline=[];serverMessages=[];feedbackSeen.clear();
  joining=true;roomId=id;state=null;rosterOrder=[];rosterSignature='';messageSignatures.clear();operation('join-status',`Joining ${title||id}`,true);busyControls();
  let accepted=false;
  try{
    await api.ensure();await api.poke('join');accepted=true;hostPresenceUntil=Date.now()+GRACE_MS;heartbeatWarning=false;rememberRoom(title);
    await api.unsubscribe(roomSub);roomSub=null;
    const receive=data=>{
      if(epoch!==roomEpoch)return false;
      // Membership is authoritative even if drawing history needs repair.
      if(data.kind==='removed'||(['state','room'].includes(data.kind)&&Array.isArray(data.players)&&!data.players.some(p=>p.ship===SELF))){if(firstView&&data.kind!=='removed')return false;const kicked=data.messages?.some(m=>m.kind==='kick'&&m.ship===SELF);if(data.kind==='removed')saveRecovery(null);if(kicked)toast('The room owner removed you. You can join again when you choose.');if(firstView)throw new Error('That room is no longer available.');localLeave();operation('join-status','Your place in that room has ended.');return false;}
      data=roomEvent(data);if(!data)return false;
      if(data.kind!=='room')throw new Error('The host did not return a room.');
      firstView=false;renderRoom(data);return true;
    };
    roomReceiver=receive;roomStream=true;
    try{roomSub=await api.subscribe(`/stream/${id}/${SELF}`,receive,true);}
    catch(e){
      if(!/host could not open|host stopped sending/.test(e.message))throw e;
      roomStream=false;
      roomSub=await api.subscribe(`/room/${id}/${SELF}`,receive,true);
    }
    $('lobby').hidden=true;$('game').hidden=false;$('room-host').textContent=`HOSTED BY ${host.toUpperCase()}`;
    document.body.classList.add('playing');requestAnimationFrame(fitCanvas);history.replaceState(null,'',`?host=${encodeURIComponent(host)}&room=${id}`);
    rememberRoom(state.title);operation('join-status','');requestAnimationFrame(focusGuess);
    if(!recovering)void gameAudio?.play('JoinRoom');
  }catch(e){showLobby({keepRoom:accepted||!!savedRoom});operation('join-status',`Could not join: ${e.message}`);throw e;}
  finally{joining=false;busyControls();}
}
async function leaveSavedRoom(){const record=savedRoom;if(!record)return;joining=true;operation('join-status','Leaving room',true);busyControls();try{await api.ensure();await api.poke('leave',{}, {host:record.host,room:record.id});}catch{}finally{saveRecovery(null);joining=false;operation('join-status','Room left.');busyControls();}}
$('rejoin-room').onclick=()=>run(async()=>{const record=savedRoom;if(!record)return;await browse(record.host);await joinRoom(record.id,record.title);});
$('leave-saved-room').onclick=()=>run(leaveSavedRoom);
setInterval(()=>{if(!state&&savedRoom)void watchRecovery();},15000);
// Only the host expires membership. A stale lobby tab must never evict an active tab.
window.addEventListener('storage',event=>{if(event.key===recoveryKey&&!state){restoreRecovery();renderRoomList();}});
async function maintainPresence(){
  if(!state||!roomId||!connectionReady||heartbeatInFlight?.epoch===roomEpoch)return;
  const current={host,room:roomId},epoch=roomEpoch;
  heartbeatInFlight={epoch};
  try{
    await api.poke('heartbeat',{},current);
    if(epoch!==roomEpoch)return;
    hostPresenceUntil=Date.now()+GRACE_MS;rememberRoom(state.title);void social?.presence({host,room:roomId,title:state.title});
    if(heartbeatWarning)toast('Room connection restored.');
    heartbeatWarning=false;
  }catch(e){
    if(epoch!==roomEpoch)return;
    if(!heartbeatWarning){heartbeatWarning=true;toast('The host is slow to respond. Retrying your room connection…');}
    if(Date.now()>=hostPresenceUntil)restartRoomUpdates();
  }finally{if(heartbeatInFlight?.epoch===epoch)heartbeatInFlight=null;}
}
setInterval(()=>{void maintainPresence();},10000);
window.addEventListener('online',()=>{void api.ensure().then(()=>maintainPresence()).catch(()=>{});if(roomRecovering)scheduleRoomRecovery();});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)void maintainPresence();});
window.addEventListener('pagehide',()=>{api.closed=true;clearTimeout(api.reconnectTimer);clearTimeout(roomRecoveryTimer);if(!api.events&&!api.opening)return;const actions=[];if(state&&roomId)actions.push({id:api.next++,action:'poke',ship:SELF.slice(1),app:'ursketch-social',mark:'json',json:{action:'presence',name:activeName,avatar:activeCharacter,title:'',room:'',host:SELF}});if(state&&roomId){rememberRoom(state.title);actions.push({id:api.next++,action:'poke',ship:SELF.slice(1),app:'ursketch',mark:'json',json:{action:'leave',host,room:roomId,request:`leave-${api.uid}`,name:activeName}});}actions.push({id:api.next++,action:'delete'});api.events?.close();fetch(api.url,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(actions),keepalive:true}).catch(()=>{});});

function isArtist() { return state?.players[0]?.ship === SELF; }
function canDraw() { return connectionReady && !roomRecovering && state?.phase === 'drawing' && isArtist(); }
function appendRoomMessages(messages){
  const key=m=>JSON.stringify([m.who,m.kind,m.text]);
  let overlap=Math.min(serverMessages.length,messages.length);
  while(overlap&&!serverMessages.slice(-overlap).every((m,i)=>key(m)===key(messages[i])))overlap--;
  const fresh=messages.slice(overlap);roomTimeline.push(...fresh);roomTimeline=roomTimeline.slice(-160);serverMessages=messages;
  return fresh;
}
function renderRoomMessages(){
  renderMessages('messages',roomTimeline.filter(m=>!['chat','chat-close','warning','kick'].includes(m.kind)));
  renderMessages('chat-messages',roomTimeline.filter(m=>['chat','chat-close','warning','kick'].includes(m.kind)||(m.kind==='system'&&m.text==='joined the room')));
}
function selectChat(which,focus=false){
  selectedChat=which;document.body.dataset.activeChat=which;
  for(const name of ['game','chat']){
    document.querySelector(`[data-chat="${name}"]`).classList.toggle('chat-selected',which===name);
    $('select-'+name+'-chat').setAttribute('aria-pressed',String(which===name));
  }
  if(focus){const input=$(which==='game'?'guess':'chat-input');(input.disabled?$(which==='game'?'messages':'chat-messages'):input).focus({preventScroll:true});}
}
for(const name of ['game','chat']){
  $('select-'+name+'-chat').onclick=()=>selectChat(name,true);
  const pane=document.querySelector(`[data-chat="${name}"]`);
  pane.addEventListener('pointerdown',()=>selectChat(name));pane.addEventListener('focusin',()=>selectChat(name));
}
for(const [id,name] of [['guess','game'],['chat-input','chat']])$(id).addEventListener('focus',()=>selectChat(name));
selectChat('game');
function roomSounds(before,after,fresh){
  if(before){
    if(after.players.some(p=>!before.players.some(old=>old.ship===p.ship)))void gameAudio?.play('JoinRoom');
    if(fresh.some(m=>m.kind==='found-word'))void gameAudio?.play('YouGotTheWord');
    if(fresh.some(m=>m.kind==='correct'&&m.ship!==SELF))void gameAudio?.play('SomeoneElseGotTheWord');
    if(after.phase==='reveal'&&before.phase==='drawing'||after.phase==='drawing'&&['waiting','finished'].includes(before.phase))void gameAudio?.play('NewRound');
    if(after.phase==='drawing'&&(before.phase!=='drawing'||before.token!==after.token)&&after.players[0]?.ship===SELF)void gameAudio?.play('YourTurnToDraw');
    if(after.phase==='drawing'&&before.phase==='drawing'&&before.token===after.token&&after.hintCount>before.hintCount)void gameAudio?.play('HintNoise');
    if(fresh.some(m=>m.kind==='warning'))void gameAudio?.play('RemindsRules');
  }
  gameAudio?.countdown(after.phase==='drawing'&&after.finishing?(after.remainingMs??after.seconds*1000):null,`${host}/${roomId}/${after.token}`);
}
function focusGuess(){if(!document.querySelector('dialog[open]')&&!$('game').hidden&&!$('guess').disabled){selectChat('game');$('guess').focus({preventScroll:true});}}
function dismissBanner(){if(state)bannerDismissed=state.token;$('artist-banner').hidden=true;}
function renderRoom(data) {
  if (data.kind === 'removed') { localLeave(); return; }
  if (data.kind !== 'room') return;
  if (!data.players.some(p => p.ship === SELF)) { localLeave(); return; }
  const changedTurn=state?.token!==data.token;
  const before=state,fresh=appendRoomMessages(data.messages);
  state=data;clockSeconds=(data.remainingMs??data.seconds*1000)/1000;clockAt=performance.now();
  roomSounds(before,data,fresh);
  if(changedTurn||before?.phase==='drawing'&&data.phase!=='drawing')drawing?.cancel();
  if(data.players[0]?.ship===SELF&&data.phase==='drawing'&&(!before||before.phase!=='drawing'||before.token!==data.token||before.players[0]?.ship!==SELF))drawing?.resetTools();
  $('room-title').textContent=data.title;
  document.body.classList.toggle('is-artist',isArtist()&&data.phase==='drawing');
  document.body.classList.toggle('is-guesser',!isArtist()&&data.phase==='drawing');
  $('round').textContent=`Round ${Math.min(data.rounds||10,data.turn+1)} / ${data.rounds||10}`;
  const artist=data.players.find(p=>p.ship===(data.artist||data.players[0]?.ship)), name=data.artistName||artist?.name||artist?.ship||'The artist';
  const labels={waiting:'Waiting for players',choosing:`${name} is choosing a word`,drawing:`${name} is drawing`,reveal:'Artwork pause — next round in 3 seconds',finished:'Game over'};
  const round=Math.min(data.rounds||10,data.turn+1);
  $('classic-round').replaceChildren(document.createTextNode(`Round ${round} of ${data.rounds||10} in ${data.title} by `),element('b','',name));
  $('classic-round').title=$('classic-round').textContent;
  $('classic-player-count').textContent=data.players.length;
  $('phase-label').textContent=labels[data.phase];$('game-status').textContent=data.phase;
  $('artist-secret').hidden=!(isArtist()&&data.phase==='drawing');
  $('word').textContent=isArtist()?data.answer:'';$('word-value').textContent=data.artistValue??10;
  $('player-count').textContent=`${data.players.length}/${data.capacity||25}`;
  rosterOrder=rosterOrder.filter(ship=>data.players.some(p=>p.ship===ship));
  for(const p of data.players)if(!rosterOrder.includes(p.ship))rosterOrder.push(p.ship);
  const roster=rosterOrder.map(ship=>data.players.find(p=>p.ship===ship)).sort((a,b)=>b.score-a.score);
  const nextRoster=JSON.stringify([data.phase,roster,data.players[0]?.ship]);
  if(rosterSignature!==nextRoster){rosterSignature=nextRoster;$('players').replaceChildren(...roster.map(p=>{
    const li=element('li',[(p.ship===SELF?'me':''),(data.phase==='drawing'&&p.solved?'solved':'')].filter(Boolean).join(' '));li.dataset.ship=p.ship;
    const portrait=element('div','player-avatar');portrait.setAttribute('aria-hidden','true');portrait.append(createCharacter(p.avatar));
    const label=element('div','player-name',p.name||p.ship);label.title=p.ship;li.tabIndex=0;li.setAttribute('role','button');li.setAttribute('aria-label',`Inspect ${p.name||p.ship}`);li.onclick=()=>inspectPlayer(p);li.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspectPlayer(p);}};
    const score=element('span','player-score',`${p.score} Points`);
    const marker=element('span','player-drawing-marker');
    if(data.phase==='drawing'&&p.ship===data.players[0]?.ship){const pencil=element('img','artist-pencil');pencil.src=PENCIL_URL;pencil.alt='Drawing';pencil.title='Currently drawing';marker.append(pencil);}
    li.append(portrait,label,score,marker);return li;
  }));
  }
  drawing.render(data.lines,data.token);rememberRoom(data.title);void social?.presence({host,room:roomId,title:data.title});roomAdmin?.render(data);
  const waiting=['waiting','finished'].includes(data.phase)&&!data.celebrating;
  $('room-notice').hidden=!waiting;
  $('room-notice-text').textContent=data.started?'Waiting for another player. The next round starts automatically.':'Waiting for players. At least two players are needed.';
  const hostStart=data.owner===SELF&&waiting&&!data.started;
  const artistPrompt=isArtist()&&data.phase==='drawing'&&bannerDismissed!==data.token&&!data.lines.some(l=>l.kind!=='clear');
  $('host-start').hidden=!hostStart;$('start').disabled=data.players.length<2;
  $('artist-instructions').hidden=!artistPrompt;
  $('banner-word').textContent=isArtist()?data.answer:'';
  $('artist-banner').hidden=!(hostStart||artistPrompt);
  $('tools').hidden=!(isArtist()&&data.phase==='drawing');
  $('round-controls').hidden=!(isArtist()&&data.phase==='drawing');
  const hintCount=data.hintCount||0,solved=data.finishing||data.players.some(p=>p.solved);
  $('hints-used').textContent=`${hintCount}/3`;
  $('give-hint').disabled=!canDraw()||hintCount>=3||solved||data.hintCount==null;
  $('give-hint').title=solved?'Hints close after the first correct guess':hintCount>=3?'All three hints have been used':`Give hint — artist reward becomes ${hintCount===0?5:hintCount===1?4:3} points`;
  const mask=data.hint||'';$('hint-display').hidden=!mask||data.phase!=='drawing';
  $('hint-letters').textContent=mask.split(' ').map(word=>Array.from(word).join(' ')).join('   ');
  $('studio-toolbar').hidden=data.phase!=='drawing'||(!isArtist()&&!mask);
  $('hint-length').textContent=mask?`${Array.from(mask).filter(c=>c!==' ').length} letters`:'';
  for(const control of $('tools').querySelectorAll('button,input'))control.disabled=!canDraw();
  $('skip').disabled=!canDraw();
  $('drawing-status').textContent=canDraw()?'Draw the word. No letters or numbers.':data.phase==='drawing'?'Watch the drawing. Enter guesses in Game.':'Everyone has an artist in them.';
  const me=data.players.find(p=>p.ship===SELF),locked=data.phase!=='drawing'||isArtist()||me?.solved;
  $('guess').disabled=locked;$('guess-form').querySelector('button').disabled=locked||data.phase!=='drawing';
  $('guess').placeholder=data.phase!=='drawing'?'Guesses open when a round starts':isArtist()?'You’re drawing this turn':me?.solved?'You guessed it!':'Type your guess…';
  finale?.update(data,`${host}/${roomId}/${data.token}`);
  renderRoomMessages();
  $('skip').textContent=solved?'Done':'Skip';
  $('round-controls').dataset.done=String(solved);
  if(changedTurn)$('guess').value='';
  const doneDrawing=before?.players[0]?.ship===SELF&&before.phase==='drawing'&&(data.players[0]?.ship!==SELF||data.phase!=='drawing');
  updateDial();requestAnimationFrame(()=>{fitCanvas();if(doneDrawing||changedTurn&&data.phase==='drawing'&&!isArtist())focusGuess();});
}
function renderMessages(id,messages){
  const signature=JSON.stringify(messages);if(messageSignatures.get(id)===signature)return;messageSignatures.set(id,signature);
  const list=$(id),atBottom=list.scrollHeight-list.scrollTop-list.clientHeight<50;
  list.replaceChildren(...messages.map(m=>{
    const row=element('div',`message ${m.kind}`);if(m.who)row.append(element('b','',m.who+':'));
    if(m.kind==='game-result'){row.append(element('strong','',m.text));
    }else if(m.kind==='found-word'){
      const prefix='You found the word: ';row.append(document.createTextNode(prefix),element('strong','',m.text.slice(prefix.length)));
    }else if(m.kind==='round-result'){
      const match=m.text.match(/"([^"]+)"$/);
      if(match)row.append(document.createTextNode(m.text.slice(0,match.index+1)),element('strong','',match[1]),document.createTextNode('"'));
      else row.append(document.createTextNode(m.text));
    }else row.append(document.createTextNode(m.text));
    return row;
  }));if(atBottom)list.scrollTop=list.scrollHeight;
}
function updateDial() {
  const dial=$('timer-dial'), inactive=!state||['waiting','reveal','finished'].includes(state.phase);
  const duration=state?.duration || ({choosing:15,drawing:120,reveal:7}[state?.phase] || 120);
  const remaining=inactive?0:Math.max(0,clockSeconds-(performance.now()-clockAt)/1000);
  dial.style.setProperty('--sweep',`${Math.min(1,remaining/duration)*360}deg`);
  dial.classList.toggle('inactive',inactive);dial.classList.toggle('urgent',remaining<=20&&state?.phase==='drawing');
  dial.setAttribute('aria-valuemax',duration);dial.setAttribute('aria-valuenow',Math.ceil(remaining));
  const label=['reveal','finished'].includes(state?.phase)?'':inactive?'Waiting for players':`${Math.ceil(remaining)} seconds remaining`;
  dial.classList.toggle('blank',['reveal','finished'].includes(state?.phase));
  dial.setAttribute('aria-valuetext',label);$('timer-label').textContent=label;
}
setInterval(updateDial,100);
async function run(fn) {try {await fn();} catch(e) {toast(e.message || 'Something went wrong. Please try again.');}}
$('start').onclick=()=>run(()=>api.poke('start'));
$('give-hint').onclick=()=>run(async()=>{const button=$('give-hint');button.disabled=true;try{await api.poke('hint');}catch(e){if(state)renderRoom(state);throw e;}});
$('skip').onclick=()=>run(async()=>{await drawing.flushAll();await api.poke('skip');});
$('guess-form').onsubmit=event=>{event.preventDefault();const text=$('guess').value.trim();if(!text||state?.phase!=='drawing')return;const token=state.token;run(async()=>{await api.poke('guess',{text});if(state?.token===token&&$('guess').value.trim()===text)$('guess').value='';});};
$('chat-form').onsubmit=event=>{event.preventDefault();const text=$('chat-input').value.trim();if(!text)return;run(async()=>{await api.poke('chat',{text});if($('chat-input').value.trim()===text)$('chat-input').value='';selectChat('chat',true);});};
$('chat-messages').onclick=event=>{if(!event.target.closest('button,a')&&!getSelection()?.toString())selectChat('chat',true);};
$('host-form').onsubmit=event=>{event.preventDefault();run(()=>browse($('host').value.trim().toLowerCase()));};
$('create-open').onclick=()=>{$('create-error').hidden=true;$('create-dialog').showModal();};$('cancel-create').onclick=()=>$('create-dialog').close();
$('create-form').onsubmit=event=>{event.preventDefault();run(async()=>{
  const previous=host,id=`room-${crypto.randomUUID().slice(0,8)}`,button=$('create-form').querySelector('button.primary');button.disabled=true;$('create-error').hidden=true;
  try{await api.ensure();await api.poke('create',{title:$('title').value.trim()},{host:SELF,room:id});host=SELF;await joinRoom(id);$('create-dialog').close();}
  catch(e){$('create-error').textContent=e.message;$('create-error').hidden=false;if(!state){roomId='';host=previous;renderLobby(knownHosts.get(previous)?.data||{kind:'lobby',rooms:[]});}throw e;}
  finally{button.disabled=false;busyControls();}
});};
function localLeave(){showLobby({keepRoom:true});}
$('leave').onclick=()=>run(async()=>{await api.poke('leave');await api.unsubscribe(roomSub);localLeave();});
$('browser-help').onclick=()=>$('help-dialog').showModal();$('browser-settings').onclick=()=>$('settings-open').click();
$('help').onclick=()=>$('help-dialog').showModal();$('close-help').onclick=()=>$('help-dialog').close();
function renderProfiles(){$('profile-current').textContent=`Playing as ${activeName}`;}
function validPlayerName(name){return !!name&&!/[\u0000-\u001f\u007f]/.test(name)&&new TextEncoder().encode(name).length<=96;}
function rememberProfile(name){activeName=name;if(!profiles.includes(name))profiles.push(name);profiles=profiles.slice(-20);try{localStorage.setItem(profileKey,JSON.stringify({names:profiles,active:name}));}catch{}renderProfiles();}
$('player-name').value=SELF||'';
$('player-name').oninput=()=>{nameDraft=true;$('player-name').setCustomValidity('');$('connect-error').textContent='';};
$('profile-form').onsubmit=async event=>{
  event.preventDefault();const name=$('player-name').value.trim(),button=$('connect-submit');
  if(!validPlayerName(name)){$('player-name').setCustomValidity('Enter a display name using at most 96 bytes, without control characters.');$('player-name').reportValidity();return;}
  button.disabled=true;button.textContent='Connecting…';$('connect-error').textContent='';
  try{
    await characterReady;rememberCharacter(characterBuilder.value,true);
    await api.ensure();const previous=activeName;activeName=name;
    try{await api.poke('profile',{}, {host:SELF,room:''});}catch(error){activeName=previous;throw error;}
    rememberCharacter(characterBuilder.value,false);rememberProfile(name);location.assign('/apps/ursketch/play');
  }catch(error){$('connect-error').textContent=error.message||'Could not connect. Please try again.';button.disabled=false;button.textContent='Connect';}
};
function inspectPlayer(player){
  social?.inspect(player);
  $('player-profile-name').textContent=player.name||player.ship;$('player-profile-ship').textContent=player.ship;
  const button=$('warn-player');button.hidden=!state||player.ship===SELF||!state.players.some(p=>p.ship===player.ship);button.disabled=false;
  button.onclick=()=>run(async()=>{button.disabled=true;try{await api.poke('warn',{player:player.ship});$('player-profile-dialog').close();}finally{button.disabled=false;}});
  const remove=$('remove-player');remove.hidden=!state||state.owner!==SELF||player.ship===SELF||!state.players.some(p=>p.ship===player.ship);remove.disabled=false;
  remove.onclick=()=>run(async()=>{remove.disabled=true;try{await api.poke('kick',{player:player.ship});$('player-profile-dialog').close();}finally{remove.disabled=false;}});
  $('player-profile-dialog').showModal();
}
function installClassicScrollbars(){
  for(const id of ['players','messages','chat-messages','browser-guide','room-list']){
    const content=$(id),shell=element('div','classic-scroll-shell'),rail=element('div','classic-scrollbar');
    const up=element('button','scroll-up'),track=element('div','scroll-track'),thumb=element('div','scroll-thumb'),down=element('button','scroll-down');
    up.type=down.type='button';up.setAttribute('aria-label','Scroll up');down.setAttribute('aria-label','Scroll down');
    thumb.tabIndex=0;thumb.setAttribute('role','scrollbar');thumb.setAttribute('aria-orientation','vertical');thumb.setAttribute('aria-controls',id);thumb.setAttribute('aria-valuemin','0');
    content.before(shell);shell.append(content,rail);track.append(thumb);rail.append(up,track,down);
    function update(){
      if(!rail.offsetHeight)return;
      const max=Math.max(0,content.scrollHeight-content.clientHeight),size=Math.min(track.clientHeight,['browser-guide','room-list'].includes(id)?42:23);
      thumb.style.height=size+'px';thumb.style.top=(max?(track.clientHeight-size)*content.scrollTop/max:0)+'px';
      thumb.setAttribute('aria-valuemax',String(max));thumb.setAttribute('aria-valuenow',String(Math.round(content.scrollTop)));
    }
    let repeat=null;
    function stop(){clearInterval(repeat);repeat=null;}
    for(const [button,amount] of [[up,-17],[down,17]]){button.onclick=()=>{content.scrollTop+=amount;};button.onpointerdown=()=>{stop();repeat=setInterval(()=>{content.scrollTop+=amount;},80);};button.onpointerup=stop;button.onpointercancel=stop;button.onpointerleave=stop;}
    let drag=null;
    thumb.onpointerdown=e=>{e.preventDefault();thumb.focus({preventScroll:true});drag={y:e.clientY,top:content.scrollTop};thumb.setPointerCapture(e.pointerId);};
    thumb.onpointermove=e=>{if(!drag)return;const distance=Math.max(1,track.clientHeight-thumb.offsetHeight);content.scrollTop=drag.top+(e.clientY-drag.y)*(content.scrollHeight-content.clientHeight)/distance;};
    thumb.onpointerup=thumb.onpointercancel=thumb.onlostpointercapture=()=>{drag=null;};
    window.addEventListener('blur',()=>{stop();drag=null;});
    track.onpointerdown=e=>{if(e.target===track){content.scrollTop+=(e.clientY<thumb.getBoundingClientRect().top?-1:1)*content.clientHeight;}};
    thumb.onkeydown=e=>{const steps={ArrowUp:-17,ArrowDown:17,PageUp:-content.clientHeight,PageDown:content.clientHeight};if(e.key in steps){e.preventDefault();e.stopPropagation();content.scrollTop+=steps[e.key];}else if(e.key==='Home'||e.key==='End'){e.preventDefault();e.stopPropagation();content.scrollTop=e.key==='Home'?0:content.scrollHeight;}};
    let scrollbarFrame=null;const requestUpdate=()=>{if(scrollbarFrame!==null)return;scrollbarFrame=requestAnimationFrame(()=>{scrollbarFrame=null;update();});};
    content.addEventListener('scroll',requestUpdate,{passive:true});new ResizeObserver(requestUpdate).observe(content);new MutationObserver(requestUpdate).observe(content,{childList:true,subtree:true,characterData:true});
  }
}
function syncThemeLayout(){
  $('guess-form').querySelector('button').textContent=document.body.dataset.mobile==='true'?'Send':'↑';
  const classic=document.body.dataset.layout==='classic';
  for(const [id,anchor] of [['guess-form','guess-form-home'],['round-controls','round-controls-home']]){
    const target=classic?$('classic-left-controls'):$(anchor).parentElement;
    if($(id).parentElement!==target){if(classic)target.append($(id));else $(anchor).after($(id));}
  }
}
function fitCanvas(){const wrap=$('canvas').parentElement;if(!wrap.clientWidth||!wrap.clientHeight)return;const width=wrap.clientWidth,height=wrap.clientHeight;$('canvas').style.width=`${width}px`;$('canvas').style.height=`${height}px`;wrap.style.setProperty('--board-left','0px');wrap.style.setProperty('--board-top','0px');wrap.style.setProperty('--board-width',`${width}px`);drawing?.fit();}
new ResizeObserver(fitCanvas).observe($('canvas').parentElement);
try{const saved=JSON.parse(localStorage.getItem(profileKey)||'null');if(saved){profiles=(saved.names||[]).filter(n=>typeof n==='string'&&validPlayerName(n));if(profiles.includes(saved.active)){activeName=saved.active;hasLocalProfile=true;}}}catch{}
$('player-name').value=activeName;
characterBuilder=createCharacterBuilder({initial:activeCharacter,onChange:value=>rememberCharacter(value,true)});
characterReady=(async()=>{
  try{
    const response=await fetch('/apps/ursketch/profile',{signal:AbortSignal.timeout(10000)});if(!response.ok)return;
    const saved=await response.json();
    if(saved?.name&&!hasLocalProfile&&!nameDraft&&validPlayerName(saved.name)){rememberProfile(saved.name);$('player-name').value=saved.name;}
    if(saved?.avatar&&!hasLocalCharacter&&!characterDraft&&!characterBuilder.dirty){characterBuilder.restore(saved.avatar);rememberCharacter(saved.avatar,false);}
  }catch{}
})();
installClassicScrollbars();
const preferences=createSettings({notify:toast,onChange:prefs=>{if(lastTheme!==prefs.theme){drawing?.resetView();lastTheme=prefs.theme;}gameAudio?.settings();syncThemeLayout();requestAnimationFrame(fitCanvas);}});
if(!connectPage)gameAudio=createGameAudio({urls:URSKETCH_CUE_URLS,getPrefs:()=>preferences.values,notify:toast});
if(!connectPage)finale=createFinale({surface:$('canvas').parentElement,layer:$('game-finale'),getAudio:()=>gameAudio,getPrefs:()=>preferences.values,onEnd:()=>{if(state?.phase==='finished'){state={...state,celebrating:false,remainingMs:0,seconds:0};renderRoom(state);}}});
roomAdmin=createRoomAdmin({getState:()=>state,perform:(action,data)=>api.poke(action,data),notify:toast});
social=createSocial({self:SELF,coordinator:GLOBAL_CHAT_HOST,perform:(action,data)=>api.poke(action,data,{host:SELF,room:''},'ursketch-social'),subscribe:handler=>api.subscribe('/friends',handler,true,SELF,'ursketch-social'),unsubscribe:id=>api.unsubscribe(id),profile:()=>({name:activeName,avatar:activeCharacter}),inspect:inspectPlayer,notify:toast,join:async target=>{await browse(target.host);await joinRoom(target.room,'A Clean Slate');}});
renderProfiles();drawing=createDrawing({canvas:$('canvas'),colors,canDraw,send:(action,data)=>api.poke(action,action==='draw'&&roomStream?{encoding:1,lines:data.lines.map(l=>UrSketchWire.pack(l))}:data),error:e=>toast(e.message||String(e)),onDraw:dismissBanner,storageKey:`ursketch.palettes.${SELF}`});restoreRecovery();
if(!connectPage)run(async()=>{if(!SELF)throw new Error('Open urSketch through your Urbit ship at /apps/ursketch.');restoreKnownHosts();void connectGlobalChat();await api.ensure();void social.start();host=SELF;$('host').value='';history.replaceState(null,'',location.pathname);operation('browse-status','Search a ship to view its rooms.');$('room-list').replaceChildren(element('p','browser-empty','Search a ship to view rooms.'));busyControls();});
