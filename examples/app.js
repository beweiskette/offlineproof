const broken=location.pathname.endsWith('/broken.html');
let notes=JSON.parse(localStorage.getItem('notes')||'[]');
function render(){const list=document.querySelector('#notes'); list.replaceChildren(); for(const note of notes){const li=document.createElement('li');li.textContent=note.text;list.append(li)}document.querySelector('#state').textContent=notes.some(n=>n.pending)?'pending':'synced';localStorage.setItem('notes',JSON.stringify(notes))}
document.querySelector('#add').onclick=()=>{const input=document.querySelector('#note');notes.push({id:crypto.randomUUID(),text:input.value,pending:!navigator.onLine});input.value='';render()};
let syncing=false;
async function sync(){
  if(syncing||!notes.some(n=>n.pending))return;
  syncing=true;
  try{
    const response=await fetch('ping.json',{cache:'no-store'});
    if(!response.ok)return;
    if(broken)notes=notes.concat(notes.filter(n=>n.pending).map(n=>({...n})));
    notes.forEach(n=>n.pending=false);render();
  }catch{
    // Network state may still be changing when an online event is delivered.
  }finally{syncing=false;}
}
window.addEventListener('online',sync);
// Recheck pending work after reload even if the browser delivers no online event.
setInterval(sync,250);
render();
navigator.serviceWorker.register('sw.js').then(()=>navigator.serviceWorker.ready).then(async()=>{if(!navigator.serviceWorker.controller){await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}))}document.querySelector('#ready').textContent='ready'});
