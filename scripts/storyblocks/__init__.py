"""Pearl Prime Storyblocks integration (phoenix_omega substrate).

EULA ground truth: docs/STORYBLOCKS_EULA_COMPLIANCE.md
Pearl Prime re-scope: docs/STORYBLOCKS_PEARL_PRIME_RESCOPE.md

AI / ML wall-off (§B): Stock Files, keywords, and embeddings derived from
Storyblocks assets MUST NOT enter model-training or fine-tuning corpora.
Selection-assist use of preview thumbnails is allowed only when explicitly
walled off from training export paths.
"""

from __future__ import annotations

from scripts.storyblocks.consumer_guard import (
    UnlicensedStoryblocksAssetError,
    assert_storyblocks_licensed_for_consumer,
)
from scripts.storyblocks.exceptions import (
    StoryblocksAuthError,
    StoryblocksConfigError,
    StoryblocksError,
    StoryblocksMauCapError,
    StoryblocksRateLimitError,
)

__all__ = [
    "StoryblocksAuthError",
    "StoryblocksConfigError",
    "StoryblocksError",
    "StoryblocksMauCapError",
    "StoryblocksRateLimitError",
    "UnlicensedStoryblocksAssetError",
    "assert_storyblocks_licensed_for_consumer",
]
