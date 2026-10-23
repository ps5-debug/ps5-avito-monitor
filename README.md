# PS5 Avito Telegram Monitor (prototype)

This GitHub Actions prototype checks an Avito search page on a schedule and sends Telegram notifications for newly detected PS5 listings.

## Setup
1. Create a Telegram bot using @BotFather and copy its token privately.
2. Open the bot in Telegram and send `/start`.
3. Obtain your numeric Telegram chat ID using a trusted Telegram bot or the Telegram Bot API. Do not share your bot token publicly.
4. Create a **public** GitHub repository (GitHub Actions minutes are generally free for public repositories).
5. Upload `monitor.py`, `requirements.txt`, and the `.github/workflows/monitor.yml` workflow file, preserving the `.github/workflows/` path.
6. In repository Settings → Secrets and variables → Actions, add repository secrets:
   - `TELEGRAM_BOT_TOKEN` = your BotFather token
   - `TELEGRAM_CHAT_ID` = your numeric chat ID
   - `SEARCH_URL` = the Avito search URL
7. Open Actions → Monitor Avito PS5 → Run workflow to test it.

## Limitations
- GitHub scheduled workflows are not guaranteed to start exactly on time. This schedule requests a run every 10 minutes.
- The first successful run only seeds the current listings, so it doesn't send a flood of existing ads.
- Avito may block automated requests, serve a challenge page, or change its markup. This script does not bypass anti-bot controls; it reports failures in the Actions logs.
- The parser is a best-effort prototype and may miss or misclassify listings. It does not guarantee that an ad is used; the search link should be configured with the used filter.
- Keep the bot token in GitHub Secrets. Never commit it into the code.
