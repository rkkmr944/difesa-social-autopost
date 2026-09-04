#!/usr/bin/env python3
"""
Post an image (fetched from a public URL) + caption to X (Twitter).
Still pay-per-post as of 2026 — off by default in config.yaml.
"""
import requests
from requests_oauthlib import OAuth1

UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWEET_URL = "https://api.twitter.com/2/tweets"


def post_image_tweet_by_url(api_key, api_secret, access_token, access_token_secret,
                             image_url: str, text: str) -> dict:
    auth = OAuth1(api_key, api_secret, access_token, access_token_secret)

    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()

    media_resp = requests.post(UPLOAD_URL, auth=auth, files={"media": img_resp.content}, timeout=60)
    media_resp.raise_for_status()
    media_id = media_resp.json()["media_id_string"]

    tweet_resp = requests.post(
        TWEET_URL, auth=auth,
        json={"text": text, "media": {"media_ids": [media_id]}},
        timeout=60,
    )
    tweet_resp.raise_for_status()
    return tweet_resp.json()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--api-secret", required=True)
    ap.add_argument("--access-token", required=True)
    ap.add_argument("--access-token-secret", required=True)
    ap.add_argument("--image-url", required=True)
    ap.add_argument("--text", required=True)
    args = ap.parse_args()
    print(post_image_tweet_by_url(args.api_key, args.api_secret, args.access_token,
                                   args.access_token_secret, args.image_url, args.text))
