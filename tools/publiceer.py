"""Versleutel data.json en zet het als data.enc.json in de app-repository (via git).

Gebruik: python3 publiceer.py <data.json> "<code>" "<github-token>"
"""
import base64, json, os, subprocess, sys, tempfile
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    os.system(f"{sys.executable} -m pip install -q --break-system-packages cryptography")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

src, code, token = sys.argv[1], sys.argv[2], sys.argv[3]
url = f"https://x-access-token:{token}@github.com/MMaker-hue/Beurs-dag-bericht-.git"
data = json.load(open(src, encoding="utf-8"))
raw = json.dumps(data, ensure_ascii=False).encode("utf-8")

def versleutel():
    it = 250000
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(code.encode("utf-8"))
    b = lambda x: base64.b64encode(x).decode()
    return json.dumps({"v": 1, "iter": it, "salt": b(salt), "iv": b(iv), "ct": b(AESGCM(key).encrypt(iv, raw, None))})

def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)

d = tempfile.mkdtemp()
r = git("clone", "-q", "--depth", "1", url, d)
if r.returncode:
    print("app niet bijgewerkt: klonen mislukt"); sys.exit(1)
for poging in range(3):
    open(os.path.join(d, "data.enc.json"), "w").write(versleutel())
    git("add", "data.enc.json", cwd=d)
    git("-c", "user.name=Dagbericht", "-c", "user.email=dagbericht@users.noreply.github.com",
        "commit", "-q", "-m", f"Editie {data.get('datum', '')} {data.get('tijd', '')}".strip(), cwd=d)
    p = git("push", "-q", url, "HEAD:main", cwd=d)
    if p.returncode == 0:
        print("app bijgewerkt"); break
    git("fetch", "-q", "--depth", "1", url, "main", cwd=d)
    git("reset", "-q", "--hard", "FETCH_HEAD", cwd=d)
else:
    print("app niet bijgewerkt: push geweigerd"); sys.exit(1)
