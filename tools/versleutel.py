"""Versleutel data.json voor de app.

Gebruik: python3 tools/versleutel.py <pad/naar/data.json> "<code>" [uitvoer, standaard data.enc.json]
AES-256-GCM met een sleutel afgeleid van de code via PBKDF2-SHA256 (250.000 rondes).
"""
import base64, json, os, sys
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    os.system(f"{sys.executable} -m pip install -q --break-system-packages cryptography")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

src, code = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data.enc.json')
raw = json.dumps(json.load(open(src, encoding='utf-8')), ensure_ascii=False).encode('utf-8')
it = 250000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(code.encode('utf-8'))
ct = AESGCM(key).encrypt(iv, raw, None)
b = lambda x: base64.b64encode(x).decode()
json.dump({"v": 1, "iter": it, "salt": b(salt), "iv": b(iv), "ct": b(ct)}, open(out, 'w'))
print("versleuteld:", os.path.abspath(out))
