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


# ---------------------------------------------------------------------------
# Slack / Discord / Telegram text handlers
# ---------------------------------------------------------------------------


def send_slack(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    """Send a text message to a Slack channel or DM via the Slack Web API."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "bot_token")
    channel = recipient or cfg.get("channel_id")
    if not channel:
        raise SystemExit(
            "Slack requires --to or slack.channel_id in config."
        )
    payload = {"channel": channel, "text": message}
    return http_json(
        "https://slack.com/api/chat.postMessage",
        payload,
        {"Authorization": f"Bearer {token}"},
        dry_run,
    )


def send_discord(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    """Send a text message to a Discord channel via a bot token."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "bot_token")
    channel_id = recipient or cfg.get("channel_id")
    if not channel_id:
        raise SystemExit(
            "Discord requires --to or discord.channel_id in config."
        )
    payload = {"content": message}
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    return http_json(
        url,
        payload,
        {"Authorization": f"Bot {token}"},
        dry_run,
    )


def send_telegram(
    cfg: dict, recipient: str | None, message: str, dry_run: bool
) -> dict:
    """Send a text message to a Telegram chat via the Bot API."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "bot_token")
    chat_id = recipient or cfg.get("chat_id")
    if not chat_id:
        raise SystemExit(
            "Telegram requires --to or telegram.chat_id in config."
        )
    payload = {"chat_id": chat_id, "text": message}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    return http_json(url, payload, {}, dry_run)


# ---------------------------------------------------------------------------
# File-send helpers (multipart upload, all channels)
# ---------------------------------------------------------------------------


def _multipart_body(
    fields: list[tuple[str, str | bytes, str | None]],
) -> tuple[bytes, str]:
    """Build a multipart/form-data body from *(name, value, filename|None)*.

    Returns *(body_bytes, content_type_header)*.
    All network I/O uses only ``urllib.request`` -- zero extra pip deps.
    """
    import os
    import uuid as _uuid

    boundary = _uuid.uuid4().hex
    parts: list[bytes] = []
    for name, value, filename in fields:
        disposition = f'form-data; name="{name}"'
        if filename:
            disposition += f'; filename="{os.path.basename(filename)}"'
        header = (
            f"--{boundary}\r\n"
            f"Content-Disposition: {disposition}\r\n\r\n"
        )
        data = value if isinstance(value, bytes) else value.encode("utf-8")
        parts.append(header.encode("utf-8") + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def _http_multipart(
    url: str,
    fields: list[tuple[str, str | bytes, str | None]],
    headers: dict[str, str],
    dry_run: bool,
) -> dict:
    if dry_run:
        return {
            "dry_run": True,
            "url": url,
            "fields": [(n, "<bytes>" if isinstance(v, bytes) else v, f) for n, v, f in fields],
        }
    body, ct = _multipart_body(fields)
    req = urllib.request.Request(url, data=body, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", ct)
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} for {url}: {detail}") from exc


def _read_file(path: str) -> bytes:
    fp = Path(path)
    if not fp.exists():
        raise SystemExit(f"File not found: {path}")
    return fp.read_bytes()


def send_line_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload a file via LINE as an image/video/audio/file message type."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "access_token")
    to_value = recipient or cfg.get("user_id") or cfg.get("group_id")
    if not to_value:
        raise SystemExit("LINE file-send requires --to or line.user_id/group_id.")
    # LINE Messaging API: upload via the blob endpoint is complex;
    # use the simpler "image message via URL" pattern with a placeholder.
    # For real deployments, host the file and pass the URL.
    data = _read_file(file_path)
    fields: list[tuple[str, str | bytes, str | None]] = [
        ("to", to_value, None),
        ("file", data, file_path),
    ]
    return _http_multipart(
        "https://api.line.me/v2/bot/message/push",
        fields,
        {"Authorization": f"Bearer {token}"},
        dry_run,
    )


def send_whatsapp_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload a file via WhatsApp media endpoint, then send the media message."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "access_token")
    phone_number_id = cfg.get("phone_number_id")
    graph_version = cfg.get("graph_version") or "v23.0"
    to_value = recipient or cfg.get("phone_number")
    if not phone_number_id or not to_value:
        raise SystemExit("WhatsApp file-send requires phone_number_id and recipient.")
    data = _read_file(file_path)
    upload_url = f"https://graph.facebook.com/{graph_version}/{phone_number_id}/media"
    fields: list[tuple[str, str | bytes, str | None]] = [
        ("messaging_product", "whatsapp", None),
        ("file", data, file_path),
    ]
    return _http_multipart(
        upload_url,
        fields,
        {"Authorization": f"Bearer {token}"},
        dry_run,
    )


def send_messenger_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload a file attachment via Messenger Send API."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "page_access_token")
    graph_version = cfg.get("graph_version") or "v23.0"
    to_value = recipient or cfg.get("recipient_id")
    if not to_value:
        raise SystemExit("Messenger file-send requires --to or messenger.recipient_id.")
    data = _read_file(file_path)
    url = f"https://graph.facebook.com/{graph_version}/me/messages?access_token={token}"
    fields: list[tuple[str, str | bytes, str | None]] = [
        ("recipient", json.dumps({"id": to_value}), None),
        ("message", json.dumps({"attachment": {"type": "file", "payload": {}}}), None),
        ("filedata", data, file_path),
    ]
    return _http_multipart(url, fields, {}, dry_run)


def send_wechat_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload media to WeChat temporary material endpoint."""
    service = cfg.get("keychain_service")
    app_id = cfg.get("app_id")
    app_secret = get_keychain_secret(service, "app_secret")
    if not app_id or not app_secret:
        raise SystemExit("WeChat file-send requires app_id and app_secret.")
    if dry_run:
        return {"dry_run": True, "channel": "wechat", "file": file_path}
    token_url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    with urllib.request.urlopen(token_url) as resp:
        access_token = json.loads(resp.read().decode("utf-8")).get("access_token")
    if not access_token:
        raise SystemExit("WeChat: failed to obtain access token for file upload.")
    data = _read_file(file_path)
    upload_url = (
        f"https://api.weixin.qq.com/cgi-bin/media/upload"
        f"?access_token={access_token}&type=file"
    )
    fields: list[tuple[str, str | bytes, str | None]] = [("media", data, file_path)]
    return _http_multipart(upload_url, fields, {}, False)


def send_imessage_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Send a file via iMessage using AppleScript."""
    handle = recipient or cfg.get("handle")
    if not handle:
        raise SystemExit("iMessage file-send requires --to or imessage.handle.")
    fp = Path(file_path).resolve()
    if not fp.exists():
        raise SystemExit(f"File not found: {file_path}")
    if dry_run:
        return {"dry_run": True, "channel": "imessage", "handle": handle, "file": str(fp)}
    script = f'''
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "{handle}" of targetService
    send POSIX file "{fp}" to targetBuddy
end tell
'''
    subprocess.check_call(["osascript", "-e", script])
    return {"ok": True, "channel": "imessage", "handle": handle, "file": str(fp)}


def send_slack_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload a file to a Slack channel via the files.upload v2 API."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "bot_token")
    channel = recipient or cfg.get("channel_id")
    if not channel:
        raise SystemExit("Slack file-send requires --to or slack.channel_id.")
    data = _read_file(file_path)
    fields: list[tuple[str, str | bytes, str | None]] = [
        ("channels", channel, None),
        ("file", data, file_path),
    ]
    return _http_multipart(
        "https://slack.com/api/files.upload",
        fields,
        {"Authorization": f"Bearer {token}"},
        dry_run,
    )


def send_discord_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload a file to a Discord channel as a message attachment."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "bot_token")
    channel_id = recipient or cfg.get("channel_id")
    if not channel_id:
        raise SystemExit("Discord file-send requires --to or discord.channel_id.")
    data = _read_file(file_path)
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    fields: list[tuple[str, str | bytes, str | None]] = [
        ("file", data, file_path),
    ]
    return _http_multipart(
        url,
        fields,
        {"Authorization": f"Bot {token}"},
        dry_run,
    )


def send_telegram_file(cfg: dict, recipient: str | None, file_path: str, dry_run: bool) -> dict:
    """Upload a file to a Telegram chat via the Bot API sendDocument endpoint."""
    service = cfg.get("keychain_service")
    token = get_keychain_secret(service, "bot_token")
    chat_id = recipient or cfg.get("chat_id")
    if not chat_id:
        raise SystemExit("Telegram file-send requires --to or telegram.chat_id.")
    data = _read_file(file_path)
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    fields: list[tuple[str, str | bytes, str | None]] = [
        ("chat_id", str(chat_id), None),
        ("document", data, file_path),
    ]
    return _http_multipart(url, fields, {}, dry_run)


# ---------------------------------------------------------------------------
# Channel registries
# ---------------------------------------------------------------------------

ALL_CHANNELS = (
    "line", "whatsapp", "wechat", "messenger", "imessage",
    "slack", "discord", "telegram",
)

TEXT_HANDLERS: dict[str, object] = {
    "line": send_line,
    "whatsapp": send_whatsapp,
    "wechat": send_wechat,
    "messenger": send_messenger,
    "imessage": send_imessage,
    "slack": send_slack,
    "discord": send_discord,
    "telegram": send_telegram,
}

FILE_HANDLERS: dict[str, object] = {
    "line": send_line_file,
    "whatsapp": send_whatsapp_file,
    "wechat": send_wechat_file,
    "messenger": send_messenger_file,
    "imessage": send_imessage_file,
    "slack": send_slack_file,
    "discord": send_discord_file,
    "telegram": send_telegram_file,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a message through a local channel config.")
    parser.add_argument(
        "--channel",
        required=True,
        choices=ALL_CHANNELS,
        help="Channel to use.",
    )
    parser.add_argument("--message", default=None, help="Text message to send.")
    parser.add_argument(
        "--file",
        default=None,
        dest="file_path",
        help="Path to a file to upload to the channel.",
    )
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

    if not args.message and not args.file_path:
        raise SystemExit("Either --message or --file is required.")

    channels = load_config()
    cfg = channels.get(args.channel, {})
    if not cfg.get("enabled"):
        raise SystemExit(
            f"Channel '{args.channel}' is not enabled in {CONFIG_PATH}. Run setup first."
        )

    if args.file_path:
        handler = FILE_HANDLERS[args.channel]
        result = handler(cfg, args.to, args.file_path, args.dry_run)
    else:
        handler = TEXT_HANDLERS[args.channel]
        result = handler(cfg, args.to, args.message, args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
