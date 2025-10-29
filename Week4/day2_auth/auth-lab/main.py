from dotenv import load_dotenv
import os
from src.auth.strategies import (
    ApiKeyAuth, BearerAuth, HmacAuth, OAuthClientCredentials,
    AuthConfigError, OAuthError, redact
)

def try_oauth():
    try:
        oauth = OAuthClientCredentials()
        headers = oauth.attach({})
        print("OAuth attached ✅", redact(headers.get("Authorization", "")))
    except (AuthConfigError, OAuthError) as e:
        print("OAuth not tested (no creds or endpoint):", str(e)[:120])

def main():
    load_dotenv()
    base_url = os.getenv("API_BASE_URL")
    if not base_url:
        raise ValueError("Missing API_BASE_URL in .env file")
    print(f"Environment loaded ✅  | Base URL: {base_url}")

    # API Key
    try:
        k = ApiKeyAuth()
        print("ApiKeyAuth header ✅", k.attach({}))
    except AuthConfigError as e:
        print("ApiKeyAuth skipped:", e)

    # Bearer
    try:
        b = BearerAuth()
        print("BearerAuth header ✅", redact(b.attach({}).get("Authorization")))
    except AuthConfigError as e:
        print("BearerAuth skipped:", e)

    # HMAC
    try:
        h = HmacAuth()
        msg = "amount=100&currency=USD"
        print("HMAC sig ✅", h.sign(msg)[:16], "…")
        print("HMAC signed headers ✅", h.signed_headers(msg))
    except AuthConfigError as e:
        print("HmacAuth skipped:", e)

    # OAuth (only if you have a real endpoint)
    try_oauth()

if __name__ == "__main__":
    main()
