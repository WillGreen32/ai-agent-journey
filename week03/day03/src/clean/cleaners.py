from __future__ import annotations
import re

# ---------- Compiled regex patterns ----------
TAG_RE        = re.compile(r"<.*?>")            # remove HTML tags (non-greedy)
SPACE_RE      = re.compile(r"\s+")              # collapse spaces
NON_DIGIT_RE  = re.compile(r"\D")               # remove non-digit chars
# week03/day03/src/clean/cleaners.py
SYMBOLS_RE = re.compile(r"[^\w\s.'@+\-$]")

EMOJI_RE      = re.compile(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]+", re.UNICODE)

# ---------- Cleaners ----------
def clean_email(email: str | None) -> str:
    """Trim, lowercase, and remove invalid email chars."""
    if not email:
        return ""
    email = email.strip().lower()
    return re.sub(r"[^a-z0-9@._%+-]", "", email)

def clean_phone_au(phone: str | None) -> str:
    """
    Normalize Australian phone numbers to 10 digits starting with '0'.

    Rules:
    - Strip all non-digits
    - If the number starts with country code 61, drop it.
      Then ensure the remaining number starts with '0' (prepend if missing).
    - Return '' unless the final result is exactly 10 digits.
    """
    if not phone:
        return ""

    digits = NON_DIGIT_RE.sub("", phone)  # keep digits only

    if digits.startswith("61"):
        # Remove country code
        digits = digits[2:]
        # Some inputs already include the trunk '0' (e.g., +61 03...), some don't (e.g., +61 499...)
        if not digits.startswith("0"):
            digits = "0" + digits

    return digits if len(digits) == 10 else ""


def strip_html(text: str | None) -> str:
    """Remove HTML tags."""
    return TAG_RE.sub("", text or "")

def normalize_whitespace(text: str | None) -> str:
    """Collapse multiple spaces/newlines into one."""
    return SPACE_RE.sub(" ", text or "").strip()

def standardize_state(state: str | None) -> str:
    """Map Australian state names to consistent abbreviations."""
    mapping = {
        "nsw": "NSW", "new south wales": "NSW",
        "vic": "VIC", "victoria": "VIC",
        "qld": "QLD", "queensland": "QLD",
        "wa": "WA", "western australia": "WA",
        "sa": "SA", "south australia": "SA",
        "tas": "TAS", "tasmania": "TAS",
        "nt": "NT", "northern territory": "NT",
        "act": "ACT", "australian capital territory": "ACT",
    }
    s = normalize_whitespace(state or "")
    return mapping.get(s.lower(), s.upper())

def remove_emoji(text: str | None) -> str:
    """Remove emoji characters."""
    return EMOJI_RE.sub("", text or "")

def remove_symbols(text: str | None) -> str:
    """Remove disallowed symbols (keeps letters, digits, punctuation)."""
    return SYMBOLS_RE.sub("", text or "")

__all__ = [
    "clean_email",
    "clean_phone_au",
    "strip_html",
    "normalize_whitespace",
    "standardize_state",
    "remove_emoji",
    "remove_symbols",
]
