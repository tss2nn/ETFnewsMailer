import smtplib
from unittest.mock import MagicMock, patch

import pytest

import main

# --- validate_env ---


def test_validate_env_passes(monkeypatch):
    monkeypatch.setenv("GMAIL_SENDER", "sender@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASS", "abcd efgh ijkl mnop")
    monkeypatch.setenv("EMAIL_RECIPIENT", "recipient@gmail.com")
    main.validate_env()


def test_validate_env_missing_all(monkeypatch):
    for var in ["GMAIL_SENDER", "GMAIL_APP_PASS", "EMAIL_RECIPIENT"]:
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(SystemExit):
        main.validate_env()


def test_validate_env_missing_one(monkeypatch):
    monkeypatch.setenv("GMAIL_SENDER", "sender@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASS", "abcd efgh ijkl mnop")
    monkeypatch.delenv("EMAIL_RECIPIENT", raising=False)
    with pytest.raises(SystemExit):
        main.validate_env()


# --- load_tickers ---


def test_load_tickers_valid(tmp_path, monkeypatch):
    f = tmp_path / "tickers.txt"
    f.write_text("SPY\nQQQ\n# comment\n\nVTI\n")
    monkeypatch.setattr(main, "TICKER_FILE", str(f))
    assert main.load_tickers() == ["SPY", "QQQ", "VTI"]


def test_load_tickers_lowercased_input(tmp_path, monkeypatch):
    f = tmp_path / "tickers.txt"
    f.write_text("spy\nqqq\n")
    monkeypatch.setattr(main, "TICKER_FILE", str(f))
    assert main.load_tickers() == ["SPY", "QQQ"]


def test_load_tickers_invalid_format(tmp_path, monkeypatch):
    f = tmp_path / "tickers.txt"
    f.write_text("SPY\nINVALID123\n")
    monkeypatch.setattr(main, "TICKER_FILE", str(f))
    with pytest.raises(SystemExit):
        main.load_tickers()


def test_load_tickers_empty_file(tmp_path, monkeypatch):
    f = tmp_path / "tickers.txt"
    f.write_text("# only comments\n\n")
    monkeypatch.setattr(main, "TICKER_FILE", str(f))
    with pytest.raises(SystemExit):
        main.load_tickers()


def test_load_tickers_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "TICKER_FILE", str(tmp_path / "nonexistent.txt"))
    with pytest.raises(SystemExit):
        main.load_tickers()


# --- search_etf_news ---

MOCK_ENTRIES = [
    {
        "title": f"News {i}",
        "link": f"https://example.com/{i}",
        "summary": f"Summary {i}",
        "published": "Mon, 24 Feb 2026",
    }
    for i in range(10)
]


def test_search_etf_news_returns_results():
    mock_feed = MagicMock()
    mock_feed.entries = MOCK_ENTRIES
    with patch("main.feedparser.parse", return_value=mock_feed):
        results = main.search_etf_news("SPY")
    assert len(results) == 5
    assert results[0]["title"] == "News 0"
    assert results[0]["url"] == "https://example.com/0"
    assert results[0]["description"] == "Summary 0"


def test_search_etf_news_limits_to_num_results():
    mock_feed = MagicMock()
    mock_feed.entries = MOCK_ENTRIES
    with patch("main.feedparser.parse", return_value=mock_feed):
        results = main.search_etf_news("SPY", num_results=3)
    assert len(results) == 3


def test_search_etf_news_no_entries():
    mock_feed = MagicMock()
    mock_feed.entries = []
    with patch("main.feedparser.parse", return_value=mock_feed):
        with pytest.raises(SystemExit):
            main.search_etf_news("SPY")


def test_search_etf_news_fetch_exception():
    with patch("main.feedparser.parse", side_effect=Exception("Network error")):
        with pytest.raises(SystemExit):
            main.search_etf_news("SPY")


# --- build_email_body ---

SAMPLE_RESULTS = [
    {
        "title": "SPY hits record high",
        "url": "https://example.com/spy",
        "description": "S&P 500 ETF closes at all-time high.",
        "published": "Mon, 24 Feb 2026",
    }
]


def test_build_email_body_returns_strings():
    plain, html = main.build_email_body("SPY", SAMPLE_RESULTS)
    assert isinstance(plain, str)
    assert isinstance(html, str)


def test_build_email_body_contains_ticker():
    plain, html = main.build_email_body("SPY", SAMPLE_RESULTS)
    assert "SPY" in plain
    assert "SPY" in html


def test_build_email_body_contains_article_data():
    plain, html = main.build_email_body("SPY", SAMPLE_RESULTS)
    assert "SPY hits record high" in plain
    assert "SPY hits record high" in html
    assert "https://example.com/spy" in plain
    assert "https://example.com/spy" in html


# --- send_email ---


def test_send_email_success(monkeypatch):
    monkeypatch.setenv("GMAIL_SENDER", "sender@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASS", "testpass")
    monkeypatch.setenv("EMAIL_RECIPIENT", "recipient@gmail.com")
    with patch("smtplib.SMTP_SSL") as mock_smtp:
        main.send_email("Subject", "Plain text", "<p>HTML</p>")
        mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()


def test_send_email_auth_failure(monkeypatch):
    monkeypatch.setenv("GMAIL_SENDER", "sender@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASS", "wrongpass")
    monkeypatch.setenv("EMAIL_RECIPIENT", "recipient@gmail.com")
    with patch("smtplib.SMTP_SSL") as mock_smtp:
        mock_smtp.return_value.__enter__.return_value.login.side_effect = (
            smtplib.SMTPAuthenticationError(535, "Auth failed")
        )
        with pytest.raises(SystemExit):
            main.send_email("Subject", "Plain text", "<p>HTML</p>")


def test_send_email_smtp_error(monkeypatch):
    monkeypatch.setenv("GMAIL_SENDER", "sender@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASS", "testpass")
    monkeypatch.setenv("EMAIL_RECIPIENT", "recipient@gmail.com")
    with patch("smtplib.SMTP_SSL") as mock_smtp:
        mock_smtp.return_value.__enter__.return_value.sendmail.side_effect = (
            smtplib.SMTPException("Send failed")
        )
        with pytest.raises(SystemExit):
            main.send_email("Subject", "Plain text", "<p>HTML</p>")
