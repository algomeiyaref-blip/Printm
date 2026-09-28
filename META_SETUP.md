# prinm0 — Meta connection setup

## WhatsApp
Use Meta's WhatsApp Business Platform / Cloud API for a business number.
Create an app in Meta for Developers, add WhatsApp, obtain the Phone Number ID
and a long-lived/system-user access token, then put them in the backend `.env`.

Variables:
- WHATSAPP_ACCESS_TOKEN
- WHATSAPP_PHONE_NUMBER_ID
- META_VERIFY_TOKEN

Set the callback URL to:
`https://YOUR-DOMAIN/webhook`

The GET webhook verifies Meta's challenge. POST webhook receives incoming
events and stores text messages. The backend can generate an AI reply and the
`/whatsapp/send` endpoint can send a text response.

## Instagram
Use an Instagram Professional account connected through Meta's ecosystem.
Configure the required Instagram messaging permissions in Meta for Developers.
Put the resulting token/page identifier in:
- INSTAGRAM_ACCESS_TOKEN
- INSTAGRAM_PAGE_ID

The exact permissions and review requirements depend on the Meta app/account
configuration. Do not place access tokens in the Android app.

## Security
- HTTPS is required in production.
- Add authentication for all owner/admin endpoints.
- Validate Meta webhook signatures before processing production traffic.
- Rotate/revoke tokens if exposed.
- Keep `.env` out of Git.
