import os
import base64
import requests
from nacl import encoding, public
from dotenv import load_dotenv

load_dotenv()

PAT = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_MEDIA_REPO", "shamith201119-ship-it/blackman-antigravity")

headers = {
    "Authorization": f"Bearer {PAT}",
    "Accept": "application/vnd.github+json"
}

# 1. Fetch repo public key
print(f"Fetching public key for {REPO}...")
r_pk = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=headers)
if r_pk.status_code != 200:
    print(f"Failed to fetch public key: {r_pk.status_code} - {r_pk.text}")
    exit(1)

pk_data = r_pk.json()
key_id = pk_data["key_id"]
public_key_b64 = pk_data["key"]

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

secrets_to_set = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY"),
    "BUFFER_ACCESS_TOKEN": os.getenv("BUFFER_ACCESS_TOKEN"),
    "BUFFER_CHANNEL_ID": os.getenv("BUFFER_CHANNEL_ID"),
    "BUFFER_PROFILE_NAME": os.getenv("BUFFER_PROFILE_NAME", "blackman_officialpage"),
    "GITHUB_TOKEN": PAT,
    "GH_PAT": PAT,
    "GITHUB_MEDIA_REPO": REPO,
}

print(f"Configuring {len(secrets_to_set)} GitHub repository secrets...")

for name, val in secrets_to_set.items():
    if not val:
        print(f"Skipping {name}: empty value")
        continue
    
    enc_val = encrypt_secret(public_key_b64, val)
    put_url = f"https://api.github.com/repos/{REPO}/actions/secrets/{name}"
    payload = {
        "encrypted_value": enc_val,
        "key_id": key_id
    }
    r = requests.put(put_url, json=payload, headers=headers)
    if r.status_code in [201, 204]:
        print(f"  [SUCCESS] Secret '{name}' configured successfully in GitHub Actions!")
    else:
        print(f"  [FAILED] Secret '{name}': {r.status_code} - {r.text}")

# Verify
r_check = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets", headers=headers)
print("Configured secrets:", [s["name"] for s in r_check.json().get("secrets", [])])
