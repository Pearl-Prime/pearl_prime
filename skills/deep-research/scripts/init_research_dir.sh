#!/usr/bin/env bash
# init_research_dir.sh — Ensure the research/ output directory exists
# and generate a filename for the current research session.
#
# Usage: bash scripts/init_research_dir.sh "topic slug here"
# Output: prints the full filepath to stdout

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RESEARCH_DIR="${REPO_ROOT}/research"

mkdir -p "${RESEARCH_DIR}"

TOPIC_SLUG="${1:?Usage: init_research_dir.sh <topic-slug>}"
# Sanitize: lowercase, replace spaces/special chars with hyphens, trim to 60 chars
SLUG=$(echo "${TOPIC_SLUG}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-60)
DATE=$(date +%Y-%m-%d)

FILEPATH="${RESEARCH_DIR}/${DATE}_${SLUG}.md"
echo "${FILEPATH}"
