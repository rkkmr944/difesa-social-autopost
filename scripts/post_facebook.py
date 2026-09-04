#!/usr/bin/env python3
"""Post a photo + caption to a Facebook Page via the Graph API."""
import sys
import requests

GRAPH_VERSION = "v21.0"


def _raise_with_fb_error(resp):
    """requests' raise_for_status() only gives a generic 'N Client Error' message,
    which hides Facebook's actual JSON error (type/message/code/error_subcode) —
    the part that actually explains WHY the call was rejected. Surface it."""
    if resp.ok:
        return
    try:
        detail = resp.json()
    except ValueError:
        detail = resp.text
    raise requests.HTTPError(f"{resp.status_code} {resp.reason} — Facebook error detail: {detail}", response=resp)


def post_photo(page_id: str, page_access_token: str, image_path: str, caption: str) -> dict:
    """Upload a local file directly."""
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/photos"
    with open(image_path, "rb") as f:
        files = {"source": f}
        data = {"caption": caption, "access_token": page_access_token}
        resp = requests.post(url, files=files, data=data, timeout=60)
    _raise_with_fb_error(resp)
    return resp.json()


def post_photo_by_url(page_id: str, page_access_token: str, image_url: str, caption: str) -> dict:
    """Post a photo Facebook fetches itself from a public URL (no local file needed)."""
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/photos"
    data = {"url": image_url, "caption": caption, "access_token": page_access_token}
    resp = requests.post(url, data=data, timeout=60)
    _raise_with_fb_error(resp)
    return resp.json()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--page-id", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--caption", required=True)
    args = ap.parse_args()
    result = post_photo(args.page_id, args.token, args.image, args.caption)
    print(result)
