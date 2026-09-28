# نشر prinm0

## Backend
Build:
`docker build -t prinm0-api ./backend`

Run with environment variables from `.env`.

Example:
`docker run --env-file ./backend/.env -p 8000:8000 prinm0-api`

Production:
- use HTTPS reverse proxy
- persistent database volume
- secret manager/environment variables
- authentication/rate limits/logging

## Android
On a development computer with Node.js and Android Studio:
1. `cd frontend`
2. `npm install`
3. `npx cap add android`
4. `npx cap sync android`
5. `npx cap open android`
6. Build a signed APK/AAB from Android Studio.

The mobile app must point `PRINM0_API` to the public HTTPS backend URL.
