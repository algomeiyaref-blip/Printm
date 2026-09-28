# prinm0 — تشغيل من الهاتف فقط

هذه النسخة تجمع الواجهة والـ Backend في خدمة واحدة. بعد النشر تحصل على رابط واحد تفتحه من الهاتف:

- `/` = التطبيق
- `/admin` = لوحة الإدارة
- `/health` = فحص الخدمة

## المطلوب من الهاتف فقط
1. ارفع ملفات المشروع إلى GitHub من المتصفح.
2. اربط المستودع مع Railway.
3. أضف متغيرات البيئة في Railway:
   - OPENAI_API_KEY
   - OPENAI_MODEL
   - META_VERIFY_TOKEN
   - WHATSAPP_ACCESS_TOKEN
   - WHATSAPP_PHONE_NUMBER_ID
   - INSTAGRAM_ACCESS_TOKEN
   - INSTAGRAM_PAGE_ID
   - ADMIN_USER
   - ADMIN_PASSWORD
4. اعمل Deploy ثم افتح الرابط الناتج من الهاتف.
5. لإضافة التطبيق إلى شاشة الهاتف: من Chrome اختر «إضافة إلى الشاشة الرئيسية» إذا ظهر الخيار.

لا تضع مفاتيح API داخل ملفات HTML أو JavaScript أو داخل GitHub.
