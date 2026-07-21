"""Metricool HTTP client — live transport (no Django).

Ported from ``docs/metricool_utils.py`` (reference-only): keeps X-Mc-Auth,
``https://app.metricool.com/api/v2/``, 3× retry [2, 4, 8]s, 4xx-no-retry,
and Pinterest ``brandId`` vs ``blogId``. Credentials come from env only.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://app.metricool.com/api/v2/"
RETRY_DELAYS_S = (2, 4, 8)
MAX_ATTEMPTS = 3


class MetricoolConfigError(ValueError):
    """Invalid client parameters or missing credentials."""


class MetricoolAPIError(RequestException):
    """Metricool HTTP / transport failure after policy-compliant retries."""


def load_credentials() -> dict[str, str]:
    """Load Metricool creds from environment (Keychain-loaded via registry)."""
    api_key = (os.environ.get("METRICOOL_API_KEY") or "").strip()
    user_id = (os.environ.get("METRICOOL_USER_ID") or "").strip()
    base_url = (os.environ.get("METRICOOL_BASE_URL") or DEFAULT_BASE_URL).strip()
    if base_url and not base_url.endswith("/"):
        base_url = base_url + "/"
    return {"api_key": api_key, "user_id": user_id, "base_url": base_url}


def call_metricool_api(
    endpoint: str,
    method: str,
    payload: dict[str, Any] | None,
    user_id: str,
    blog_id: str,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout: int = 30,
) -> dict[str, Any] | list[Any]:
    """Base API wrapper with exponential backoff.

    Retries on 5xx / timeout / connection errors. Never retries 4xx.
    Pinterest endpoints use ``brandId``; all others use ``blogId``.
    """
    if not endpoint or not isinstance(endpoint, str):
        raise MetricoolConfigError("Invalid endpoint parameter: must be a non-empty string")

    method = method.upper()
    if method not in ("GET", "POST", "DELETE"):
        raise MetricoolConfigError(
            f'Invalid method parameter: must be "GET", "POST", or "DELETE", got "{method}"'
        )

    if not user_id or not blog_id or not api_key:
        raise MetricoolConfigError("Missing required parameters: user_id, blog_id, or api_key")

    if method == "POST" and (payload is None or not isinstance(payload, dict)):
        raise MetricoolConfigError("Invalid payload parameter: POST requests require a non-null dict payload")

    if base_url and not base_url.endswith("/"):
        base_url = base_url + "/"

    blog_param_name = "brandId" if "pinterest" in endpoint.lower() else "blogId"
    full_url = f"{base_url}{endpoint}?userId={user_id}&{blog_param_name}={blog_id}"

    last_error: Exception | None = None
    logger.info(
        "[METRICOOL] %s %s (user_id=%s, %s=%s)",
        method,
        endpoint,
        user_id,
        blog_param_name,
        blog_id,
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            headers = {
                "X-Mc-Auth": api_key,
                "Content-Type": "application/json",
            }
            if method == "POST":
                response = requests.post(full_url, json=payload, headers=headers, timeout=timeout)
            elif method == "DELETE":
                if payload is not None:
                    response = requests.delete(full_url, json=payload, headers=headers, timeout=timeout)
                else:
                    response = requests.delete(full_url, headers=headers, timeout=timeout)
            else:
                response = requests.get(full_url, headers=headers, timeout=timeout)

            status_code = response.status_code

            if 200 <= status_code < 300:
                try:
                    return response.json()
                except ValueError as parse_error:
                    raise MetricoolAPIError(
                        f"Failed to parse JSON response: {parse_error}. "
                        f"Response: {response.text[:200]}"
                    ) from parse_error

            if 400 <= status_code < 500:
                response_body = response.text[:500]
                error_message = f"Metricool API error {status_code}"
                try:
                    error_data = response.json()
                    detail = (
                        error_data.get("error")
                        or error_data.get("message")
                        or error_data.get("detail")
                    )
                    if detail:
                        error_message += f": {detail}"
                    else:
                        error_message += f": {response_body}"
                except ValueError:
                    error_message += f": {response_body}"
                raise MetricoolAPIError(error_message)

            # 5xx or unexpected — retry
            last_error = MetricoolAPIError(
                f"Metricool API server/unexpected status {status_code}: {response.text[:200]}"
            )
            if attempt < MAX_ATTEMPTS:
                delay = RETRY_DELAYS_S[attempt - 1]
                logger.warning(
                    "[METRICOOL] %s %s -> %s; retry in %ss (attempt %s/%s)",
                    method,
                    endpoint,
                    status_code,
                    delay,
                    attempt,
                    MAX_ATTEMPTS,
                )
                time.sleep(delay)
                continue

        except MetricoolAPIError:
            raise
        except (Timeout, ConnectionError) as network_error:
            last_error = network_error
            if attempt < MAX_ATTEMPTS:
                delay = RETRY_DELAYS_S[attempt - 1]
                logger.warning(
                    "[METRICOOL] network/timeout on %s %s; retry in %ss (attempt %s/%s)",
                    method,
                    endpoint,
                    delay,
                    attempt,
                    MAX_ATTEMPTS,
                )
                time.sleep(delay)
                continue

    raise MetricoolAPIError(
        f"Metricool API request failed after {MAX_ATTEMPTS} attempts. Last error: {last_error}"
    )


def schedule_post(
    post_payload: dict[str, Any],
    user_id: str,
    blog_id: str,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    """POST ``scheduler/posts`` and return the Metricool response (includes postId)."""
    if not post_payload or not isinstance(post_payload, dict):
        raise MetricoolConfigError("Invalid post_payload: must be a non-null dict")

    required_fields = ("media", "publicationDate", "providers")
    missing = [field for field in required_fields if field not in post_payload]
    if missing:
        raise MetricoolConfigError(f"Missing required payload fields: {', '.join(missing)}")

    response = call_metricool_api(
        endpoint="scheduler/posts",
        method="POST",
        payload=post_payload,
        user_id=user_id,
        blog_id=blog_id,
        api_key=api_key,
        base_url=base_url,
    )
    if isinstance(response, dict):
        return response
    return {}


def list_scheduler_posts(
    user_id: str,
    blog_id: str,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    *,
    start: str | None = None,
    end: str | None = None,
    timezone: str | None = None,
    post_id: str | None = None,
) -> dict[str, Any] | list[Any]:
    """GET ``scheduler/posts`` — auth proof and postId poll (no publish).

    Metricool returns an empty list unless a date window is supplied for range
    queries. Pass ``start``/``end`` (ISO local datetimes) or ``post_id`` for a
    single-post fetch (``scheduler/posts/{post_id}``).
    """
    if not user_id or not blog_id or not api_key:
        raise MetricoolConfigError("Missing required parameters: user_id, blog_id, or api_key")

    if base_url and not base_url.endswith("/"):
        base_url = base_url + "/"

    if post_id:
        endpoint = f"scheduler/posts/{post_id}"
        return call_metricool_api(
            endpoint=endpoint,
            method="GET",
            payload=None,
            user_id=user_id,
            blog_id=blog_id,
            api_key=api_key,
            base_url=base_url,
        )

    # Range GET needs extra query params beyond userId/blogId — build URL manually
    # but reuse the same auth/retry policy as call_metricool_api for 5xx.
    blog_param_name = "blogId"
    query = [f"userId={user_id}", f"{blog_param_name}={blog_id}"]
    if start:
        query.append(f"start={start}")
    if end:
        query.append(f"end={end}")
    if timezone:
        query.append(f"timezone={timezone}")
    full_url = f"{base_url}scheduler/posts?" + "&".join(query)

    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            headers = {"X-Mc-Auth": api_key, "Content-Type": "application/json"}
            response = requests.get(full_url, headers=headers, timeout=30)
            status_code = response.status_code
            if 200 <= status_code < 300:
                try:
                    return response.json()
                except ValueError as parse_error:
                    raise MetricoolAPIError(
                        f"Failed to parse JSON response: {parse_error}. "
                        f"Response: {response.text[:200]}"
                    ) from parse_error
            if 400 <= status_code < 500:
                raise MetricoolAPIError(
                    f"Metricool API error {status_code}: {response.text[:500]}"
                )
            last_error = MetricoolAPIError(f"Metricool API server error {status_code}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAYS_S[attempt - 1])
                continue
        except (Timeout, ConnectionError) as network_error:
            last_error = network_error
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAYS_S[attempt - 1])
                continue
            break
    raise MetricoolAPIError(f"list_scheduler_posts failed after retries: {last_error}")


def get_connected_platforms(
    blog_id: str,
    user_id: str,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    """GET ``settings/brands/:blogId`` — connected networks for a Metricool brand."""
    response = call_metricool_api(
        endpoint=f"settings/brands/{blog_id}",
        method="GET",
        payload=None,
        user_id=user_id,
        blog_id=blog_id,
        api_key=api_key,
        base_url=base_url,
    )
    if isinstance(response, dict):
        return response
    return {}
