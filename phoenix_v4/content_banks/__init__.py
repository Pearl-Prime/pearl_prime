"""Content fragment banks (YAML) — loader, selector, doctrine quarantine, selection logging."""

from __future__ import annotations

from phoenix_v4.content_banks.loader import ContentBankRegistry, get_content_bank_registry
from phoenix_v4.content_banks.quarantine import apply_doctrine_quarantine
from phoenix_v4.content_banks.selector import FragmentContext, select_fragment
from phoenix_v4.content_banks.session import ContentBankSession, get_or_create_bank_session
from phoenix_v4.content_banks.variant_log import VariantSelectionLogger

__all__ = [
    "ContentBankRegistry",
    "ContentBankSession",
    "FragmentContext",
    "VariantSelectionLogger",
    "apply_doctrine_quarantine",
    "get_content_bank_registry",
    "get_or_create_bank_session",
    "select_fragment",
]
