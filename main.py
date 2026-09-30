import os, sqlite3, json, secrets, hashlib
from typing import Optional
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_NAME = "prinm0"

load_dotenv()
app=FastAPI(title="prinm0 API", version="2.0")
@app.get("/debug/frontend", include_in_schema=False)
def debug_frontend():
    return {
        "main_file": os.path.abspath(__file__),
        "frontend_dir": os.path.abspath(FRONTEND_DIR),
        "index_html": os.path.exists(os.path.join(FRONTEND_DIR, "index.html")),
        "app_js": os.path.exists(os.path.join(FRONTEND_DIR, "app.js")),
        "app_v10_js": os.path.exists(os.path.join(FRONTEND_DIR, "app_v10.js")),
        "sw_js": os.path.exists(os.path.join(FRONTEND_DIR, "sw.js"))
         }
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_FRONTEND_CANDIDATES = [
    BASE_DIR,
    os.path.join(BASE_DIR, "frontend"),
    os.path.join(BASE_DIR, "..", "frontend"),
    "/app",
    "/app/frontend",
]

FRONTEND_DIR = BASE_DIR

for _candidate in _FRONTEND_CANDIDATES:
    _candidate = os.path.abspath(_candidate)
    if os.path.exists(os.path.join(_candidate, "index.html")):
        FRONTEND_DIR = _candidate
        break
DB="prinm0.db"
ADMIN_USER=os.getenv('ADMIN_USER','admin')
ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD','change-this-password')
SESSIONS=set()
def db():
    con=sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, customer_id TEXT,
      direction TEXT, text TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    con.execute("""CREATE TABLE IF NOT EXISTS customers(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT UNIQUE,
      instagram TEXT, notes TEXT DEFAULT '', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    con.execute("""CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price TEXT,
      stock INTEGER DEFAULT 0, description TEXT DEFAULT '', active INTEGER DEFAULT 1)""")
    con.execute("""CREATE TABLE IF NOT EXISTS orders(
      id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, total TEXT,
      status TEXT DEFAULT 'new', notes TEXT DEFAULT '',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    con.commit()
    return con

class ChatRequest(BaseModel):
    channel:str="test"
    customer_id:str="demo"
    message:str

class LoginRequest(BaseModel):
    username:str
    password:str

class CustomerIn(BaseModel):
    name:str
    phone:str=""
    instagram:str=""
    notes:str=""

class ProductIn(BaseModel):
    name:str
    price:str=""
    stock:int=0
    description:str=""

class OrderIn(BaseModel):
    customer_id:int|None=None
    total:str=""
    status:str="new"
    notes:str=""

async def ai_reply(message:str)->str:
    key=os.getenv("OPENAI_API_KEY")
    if not key:
        return "مرحباً 👋 نظام prinm0 جاهز. اربط مفتاح OpenAI في الخادم لتفعيل الرد الذكي."
    model=os.getenv("OPENAI_MODEL","gpt-5.6-mini")
    payload={"model":model,"input":[
      {"role":"system","content":"أنت مساعد خدمة عملاء باسم prinm0. أجب بالعربية باختصار واحتراف، ولا تخترع أسعاراً أو مخزوناً أو مواعيد. إذا لم تتوفر المعلومة اطلب من العميل التفاصيل أو حوّل المحادثة للموظف."},
      {"role":"user","content":message}
    ]}
    async with httpx.AsyncClient(timeout=45) as c:
        r=await c.post("https://api.openai.com/v1/responses",
          headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json=payload)
        r.raise_for_status()
        data=r.json()
    # Responses API returns output content; robust extraction:
    parts=[]
    for item in data.get("output",[]):
        for c in item.get("content",[]) or []:
            if c.get("type")=="output_text": parts.append(c.get("text",""))
    return "".join(parts).strip() or "أهلاً بك، كيف يمكنني مساعدتك؟"

@app.get("/health")
def health(): return {"app":"prinm0","status":"ok","version":"2.0"}


def require_admin(authorization: str|None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401,"Admin authentication required")
    token=authorization[7:]
    if token not in SESSIONS:
        raise HTTPException(401,"Invalid session")

@app.post("/admin/login")
def admin_login(req:LoginRequest):
    if not secrets.compare_digest(req.username, ADMIN_USER) or not secrets.compare_digest(req.password, ADMIN_PASSWORD):
        raise HTTPException(401,"Invalid credentials")
    token=secrets.token_urlsafe(32)
    SESSIONS.add(token)
    return {"token":token}

@app.post("/admin/logout")
def admin_logout(authorization: str|None=Header(default=None)):
    require_admin(authorization); SESSIONS.discard(authorization[7:])
    return {"ok":True}

@app.get("/admin/customers")
def customers(authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db()
    rows=con.execute("SELECT id,name,phone,instagram,notes,created_at FROM customers ORDER BY id DESC").fetchall(); con.close()
    return {"items":[dict(zip(["id","name","phone","instagram","notes","created_at"],r)) for r in rows]}

@app.post("/admin/customers")
def add_customer(x:CustomerIn,authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db()
    cur=con.execute("INSERT INTO customers(name,phone,instagram,notes) VALUES(?,?,?,?)",(x.name,x.phone,x.instagram,x.notes))
    con.commit(); ident=cur.lastrowid; con.close(); return {"id":ident}

@app.delete("/admin/customers/{item_id}")
def del_customer(item_id:int,authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db(); con.execute("DELETE FROM customers WHERE id=?",(item_id,)); con.commit(); con.close(); return {"ok":True}

@app.get("/admin/products")
def products(authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db()
    rows=con.execute("SELECT id,name,price,stock,description,active FROM products ORDER BY id DESC").fetchall(); con.close()
    return {"items":[dict(zip(["id","name","price","stock","description","active"],r)) for r in rows]}

@app.post("/admin/products")
def add_product(x:ProductIn,authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db()
    cur=con.execute("INSERT INTO products(name,price,stock,description) VALUES(?,?,?,?)",(x.name,x.price,x.stock,x.description))
    con.commit(); ident=cur.lastrowid; con.close(); return {"id":ident}

@app.delete("/admin/products/{item_id}")
def del_product(item_id:int,authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db(); con.execute("DELETE FROM products WHERE id=?",(item_id,)); con.commit(); con.close(); return {"ok":True}

@app.get("/admin/orders")
def orders(authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db()
    rows=con.execute("SELECT id,customer_id,total,status,notes,created_at FROM orders ORDER BY id DESC").fetchall(); con.close()
    return {"items":[dict(zip(["id","customer_id","total","status","notes","created_at"],r)) for r in rows]}

@app.post("/admin/orders")
def add_order(x:OrderIn,authorization: str|None=Header(default=None)):
    require_admin(authorization); con=db()
    cur=con.execute("INSERT INTO orders(customer_id,total,status,notes) VALUES(?,?,?,?)",(x.customer_id,x.total,x.status,x.notes))
    con.commit(); ident=cur.lastrowid; con.close(); return {"id":ident}

@app.patch("/admin/orders/{item_id}")
async def update_order(item_id:int, request:Request, authorization: str|None=Header(default=None)):
    require_admin(authorization); data=await request.json()
    con=db()
    if "status" in data: con.execute("UPDATE orders SET status=? WHERE id=?",(str(data["status"]),item_id))
    if "notes" in data: con.execute("UPDATE orders SET notes=? WHERE id=?",(str(data["notes"]),item_id))
    con.commit(); con.close(); return {"ok":True}


@app.get("/", include_in_schema=False)
def frontend_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/admin", include_in_schema=False)
def frontend_admin():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))

@app.get("/webhook")
async def verify_webhook(request:Request):
    q=request.query_params
    mode=q.get("hub.mode"); token=q.get("hub.verify_token"); challenge=q.get("hub.challenge")
    if mode=="subscribe" and token==os.getenv("META_VERIFY_TOKEN"):
        return PlainTextResponse(challenge or "")
    raise HTTPException(403,"Webhook verification failed")

@app.post("/webhook")
async def webhook(request:Request):
    body=await request.json()
    # Store raw webhook safely; channel-specific handlers can be added as credentials are configured.
    con=db()
    try:
        # WhatsApp-style extraction
        for entry in body.get("entry",[]):
            for change in entry.get("changes",[]):
                value=change.get("value",{})
                for msg in value.get("messages",[]) or []:
                    text=(msg.get("text") or {}).get("body","")
                    sender=msg.get("from","")
                    if text:
                        con.execute("INSERT INTO messages(channel,customer_id,direction,text) VALUES(?,?,?,?)",
                                    ("whatsapp",sender,"in",text))
        con.commit()
    finally: con.close()
    return {"received":True}

@app.post("/chat")
async def chat(req:ChatRequest):
    con=db()
    con.execute("INSERT INTO messages(channel,customer_id,direction,text) VALUES(?,?,?,?)",
                (req.channel,req.customer_id,"in",req.message))
    con.commit(); con.close()
    reply=await ai_reply(req.message)
    con=db()
    con.execute("INSERT INTO messages(channel,customer_id,direction,text) VALUES(?,?,?,?)",
                (req.channel,req.customer_id,"out",reply))
    con.commit(); con.close()
    return {"reply":reply}

@app.get("/messages")
def messages(limit:int=50):
    con=db()
    rows=con.execute("SELECT id,channel,customer_id,direction,text,created_at FROM messages ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    con.close()
    return {"messages":[dict(zip(["id","channel","customer_id","direction","text","created_at"],r)) for r in rows]}


async def send_whatsapp_text(to: str, text: str):
    token=os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    if not token or not phone_id:
        return {"sent":False,"reason":"WhatsApp credentials are not configured"}
    url=f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    payload={"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text}}
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.post(url,headers={"Authorization":f"Bearer {token}"},json=payload)
    if r.status_code >= 400:
        return {"sent":False,"status":r.status_code,"detail":r.text[:500]}
    return {"sent":True,"data":r.json()}

@app.post("/whatsapp/send")
async def whatsapp_send(req:ChatRequest):
    reply=await ai_reply(req.message)
    result=await send_whatsapp_text(req.customer_id, reply)
    return {"reply":reply, "delivery":result}

@app.get("/config/status")
def config_status():
    return {
      "app":"prinm0",
      "openai":bool(os.getenv("OPENAI_API_KEY")),
      "whatsapp":bool(os.getenv("WHATSAPP_ACCESS_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID")),
      "instagram":bool(os.getenv("INSTAGRAM_ACCESS_TOKEN") and os.getenv("INSTAGRAM_PAGE_ID")),
      "webhook_verify":bool(os.getenv("META_VERIFY_TOKEN"))
    }


@app.get("/admin/summary")
def admin_summary():
    con=db()
    count=con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    incoming=con.execute("SELECT COUNT(*) FROM messages WHERE direction='in'").fetchone()[0]
    outgoing=con.execute("SELECT COUNT(*) FROM messages WHERE direction='out'").fetchone()[0]
    con.close()
    return {"messages":count,"incoming":incoming,"outgoing":outgoing}

@app.get("/admin/settings")
def admin_settings():
    return {"auto_reply":True,"human_handoff":True,"language":"ar","tone":"friendly_professional"}

# Serve the phone web app from the same service so the user only needs one URL.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
