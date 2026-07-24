from pathlib import Path
import pytest
from PIL import Image
from scripts.publish.bank_image_picker import CoverBankPickError, pick_image
from scripts.storyblocks.license_store import LicenseRecord, LicenseStore

def _licensed(tmp_path: Path, *, topic="anxiety", description="calm breathing for anxiety", verified=True, surface="cover", stock_id="101"):
    image = tmp_path / f"{stock_id}.jpg"; Image.new("RGB", (20, 20), "navy").save(image)
    index = tmp_path / "licenses.jsonl"; store = LicenseStore(bank_root=tmp_path / "bank", index_path=index)
    store.put(LicenseRecord("storyblocks", stock_id, "book", "book-1", "brand", "en_US", surface, "image", "operator", "2026-07-23T00:00:00Z", str(image), metadata={"topic_keys": [topic], "topic_verified": verified, "title": description, "description": description, "keywords": [topic]}))
    return index, store, image

def test_storyblocks_is_selected_and_deterministic(tmp_path):
    index, store, image = _licensed(tmp_path)
    a = pick_image("anxiety", seed="same", index_path=index, license_store=store)
    assert a.path == image and a.provider == "storyblocks" and a == pick_image("anxiety", seed="same", index_path=index, license_store=store)

@pytest.mark.parametrize("topic,description,verified,surface", [("grief", "calm breathing for anxiety", True, "cover"), ("anxiety", "generic landscape", True, "cover"), ("anxiety", "calm breathing for anxiety", False, "cover"), ("anxiety", "calm breathing for anxiety", True, "social")])
def test_mismatch_or_unverified_fails_closed(tmp_path, topic, description, verified, surface):
    index, store, _ = _licensed(tmp_path, topic=topic, description=description, verified=verified, surface=surface)
    with pytest.raises(CoverBankPickError): pick_image("anxiety", index_path=index, license_store=store)

def test_legacy_requires_explicit_escape_hatch(tmp_path):
    legacy = tmp_path / "old.jpg"; Image.new("RGB", (10, 10)).save(legacy)
    row = {"path": str(legacy), "topic_keys": ["anxiety"], "topic_verified": True}
    with pytest.raises(CoverBankPickError): pick_image("anxiety", index_path=tmp_path / "missing.jsonl", legacy_candidates=(row,))
    assert pick_image("anxiety", index_path=tmp_path / "missing.jsonl", legacy_candidates=(row,), allow_legacy_bank=True).provider == "legacy"

def test_missing_local_hd_fails_closed(tmp_path):
    index, store, image = _licensed(tmp_path); image.unlink()
    with pytest.raises(CoverBankPickError): pick_image("anxiety", index_path=index, license_store=store)
