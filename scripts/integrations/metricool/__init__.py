"""Metricool live-posting transport (Pearl_Int).

Payload construction reuses ``phoenix_v4.social.deterministic_social.build_metricool_payload``.
This package owns HTTP transport, brand→blog_id routing, and the publish CLI.
"""

from .client import (
    MetricoolAPIError,
    MetricoolConfigError,
    call_metricool_api,
    get_connected_platforms,
    load_credentials,
    schedule_post,
)

__all__ = [
    "MetricoolAPIError",
    "MetricoolConfigError",
    "call_metricool_api",
    "get_connected_platforms",
    "load_credentials",
    "schedule_post",
]
