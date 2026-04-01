#!/usr/bin/env python3
"""
Instagram Graph API (Reels) OAuth Token Generator — automated local browser flow.

Opens the user's browser for Meta/Facebook consent, captures the auth code via
a local redirect server, exchanges it for a short-lived token, then swaps that
for a long-lived token (60-day lifetime).  Finally retrieves the Instagram
Business/Creator account user ID linked to the Facebook Page.

Usage:
  # Interactive — opens browser, prompts for brand suffix:
  python scripts/video/credential_setup/instagram_oauth.py

  # Non-interactive — specify everything:
  python scripts/video/credential_setup/instagram_oauth.py \
    --app-id <ID> --app-secret <SECRET> --brand-suffix _SP

  # Read app credentials from env:
  export IG_APP_ID=... IG_APP_SECRET=...
  python scripts/video/credential_setup/instagram_oauth.py --brand-suffix _CC

  # Batch mode — process multiple brands from manifest:
  python scripts/video/credential_setup/instagram_oauth.py --manifest credentials_manifest.yaml

Output: prints the long-lived access token and IG user ID, optionally appends
to a credentials file.

Note: Long-lived tokens last 60 days and must be refreshed before expiry via
  GET https://graph.facebook.com/v18.0/oauth/access_token
    ?grant_type=fb_exchange_token&client_id=...&client_secret=...&fb_exchange_token=...
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

SCOPES = [
    "instagram_basic",
    "instagram_content_publish",
    "pages_read_engagement",
]
AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
GRAPH_BASE = "https://graph.facebook.com/v18.0"
REDIRECT_PORT = 8097
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Captures the OAuth callback and extracts the authorization code."""

    auth_code: str | None = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        code = query.get("code", [None])[0]
        if code:
            OAuthCallbackHandler.auth_code = code
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Authorization successful!</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
                b"</body></html>"
            )
        else:
            error = query.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h2>Error: {error}</h2></body></html>".encode())

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def get_auth_code(app_id: str) -> str:
    """Open browser for consent and capture the auth code via local redirect."""
    params = urlencode({
        "client_id": app_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": ",".join(SCOPES),
    })
    auth_url = f"{AUTH_URL}?{params}"

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print(f"\nOpening browser for Instagram/Meta authorization...")
    print(f"If the browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    server_thread.join(timeout=120)
    server.server_close()

    if not OAuthCallbackHandler.auth_code:
        print("ERROR: No authorization code received within timeout.", file=sys.stderr)
        sys.exit(1)

    code = OAuthCallbackHandler.auth_code
    OAuthCallbackHandler.auth_code = None  # Reset for next use
    return code


def _graph_get(url: str, timeout: int = 30) -> dict:
    """Helper: GET a Graph API URL, return parsed JSON."""
    req = Request(url, method="GET")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def exchange_code_for_token(app_id: str, app_secret: str, code: str) -> str:
    """Exchange authorization code for a short-lived access token."""
    params = urlencode({
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    })
    url = f"{TOKEN_URL}?{params}"
    data = _graph_get(url)
    token = data.get("access_token", "")
    if not token:
        print(f"ERROR: No access_token in response: {data}", file=sys.stderr)
        sys.exit(1)
    return token


def exchange_for_long_lived_token(app_id: str, app_secret: str, short_token: str) -> str:
    """Swap a short-lived token for a 60-day long-lived token."""
    params = urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    })
    url = f"{TOKEN_URL}?{params}"
    data = _graph_get(url)
    token = data.get("access_token", "")
    if not token:
        print(f"ERROR: Long-lived token exchange failed: {data}", file=sys.stderr)
        sys.exit(1)
    expires_in = data.get("expires_in", "unknown")
    print(f"  Long-lived token obtained (expires in {expires_in}s / ~60 days)")
    return token


def get_instagram_user_id(access_token: str) -> str:
    """Retrieve the Instagram Business/Creator account ID via the linked FB Page."""
    # Step 1: Get Facebook Pages the user manages
    pages_url = f"{GRAPH_BASE}/me/accounts?access_token={access_token}"
    pages_data = _graph_get(pages_url)
    pages = pages_data.get("data", [])

    if not pages:
        print("ERROR: No Facebook Pages found for this account.", file=sys.stderr)
        print("Make sure the authorized user manages a Page linked to an Instagram Business/Creator account.", file=sys.stderr)
        sys.exit(1)

    # If multiple pages, let user pick; if one, use it
    if len(pages) == 1:
        page = pages[0]
    else:
        print(f"\n  Found {len(pages)} Facebook Page(s):")
        for i, p in enumerate(pages):
            print(f"    [{i}] {p.get('name', 'Unnamed')} (id: {p['id']})")
        choice = input(f"  Select page [0-{len(pages)-1}]: ").strip()
        try:
            page = pages[int(choice)]
        except (ValueError, IndexError):
            print("ERROR: Invalid selection.", file=sys.stderr)
            sys.exit(1)

    page_id = page["id"]
    page_name = page.get("name", page_id)
    print(f"  Using Facebook Page: {page_name} ({page_id})")

    # Step 2: Get the Instagram Business Account linked to the Page
    ig_url = f"{GRAPH_BASE}/{page_id}?fields=instagram_business_account&access_token={access_token}"
    ig_data = _graph_get(ig_url)
    ig_account = ig_data.get("instagram_business_account", {})
    ig_user_id = ig_account.get("id", "")

    if not ig_user_id:
        print(f"ERROR: No Instagram Business/Creator account linked to Page '{page_name}'.", file=sys.stderr)
        print("Link an Instagram Professional account to this Page in Meta Business Suite.", file=sys.stderr)
        sys.exit(1)

    print(f"  Instagram User ID: {ig_user_id}")
    return ig_user_id


def process_brand(app_id: str, app_secret: str, brand_suffix: str, output_file: Path | None) -> dict:
    """Run the full OAuth flow for one brand."""
    print(f"\n{'='*60}")
    print(f"  Instagram OAuth for brand suffix: {brand_suffix}")
    print(f"{'='*60}")
    print(f"Sign in with the Facebook account that manages the Instagram")
    print(f"Business/Creator account for brand '{brand_suffix}'.\n")

    code = get_auth_code(app_id)
    print(f"  Authorization code received.")

    short_token = exchange_code_for_token(app_id, app_secret, code)
    print(f"  Short-lived token obtained.")

    long_token = exchange_for_long_lived_token(app_id, app_secret, short_token)

    ig_user_id = get_instagram_user_id(long_token)

    result = {
        f"IG_ACCESS_TOKEN{brand_suffix}": long_token,
        f"IG_USER_ID{brand_suffix}": ig_user_id,
    }

    if output_file:
        with open(output_file, "a") as f:
            for key, val in result.items():
                f.write(f"{key}={val}\n")
        print(f"  Credentials appended to {output_file}")

    print(f"\n  WARNING: This long-lived token expires in ~60 days.")
    print(f"  Schedule a refresh before expiry.\n")
    return result


def main():
    parser = argparse.ArgumentParser(description="Instagram Graph API OAuth token generator")
    parser.add_argument("--app-id", help="Meta App ID (or set IG_APP_ID env)")
    parser.add_argument("--app-secret", help="Meta App Secret (or set IG_APP_SECRET env)")
    parser.add_argument("--brand-suffix", help="Brand credential suffix (e.g., _SP, _CC)")
    parser.add_argument("--output", type=Path, help="Append credentials to this file")
    parser.add_argument("--manifest", type=Path, help="YAML manifest with list of brands to process")
    args = parser.parse_args()

    app_id = args.app_id or os.environ.get("IG_APP_ID", "")
    app_secret = args.app_secret or os.environ.get("IG_APP_SECRET", "")

    if not app_id or not app_secret:
        print("ERROR: Provide --app-id and --app-secret, or set IG_APP_ID and IG_APP_SECRET env vars.")
        sys.exit(1)

    if args.manifest:
        try:
            import yaml
            manifest = yaml.safe_load(args.manifest.read_text())
        except ImportError:
            print("ERROR: PyYAML required for manifest mode. pip install pyyaml")
            sys.exit(1)

        brands = manifest.get("brands", [])
        print(f"Processing {len(brands)} brands from manifest...")
        for brand in brands:
            suffix = brand.get("suffix", "")
            if not suffix:
                continue
            input(f"\nPress Enter when ready to authorize brand {suffix}...")
            process_brand(app_id, app_secret, suffix, args.output)
    else:
        suffix = args.brand_suffix
        if not suffix:
            suffix = input("Enter brand suffix (e.g., _SP, _CC): ").strip()
        process_brand(app_id, app_secret, suffix, args.output)


if __name__ == "__main__":
    main()
