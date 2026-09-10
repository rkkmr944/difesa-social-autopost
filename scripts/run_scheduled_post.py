#!/usr/bin/env python3
"""
Difesa Security — calendar-driven social post publisher.

Reads content_calendar.json, finds the entry for a given date (default:
today), checks that Kashyap has uploaded the matching photo to
https://difesasecurityservices.com/social/<date>.jpg via FTP, and — for
every platform enabled in config.yaml — posts that photo with that day's
caption and hashtags. No image generation, no local files: the image
already lives on the client's own website, and every platform that needs
a public URL (Instagram, Google Business Profile) or accepts one
(Facebook) is pointed straight at it.

If the image hasn't been uploaded yet, the run stops for that platform
and reports it clearly, rather than posting with a broken image or
silently skipping.

Usage:
    python3 run_scheduled_post.py                  # posts today's entry
    python3 run_scheduled_post.py --date 2026-09-07 # posts a specific date
    python3 run_scheduled_post.py --dry-run          # check only, don't post
"""
import argparse
import json
import os
import sys
from datetime import date as date_cls
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).parent.parent

# Maps each config.yaml field to the environment variable (GitHub Actions
# Secret) that overrides it at run time. config.yaml itself never needs to
# hold real credentials — leave it as the checked-in template and set these
# as repo Secrets instead. A platform is auto-enabled if its *_ENABLED env
# var is "true", regardless of what config.yaml says.
ENV_OVERRIDES = {
    "facebook": {
        "page_id": "FACEBOOK_PAGE_ID",
        "page_access_token": "FACEBOOK_PAGE_ACCESS_TOKEN",
    },
    "instagram": {
        "ig_business_id": "INSTAGRAM_IG_BUSINESS_ID",
        "page_access_token": "INSTAGRAM_PAGE_ACCESS_TOKEN",
    },
    "linkedin": {
        "organization_urn": "LINKEDIN_ORGANIZATION_URN",
        "access_token": "LINKEDIN_ACCESS_TOKEN",
    },
    "google_business_profile": {
        "account_id": "GBP_ACCOUNT_ID",
        "location_id": "GBP_LOCATION_ID",
        "access_token": "GBP_ACCESS_TOKEN",
        "refresh_token": "GBP_REFRESH_TOKEN",
        "client_id": "GBP_CLIENT_ID",
        "client_secret": "GBP_CLIENT_SECRET",
    },
    "twitter_x": {
        "api_key": "TWITTER_API_KEY",
        "api_secret": "TWITTER_API_SECRET",
        "access_token": "TWITTER_ACCESS_TOKEN",
        "access_token_secret": "TWITTER_ACCESS_TOKEN_SECRET",
    },
}


def load_calendar():
    with open(ROOT / "content_calendar.json") as f:
        return json.load(f)


def load_config(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)

    for section, fields in ENV_OVERRIDES.items():
        block = cfg.setdefault(section, {})
        for field, env_name in fields.items():
            val = os.environ.get(env_name)
            if val:
                block[field] = val
        enabled_env = os.environ.get(f"{section.upper()}_ENABLED")
        if enabled_env is not None:
            block["enabled"] = enabled_env.strip().lower() in ("1", "true", "yes")

    return cfg


def find_entry(calendar, target_date: str):
    for row in calendar:
        if row["date"] == target_date:
            return row
    return None


IMAGE_CHECK_HEADERS = {
    # Some hosts (Cloudflare, hosting-panel firewalls, etc.) block requests
    # whose User-Agent looks like a bot/script rather than a browser, and
    # will 403 a plain python-requests call even though the same URL loads
    # fine in an actual browser. Presenting a normal browser UA avoids that.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}


def image_is_live(image_url: str) -> bool:
    try:
        resp = requests.head(image_url, headers=IMAGE_CHECK_HEADERS, timeout=15, allow_redirects=True)
        if resp.status_code == 200:
            return True
        # some hosts don't support HEAD properly, or still block it; fall back to a light GET
        resp = requests.get(image_url, headers=IMAGE_CHECK_HEADERS, timeout=15, stream=True)
        if resp.status_code == 200:
            return True
        print(f"   (image check got HTTP {resp.status_code} for {image_url})")
        return False
    except requests.RequestException as e:
        print(f"   (image check raised {e!r} for {image_url})")
        return False


def build_caption(entry: dict) -> str:
    hashtags = " ".join(entry.get("hashtags", []))
    return f"{entry['caption']}\n\n{hashtags}".strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    ap.add_argument("--dry-run", action="store_true", help="check everything but don't post")
    args = ap.parse_args()

    target_date = args.date or date_cls.today().isoformat()
    calendar = load_calendar()
    entry = find_entry(calendar, target_date)

    if entry is None:
        print(f"No calendar entry for {target_date} (outside the 3-month plan, or a non-posting day).")
        sys.exit(0)

    cfg = load_config(args.config)
    caption = build_caption(entry)
    image_url = entry["image_url"]

    print(f"=== {target_date} ({entry['day']}) — {entry['theme']} ===")
    print(f"Headline: {entry['headline']}")
    print(f"Image expected at: {image_url}")

    image_ok = image_is_live(image_url)
    if not image_ok:
        print(f"\n⚠️  Image NOT found at {image_url}")
        print(f"   Upload the photo for this post ({entry['image_brief']}) to /social/{entry['image_filename']} "
              f"on difesasecurityservices.com before this runs, or as soon as possible after.")
        if not args.dry_run:
            # Still write a local record so nothing is silently lost.
            pass
    else:
        print("Image confirmed live and reachable.")

    print(f"\nCaption:\n{caption}\n")

    results = {"date": target_date, "image_ok": image_ok}

    if args.dry_run:
        print("Dry run — no posts made.")
        return

    if not image_ok:
        print("Skipping all platforms until the image is uploaded.")
        results["skipped"] = "image not live"
        _save_result(target_date, results)
        return

    # --- Facebook ---
    fb = cfg.get("facebook", {})
    if fb.get("enabled"):
        from post_facebook import post_photo_by_url
        try:
            r = post_photo_by_url(fb["page_id"], fb["page_access_token"], image_url, caption)
            results["facebook"] = {"ok": True, "response": r}
        except Exception as e:
            results["facebook"] = {"ok": False, "error": str(e)}
    else:
        results["facebook"] = {"ok": None, "note": "disabled/not configured"}

    # --- Instagram ---
    ig = cfg.get("instagram", {})
    if ig.get("enabled"):
        from post_instagram import post_image
        try:
            r = post_image(ig["ig_business_id"], ig["page_access_token"], image_url, caption)
            results["instagram"] = {"ok": True, "response": r}
        except Exception as e:
            results["instagram"] = {"ok": False, "error": str(e)}
    else:
        results["instagram"] = {"ok": None, "note": "disabled/not configured"}

    # --- LinkedIn ---
    li = cfg.get("linkedin", {})
    if li.get("enabled"):
        from post_linkedin_url import post_image_by_url
        try:
            r = post_image_by_url(li["organization_urn"], li["access_token"], image_url, caption)
            results["linkedin"] = {"ok": True, "response": r}
        except Exception as e:
            results["linkedin"] = {"ok": False, "error": str(e)}
    else:
        results["linkedin"] = {"ok": None, "note": "disabled/not configured"}

    # --- Google Business Profile ---
    gbp = cfg.get("google_business_profile", {})
    if gbp.get("enabled"):
        from post_google_business import refresh_access_token, create_post
        try:
            token = refresh_access_token(gbp["client_id"], gbp["client_secret"], gbp["refresh_token"])
            r = create_post(gbp["account_id"], gbp["location_id"], token,
                             entry["headline"] + " — " + entry.get("subhead", ""),
                             image_url, cta_url=cfg.get("brand", {}).get("website"))
            results["google_business_profile"] = {"ok": True, "response": r}
        except Exception as e:
            results["google_business_profile"] = {"ok": False, "error": str(e)}
    else:
        results["google_business_profile"] = {"ok": None, "note": "disabled/not configured"}

    # --- X / Twitter (still pay-per-post, off by default) ---
    tw = cfg.get("twitter_x", {})
    if tw.get("enabled"):
        from post_twitter_url import post_image_tweet_by_url
        try:
            r = post_image_tweet_by_url(tw["api_key"], tw["api_secret"], tw["access_token"],
                                         tw["access_token_secret"], image_url, caption[:280])
            results["twitter_x"] = {"ok": True, "response": r}
        except Exception as e:
            results["twitter_x"] = {"ok": False, "error": str(e)}
    else:
        results["twitter_x"] = {"ok": None, "note": "disabled (pay-per-post)"}

    _save_result(target_date, results)
    print(json.dumps(results, indent=2, default=str))
    failed = [p for p, r in results.items() if isinstance(r, dict) and r.get("ok") is False]
    if failed:
        print("FAILED platforms: " + ", ".join(failed) + " - see errors above / results.json")
        sys.exit(1)


def _save_result(target_date, results):
    out_dir = ROOT / "posts" / target_date
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
