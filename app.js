const modal=document.getElementById('screen');
function showScreen(name){
  if(name==='home'){modal.classList.add('hidden');return}
  modal.classList.remove('hidden');
  const title={chats:'المحادثات',orders:'الطلبات',settings:'الإعدادات'}[name]||'prinm0';
  modal.innerHTML=`<div class="panel"><button class="back" onclick="showScreen('home')">← رجوع</button><h1>${title}</h1>
  ${name==='chats'?'<div class="account"><div class="icon ai">✦</div><div><b>الرد الآلي</b><small>يمكن تفعيله بعد ربط الحسابات</small></div><span class="pill off">متوقف</span></div><div class="chat"><div class="avatar user">م</div><div class="chat-body"><b>محمد</b><p>أريد معرفة سعر المنتج</p></div></div>':
  name==='orders'?'<div class="account"><div><b>لا توجد طلبات حقيقية بعد</b><small>ستظهر الطلبات هنا بعد ربط WhatsApp/Instagram.</small></div></div>':
  '<div class="account"><div><b>إعدادات الذكاء الاصطناعي</b><small>أسلوب الرد: ودود واحترافي</small></div></div><div class="account"><div><b>الربط بالحسابات</b><small>WhatsApp Business • Instagram • OpenAI</small></div></div>'}</div>`;
}
function openChat(name,msg){
  modal.classList.remove('hidden');
  modal.innerHTML=`<div class="panel"><button class="back" onclick="showScreen('home')">← رجوع</button><h2>${name}</h2>
  <div class="msg">${msg}</div><div class="msg me">أهلاً بك 👋 يمكنني مساعدتك في معرفة السعر وتفاصيل الطلب.</div>
  <div class="input"><input placeholder="اكتب رسالة تجريبية"><button onclick="toast('الربط الحقيقي يحتاج إعداد API')">إرسال</button></div></div>`;
}
function toast(t){alert(t)}
if('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js');
