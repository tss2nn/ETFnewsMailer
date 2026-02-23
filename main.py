import argparse
import datetime
import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser
from dotenv import load_dotenv

REQUIRED_ENV_VARS = ["GMAIL_SENDER", "GMAIL_APP_PASS", "EMAIL_RECIPIENT"]


def validate_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)


def parse_args() -> list[str]:
    parser = argparse.ArgumentParser(
        description="Search Google for ETF news and email the top 5 results."
    )
    parser.add_argument(
        "ticker",
        help="ETF ticker symbol(s), e.g. SPY or SPY,QQQ,VTI",
    )
    args = parser.parse_args()
    tickers = [t.strip().upper() for t in args.ticker.split(",")]
    for t in tickers:
        if not re.match(r"^[A-Z]{1,5}$", t):
            print(f"Error: '{t}' is not a valid ETF ticker (1-5 uppercase letters).")
            sys.exit(1)
    return tickers


def search_etf_news(ticker: str, num_results: int = 5) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={ticker}+ETF&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"Error: Failed to fetch news feed: {e}")
        sys.exit(1)

    if not feed.entries:
        print(f"Error: No results returned for {ticker}. Check your internet connection.")
        sys.exit(1)

    return [
        {
            "title": entry.get("title", "No title"),
            "url": entry.get("link", ""),
            "description": entry.get("summary", "No description available."),
            "published": entry.get("published", ""),
        }
        for entry in feed.entries[:num_results]
    ]


def build_email_body(ticker: str, results: list[dict]) -> tuple[str, str]:
    today = datetime.date.today().isoformat()

    # Plain text
    lines = [f"ETF News Report: {ticker}", f"Date: {today}", "=" * 50, ""]
    for i, r in enumerate(results, 1):
        lines += [
            f"{i}. {r['title']}",
            f"   {r['published']}",
            f"   URL: {r['url']}",
            f"   {r['description']}",
            "",
        ]
    lines += ["=" * 50, "Sent by ETFnews"]
    plain = "\n".join(lines)

    # HTML
    items_html = ""
    for i, r in enumerate(results, 1):
        items_html += f"""
        <div style="margin-bottom:24px;">
          <span style="color:#999;font-size:13px;">#{i} &middot; {r['published']}</span>
          <h3 style="margin:4px 0;">
            <a href="{r['url']}" style="color:#1a73e8;text-decoration:none;">{r['title']}</a>
          </h3>
          <p style="margin:4px 0;color:#444;">{r['description']}</p>
          <small style="color:#aaa;">{r['url']}</small>
        </div>"""

    html = f"""<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
  <h2 style="color:#1a73e8;">ETF News Report: {ticker}</h2>
  <p style="color:#666;">Date: {today}</p>
  <hr style="border:none;border-top:1px solid #eee;">
  {items_html}
  <hr style="border:none;border-top:1px solid #eee;">
  <small style="color:#aaa;">Sent by ETFnews</small>
</body>
</html>"""

    return plain, html


def send_email(subject: str, plain: str, html: str):
    sender = os.environ["GMAIL_SENDER"]
    app_pass = os.environ["GMAIL_APP_PASS"]
    recipient = os.environ["EMAIL_RECIPIENT"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_pass)
            server.sendmail(sender, recipient, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        print("Error: Gmail authentication failed. Check GMAIL_SENDER and GMAIL_APP_PASS.")
        print("Make sure you are using an App Password, not your regular Gmail password.")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"Error: Failed to send email: {e}")
        sys.exit(1)


def main():
    load_dotenv()
    validate_env()
    tickers = parse_args()
    for ticker in tickers:
        print(f"Searching for {ticker} ETF news...")
        results = search_etf_news(ticker)
        subject = f"ETF News: {ticker} - {datetime.date.today()}"
        plain, html = build_email_body(ticker, results)
        send_email(subject, plain, html)
        print(f"Email sent for {ticker}.")


if __name__ == "__main__":
    main()
