# Admin security
- الإدارة الآن خلف `/admin/login`.
- غيّر `ADMIN_PASSWORD` قبل النشر.
- استخدم HTTPS.
- لا تضع API keys داخل التطبيق.
- في الإنتاج يُفضّل استبدال جلسات الذاكرة بـ Redis/DB sessions وإضافة 2FA وrate limiting.
