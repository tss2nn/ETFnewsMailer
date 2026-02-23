# ETFnews

A Python script that fetches the top 5 Google News articles for a given ETF ticker and emails them to you.

## Setup

**1. Clone and install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure credentials**
```bash
cp .env.example .env
```

Edit `.env` with your values:

| Variable | Description |
|----------|-------------|
| `GMAIL_SENDER` | Gmail address to send from |
| `GMAIL_APP_PASS` | 16-character Gmail App Password (not your regular password) |
| `EMAIL_RECIPIENT` | Email address to send the report to |

To generate a Gmail App Password: **Google Account → Security → 2-Step Verification → App passwords**

## Usage

```bash
# Single ticker
python main.py SPY

# Multiple tickers (one email per ticker)
python main.py SPY,QQQ,VTI
```

## Scheduling (macOS/Linux)

To receive a daily digest on weekday mornings, add a cron job:

```bash
crontab -e
```

```
0 7 * * 1-5 /path/to/python /path/to/ETFnews/main.py SPY
```

Find your Python path with `which python`.

## Dependencies

- [feedparser](https://github.com/kurtmckee/feedparser) — parses Google News RSS feed
- [python-dotenv](https://github.com/theskumar/python-dotenv) — loads credentials from `.env`
