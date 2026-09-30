import os
from typing import Optional

def upload_image(image_path: str, dry_run: bool = False) -> str:
    """
    Uploads an image to Cloudinary and returns the public secure HTTPS URL.
    In dry-run or unconfigured mode, returns a mock placeholder URL.
    """
    if dry_run:
        print("[Uploader] DRY-RUN enabled: Skipping Cloudinary network upload.")
        return "https://res.cloudinary.com/demo/image/upload/sample.jpg"

    cloudinary_url = os.getenv("CLOUDINARY_URL")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    # Verify if credentials exist
    has_creds = bool(cloudinary_url) or (cloud_name and api_key and api_secret)
    if not has_creds or (cloudinary_url and "cloudinary://<API_KEY>" in cloudinary_url):
        print("[Uploader] Cloudinary credentials missing or placeholder. Running in mock mode.")
        return "https://res.cloudinary.com/demo/image/upload/sample.jpg"

    try:
        import cloudinary
        import cloudinary.uploader

        if cloudinary_url:
            cloudinary.config(cloudinary_url=cloudinary_url)
        else:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )

        print(f"[Uploader] Uploading {image_path} to Cloudinary...")
        response = cloudinary.uploader.upload(
            image_path,
            folder="blackman_instagram_posts",
            resource_type="image",
            use_filename=True,
            unique_filename=True
        )

        secure_url = response.get("secure_url") or response.get("url")
        if not secure_url:
            raise ValueError(f"No URL in Cloudinary response: {response}")

        print(f"[Uploader] Successfully uploaded to Cloudinary: {secure_url}")
        return secure_url

    except Exception as e:
        print(f"[Uploader] Failed to upload image to Cloudinary: {e}")
        raise e

if __name__ == "__main__":
    url = upload_image("output/test_post.jpg", dry_run=True)
    print(f"Uploader output URL: {url}")
