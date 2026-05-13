"""Notifications: Telegram + Email (SMTP)."""
from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger("applyflow.notifications")


async def send_telegram(message: str, chat_id: str | None = None) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    chat = chat_id or settings.TELEGRAM_CHAT_ID
    if not token or not chat:
        logger.debug("Telegram not configured")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, json={"chat_id": chat, "text": message, "parse_mode": "Markdown"})
            return r.status_code == 200
        except Exception as e:
            logger.warning(f"Telegram send failed: {e}")
            return False


async def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.debug("SMTP not configured")
        return False
    from email.message import EmailMessage

    import aiosmtplib

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        return True
    except Exception as e:
        logger.warning(f"Email send failed: {e}")
        return False


async def notify_user(message: str, email: str | None = None) -> None:
    await send_telegram(message)
    if email:
        await send_email(email, "[ApplyFlow AI] Update", message)
