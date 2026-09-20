import os

# --- Secrets (from environment / GitHub Secrets) ---
# .strip() guards against a trailing newline from pasting into the GitHub
# Secrets UI -- SMTP rejects a newline in RCPT TO outright.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "").strip()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "").strip()

# --- Gemini settings ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- Email settings ---
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465  # SSL

# --- Topic categories ---
# The script picks a random category each week, then Gemini picks a specific topic within it.
TOPIC_CATEGORIES = [
    "Science & Nature",
    "Technology & Innovation",
    "History & World Events",
    "Geography & Cultures",
    "Philosophy & Big Questions",
    "Mathematics & Logic",
    "Economics & Money",
    "Psychology & Human Behavior",
    "Health & Medicine",
    "Arts & Culture",
    "Politics & Society",
]
