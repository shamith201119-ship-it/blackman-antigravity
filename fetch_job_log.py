import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
repo = "shamith201119-ship-it/blackman-antigravity"
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

r = requests.get(f"https://api.github.com/repos/{repo}/actions/jobs/104495818265/logs", headers=headers)
with open("github_action_job.log", "w", encoding="utf-8") as f:
    f.write(r.text)

print("Saved job log, size:", len(r.text))
