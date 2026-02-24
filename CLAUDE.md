# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the mailer
python main.py
```

## Architecture

Single-file script (`main.py`) with a linear pipeline:

1. **`load_dotenv()` + `validate_env()`** — reads `.env` for `GMAIL_SENDER`, `GMAIL_APP_PASS`, `EMAIL_RECIPIENT`
2. **`load_tickers()`** — reads `tickers.txt` (one ticker per line, `#` comments ignored, validates 1–5 uppercase letters)
3. **`search_etf_news(ticker)`** — fetches top 5 results from Google News RSS (`feedparser`)
4. **`build_email_body(ticker, results)`** — returns `(plain_text, html)` tuple
5. **`send_email(...)`** — sends via Gmail SMTP SSL on port 465 using an App Password

One email is sent per ticker. All errors are fatal (`sys.exit(1)`).

## Configuration

- **`tickers.txt`** — one ETF ticker per line; `#` lines are comments
- **`.env`** — copy from `.env.example`; requires a Gmail App Password (not a regular Gmail password)

> **Note:** The README describes passing tickers as CLI args, but the code was refactored to read from `tickers.txt`. The README is outdated on this point.
