# Beursdagbericht

Persoonlijke web-app (PWA) met het dagbericht beurs en economie.
De inhoud staat versleuteld in `data.enc.json` (AES-256-GCM, sleutel via PBKDF2 uit een code);
de app vraagt de code één keer en onthoudt hem op het toestel.

Bijwerken: `python3 tools/versleutel.py data.json "<code>"` en daarna `data.enc.json` committen.
