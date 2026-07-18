#!/usr/bin/env python3
"""
TikTok OAuth2 Token Generator — automated local browser flow.

Opens the user's browser for TikTok authorization consent, captures the auth
code via a local redirect server, and exchanges it for an access token.

NOTE: TikTok access tokens expire (typically after 24 hours) and need periodic
refresh using the refresh_token returned alongside the access token. This script
outputs the initial token pair; callers should implement refresh logic using the
TikTok token refresh endpoint for long-lived automation.

Usage:
  # Interactive — opens browser, prompts for brand suffix:
  python scripts/video/credential_setup/tiktok_oauth.py

  # Non-interactive — specify everything:
  python scripts/video/credential_setup/tiktok_oauth.py \
    --client-key <KEY> --client-secret <SECRET> --brand-suffix _SP

  # Read client key/secret from env:
  export TIKTOK_CLIENT_KEY=... TIKTOK_CLIENT_SECRET=...
  python scripts/video/credential_setup/tiktok_oauth.py --brand-suffix _CC

  # Batch mode — process multiple brands from manifest:
  python scripts/video/credential_setup/tiktok_oauth.py --manifest credentials_manifest.yaml

Output: prints the access token and optionally appends to a credentials file.
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
    "video.publish",
    "video.upload",
]
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
REDIRECT_PORT = 8096
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
                b"<html><body><h2>TikTok authorization successful!</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
                b"</body></html>"
            )
        else:
            error = query.get("error", ["unknown"])[0]
            error_desc = query.get("error_description", [""])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"<html><body><h2>Error: {error}</h2>"
                f"<p>{error_desc}</p></body></html>".encode()
            )

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def get_auth_code(client_key: str) -> str:
    """Open browser for consent and capture the auth code via local redirect."""
    params = urlencode({
        "client_key": client_key,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": ",".join(SCOPES),
    })
    auth_url = f"{AUTH_URL}?{params}"

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print(f"\nOpening browser for TikTok authorization...")
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


def exchange_code_for_tokens(client_key: str, client_secret: str, code: str) -> dict:
    """Exchange authorization code for access and refresh tokens."""
    body = urlencode({
        "code": code,
        "client_key": client_key,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = Request(TOKEN_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def process_brand(client_key: str, client_secret: str, brand_suffix: str, output_file: Path | None) -> dict:
    """Run the full OAuth flow for one brand."""
    print(f"\n{'='*60}")
    print(f"  TikTok OAuth for brand suffix: {brand_suffix}")
    print(f"{'='*60}")
    print(f"Sign in with the TikTok account that owns the channel")
    print(f"for brand '{brand_suffix}'.\n")

    code = get_auth_code(client_key)
    print(f"Authorization code received.")

    token_resp = exchange_code_for_tokens(client_key, client_secret, code)

    # TikTok v2 wraps tokens under a "data" key in some responses
    token_data = token_resp.get("data", token_resp)
    access_token = token_data.get("access_token", "")

    if not access_token:
        error_msg = token_resp.get("message", token_resp.get("error", "unknown error"))
        print(f"ERROR: No access_token returned. API response: {error_msg}", file=sys.stderr)
        return {}

    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data.get("expires_in", "unknown")
    print(f"\nAccess token obtained for {brand_suffix} (expires in {expires_in}s)")
    if refresh_token:
        print(f"Refresh token also obtained — store it for automated refresh.")

    result = {
        f"TIKTOK_CLIENT_KEY{brand_suffix}": client_key,
        f"TIKTOK_CLIENT_SECRET{brand_suffix}": client_secret,
        f"TIKTOK_ACCESS_TOKEN{brand_suffix}": access_token,
    }

    if refresh_token:
        result[f"TIKTOK_REFRESH_TOKEN{brand_suffix}"] = refresh_token

    if output_file:
        with open(output_file, "a") as f:
            for key, val in result.items():
                f.write(f"{key}={val}\n")
        print(f"Credentials appended to {output_file}")

    return result


def main():
    parser = argparse.ArgumentParser(description="TikTok OAuth2 token generator")
    parser.add_argument("--client-key", help="TikTok Client Key (or set TIKTOK_CLIENT_KEY env)")
    parser.add_argument("--client-secret", help="TikTok Client Secret (or set TIKTOK_CLIENT_SECRET env)")
    parser.add_argument("--brand-suffix", help="Brand credential suffix (e.g., _SP, _CC)")
    parser.add_argument("--output", type=Path, help="Append credentials to this file")
    parser.add_argument("--manifest", type=Path, help="YAML manifest with list of brands to process")
    args = parser.parse_args()

    client_key = args.client_key or os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = args.client_secret or os.environ.get("TIKTOK_CLIENT_SECRET", "")

    if not client_key or not client_secret:
        print("ERROR: Provide --client-key and --client-secret, or set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET env vars.")
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
            process_brand(client_key, client_secret, suffix, args.output)
    else:
        suffix = args.brand_suffix
        if not suffix:
            suffix = input("Enter brand suffix (e.g., _SP, _CC): ").strip()
        process_brand(client_key, client_secret, suffix, args.output)


if __name__ == "__main__":
    main()
