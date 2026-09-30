import os
import time
from typing import Dict, Any, Optional
import requests

API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

def publish_instagram_post(
    image_url: str,
    caption: str,
    ig_user_id: Optional[str] = None,
    access_token: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Publishes an image with caption to Instagram Business Account via Meta Graph API.
    Handles container creation, status polling, and media publishing.
    """
    if dry_run:
        print("[Publisher] DRY-RUN enabled: Simulating Instagram Graph API posting.")
        return {
            "status": "success",
            "mode": "dry-run",
            "media_id": "mock_instagram_media_id_123456789",
            "container_id": "mock_container_id_987654321",
            "permalink": "https://instagram.com/p/mock_post"
        }

    token = access_token or os.getenv("IG_ACCESS_TOKEN")
    user_id = ig_user_id or os.getenv("IG_USER_ID")

    if not token or not user_id or token == "your_long_lived_meta_graph_api_access_token":
        print("[Publisher] Meta Instagram Graph API credentials missing. Running in mock mode.")
        return {
            "status": "skipped",
            "mode": "mock",
            "message": "IG_ACCESS_TOKEN or IG_USER_ID not configured."
        }

    # Step 1: Create Media Container
    print(f"[Publisher] Step 1: Creating Instagram media container for account {user_id}...")
    container_url = f"{BASE_URL}/{user_id}/media"
    container_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }

    resp = requests.post(container_url, data=container_payload, timeout=30)
    resp_data = resp.json()

    if resp.status_code != 200 or "id" not in resp_data:
        raise RuntimeError(f"[Publisher] Error creating media container: {resp.status_code} - {resp_data}")

    container_id = resp_data["id"]
    print(f"[Publisher] Container created successfully. Container ID: {container_id}")

    # Step 2: Poll container status until ready (Meta processes external image asset)
    print("[Publisher] Step 2: Checking media container processing status...")
    status_url = f"{BASE_URL}/{container_id}"
    max_retries = 10
    
    for attempt in range(max_retries):
        status_resp = requests.get(
            status_url,
            params={"fields": "status_code,status", "access_token": token},
            timeout=20
        )
        status_data = status_resp.json()
        status_code = status_data.get("status_code")

        if status_code == "FINISHED":
            print("[Publisher] Media container ready for publishing.")
            break
        elif status_code == "ERROR":
            raise RuntimeError(f"[Publisher] Media container failed processing: {status_data}")
        elif status_code in ["IN_PROGRESS", "EXPIRED"] or not status_code:
            print(f"[Publisher] Waiting for processing... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(3)
        else:
            time.sleep(2)

    # Step 3: Publish Media Container
    print(f"[Publisher] Step 3: Publishing media container {container_id}...")
    publish_url = f"{BASE_URL}/{user_id}/media_publish"
    publish_payload = {
        "creation_id": container_id,
        "access_token": token
    }

    publish_resp = requests.post(publish_url, data=publish_payload, timeout=30)
    publish_data = publish_resp.json()

    if publish_resp.status_code != 200 or "id" not in publish_data:
        raise RuntimeError(f"[Publisher] Error publishing media container: {publish_resp.status_code} - {publish_data}")

    media_id = publish_data["id"]
    print(f"[Publisher] Post published successfully! Media ID: {media_id}")

    # Step 4: Fetch permalink
    permalink = None
    try:
        media_info_url = f"{BASE_URL}/{media_id}"
        info_resp = requests.get(media_info_url, params={"fields": "permalink", "access_token": token}, timeout=15)
        if info_resp.status_code == 200:
            permalink = info_resp.json().get("permalink")
            if permalink:
                print(f"[Publisher] Post URL: {permalink}")
    except Exception:
        pass

    return {
        "status": "success",
        "media_id": media_id,
        "container_id": container_id,
        "permalink": permalink
    }

if __name__ == "__main__":
    res = publish_instagram_post(
        image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
        caption="Test caption #blackmanin",
        dry_run=True
    )
    print(f"Result: {res}")
