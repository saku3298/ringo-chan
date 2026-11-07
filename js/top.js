/* りんごちゃん トップページ（タブ切り替え・話数の範囲と並べ替え・コミックスの並べ替え） */
(()=>{
const tabs=[...document.querySelectorAll('nav button[data-tab]')],panels=[...document.querySelectorAll('.panel')];
function openTab(id,hash=true){if(!panels.some(p=>p.id===id))id='episodes';tabs.forEach(t=>t.classList.toggle('active',t.dataset.tab===id));panels.forEach(p=>p.classList.toggle('active',p.id===id));if(hash)history.replaceState(null,'',id==='episodes'?location.pathname:'#'+id)}
tabs.forEach(t=>t.addEventListener('click',()=>openTab(t.dataset.tab)));
openTab(location.hash.slice(1)||'episodes',false);
addEventListener('hashchange',()=>openTab(location.hash.slice(1)||'episodes',false));
const PER=Number(document.getElementById('episodes').dataset.perRange)||50;
let currentEpisodeRange=[1,PER];
function applyEpisodeRange(){
  document.querySelectorAll('#episodes .episode-row[data-episode]').forEach(item=>{const n=Number(item.dataset.episode);item.hidden=n<currentEpisodeRange[0]||n>currentEpisodeRange[1]});
  document.querySelectorAll('.episode-range-btn').forEach(btn=>{const active=Number(btn.dataset.rangeStart)===currentEpisodeRange[0];btn.classList.toggle('active',active);btn.setAttribute('aria-pressed',String(active))});
}
function setOrder(kind,order){
  const section=document.getElementById(kind==='episode'?'episodes':'volumes');
  const selector=kind==='episode'?'.episode-row[data-episode]':'.entry[data-volume]';
  const attr=kind==='episode'?'episode':'volume';
  const items=Array.from(section.querySelectorAll(selector));
  if(!items.length)return;
  const parent=items[0].parentElement;
  items.sort((a,b)=>order==='asc'?Number(a.dataset[attr])-Number(b.dataset[attr]):Number(b.dataset[attr])-Number(a.dataset[attr]));
  items.forEach(item=>parent.appendChild(item));
  section.querySelectorAll('.sort-btn[data-sort="'+kind+'"]').forEach(btn=>{const active=btn.dataset.order===order;btn.classList.toggle('active',active);btn.setAttribute('aria-pressed',String(active))});
  if(kind==='episode'){
    // 「最新話から」は最新話を含む範囲へ移動する。
    if(order==='desc'){const latest=Math.max(...items.map(item=>Number(item.dataset.episode)));const first=Math.floor((latest-1)/PER)*PER+1;currentEpisodeRange=[first,first+PER-1]}
    else currentEpisodeRange=[1,PER];
    applyEpisodeRange();
  }
}
document.querySelectorAll('.sort-btn[data-sort]').forEach(btn=>btn.addEventListener('click',()=>setOrder(btn.dataset.sort,btn.dataset.order)));
document.querySelectorAll('.episode-range-btn').forEach(btn=>btn.addEventListener('click',()=>{currentEpisodeRange=[Number(btn.dataset.rangeStart),Number(btn.dataset.rangeEnd)];applyEpisodeRange()}));
})();
