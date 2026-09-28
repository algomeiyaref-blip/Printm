# prinm0 Backend v2

## تشغيل محلي
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Termux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API
- GET /health
- POST /chat
- GET /messages
- GET/POST /webhook

## الربط الحقيقي
- Meta Webhooks يرسل الرسائل إلى `/webhook`.
- OPENAI_API_KEY يبقى في الخادم فقط.
- WHATSAPP_ACCESS_TOKEN وINSTAGRAM_ACCESS_TOKEN تبقى في الخادم.
- لا تضع أي Token في HTML/JS أو APK.

قبل الإنتاج يجب إضافة مصادقة للوحة الإدارة، HTTPS، تشفير/حماية الأسرار، rate limiting، والتحقق من توقيع Webhook.
