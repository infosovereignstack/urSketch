/* Saved characters use stable part IDs, never positions in a menu. */
const CHARACTER_CATALOG=URSKETCH_CHARACTER_CATALOG;
const characterParts=['body','face','hat'];
function normalizeCharacter(value){
  return Object.fromEntries(characterParts.map(part=>[part,typeof value?.[part]==='string'&&/^[a-z0-9-]{1,40}$/.test(value[part])?value[part]:CHARACTER_CATALOG.defaults[part]]));
}
function createCharacter(value,{className='',label='Player character'}={}){
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox',CHARACTER_CATALOG.viewBox.join(' '));svg.setAttribute('preserveAspectRatio','xMidYMid meet');svg.classList.add('cat-character');if(className)svg.classList.add(className);svg.setAttribute('role','img');svg.setAttribute('aria-label',label);
  const selected=normalizeCharacter(value);
  for(const part of characterParts){
    const choices=CHARACTER_CATALOG.parts[part],entry=choices.find(v=>v.id===selected[part])||choices.find(v=>v.id===CHARACTER_CATALOG.defaults[part]);
    if(!entry?.url)continue;
    const image=document.createElementNS('http://www.w3.org/2000/svg','image');
    for(const name of ['x','y','width','height'])image.setAttribute(name,String(entry[name]));image.setAttribute('href',entry.url);image.dataset.part=part;image.dataset.partId=entry.id;svg.append(image);
  }
  return svg;
}
function createCharacterBuilder({initial,onChange}){
  let value=normalizeCharacter(initial),dirty=false;
  const stage=document.getElementById('character-preview'),status=document.getElementById('character-status');
  function render(){
    stage.replaceChildren(createCharacter(value,{label:'Your character preview'}));
    for(const part of characterParts){const entry=CHARACTER_CATALOG.parts[part].find(p=>p.id===value[part]);document.getElementById('character-'+part+'-value').textContent=entry?.label||'Saved option (unavailable)';}
  }
  for(const button of document.querySelectorAll('[data-character-part]'))button.onclick=()=>{
    const part=button.dataset.characterPart,choices=CHARACTER_CATALOG.parts[part],i=choices.findIndex(p=>p.id===value[part]),step=Number(button.dataset.step);
    const next=i<0?(step>0?0:choices.length-1):(i+step+choices.length)%choices.length;
    value={...value,[part]:choices[next].id};dirty=true;render();status.textContent=`${part}: ${choices.find(p=>p.id===value[part]).label}`;onChange?.({...value});
  };
  render();return{get value(){return{...value};},get dirty(){return dirty;},restore(next){if(dirty)return;value=normalizeCharacter(next);render();}};
}
