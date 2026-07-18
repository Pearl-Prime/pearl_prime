#!/usr/bin/env python3
"""
Writing Campaign Orchestrator — run_writing_campaign.py

Generates a campaign plan for ~7,152 new atoms in English.
Does NOT call any external API. Designed to be driven from Claude Code
sessions using the Agent tool (zero external API cost).

Usage:
  # Generate campaign plan (JSON file for Claude Code to iterate)
  python scripts/atom_writing/run_writing_campaign.py --plan

  # List available tasks
  python scripts/atom_writing/run_writing_campaign.py --list-tasks

  # Generate plan for single task
  python scripts/atom_writing/run_writing_campaign.py --plan --task teacher_stories

  # Dry run — show prompts without generating plan
  python scripts/atom_writing/run_writing_campaign.py --dry-run

  # Show campaign stats
  python scripts/atom_writing/run_writing_campaign.py --stats

How to execute the plan from Claude Code:
  1. Run: python scripts/atom_writing/run_writing_campaign.py --plan
  2. In Claude Code, read artifacts/atom_writing/campaign_plan.json
  3. For each item, spawn an Agent subagent with the system+user prompt
  4. Parse the subagent output and write via write_canonical()
  5. Validate with validate_output()
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml as _yaml

    def _load_yaml(p: Path) -> dict:
        return _yaml.safe_load(p.read_text()) or {}
except ImportError:
    _yaml = None  # type: ignore

    def _load_yaml(p: Path) -> dict:
        """Minimal YAML parser for flat config files."""
        result: dict[str, Any] = {}
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                val = val.strip().strip('"').strip("'")
                # Try to parse numbers and booleans
                if val.lower() == "true":
                    result[key.strip()] = True
                elif val.lower() == "false":
                    result[key.strip()] = False
                elif val.replace(".", "", 1).isdigit():
                    result[key.strip()] = float(val) if "." in val else int(val)
                else:
                    result[key.strip()] = val
        return result


from scripts.atom_writing.write_atoms_claude import (
    ALL_PERSONAS,
    ALL_TOPICS,
    ENGINE_DIRS,
    build_system_prompt,
    build_user_prompt,
    generate_campaign_plan,
    load_existing_examples,
    validate_output,
    write_atoms,
    write_canonical,
)
from scripts.atom_writing.write_teacher_stories import (
    ALL_TEACHERS,
    TEACHER_STORY_SYSTEM_PROMPT,
    build_teacher_prompt,
    count_existing_stories,
    load_existing_stories,
    load_teacher_doctrine,
    load_teacher_kb,
    write_teacher_stories,
    write_teacher_yaml_files,
)

logger = logging.getLogger("writing_campaign")

# ─── CONFIGURATION ──────────────────────────────────────────────────────────

DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "atom_writing" / "writing_campaign_config.yaml"
DEFAULT_LOG_PATH = REPO_ROOT / "artifacts" / "atom_writing" / "campaign_log.jsonl"

# New topics to be written across all personas
NEW_TOPICS = [
    "adhd_focus", "people_pleasing", "trauma_recovery",
    "emotional_regulation", "loneliness",
]


@dataclass
class CampaignConfig:
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    temperature: float = 0.7
    max_concurrent_tasks: int = 5
    variants_per_slot_default: int = 6
    output_dir: Path = REPO_ROOT / "atoms"
    teacher_output_dir: Path = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
    log_file: Path = DEFAULT_LOG_PATH
    validate_before_write: bool = True

    @classmethod
    def from_yaml(cls, path: Path) -> CampaignConfig:
        if not path.exists():
            logger.warning("Config file not found: %s, using defaults", path)
            return cls()
        data = _load_yaml(path)
        return cls(
            model=data.get("model", cls.model),
            max_tokens=data.get("max_tokens", cls.max_tokens),
            temperature=data.get("temperature", cls.temperature),
            max_concurrent_tasks=data.get("max_concurrent_tasks", cls.max_concurrent_tasks),
            variants_per_slot_default=data.get("variants_per_slot_default", cls.variants_per_slot_default),
            output_dir=Path(data.get("output_dir", str(cls.output_dir))),
            teacher_output_dir=Path(data.get("teacher_output_dir", str(cls.teacher_output_dir))),
            log_file=Path(data.get("log_file", str(cls.log_file))),
            validate_before_write=data.get("validate_before_write", cls.validate_before_write),
        )


# ─── CAMPAIGN TASKS ─────────────────────────────────────────────────────────

TASKS: list[dict[str, Any]] = [
    {
        "name": "pivot_takeaway_thread_permission",
        "description": "Write PIVOT/TAKEAWAY/THREAD/PERMISSION for 4 key personas across all 15 topics",
        "personas": ["entrepreneurs", "first_responders", "healthcare_rns", "millennial_women_professionals"],
        "slot_types": ["PIVOT", "TAKEAWAY", "THREAD", "PERMISSION"],
        "topics": "all_15",
        "variants_per": 13,
    },
    {
        "name": "new_topics",
        "description": "Write 6 core slot types for 5 new topics across all 10 main personas",
        "personas": "all_10",
        "slot_types": ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
        "topics": NEW_TOPICS,
        "variants_per": 6,
    },
    {
        "name": "teacher_stories",
        "description": "Write teacher STORY atoms up to 20 total per teacher",
        "teachers": [
            "junko", "miyuki", "maat", "miki", "master_sha", "master_wu",
            "joshin", "master_feung", "omote", "pamela_fellows", "ra", "sai_ma",
        ],
        "target_per_teacher": 20,
    },
    {
        "name": "exercise_compression_gap",
        "description": "Fill EXERCISE and COMPRESSION gaps for specific personas",
        "items": [
            {"persona": "corporate_managers", "slot": "EXERCISE", "target": 200},
            {"persona": "first_responders", "slot": "COMPRESSION", "target": 200},
        ],
    },
    {
        "name": "engine_atoms_new_topics",
        "description": "Write engine atoms for 5 new topics across all 10 personas and 7 engines",
        "topics": NEW_TOPICS,
        "engines": ["watcher", "shame", "comparison", "false_alarm", "overwhelm", "grief", "spiral"],
        "personas": "all_10",
        "variants_per": 5,
    },
]


# ─── LOGGING ────────────────────────────────────────────────────────────────

class CampaignLogger:
    """Append-only JSONL logger for campaign progress."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, entry: dict[str, Any]) -> None:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def get_completed(self) -> set[str]:
        """Read log and return set of completed item keys."""
        completed: set[str] = set()
        if not self.log_path.exists():
            return completed
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("status") == "completed":
                        completed.add(entry.get("key", ""))
                except json.JSONDecodeError:
                    continue
        return completed


# ─── TASK EXECUTORS ─────────────────────────────────────────────────────────

def resolve_personas(spec: str | list[str]) -> list[str]:
    if spec == "all_10":
        return ALL_PERSONAS[:10]
    if spec == "all_12":
        return ALL_PERSONAS
    if isinstance(spec, list):
        return spec
    return [spec]


def resolve_topics(spec: str | list[str]) -> list[str]:
    if spec == "all_15":
        return ALL_TOPICS
    if isinstance(spec, list):
        return spec
    return [spec]


def execute_slot_writing(
    persona: str,
    topic: str,
    slot_type: str,
    variants: int,
    config: CampaignConfig,
    campaign_logger: CampaignLogger,
    completed: set[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute a single persona/topic/slot writing job."""
    key = f"{persona}/{topic}/{slot_type}"

    if key in completed:
        return {"key": key, "status": "skipped", "reason": "already_completed"}

    try:
        # Load few-shot examples
        examples = load_existing_examples(persona, topic, slot_type, max_examples=2)

        content = write_atoms(
            persona_id=persona,
            topic_id=topic,
            slot_type=slot_type,
            num_variants=variants,
            model=config.model,
            existing_examples=examples,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            dry_run=dry_run,
        )

        if dry_run:
            return {"key": key, "status": "dry_run"}

        # Validate
        result = validate_output(content, slot_type)

        if config.validate_before_write and not result.valid:
            campaign_logger.log({
                "key": key, "status": "validation_failed",
                "errors": result.errors, "variants": result.variant_count,
            })
            return {
                "key": key, "status": "validation_failed",
                "errors": result.errors, "variants": result.variant_count,
            }

        # Write
        out_path = write_canonical(
            persona_id=persona,
            topic_id=topic,
            slot_type=slot_type,
            content=content,
            output_dir=config.output_dir,
        )

        campaign_logger.log({
            "key": key, "status": "completed",
            "variants": result.variant_count,
            "word_counts": result.word_counts,
            "warnings": result.warnings,
            "file": str(out_path),
        })

        return {
            "key": key, "status": "completed",
            "variants": result.variant_count,
            "file": str(out_path),
        }

    except Exception as exc:
        campaign_logger.log({"key": key, "status": "error", "error": str(exc)})
        logger.error("Error writing %s: %s", key, exc)
        return {"key": key, "status": "error", "error": str(exc)}


def execute_engine_writing(
    persona: str,
    topic: str,
    engine: str,
    variants: int,
    config: CampaignConfig,
    campaign_logger: CampaignLogger,
    completed: set[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute a single engine atom writing job."""
    key = f"{persona}/{topic}/{engine}"

    if key in completed:
        return {"key": key, "status": "skipped", "reason": "already_completed"}

    try:
        content = write_atoms(
            persona_id=persona,
            topic_id=topic,
            slot_type=engine,
            num_variants=variants,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            dry_run=dry_run,
        )

        if dry_run:
            return {"key": key, "status": "dry_run"}

        result = validate_output(content, engine)

        out_path = write_canonical(
            persona_id=persona,
            topic_id=topic,
            slot_type=engine,
            content=content,
            output_dir=config.output_dir,
            is_engine=True,
            engine_name=engine,
        )

        campaign_logger.log({
            "key": key, "status": "completed",
            "variants": result.variant_count,
            "file": str(out_path),
        })

        return {"key": key, "status": "completed", "variants": result.variant_count}

    except Exception as exc:
        campaign_logger.log({"key": key, "status": "error", "error": str(exc)})
        logger.error("Error writing %s: %s", key, exc)
        return {"key": key, "status": "error", "error": str(exc)}


def run_task_pivot_takeaway_thread_permission(
    task: dict, config: CampaignConfig, campaign_logger: CampaignLogger,
    completed: set[str], dry_run: bool, max_workers: int,
) -> list[dict]:
    """Task 1: PIVOT/TAKEAWAY/THREAD/PERMISSION for 4 personas across all topics."""
    personas = resolve_personas(task["personas"])
    topics = resolve_topics(task["topics"])
    slots = task["slot_types"]
    variants = task["variants_per"]

    jobs = []
    for persona in personas:
        for topic in topics:
            for slot in slots:
                jobs.append((persona, topic, slot))

    logger.info("Task '%s': %d jobs (%d personas x %d topics x %d slots)",
                task["name"], len(jobs), len(personas), len(topics), len(slots))

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                execute_slot_writing,
                persona, topic, slot, variants,
                config, campaign_logger, completed, dry_run,
            ): f"{persona}/{topic}/{slot}"
            for persona, topic, slot in jobs
        }

        for future in as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
                results.append(result)
                status = result.get("status", "unknown")
                logger.info("[%s] %s", status.upper(), key)
            except Exception as exc:
                logger.error("[ERROR] %s: %s", key, exc)
                results.append({"key": key, "status": "error", "error": str(exc)})

    return results


def run_task_new_topics(
    task: dict, config: CampaignConfig, campaign_logger: CampaignLogger,
    completed: set[str], dry_run: bool, max_workers: int,
) -> list[dict]:
    """Task 2: 6 core slots for new topics across all personas."""
    personas = resolve_personas(task["personas"])
    topics = task["topics"]
    slots = task["slot_types"]
    variants = task["variants_per"]

    jobs = []
    for persona in personas:
        for topic in topics:
            for slot in slots:
                jobs.append((persona, topic, slot))

    logger.info("Task '%s': %d jobs", task["name"], len(jobs))

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                execute_slot_writing,
                persona, topic, slot, variants,
                config, campaign_logger, completed, dry_run,
            ): f"{persona}/{topic}/{slot}"
            for persona, topic, slot in jobs
        }

        for future in as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
                results.append(result)
                logger.info("[%s] %s", result.get("status", "?").upper(), key)
            except Exception as exc:
                logger.error("[ERROR] %s: %s", key, exc)
                results.append({"key": key, "status": "error", "error": str(exc)})

    return results


def run_task_teacher_stories(
    task: dict, config: CampaignConfig, campaign_logger: CampaignLogger,
    completed: set[str], dry_run: bool, max_workers: int,
) -> list[dict]:
    """Task 3: Teacher STORY atoms up to target_per_teacher."""
    teachers = task["teachers"]
    target = task["target_per_teacher"]

    results = []
    for teacher_id in teachers:
        key = f"teacher/{teacher_id}"
        if key in completed:
            results.append({"key": key, "status": "skipped"})
            continue

        existing = count_existing_stories(teacher_id)
        needed = max(0, target - existing)
        if needed == 0:
            logger.info("Teacher %s already at %d (target=%d), skipping", teacher_id, existing, target)
            results.append({"key": key, "status": "skipped", "existing": existing})
            continue

        try:
            content = write_teacher_stories(
                teacher_id=teacher_id,
                num_stories=needed,
                model=config.model,
                temperature=config.temperature,
                max_tokens=8192,  # teacher stories need more tokens
                dry_run=dry_run,
            )

            if dry_run:
                results.append({"key": key, "status": "dry_run"})
                continue

            written = write_teacher_yaml_files(teacher_id, content)

            campaign_logger.log({
                "key": key, "status": "completed",
                "stories_written": len(written),
            })
            results.append({"key": key, "status": "completed", "stories_written": len(written)})

        except Exception as exc:
            logger.error("[ERROR] %s: %s", key, exc)
            campaign_logger.log({"key": key, "status": "error", "error": str(exc)})
            results.append({"key": key, "status": "error", "error": str(exc)})

    return results


def run_task_exercise_compression_gap(
    task: dict, config: CampaignConfig, campaign_logger: CampaignLogger,
    completed: set[str], dry_run: bool, max_workers: int,
) -> list[dict]:
    """Task 4: Fill EXERCISE and COMPRESSION gaps."""
    results = []

    for item in task["items"]:
        persona = item["persona"]
        slot = item["slot"]
        target = item["target"]

        # We generate in batches across topics
        for topic in ALL_TOPICS:
            key = f"{persona}/{topic}/{slot}_gap"
            if key in completed:
                results.append({"key": key, "status": "skipped"})
                continue

            # Calculate how many per topic
            variants_per = target // len(ALL_TOPICS)
            if variants_per < 1:
                variants_per = 1

            try:
                examples = load_existing_examples(persona, topic, slot, max_examples=2)

                content = write_atoms(
                    persona_id=persona,
                    topic_id=topic,
                    slot_type=slot,
                    num_variants=variants_per,
                    model=config.model,
                    existing_examples=examples,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    dry_run=dry_run,
                )

                if dry_run:
                    results.append({"key": key, "status": "dry_run"})
                    continue

                result = validate_output(content, slot)

                out_path = write_canonical(
                    persona_id=persona,
                    topic_id=topic,
                    slot_type=slot,
                    content=content,
                    output_dir=config.output_dir,
                )

                campaign_logger.log({
                    "key": key, "status": "completed",
                    "variants": result.variant_count, "file": str(out_path),
                })
                results.append({"key": key, "status": "completed", "variants": result.variant_count})

            except Exception as exc:
                logger.error("[ERROR] %s: %s", key, exc)
                campaign_logger.log({"key": key, "status": "error", "error": str(exc)})
                results.append({"key": key, "status": "error", "error": str(exc)})

    return results


def run_task_engine_atoms_new_topics(
    task: dict, config: CampaignConfig, campaign_logger: CampaignLogger,
    completed: set[str], dry_run: bool, max_workers: int,
) -> list[dict]:
    """Task 5: Engine atoms for new topics."""
    personas = resolve_personas(task["personas"])
    topics = task["topics"]
    engines = task["engines"]
    variants = task["variants_per"]

    jobs = []
    for persona in personas:
        for topic in topics:
            for engine in engines:
                jobs.append((persona, topic, engine))

    logger.info("Task '%s': %d jobs", task["name"], len(jobs))

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                execute_engine_writing,
                persona, topic, engine, variants,
                config, campaign_logger, completed, dry_run,
            ): f"{persona}/{topic}/{engine}"
            for persona, topic, engine in jobs
        }

        for future in as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
                results.append(result)
                logger.info("[%s] %s", result.get("status", "?").upper(), key)
            except Exception as exc:
                logger.error("[ERROR] %s: %s", key, exc)
                results.append({"key": key, "status": "error", "error": str(exc)})

    return results


# ─── TASK DISPATCHER ────────────────────────────────────────────────────────

TASK_RUNNERS = {
    "pivot_takeaway_thread_permission": run_task_pivot_takeaway_thread_permission,
    "new_topics": run_task_new_topics,
    "teacher_stories": run_task_teacher_stories,
    "exercise_compression_gap": run_task_exercise_compression_gap,
    "engine_atoms_new_topics": run_task_engine_atoms_new_topics,
}


def run_campaign(
    task_filter: str | None = None,
    config: CampaignConfig | None = None,
    dry_run: bool = False,
    resume: bool = False,
    max_workers: int | None = None,
) -> dict[str, Any]:
    """Run the full writing campaign or a single task."""
    if config is None:
        config = CampaignConfig.from_yaml(DEFAULT_CONFIG_PATH)

    if max_workers is None:
        max_workers = config.max_concurrent_tasks

    campaign_logger = CampaignLogger(config.log_file)
    completed = campaign_logger.get_completed() if resume else set()

    if completed:
        logger.info("Resuming: %d items already completed", len(completed))

    tasks_to_run = TASKS
    if task_filter:
        tasks_to_run = [t for t in TASKS if t["name"] == task_filter]
        if not tasks_to_run:
            raise ValueError(f"Unknown task: {task_filter}. Available: {[t['name'] for t in TASKS]}")

    campaign_logger.log({
        "key": "__campaign_start__",
        "status": "started",
        "tasks": [t["name"] for t in tasks_to_run],
        "config": {
            "model": config.model,
            "max_workers": max_workers,
            "dry_run": dry_run,
            "resume": resume,
        },
    })

    all_results: dict[str, list[dict]] = {}
    t0 = time.monotonic()

    for task in tasks_to_run:
        name = task["name"]
        runner = TASK_RUNNERS.get(name)
        if not runner:
            logger.error("No runner for task: %s", name)
            continue

        logger.info("=" * 60)
        logger.info("STARTING TASK: %s", name)
        logger.info("  %s", task.get("description", ""))
        logger.info("=" * 60)

        task_t0 = time.monotonic()
        results = runner(task, config, campaign_logger, completed, dry_run, max_workers)
        task_elapsed = time.monotonic() - task_t0

        # Summarize
        statuses = {}
        for r in results:
            s = r.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1

        logger.info("Task '%s' completed in %.1fs: %s", name, task_elapsed, statuses)
        all_results[name] = results

    elapsed = time.monotonic() - t0

    summary = {
        "elapsed_seconds": round(elapsed, 1),
        "tasks_run": len(tasks_to_run),
        "task_summaries": {},
    }
    for name, results in all_results.items():
        statuses = {}
        total_variants = 0
        for r in results:
            s = r.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
            total_variants += r.get("variants", 0) + r.get("stories_written", 0)
        summary["task_summaries"][name] = {
            "statuses": statuses,
            "total_variants": total_variants,
        }

    campaign_logger.log({"key": "__campaign_end__", "status": "completed", "summary": summary})
    return summary


# ─── CLI ────────────────────────────────────────────────────────────────────

def generate_full_plan(
    task_filter: str | None = None,
    output_path: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Generate a full campaign plan including teacher stories.

    Returns a list of plan items, each with:
    - task, persona/teacher_id, topic, slot_type
    - system_prompt, user_prompt
    - output_path
    """
    if output_path is None:
        output_path = REPO_ROOT / "artifacts" / "atom_writing" / "campaign_plan.json"

    # Get base plan from write_atoms_claude
    plan = generate_campaign_plan()

    # Add teacher story items
    if task_filter is None or task_filter == "teacher_stories":
        for teacher_id in ALL_TEACHERS:
            existing_count = count_existing_stories(teacher_id)
            target = 20
            needed = max(0, target - existing_count)
            if needed == 0:
                continue

            try:
                doctrine = load_teacher_doctrine(teacher_id)
                existing = load_existing_stories(teacher_id)
                kb_summary = load_teacher_kb(teacher_id)

                user_prompt = build_teacher_prompt(
                    teacher_id=teacher_id,
                    doctrine=doctrine,
                    existing_examples=existing,
                    num_stories=needed,
                    start_index=existing_count,
                    kb_summary=kb_summary,
                )

                plan.append({
                    "task": "teacher_stories",
                    "teacher_id": teacher_id,
                    "stories_needed": needed,
                    "existing_count": existing_count,
                    "system_prompt": TEACHER_STORY_SYSTEM_PROMPT,
                    "user_prompt": user_prompt,
                    "output_path": f"SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/approved_atoms/STORY/",
                })
            except FileNotFoundError:
                logger.warning("Doctrine not found for %s, skipping", teacher_id)

    # Filter by task if specified
    if task_filter and task_filter != "teacher_stories":
        plan = [p for p in plan if p.get("task") == task_filter]

    # Write plan
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    logger.info("Full campaign plan: %d items -> %s", len(plan), output_path)

    return plan


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Phoenix Omega Atom Writing Campaign (Plan Generator)",
    )
    parser.add_argument("--plan", action="store_true", help="Generate campaign plan JSON")
    parser.add_argument("--task", help="Filter to a single task by name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be planned")
    parser.add_argument("--list-tasks", action="store_true", help="List available tasks")
    parser.add_argument("--stats", action="store_true", help="Show campaign statistics")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--output", type=Path,
        default=REPO_ROOT / "artifacts" / "atom_writing" / "campaign_plan.json",
    )

    args = parser.parse_args()

    if args.list_tasks:
        print("Available campaign tasks:")
        for task in TASKS:
            print(f"  {task['name']:40s} {task.get('description', '')}")
        return

    if args.stats:
        plan = generate_full_plan(task_filter=args.task, output_path=args.output)
        tasks: dict[str, int] = {}
        for item in plan:
            t = item.get("task", "unknown")
            tasks[t] = tasks.get(t, 0) + 1
        print(f"Total plan items: {len(plan)}")
        for t, count in sorted(tasks.items()):
            print(f"  {t}: {count} items")
        # Estimate total atoms
        total_variants = sum(item.get("variants", item.get("stories_needed", 0)) for item in plan)
        print(f"Estimated total atoms to generate: {total_variants}")
        return

    if args.plan or args.dry_run:
        plan = generate_full_plan(task_filter=args.task, output_path=args.output)
        tasks = {}
        for item in plan:
            t = item.get("task", "unknown")
            tasks[t] = tasks.get(t, 0) + 1
        print(f"\n=== CAMPAIGN PLAN ===")
        print(f"Total items: {len(plan)}")
        for t, count in sorted(tasks.items()):
            print(f"  {t}: {count} items")
        print(f"\nPlan written to: {args.output}")
        print("\nTo execute from Claude Code:")
        print("  1. Read the plan JSON")
        print("  2. For each item, spawn Agent(subagent_type='general-purpose')")
        print("     with the system_prompt + user_prompt")
        print("  3. Parse output and write via write_canonical() or write_teacher_yaml_files()")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
