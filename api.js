const PRINM0_API = localStorage.getItem('prinm0_api') || window.location.origin;
async function askAI(message){
  const r=await fetch(PRINM0_API+'/chat',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({channel:'app',customer_id:'owner',message})});
  if(!r.ok) throw new Error('API error');
  return (await r.json()).reply;
}

async function prinm0Status(){
  const r=await fetch(PRINM0_API+'/config/status');
  return await r.json();
}
