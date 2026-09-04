# Hosting the scheduler on GitHub Actions

This repo posts automatically every Mon/Wed/Fri at 10:00 AM IST via
`.github/workflows/post.yml`. GitHub's servers have normal internet access,
so they can reach `difesasecurityservices.com` (unlike the Claude sandbox
this was built in) and every platform's API.

## 1. Create the repo

1. Go to https://github.com/new
2. Name it e.g. `difesa-social-autopost`
3. Set it to **Private** (it will hold your API credentials as encrypted
   Secrets — private just adds a second layer of caution)
4. Create it, then push this folder's contents to it:
   ```bash
   cd difesa_autopost
   git init
   git add .
   git commit -m "Initial commit — Difesa social autopost"
   git branch -M main
   git remote add origin https://github.com/<your-username>/difesa-social-autopost.git
   git push -u origin main
   ```
   (Use a GitHub Personal Access Token or `gh auth login` when it asks for
   a password — GitHub removed plain password pushes.)

## 2. Add your credentials as repo Secrets

Go to **Settings → Secrets and variables → Actions → New repository
secret** on your new repo, and add each of these (only add the ones for
platforms you're ready to enable — anything left unset just stays
disabled and is skipped by the run):

| Secret name | What it is |
|---|---|
| `FACEBOOK_ENABLED` | `true` to turn Facebook posting on |
| `FACEBOOK_PAGE_ID` | Difesa Facebook Page ID |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Long-lived Page Access Token (Graph API) |
| `INSTAGRAM_ENABLED` | `true` to turn Instagram posting on |
| `INSTAGRAM_IG_BUSINESS_ID` | Instagram Business Account ID |
| `INSTAGRAM_PAGE_ACCESS_TOKEN` | Same Page Access Token, with `instagram_business_content_publish` |
| `LINKEDIN_ENABLED` | `true` to turn LinkedIn posting on |
| `LINKEDIN_ORGANIZATION_URN` | e.g. `urn:li:organization:12345678` |
| `LINKEDIN_ACCESS_TOKEN` | OAuth token with `w_organization_social` |
| `GOOGLE_BUSINESS_PROFILE_ENABLED` | `true` to turn GBP posting on |
| `GBP_ACCOUNT_ID`, `GBP_LOCATION_ID`, `GBP_ACCESS_TOKEN`, `GBP_REFRESH_TOKEN`, `GBP_CLIENT_ID`, `GBP_CLIENT_SECRET` | From Google Cloud OAuth setup |
| `TWITTER_X_ENABLED` | `true` to turn X posting on (pay-per-post) |
| `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET` | From your X developer app |

You never need to edit `config.yaml` with real values — it stays a safe
template in the repo, and these Secrets override it at run time.

## 3. Test it

Go to the **Actions** tab → **Difesa Scheduled Social Post** → **Run
workflow**. Tick "Dry run" the first time to confirm it finds the image
and builds the caption without posting anywhere, then run it for real
once you're ready.

## 4. Let it run

Once secrets are set, no further action is needed — it fires automatically
every Monday, Wednesday, and Friday at 10:00 AM IST, checks that day's
photo is live, and posts to every enabled platform. Each run's result is
saved as a downloadable artifact on that run's Actions page.
