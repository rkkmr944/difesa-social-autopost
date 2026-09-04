#!/usr/bin/env python3
"""
Create a "What's New" post on a Google Business Profile location.

Note: Google Business Profile API access must be manually approved by
Google (see setup guide) before account_id/location_id calls will work.
"""
import requests

API_BASE = "https://mybusiness.googleapis.com/v4"


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def create_post(account_id: str, location_id: str, access_token: str,
                 summary: str, image_url: str, cta_url: str = None) -> dict:
    url = f"{API_BASE}/accounts/{account_id}/locations/{location_id}/localPosts"
    body = {
        "languageCode": "en-US",
        "summary": summary,
        "media": [{"mediaFormat": "PHOTO", "sourceUrl": image_url}],
        "topicType": "STANDARD",
    }
    if cta_url:
        body["callToAction"] = {"actionType": "LEARN_MORE", "url": cta_url}

    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--account-id", required=True)
    ap.add_argument("--location-id", required=True)
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    ap.add_argument("--refresh-token", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--image-url", required=True, help="Publicly reachable URL of the image")
    ap.add_argument("--cta-url", default=None)
    args = ap.parse_args()
    token = refresh_access_token(args.client_id, args.client_secret, args.refresh_token)
    result = create_post(args.account_id, args.location_id, token, args.summary, args.image_url, args.cta_url)
    print(result)
