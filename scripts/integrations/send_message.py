#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to use send_message.py") from exc


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / ".messaging_channels.local.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(
            f"Missing {CONFIG_PATH}. Run setup_messaging_channels_local.sh first."
        )
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("channels", {})


def get_keychain_secret(service: str, account: str) -> str:
    out = subprocess.check_output(
        ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
        text=True,
    )
    return out.strip()


def http_json(
    url: str,
    payload: dict,
    headers: dict[str, str],
    dry_run: bool,
) -> dict:
    if dry_run:
        return {"dry_run": True, "url": url, "payload": payload, "headers": headers}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    for key, value in headers.items():
        req.add_header(key, value)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} for {url}: {detail}") from exc


def send_line(cfg: dict, recipient: str | None, message: str, dry_run: bool) -> dict:
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "access_token")
    to_value = recipient or cfg.get("user_id") or cfg.get("group_id")
    if not to_value:
        raise SystemExit("LINE requires --to or line.user_id/group_id in config.")
    payload = {"to": to_value, "messages": [{"type": "text", "text": message}]}
    return http_json(
        "https://api.line.me/v2/bot/message/push",
        payload,
        {"Authorization": f"Bearer {token}"},
        dry_run,
    )


def send_whatsapp(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "access_token")
    phone_number_id = cfg.get("phone_number_id")
    graph_version = cfg.get("graph_version") or "v23.0"
    to_value = recipient or cfg.get("phone_number")
    if not phone_number_id or not to_value:
        raise SystemExit(
            "WhatsApp requires phone_number_id and recipient phone number in config or via --to."
        )
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_value,
        "type": "text",
        "text": {"preview_url": False, "body": message},
    }
    url = f"https://graph.facebook.com/{graph_version}/{phone_number_id}/messages"
    return http_json(
        url,
        payload,
        {"Authorization": f"Bearer {token}"},
        dry_run,
    )


def send_messenger(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "page_access_token")
    graph_version = cfg.get("graph_version") or "v23.0"
    to_value = recipient or cfg.get("recipient_id")
    if not to_value:
        raise SystemExit("Messenger requires --to or messenger.recipient_id in config.")
    payload = {"recipient": {"id": to_value}, "message": {"text": message}}
    url = f"https://graph.facebook.com/{graph_version}/me/messages?access_token={token}"
    return http_json(url, payload, {}, dry_run)


def send_wechat(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    service = cfg.get("keychain_service")
    app_id = cfg.get("app_id")
    app_secret = get_keychain_secret(service, "app_secret")
    to_value = recipient or cfg.get("recipient_openid")
    if not app_id or not app_secret or not to_value:
        raise SystemExit(
            "WeChat requires app_id, app_secret, and recipient openid in config or via --to."
        )
    token_url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    if dry_run:
        access_token = "<dry-run-access-token>"
    else:
        with urllib.request.urlopen(token_url) as resp:
            token_payload = json.loads(resp.read().decode("utf-8"))
        access_token = token_payload.get("access_token")
        if not access_token:
            raise SystemExit(f"WeChat access token error: {token_payload}")
    payload = {
        "touser": to_value,
        "msgtype": "text",
        "text": {"content": message},
    }
    url = (
        "https://api.weixin.qq.com/cgi-bin/message/custom/send"
        f"?access_token={access_token}"
    )
    return http_json(url, payload, {}, dry_run)


def send_imessage(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    handle = recipient or cfg.get("handle")
    if not handle:
        raise SystemExit("iMessage requires --to or imessage.handle in config.")
    escaped_message = message.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "{handle}" of targetService
    send "{escaped_message}" to targetBuddy
end tell
'''
    if dry_run:
        return {"dry_run": True, "channel": "imessage", "handle": handle}
    subprocess.check_call(["osascript", "-e", script])
    return {"ok": True, "channel": "imessage", "handle": handle}


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a message through a local channel config.")
    parser.add_argument(
        "--channel",
        required=True,
        choices=("line", "whatsapp", "wechat", "messenger", "imessage"),
        help="Channel to use.",
    )
    parser.add_argument("--message", required=True, help="Text message to send.")
    parser.add_argument(
        "--to",
        default=None,
        help="Override recipient. If omitted, uses the channel recipient in local config.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the request payload without sending it.",
    )
    args = parser.parse_args()

    channels = load_config()
    cfg = channels.get(args.channel, {})
    if not cfg.get("enabled"):
        raise SystemExit(
            f"Channel '{args.channel}' is not enabled in {CONFIG_PATH}. Run setup first."
        )

    handlers = {
        "line": send_line,
        "whatsapp": send_whatsapp,
        "wechat": send_wechat,
        "messenger": send_messenger,
        "imessage": send_imessage,
    }
    result = handlers[args.channel](cfg, args.to, args.message, args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
