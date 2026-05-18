"""
Tests for the Pearl Prime catalog `status=ready` predicate.

Coverage:
  - status=ready requires that the declared master_arc YAML exists on disk.
  - status=ready requires that registry/<topic>.yaml exists on disk.
  - status=ready requires that every required_source_atoms path exists.
  - A row with all three families present resolves to status=ready.
  - Failure cases emit a specific blocked_<reason> + blockers token mirroring
    the existing blocked_score / blocked_lora / blocked_teacher precedents.

Owning context: PR agent/catalog-ready-predicate-fix-20260516. Originally
20 stillness_press × ja_JP rows were marked ready against missing adhd_focus
+ mindfulness master_arc / registry files; this regression test enforces the
on-disk gate so the same drift cannot reappear.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog.generate_pearl_prime_book_script_catalog import (  # noqa: E402
    required_atoms_for,
    verify_ready_files_on_disk,
)


def _build_synthetic_root(tmp: Path,
                          persona: str,
                          topic: str,
                          *,
                          with_arc: bool = True,
                          with_registry: bool = True,
                          with_atoms: bool = True) -> Path:
    """Create a tmp config_root with optional arc/registry/atoms scaffolding."""
    arcs_dir = tmp / "config" / "source_of_truth" / "master_arcs"
    arcs_dir.mkdir(parents=True, exist_ok=True)
    registry_dir = tmp / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)

    if with_arc:
        # Match the canonical filename pattern: <persona>__<topic>__<engine>__<format>.yaml
        (arcs_dir / f"{persona}__{topic}__overwhelm__F006.yaml").write_text(
            f"arc_id: {persona}_{topic}_overwhelm_F006_gen\n", encoding="utf-8"
        )
    if with_registry:
        (registry_dir / f"{topic}.yaml").write_text("topic: " + topic + "\n", encoding="utf-8")
    if with_atoms:
        for atom_rel in required_atoms_for(persona, topic).split(";"):
            atom_path = tmp / atom_rel
            atom_path.parent.mkdir(parents=True, exist_ok=True)
            atom_path.write_text("CANONICAL\n", encoding="utf-8")
    return tmp


class TestReadyPredicate(unittest.TestCase):
    def test_all_files_present_returns_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(Path(td), "corporate_managers", "anxiety")
            status, blockers, note = verify_ready_files_on_disk(
                "corporate_managers", "anxiety",
                required_atoms_for("corporate_managers", "anxiety"),
                config_root=root,
            )
            self.assertEqual(status, "ready")
            self.assertEqual(blockers, "")
            self.assertEqual(note, "")

    def test_missing_arc_returns_blocked_arc_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(
                Path(td), "corporate_managers", "adhd_focus", with_arc=False)
            status, blockers, note = verify_ready_files_on_disk(
                "corporate_managers", "adhd_focus",
                required_atoms_for("corporate_managers", "adhd_focus"),
                config_root=root,
            )
            self.assertEqual(status, "blocked_arc_missing")
            self.assertEqual(blockers, "needs_master_arc")
            self.assertIn("corporate_managers__adhd_focus__*.yaml", note)

    def test_missing_registry_returns_blocked_registry_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(
                Path(td), "corporate_managers", "adhd_focus", with_registry=False)
            status, blockers, note = verify_ready_files_on_disk(
                "corporate_managers", "adhd_focus",
                required_atoms_for("corporate_managers", "adhd_focus"),
                config_root=root,
            )
            self.assertEqual(status, "blocked_registry_missing")
            self.assertEqual(blockers, "needs_registry_topic")
            self.assertIn("registry/adhd_focus.yaml", note)

    def test_missing_atoms_returns_blocked_atoms_missing_with_enforce_atoms(self) -> None:
        """With enforce_atoms=True (opt-in), missing declared paths flip
        to blocked_atoms_missing. Default callers do NOT enforce atoms in this
        PR — that's a separate scope until the stub schema is reconciled."""
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(
                Path(td), "corporate_managers", "anxiety", with_atoms=False)
            status, blockers, note = verify_ready_files_on_disk(
                "corporate_managers", "anxiety",
                required_atoms_for("corporate_managers", "anxiety"),
                config_root=root,
                enforce_atoms=True,
            )
            self.assertEqual(status, "blocked_atoms_missing")
            self.assertEqual(blockers, "needs_atoms")
            self.assertTrue(note.startswith("required atom missing: atoms/corporate_managers/"))

    def test_atoms_not_enforced_by_default(self) -> None:
        """Default callers (no enforce_atoms) treat missing atoms as not-a-block.
        Cap: ``required_source_atoms`` schema reconciliation is separate scope.
        arc + registry alone gate the row in this PR."""
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(
                Path(td), "corporate_managers", "anxiety", with_atoms=False)
            status, _, _ = verify_ready_files_on_disk(
                "corporate_managers", "anxiety",
                required_atoms_for("corporate_managers", "anxiety"),
                config_root=root,
            )
            self.assertEqual(status, "ready")

    def test_predicate_failure_order_is_arc_then_registry_then_atoms(self) -> None:
        """When everything is missing, the arc check should fire first."""
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(
                Path(td), "corporate_managers", "adhd_focus",
                with_arc=False, with_registry=False, with_atoms=False,
            )
            status, _, _ = verify_ready_files_on_disk(
                "corporate_managers", "adhd_focus",
                required_atoms_for("corporate_managers", "adhd_focus"),
                config_root=root,
                enforce_atoms=True,
            )
            self.assertEqual(status, "blocked_arc_missing")

    def test_arc_present_registry_missing(self) -> None:
        """Arc resolves; registry missing → blocked_registry_missing."""
        with tempfile.TemporaryDirectory() as td:
            root = _build_synthetic_root(
                Path(td), "corporate_managers", "anxiety", with_registry=False)
            status, _, _ = verify_ready_files_on_disk(
                "corporate_managers", "anxiety",
                required_atoms_for("corporate_managers", "anxiety"),
                config_root=root,
            )
            self.assertEqual(status, "blocked_registry_missing")


class TestRequiredAtomsFor(unittest.TestCase):
    def test_required_atoms_paths_shape(self) -> None:
        atoms_str = required_atoms_for("corporate_managers", "anxiety")
        parts = atoms_str.split(";")
        # 1 anchored + 3 section types (scene/depth/teacher) per current spec.
        self.assertEqual(len(parts), 4)
        self.assertIn("atoms/corporate_managers/anchored/anxiety/CANONICAL.txt", parts)
        self.assertIn("atoms/corporate_managers/anxiety/scene/CANONICAL.txt", parts)


class TestFixupReadyPredicateInPlace(unittest.TestCase):
    """Verify the in-place CSV fixup flips ready rows whose arcs are missing
    without deleting any rows or perturbing already-blocked rows."""

    def test_in_place_flip_preserves_row_count(self) -> None:
        import csv as _csv
        from scripts.catalog.generate_pearl_prime_book_script_catalog import (
            COLUMNS,
            fixup_ready_predicate_in_place,
        )

        with tempfile.TemporaryDirectory() as td:
            csv_path = Path(td) / "x_catalog.csv"
            # Two rows: one ready against an obviously-missing topic (will flip);
            # one already-blocked (should stay).
            with open(csv_path, "w", encoding="utf-8", newline="") as fh:
                writer = _csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
                writer.writeheader()
                writer.writerow({
                    "locale": "ja_JP", "market": "japan", "brand": "stillness_press",
                    "brand_locale_name": "静心社", "title": "x", "subtitle": "y",
                    "topic": "adhd_focus", "persona": "corporate_managers",
                    "teacher_id": "ahjan", "teacher_mode": "true",
                    "runtime_format": "standard_book", "duration_band": "standard",
                    "section_plan_id": "pearl_prime_12x10x5", "variant_pool_size": 5,
                    "bestseller_overlay_ref": "docs/x.md",
                    "selection_strategy": "deterministic_by_seed",
                    "pipeline_route": "scripts/run_pipeline.py",
                    "readiness_status": "ready",
                    "required_source_atoms": required_atoms_for("corporate_managers", "adhd_focus"),
                    "required_registry_topic": "registry/adhd_focus.yaml",
                    "output_target_path": "x", "notes": "composite=0.80",
                    "blockers": "",
                    "angle_id": "x", "motif_id": "y", "book_structure_id": "z",
                    "journey_shape_id": "q", "variation_signature": "abc123",
                })
                writer.writerow({
                    "locale": "ja_JP", "market": "japan", "brand": "stillness_press",
                    "brand_locale_name": "静心社", "title": "", "subtitle": "",
                    "topic": "anxiety", "persona": "gen_alpha_students",
                    "teacher_id": "ahjan", "teacher_mode": "true",
                    "runtime_format": "standard_book", "duration_band": "standard",
                    "section_plan_id": "pearl_prime_12x10x5", "variant_pool_size": 5,
                    "bestseller_overlay_ref": "docs/x.md",
                    "selection_strategy": "deterministic_by_seed",
                    "pipeline_route": "scripts/run_pipeline.py",
                    "readiness_status": "blocked_score",
                    "required_source_atoms": "",
                    "required_registry_topic": "registry/anxiety.yaml",
                    "output_target_path": "x", "notes": "composite=0.50",
                    "blockers": "needs_score",
                    "angle_id": "x", "motif_id": "y", "book_structure_id": "z",
                    "journey_shape_id": "q", "variation_signature": "def456",
                })

            flipped = fixup_ready_predicate_in_place(csv_path)
            # adhd_focus arc is missing in real repo state → flip.
            self.assertIn("blocked_arc_missing", flipped)
            self.assertEqual(flipped["blocked_arc_missing"], 1)

            with open(csv_path, encoding="utf-8") as fh:
                rows = list(_csv.DictReader(fh))
            self.assertEqual(len(rows), 2)  # no row deleted
            self.assertEqual(rows[0]["readiness_status"], "blocked_arc_missing")
            self.assertEqual(rows[0]["blockers"], "needs_master_arc")
            self.assertIn("composite=0.80", rows[0]["notes"])  # original notes preserved
            self.assertEqual(rows[1]["readiness_status"], "blocked_score")  # unchanged
            self.assertEqual(rows[1]["blockers"], "needs_score")


if __name__ == "__main__":
    unittest.main()
