#!/usr/bin/env python3
"""Post an image (by public URL) + caption to a LinkedIn Company Page."""
import requests

API_BASE = "https://api.linkedin.com/rest"
LI_VERSION = "202601"


def _headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def register_and_upload_image_from_url(org_urn: str, access_token: str, image_url: str) -> str:
    # Step 1: register upload
    init_resp = requests.post(
        f"{API_BASE}/images?action=initializeUpload",
        headers=_headers(access_token),
        json={"initializeUploadRequest": {"owner": org_urn}},
        timeout=60,
    )
    init_resp.raise_for_status()
    value = init_resp.json()["value"]
    upload_url = value["uploadUrl"]
    image_urn = value["image"]

    # Step 2: fetch the image bytes from the client's website, then upload to LinkedIn
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()

    up_resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {access_token}"},
        data=img_resp.content,
        timeout=120,
    )
    up_resp.raise_for_status()
    return image_urn


def post_image_by_url(org_urn: str, access_token: str, image_url: str, caption: str) -> dict:
    image_urn = register_and_upload_image_from_url(org_urn, access_token, image_url)

    body = {
        "author": org_urn,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {"media": {"id": image_urn}},
        "lifecycleState": "PUBLISHED",
    }

    resp = requests.post(f"{API_BASE}/posts", headers=_headers(access_token), json=body, timeout=60)
    resp.raise_for_status()
    return {"status": resp.status_code, "post_id_header": resp.headers.get("x-restli-id")}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--org-urn", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("--image-url", required=True)
    ap.add_argument("--caption", required=True)
    args = ap.parse_args()
    print(post_image_by_url(args.org_urn, args.token, args.image_url, args.caption))
