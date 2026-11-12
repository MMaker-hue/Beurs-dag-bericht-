"""Versleutel data.json en zet het via de GitHub-API in de app (data.enc.json).

Gebruik: python3 publiceer.py <data.json> "<code>" "<github-token>"
Alleen standaardbibliotheek plus 'cryptography' (wordt zo nodig geïnstalleerd).
"""
import base64, json, os, sys, urllib.request, urllib.error
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    os.system(f"{sys.executable} -m pip install -q --break-system-packages cryptography")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

REPO = "MMaker-hue/Beurs-dag-bericht-"
PAD = "data.enc.json"
src, code, token = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(src, encoding="utf-8"))
raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
it = 250000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(code.encode("utf-8"))
b = lambda x: base64.b64encode(x).decode()
env = json.dumps({"v": 1, "iter": it, "salt": b(salt), "iv": b(iv), "ct": b(AESGCM(key).encrypt(iv, raw, None))}).encode()

def call(method, body=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{PAD}", method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "dagbericht"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

for poging in range(3):
    try:
        sha = call("GET")["sha"]
        call("PUT", {"message": f"Editie {data.get('datum', '')} {data.get('tijd', '')}".strip(),
                     "content": base64.b64encode(env).decode(), "sha": sha, "branch": "main"})
        print("app bijgewerkt"); break
    except urllib.error.HTTPError as e:
        if e.code == 409 and poging < 2: continue
        print("app niet bijgewerkt: HTTP", e.code); sys.exit(1)
