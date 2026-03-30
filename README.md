# BMS MI vs RCB Ticket Checker

Automatically checks BookMyShow every 10 minutes for **MI vs RCB (April 12, 2026)** ticket availability and sends a Discord notification the moment they go live.

Runs entirely free on **GitHub Actions** — no server, no laptop needed.

---

## Notifications

**Every run (heartbeat):** Lets you know the bot is alive and what status it detected.
```
🤖 BMS Checker: Still watching
Status: No tickets yet — Unavailability signal found: 'Sold Out'
Checked at: 30 Mar 2026, 10:00 AM IST
```

**When tickets open:**
```
🚨 MI vs RCB Tickets AVAILABLE on BookMyShow!
👉 Book Now on BookMyShow  ← direct link
```

---

## Setup (5 minutes)

### Step 1: Create the GitHub repo

1. Go to [github.com/new](https://github.com/new)
2. Create a **private** repo (e.g. `bms-ticket-checker`)
3. Push this folder's contents to it:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/bms-ticket-checker.git
git push -u origin main
```

---

### Step 2: Create a Discord Webhook

1. Open a Discord server you own (or create a personal one)
2. Click the gear icon on any text channel → **Integrations** → **Webhooks** → **New Webhook**
3. Name it `BMS Checker`, then click **Copy Webhook URL**

---

### Step 3: Add GitHub Secret

In your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name            | Value                        |
|------------------------|------------------------------|
| `DISCORD_WEBHOOK_URL`  | The webhook URL from Step 2  |

---

### Step 4: Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will now run automatically every 10 minutes

---

## Test It Manually

Go to **Actions → BMS MI vs RCB Ticket Checker → Run workflow**

You'll receive a heartbeat Discord message immediately confirming the bot is working.

---

## Customisation

| What to change     | Where                              |
|--------------------|------------------------------------|
| Check frequency    | `cron` line in `ticket-checker.yml`|
| BMS event URL      | `BMS_EVENT_URL` in `checker.py`    |
| Detection keywords | `AVAILABILITY_SIGNALS` list        |

---

## How Detection Works

The checker scans the raw HTML of the BMS event page for signals:

**Tickets available** (triggers alert): `Book Now`, `Fast Filling`, `Filling Fast`, `Going Fast`, `Few Tickets`, `Select Seats`, etc.

**Tickets not available** (triggers heartbeat only): `Sold Out`, `Coming Soon`, `Notify Me`, `Registration Closed`

If BMS changes their page structure, update `AVAILABILITY_SIGNALS` in `checker.py`.

---

## Notes

- GitHub Actions free tier allows **2,000 minutes/month** — running every 10 min uses ~60 min/month, well within limits.
- This is for personal use only. Don't abuse BMS servers with very frequent polling.
