from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

import yaml

from scripts.artifacts import r2_sync


class _Body:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload


class _ShardClient:
    def __init__(self, payloads: dict[str, bytes]):
        self.payloads = payloads

    def get_object(self, *, Bucket: str, Key: str):  # noqa: N803 - boto3 shape
        assert Bucket == "phoenix-omega-artifacts"
        return {"Body": _Body(self.payloads[Key])}


def _source_manifest() -> dict:
    artifacts = [
        {
            "key": "qa_runs/example/a.json",
            "sha256": "a" * 64,
            "bytes": 12,
            "content_type": "application/json",
        },
        {
            "key": "qa_runs/example/b.png",
            "sha256": "b" * 64,
            "bytes": 34,
            "content_type": "image/png",
        },
        {
            "key": "qa_runs/example/c.txt",
            "sha256": "c" * 64,
            "bytes": 56,
            "content_type": "text/plain",
        },
    ]
    return {
        "manifest_schema": "1.0.0",
        "manifest_id": "qa_runs/example",
        "namespace": "pearl_prime_qa_runs",
        "bucket": "phoenix-omega-artifacts",
        "produced_by": "operator",
        "produced_at": "2026-07-24T00:00:00Z",
        "artifacts": artifacts,
        "total_bytes": sum(item["bytes"] for item in artifacts),
        "total_artifacts": len(artifacts),
    }


class ManifestIndexTests(unittest.TestCase):
    def test_index_manifest_round_trip_preserves_order_and_totals(self):
        source = _source_manifest()
        index, payload_items = r2_sync.build_index_manifest(
            source,
            shard_prefix="manifest_shards/v1/qa_runs/example/",
            part_size=2,
        )

        self.assertEqual(index["manifest_schema"], "1.1.0")
        self.assertEqual(index["total_artifacts"], 3)
        self.assertEqual(index["total_bytes"], 102)
        self.assertEqual(len(index["parts"]), 2)
        self.assertFalse(r2_sync._validate_manifest(index))

        payloads = dict(payload_items)
        loaded = r2_sync._load_indexed_artifacts(index, _ShardClient(payloads))
        self.assertEqual(loaded, source["artifacts"])

    def test_index_manifest_rejects_tampered_part(self):
        source = _source_manifest()
        index, payload_items = r2_sync.build_index_manifest(
            source,
            shard_prefix="manifest_shards/v1/qa_runs/example/",
            part_size=2,
        )
        payloads = dict(payload_items)
        first_key = index["parts"][0]["key"]
        payloads[first_key] += b"tampered"

        with self.assertRaisesRegex(r2_sync.R2SyncError, "bytes mismatch"):
            r2_sync._load_indexed_artifacts(index, _ShardClient(payloads))

    def test_part_names_are_content_addressed_and_deterministic(self):
        source = _source_manifest()
        index_a, payloads_a = r2_sync.build_index_manifest(
            source,
            shard_prefix="manifest_shards/v1/qa_runs/example/",
            part_size=2,
        )
        index_b, payloads_b = r2_sync.build_index_manifest(
            source,
            shard_prefix="manifest_shards/v1/qa_runs/example/",
            part_size=2,
        )

        self.assertEqual(index_a, index_b)
        self.assertEqual(payloads_a, payloads_b)
        for part, (_key, payload) in zip(index_a["parts"], payloads_a):
            self.assertEqual(part["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertIn(part["sha256"][:12], part["key"])

    def test_config_preserves_voice_namespace_and_adds_cleanup_namespaces(self):
        config = yaml.safe_load(r2_sync.CONFIG.read_text(encoding="utf-8"))
        namespaces = config["namespaces"]

        self.assertIn("social_media_voice_bank", namespaces)
        self.assertEqual(namespaces["misc_working_banks"]["prefix"], "misc/")
        self.assertEqual(
            namespaces["manga_catalog_render_cache"]["prefix"],
            "manga_catalog_cache/",
        )
        self.assertEqual(config["manifests"]["shard_prefix"], "manifest_shards/v1/")

    def test_push_is_parallel_but_manifest_order_stays_sorted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src = root / "source"
            src.mkdir()
            (src / "b.txt").write_text("b", encoding="utf-8")
            (src / "a.txt").write_text("a", encoding="utf-8")

            uploaded = []

            class Client:
                def put_object(self, **kwargs):
                    uploaded.append(kwargs["Key"])

            captured = {}
            args = Namespace(
                namespace="tmp",
                src=str(src),
                manifest=str(root / "manifest.yaml"),
                series_id=None,
                book_id=None,
                run_id="test",
                dry_run=False,
                workers=8,
            )
            config = {
                "buckets": {"artifacts": {"name": "phoenix-omega-artifacts"}},
                "namespaces": {"tmp": {"prefix": "tmp/"}},
            }
            with (
                mock.patch.object(r2_sync, "_load_config", return_value=config),
                mock.patch.object(r2_sync, "_r2_client", return_value=Client()),
                mock.patch.object(
                    r2_sync,
                    "_write_manifest",
                    side_effect=lambda _path, data: captured.update(data),
                ),
                mock.patch.dict(
                    os.environ,
                    {"PHOENIX_OMEGA_REMOTE": "local-override"},
                    clear=False,
                ),
            ):
                self.assertEqual(r2_sync.cmd_push(args), 0)

            self.assertEqual(
                sorted(uploaded),
                ["tmp/test/a.txt", "tmp/test/b.txt"],
            )
            self.assertEqual(
                [item["key"] for item in captured["artifacts"]],
                ["tmp/test/a.txt", "tmp/test/b.txt"],
            )
            self.assertEqual(captured["produced_by"], "operator")


if __name__ == "__main__":
    unittest.main()
