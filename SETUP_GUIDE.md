# Difesa Security — Social Auto-Post: Setup Guide

## How this works now

You upload real photos, I write and schedule real posts. No AI-generated
graphics — every post uses an actual photo of your team, sites, or work,
matched to a 3-month content calendar already written for Difesa.

1. **`content_calendar.json` / `content_calendar.csv`** — the full plan:
   39 posts, 3× a week (Mon/Wed/Fri), September 7 – December 4, 2026.
   Every entry has a date, theme, headline, full caption, hashtags, and
   an **image_brief** telling you exactly what kind of photo to upload
   (e.g. "Photo of a Difesa guard at an apartment/gated community entrance").
   Open the `.csv` in Excel or Google Sheets to browse or edit any of it.

2. **You upload one photo per post date** to your own website via FTP,
   named by date: `https://difesasecurityservices.com/social/2026-09-07.jpg`,
   `2026-09-10.jpg`, `2026-09-14.jpg`, and so on — one file per scheduled
   date, matching the `image_filename` column in the calendar. Upload a
   few posts ahead of time whenever convenient; there's no rush to do all
   39 at once.

3. **Every Monday, Wednesday, and Friday at 10:00 AM IST**, the scheduled
   run automatically:
   - looks up that day's entry in the calendar
   - checks whether `https://difesasecurityservices.com/social/<date>.jpg` is live
   - if yes: posts that photo with that day's caption + hashtags to every
     platform you've enabled in `config.yaml`
   - if no: skips posting and tells you exactly which photo is still needed,
     so you know what to upload before (or right after) that day

No image generation, no separate hosting step — the photo already lives on
your own website, which is also what Instagram and Google Business Profile
require (a public image URL, not a file upload).

## Platform status

### Facebook — in progress, further along than the rest
Your existing Meta app ("DIFESA SECURITY SERVICES") now has the Pages
use case added, and a Page Access Token with `pages_manage_posts` and
`pages_read_engagement` is ready. One thing is still needed before this
can go fully live: Meta requires **one real successful post** through
the API before the formal App Review submission can proceed (their
checklist: Business Verification ✅ done, Access verification, App
Review, 1 successful API call, Data handling questions — all still
pending except verification). That first live post can simply be
Monday's scheduled post, so no separate test post is needed — once
Monday's run succeeds, that requirement is satisfied and I'll move the
App Review submission forward (I'll show you the demo/answers before
submitting anything to Meta).

### Instagram — needs Meta Business verification
Same underlying app as Facebook. Requires Meta to verify Difesa's
business documents before `instagram_content_publish` unlocks — can take
days to a couple of weeks. I'll start this once Facebook's review is
underway.

### LinkedIn — free, self-serve, not started yet
Apply for the Community Management API at developer.linkedin.com — open
to all developers, no partnership needed. Needs admin rights on the
Difesa LinkedIn Company Page.

### Google Business Profile — free, approval required
Google's own approval process (Difesa's listing already meets the 60+
day verification and website requirements). Apply via Google's request
form; approval timing is outside our control.

### X / Twitter — not free as of 2026
X's API is pay-per-request (~$0.015/post) with no free tier. Left
disabled by default — post manually to X for now, or say the word if you
want it wired in and are fine with the small per-post cost.

## How to fill in credentials

Edit `config.yaml`: paste each platform's token/ID into its section and
set `enabled: true`. Nothing posts to a platform until both are done —
everything else just gets skipped and reported each run.

## Files in this project

```
difesa_autopost/
├── config.yaml                 # live tokens — keep private
├── content_calendar.json       # machine-readable 3-month plan
├── content_calendar.csv        # human-readable — open in Excel/Sheets
├── SETUP_GUIDE.md               # this file
├── requirements.txt
└── scripts/
    ├── run_scheduled_post.py    # the orchestrator — runs Mon/Wed/Fri
    ├── generate_calendar.py     # regenerates the calendar (only if you want to rebuild it)
    ├── post_facebook.py
    ├── post_instagram.py
    ├── post_linkedin_url.py
    ├── post_google_business.py
    └── post_twitter_url.py      # off by default (paid API)
```

## Editing the calendar

To change a post's copy, photo brief, or swap the order: edit
`content_calendar.csv` in Excel/Sheets, then tell me to regenerate
`content_calendar.json` from it (or send me the edited file and I'll do
it) — the scheduled run always reads the `.json` file.
