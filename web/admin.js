/* Room-owner actions are validated again by the hosting ship. */
function createRoomAdmin({getState,perform,notify}){
  const $=id=>document.getElementById(id),dialog=$('admin-dialog');let signature='',busy=false;
  const choices=[['default','Default'],['easy','Easy'],['hard','Hard'],['urbit','Urbit Words'],['milady','Milady Words']];
  const lorem='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae erat at neque interdum facilisis. Sed posuere, arcu quis commodo tincidunt, justo urna consequat velit, vitae aliquet nisl augue quis ipsum.';
  function row(id,label,disabled=false){const item=document.createElement('div');item.className='word-list-row';const check=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.value=id;input.disabled=disabled;check.append(input,document.createTextNode(label+(disabled?' (placeholder)':'')));const info=document.createElement('details'),summary=document.createElement('summary'),text=document.createElement('p');summary.textContent='i';summary.setAttribute('aria-label','About '+label);text.textContent=lorem;info.append(summary,text);item.append(check,info);return item;}
  for(const [id,label] of choices)$('admin-word-lists').append(row(id,label,id==='milady'));
  $('admin-word-lists').append(row('custom','Custom word list'));
  $('admin-open').onclick=()=>{signature='';render(getState());dialog.showModal();};
  $('admin-close').onclick=()=>dialog.close();
  $('admin-length').onchange=()=>{$('admin-custom-length').hidden=$('admin-length').value!=='custom';};
  $('admin-reset-timer').onclick=()=>act('reset-timer');
  async function act(action,data={}){if(busy)return;busy=true;$('admin-status').textContent='Applying…';try{await perform(action,data);$('admin-status').textContent=action==='reset-timer'?'Timer reset to the full round length.':'Room settings saved.';}catch(e){$('admin-status').textContent=e.message;}finally{busy=false;render(getState());}}
  $('admin-form').onsubmit=event=>{
    event.preventDefault();const state=getState();if(!state?.admin||busy)return;
    const seconds=Number($('admin-length').value==='custom'?$('admin-seconds').value:$('admin-length').value);
    if(!Number.isInteger(seconds)||seconds<10||seconds>600){$('admin-status').textContent='Choose a round length from 10 to 600 seconds.';return;}
    const enabled=[...$('admin-word-lists').querySelectorAll('input:checked')].map(e=>e.value==='custom'?$('admin-custom-list').value:e.value).filter(Boolean);
    if(!enabled.length){$('admin-status').textContent='Select at least one available word list.';return;}
    const overrides=new Map((state.admin.individual||[]).map(p=>[p.ship,p.difficulty]));
    for(const select of $('admin-players').querySelectorAll('select')){if(select.value==='inherit')overrides.delete(select.dataset.ship);else overrides.set(select.dataset.ship,select.value);}
    act('admin',{seconds,difficulty:$('admin-difficulty').value,enabled,individual:[...overrides].map(([ship,difficulty])=>({ship,difficulty}))});
  };
  $('admin-word-file').onchange=async event=>{
    const file=event.target.files[0];if(!file||busy)return;
    try{
      if(!/\.md$/i.test(file.name)||file.size>256*1024)throw new Error('Choose a Markdown (.md) file up to 256 KB.');
      const words=parseWordList(await file.text());if(words.length<101||words.length>5000)throw new Error('Use 101–5,000 unique words so the last 100 words can stay excluded.');
      const id='custom-'+(file.name.replace(/\.md$/i,'').toLowerCase().replace(/[^a-z0-9-]+/g,'-').replace(/^-+|-+$/g,'').slice(0,30)||'words');
      await act('custom-words',{list:id,words});
    }catch(e){$('admin-status').textContent=e.message;}finally{event.target.value='';}
  };
  function render(state){
    const allowed=!!state&&state.owner===window.URSKETCH_SHIP&&!!state.admin;$('admin-open').hidden=!allowed;document.body.classList.toggle('room-owner',allowed);
    if(!allowed){if(dialog.open)dialog.close();return;}
    $('admin-reset-timer').disabled=state.phase!=='drawing'||busy;
    const next=JSON.stringify([state.admin,state.players.map(p=>[p.ship,p.name])]);if(next===signature)return;signature=next;
    const a=state.admin,standard=[120,150,180].includes(a.seconds);$('admin-length').value=standard?String(a.seconds):'custom';$('admin-seconds').value=a.seconds;$('admin-custom-length').hidden=standard;$('admin-difficulty').value=a.difficulty;
    for(const input of $('admin-word-lists').querySelectorAll('input'))input.checked=a.enabled.includes(input.value)||input.value==='custom'&&a.enabled.some(id=>id.startsWith('custom-'));
    const select=$('admin-custom-list');select.replaceChildren(...(a.custom||[]).map(list=>new Option(`${list.id.slice(7)} (${list.count} words)`,list.id)));select.disabled=!select.options.length;
    const selected=a.enabled.find(id=>id.startsWith('custom-'));if(selected)select.value=selected;
    document.querySelector('#admin-word-lists input[value=custom]').disabled=!select.options.length;
    const overrides=new Map((a.individual||[]).map(p=>[p.ship,p.difficulty]));
    $('admin-players').replaceChildren(...state.players.map(p=>{const label=document.createElement('label');label.textContent=p.name||p.ship;label.title=p.ship;const choice=document.createElement('select');choice.dataset.ship=p.ship;for(const [id,name] of [['inherit','Use room difficulty'],['default','Selected word lists'],['easy','Easy'],['hard','Hard']])choice.add(new Option(name,id));choice.value=overrides.get(p.ship)||'inherit';label.append(choice);return label;}));
  }
  return {render};
}
function parseWordList(markdown){
  const words=[];let fenced=false;
  for(let line of markdown.replace(/^\uFEFF/,'').split(/\r?\n/)){
    if(/^\s*```/.test(line)){fenced=!fenced;continue;}if(fenced||/^\s*(#|>|<!--|---|\|)/.test(line)||!line.trim())continue;
    line=line.trim().replace(/^(?:[-*+]\s+(?:\[[ xX]\]\s*)?|\d+[.)]\s+)/,'').replace(/^`(.+)`$/,'$1').toLowerCase();
    if(line.length>64||/[^\x20-\x7e]/.test(line))throw new Error('Each word must be 1–64 plain-text characters, one word or phrase per line.');
    if(line)words.push(line);
  }
  return [...new Set(words)];
}
