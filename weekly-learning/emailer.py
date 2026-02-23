import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    GMAIL_ADDRESS,
    GMAIL_APP_PASSWORD,
    GMAIL_SMTP_PORT,
    GMAIL_SMTP_SERVER,
    EMAIL_RECIPIENT,
)

logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "Science & Nature": "#2e7d32",
    "Technology & Innovation": "#1565c0",
    "History & World Events": "#bf360c",
    "Geography & Cultures": "#00838f",
    "Philosophy & Big Questions": "#6a1b9a",
    "Mathematics & Logic": "#e65100",
    "Economics & Money": "#37474f",
    "Psychology & Human Behavior": "#ad1457",
    "Health & Medicine": "#00695c",
    "Arts & Culture": "#4527a0",
    "Politics & Society": "#c62828",
}


def _build_html(article: dict, date_str: str) -> str:
    """Build a clean HTML email body from the generated article."""
    category = article.get("category", "")
    badge_color = CATEGORY_COLORS.get(category, "#555555")

    # Build sections HTML
    sections_html = ""
    for section in article.get("sections", []):
        # Convert newlines in content to <br> for paragraphs
        content = section.get("content", "")
        paragraphs = content.split("\n\n")
        content_html = "".join(
            f'<p style="margin: 0 0 16px 0; font-size: 16px; color: #333; line-height: 1.8;">{p.strip()}</p>'
            for p in paragraphs
            if p.strip()
        )

        sections_html += f"""
                    <tr>
                        <td style="padding: 20px 0 4px 0;">
                            <h2 style="margin: 0; font-size: 17px; font-weight: 600; color: #1a1a1a;">
                                {section.get("heading", "")}
                            </h2>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;">
                            {content_html}
                        </td>
                    </tr>"""

    # Build further reading list
    reading_html = ""
    for item in article.get("further_reading", []):
        reading_html += f"""
                                <tr>
                                    <td style="padding: 3px 0; font-size: 14px; color: #444; line-height: 1.5;">
                                        <span style="color: #1565c0; margin-right: 6px;">&#x2192;</span>{item}
                                    </td>
                                </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #1a1a2e; padding: 24px 32px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700;">
                                Weekly Learning
                            </h1>
                            <p style="margin: 4px 0 0 0; color: #a0a0c0; font-size: 13px;">
                                {date_str}
                            </p>
                        </td>
                    </tr>
                    <!-- Topic title + category -->
                    <tr>
                        <td style="padding: 28px 32px 0 32px;">
                            <span style="display: inline-block; background-color: {badge_color}; color: #ffffff; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                                {category}
                            </span>
                            <h1 style="margin: 12px 0 0 0; font-size: 24px; font-weight: 700; color: #1a1a1a; line-height: 1.3;">
                                {article.get("topic", "Untitled")}
                            </h1>
                        </td>
                    </tr>
                    <!-- Hook -->
                    <tr>
                        <td style="padding: 16px 32px 0 32px;">
                            <p style="margin: 0; font-size: 17px; color: #555; line-height: 1.8; font-style: italic;">
                                {article.get("hook", "")}
                            </p>
                        </td>
                    </tr>
                    <!-- Sections -->
                    <tr>
                        <td style="padding: 8px 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                {sections_html}
                            </table>
                        </td>
                    </tr>
                    <!-- Surprising fact -->
                    <tr>
                        <td style="padding: 8px 32px 16px 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fff8e1; border-left: 4px solid #ffc107; border-radius: 4px;">
                                <tr>
                                    <td style="padding: 16px 20px;">
                                        <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: 700; color: #f57f17; text-transform: uppercase; letter-spacing: 0.5px;">
                                            Surprising Fact
                                        </p>
                                        <p style="margin: 0; font-size: 14px; color: #333; line-height: 1.6;">
                                            {article.get("surprising_fact", "")}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Further reading -->
                    <tr>
                        <td style="padding: 0 32px 24px 32px;">
                            <p style="margin: 0 0 8px 0; font-size: 14px; font-weight: 700; color: #1a1a1a;">
                                Go Deeper
                            </p>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                {reading_html}
                            </table>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 16px 32px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #999;">
                                Generated by Automation Lab &middot; weekly-learning
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return html


def send_email(article: dict, date_str: str) -> bool:
    """Send the weekly learning email via Gmail SMTP. Returns True on success."""
    if not all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, EMAIL_RECIPIENT]):
        logger.error("Gmail credentials or recipient not set. Cannot send email.")
        return False

    if not article:
        logger.warning("Empty article -- not sending email.")
        return False

    html_body = _build_html(article, date_str)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Weekly Learning: {article.get('topic', 'Untitled')} -- {date_str}"
    msg["From"] = f"Weekly Learning <{GMAIL_ADDRESS}>"
    msg["To"] = EMAIL_RECIPIENT

    # Plain-text fallback
    plain_text = f"Weekly Learning -- {date_str}\n"
    plain_text += f"Category: {article.get('category', '')}\n"
    plain_text += f"Topic: {article.get('topic', '')}\n\n"
    plain_text += f"{article.get('hook', '')}\n\n"
    for section in article.get("sections", []):
        plain_text += f"## {section.get('heading', '')}\n\n"
        plain_text += f"{section.get('content', '')}\n\n"
    plain_text += f"Surprising Fact: {article.get('surprising_fact', '')}\n\n"
    plain_text += "Go Deeper:\n"
    for item in article.get("further_reading", []):
        plain_text += f"  -> {item}\n"

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, EMAIL_RECIPIENT, msg.as_string())
        logger.info("Weekly learning email sent to %s.", EMAIL_RECIPIENT)
        return True
    except smtplib.SMTPException as e:
        logger.error("Failed to send email: %s", e)
        return False
