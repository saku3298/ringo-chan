/* りんごちゃん イラスト集ビューア */
// 指定された組み合わせを固定。右開き: 各ペアの先頭ページが右、次が左。
const cfg=document.getElementById('spread').dataset;
const groups=JSON.parse(cfg.groups);
const TOTAL=Number(cfg.total);
const BASE=cfg.base;
let index=0, portraitPage=0;
const spread=document.getElementById('spread');
const counter=document.getElementById('counter');
const isPortrait=()=>matchMedia('(max-width:650px) and (orientation:portrait)').matches;
function render(){
 const pages=groups[index], portrait=isPortrait();
 const selected=portrait?[pages[portraitPage]]:pages;
 spread.replaceChildren();
 spread.className=selected.length===2?'pair':'single';
 // ペアは左から2番目、1番目の順に配置（右開き）
 const visualOrder=selected.length===2?[selected[1],selected[0]]:selected;
 for(const n of visualOrder){
   const sheet=document.createElement('div');sheet.className='sheet';
   const img=document.createElement('img');
   img.src=BASE+'illustration-'+String(n).padStart(3,'0')+'.jpg';
   img.alt='イラスト集 '+n+'ページ';img.draggable=false;
   sheet.append(img);spread.append(sheet);
 }
 const shown=selected.join('・');
 counter.textContent=shown+' / '+TOTAL+'ページ';
 document.getElementById('prev').disabled=index===0&&(!portrait||portraitPage===0);
 document.getElementById('next').disabled=index===groups.length-1&&(!portrait||portraitPage===groups[index].length-1);
}
function go(direction){
 if(isPortrait()){
   let next=portraitPage+direction;
   if(next>=0&&next<groups[index].length){portraitPage=next;render();return}
 }
 const target=index+direction;
 if(target<0||target>=groups.length)return;
 index=target;
 portraitPage=isPortrait()&&direction<0?groups[index].length-1:0;
 render();
}
document.getElementById('prev').onclick=()=>go(-1);
document.getElementById('next').onclick=()=>go(1);
document.addEventListener('keydown',e=>{
 if(e.key==='ArrowLeft')go(1);
 if(e.key==='ArrowRight')go(-1);
});
let start=null;
spread.addEventListener('touchstart',e=>{
 if(e.touches.length!==1){start=null;return}
 start={x:e.touches[0].clientX,y:e.touches[0].clientY};
},{passive:true});
spread.addEventListener('touchend',e=>{
 if(!start||e.changedTouches.length!==1)return;
 const dx=e.changedTouches[0].clientX-start.x,dy=e.changedTouches[0].clientY-start.y;
 start=null;
 if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.4)go(dx>0?1:-1);
},{passive:true});
addEventListener('resize',()=>{portraitPage=0;render()});
render();
