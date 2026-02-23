import os

# --- Secrets (from environment / GitHub Secrets) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "")

# --- Gemini settings ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- Email settings ---
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465  # SSL

# --- Topic categories ---
# The script picks a random category each week, then Gemini picks a specific topic within it.
TOPIC_CATEGORIES = [
    "Science & Nature",
    "Technology & Computing",
    "History & Civilization",
    "Geography & Cultures",
    "Philosophy & Ideas",
    "Mathematics & Logic",
    "Economics & Systems",
    "Psychology & Human Behavior",
]
