# 🏏 BookMyShow MI vs RCB Ticket Checker

Automatically checks BookMyShow every 10 minutes for **MI vs RCB (April 12, 2026)**
ticket availability and emails you the moment they go live.

Runs entirely free on **GitHub Actions** — no server, no laptop needed.

---

## 🚀 Setup (5 minutes)

### Step 1: Create the GitHub repo

1. Go to [github.com/new](https://github.com/new)
2. Create a **private** repo (e.g. `bms-ticket-checker`)
3. Push this folder's contents to it:

```bash
cd bms-ticket-checker
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/bms-ticket-checker.git
git push -u origin main
```

---

### Step 2: Get a Gmail App Password

Gmail requires an **App Password** (not your real password) for SMTP:

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (required)
3. Search for **"App passwords"** → create one → name it "BMS Checker"
4. Copy the 16-character password (e.g. `abcd efgh ijkl mnop`)

---

### Step 3: Add GitHub Secrets

In your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these 3 secrets:

| Secret Name         | Value                                 |
|---------------------|---------------------------------------|
| `GMAIL_USER`        | `your.email@gmail.com`                |
| `GMAIL_APP_PASSWORD`| The 16-char app password from Step 2  |
| `ALERT_TO_EMAIL`    | Email to send alerts to (can be same) |

---

### Step 4: Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will now run automatically every 10 minutes ✅

---

## 🧪 Test It Manually

Go to **Actions → BMS MI vs RCB Ticket Checker → Run workflow**

Set `send_heartbeat = true` to receive a test email and confirm everything works.

---

## 📬 What You'll Receive

**When tickets are found:**
```
🚨 MI vs RCB Tickets AVAILABLE on BookMyShow!
[Book Now button linking directly to BMS]
```

**Heartbeat (manual run only):**
```
🤖 BMS Checker: Still watching (no tickets yet)
```

---

## ⚙️ Customisation

| What to change              | Where                          |
|-----------------------------|--------------------------------|
| Check frequency             | `cron` line in the workflow    |
| BMS event URL               | `BMS_EVENT_URL` in checker.py  |
| Detection keywords          | `AVAILABILITY_SIGNALS` list    |
| Enable daily heartbeat email| Set `SEND_HEARTBEAT=true` in workflow env |

---

## ⚠️ Important Notes

- **BMS is JS-heavy** — the checker scans raw HTML signals. If BMS changes their
  page structure, update `AVAILABILITY_SIGNALS` in `checker.py`.
- GitHub Actions free tier allows **2,000 minutes/month** — running every 10 min
  uses ~2 min/day × 30 = ~60 min/month. Well within limits.
- This is for personal use only. Don't abuse BMS servers with very frequent polling.
