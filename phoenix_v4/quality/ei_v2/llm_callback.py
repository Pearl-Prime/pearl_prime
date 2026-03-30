"""
LLM callback contracts for EI V2 quality modules.

These are typing.Protocol definitions only — no network or vendor SDK calls.
Injected callbacks are responsible for API I/O and secrets.

**Determinism:** Heuristic code paths in EI V2 remain deterministic for fixed
inputs. Scores produced via LLM callbacks depend entirely on the injected
callback's behavior; use deterministic mocks in tests and reproducible models in
production when determinism is required.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Protocol, runtime_checkable

# --- Tracker layout (mutable dict shared by wrapped callbacks) ----------------
# Keys are optional; missing keys behave as 0. Use reset_chapter_budget() between
# chapters so per-chapter limits apply correctly.


def reset_chapter_budget(budget_tracker: dict) -> None:
    """Reset the per-chapter call counter; keep per-book counts."""
    budget_tracker["chapter_calls"] = 0


class LLMBudgetExceeded(Exception):
    """Raised when an LLM call would exceed configured budgets (strict mode)."""


@runtime_checkable
class LLMTextCallback(Protocol):
    """Cross-encoder style relevance: prompt + text → score in [0, 1]."""

    def __call__(self, prompt: str, text: str) -> float: ...


@runtime_checkable
class LLMJsonCallback(Protocol):
    """Structured craft-style evaluation."""

    def __call__(self, text: str, aspect: str, question: str) -> dict: ...


@runtime_checkable
class LLMClassifyCallback(Protocol):
    """Safety-style classification over a fixed category vocabulary."""

    def __call__(self, text: str, categories: list[str]) -> dict: ...


def cost_guarded(
    callback: Callable[..., Any],
    *,
    max_calls_per_book: int = 100,
    max_calls_per_chapter: int = 10,
    budget_tracker: Optional[dict] = None,
    raise_on_exhaust: bool = False,
) -> Callable[..., Any]:
    """
    Wrap ``callback`` with book- and chapter-level call budgets.

    The tracker records:
      - ``book_calls`` — total successful invocations this book
      - ``chapter_calls`` — invocations since last ``reset_chapter_budget``

    When a limit would be exceeded **before** scheduling another call:
      - Default (``raise_on_exhaust=False``): return ``None`` without invoking
        ``callback``. Callers should treat ``None`` as "use heuristic fallback".
      - If ``raise_on_exhaust=True``: raise ``LLMBudgetExceeded``.

    On success, counters increment and ``callback(*args, **kwargs)`` is returned.
    """
    tracker = budget_tracker if budget_tracker is not None else {}

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        book_n = int(tracker.get("book_calls", 0))
        chap_n = int(tracker.get("chapter_calls", 0))

        if book_n >= max_calls_per_book or chap_n >= max_calls_per_chapter:
            if raise_on_exhaust:
                raise LLMBudgetExceeded(
                    f"LLM budget exhausted (book={book_n}/{max_calls_per_book}, "
                    f"chapter={chap_n}/{max_calls_per_chapter})"
                )
            return None

        tracker["book_calls"] = book_n + 1
        tracker["chapter_calls"] = chap_n + 1
        return callback(*args, **kwargs)

    return wrapped
