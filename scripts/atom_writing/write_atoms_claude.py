#!/usr/bin/env python3
"""
DEPRECATED — DO NOT USE THIS SCRIPT DIRECTLY.

Atom writing is done via Claude Code Agent tool (subagents), NOT via
the Anthropic API. This script existed briefly and made unauthorized
API calls. It has been replaced with a stub.

The correct way to write atoms:
    Claude Code Agent tool → spawns Pearl_Writer subagents → writes to disk
    Zero external API cost. Included in Claude Code subscription.

See: docs/ATOM_WRITING_HANDOFF.md for the full procedure.
"""
import sys
print("ERROR: This script is deprecated. Use Claude Code Agent tool instead.", file=sys.stderr)
print("See docs/ATOM_WRITING_HANDOFF.md", file=sys.stderr)
sys.exit(1)
