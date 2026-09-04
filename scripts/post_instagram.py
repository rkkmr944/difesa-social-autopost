#!/usr/bin/env python3
"""
Post an image + caption to an Instagram Business account via the Graph API.

Instagram's Content Publishing API requires the image to be fetched by
Meta's servers from a PUBLIC URL (it will not accept a raw file upload) so
this script expects the image to already be hosted somewhere reachable
(e.g. your website's /social/ folder, or any public object storage) and
takes that URL directly.
"""
import time
import requests

GRAPH_VERSION = "v21.0"


def post_image(ig_business_id: str, access_token: str, image_url: str, caption: str) -> dict:
    base = f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_business_id}"

    # Step 1: create a media container
    create_resp = requests.post(
        f"{base}/media",
        data={"image_url": image_url, "caption": caption, "access_token": access_token},
        timeout=60,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    # Step 2: poll container status until FINISHED
    for _ in range(15):
        status_resp = requests.get(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        status_resp.raise_for_status()
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            break
        time.sleep(2)

    # Step 3: publish
    publish_resp = requests.post(
        f"{base}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=60,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ig-business-id", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("--image-url", required=True, help="Publicly reachable URL of the image")
    ap.add_argument("--caption", required=True)
    args = ap.parse_args()
    result = post_image(args.ig_business_id, args.token, args.image_url, args.caption)
    print(result)
