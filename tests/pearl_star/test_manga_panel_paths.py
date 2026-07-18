"""Pearl Star manga dest_path mapping — no macOS /private/var leak."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.pearl_star import manga_panel_paths as mpp


def test_pearl_star_dest_path_no_private_var_on_mac(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Mac .resolve() must not leak /private/var into SSH payload dest_path."""
    repo = tmp_path / "phoenix_omega"
    panel = (
        repo
        / "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
        / "image_bank/L3/kettle_on_burner_boiling.png"
    )
    panel.parent.mkdir(parents=True)
    panel.touch()

    monkeypatch.setenv("PS_LOCAL_REPO", str(repo))
    monkeypatch.setenv("PS_MANGA_OUT_ROOT", "/var/lib/pearl-star/manga_out")

    dest = mpp.pearl_star_dest_path(panel)
    assert dest.startswith("/var/lib/pearl-star/manga_out/")
    assert "/private/var" not in dest
    assert dest.endswith("kettle_on_burner_boiling.png")


def test_linux_dest_path_strips_private_var_prefix() -> None:
    assert str(mpp._linux_dest_path(Path("/private/var/lib/pearl-star/manga_out/x.png"))) == (
        "/var/lib/pearl-star/manga_out/x.png"
    )


def test_join_pearl_star_path_avoids_resolve() -> None:
    root = Path("/var/lib/pearl-star/manga_out")
    joined = mpp._join_pearl_star_path(root, "artifacts", "manga", "panel.png")
    assert str(joined) == "/var/lib/pearl-star/manga_out/artifacts/manga/panel.png"
    assert "/private/var" not in str(joined)
