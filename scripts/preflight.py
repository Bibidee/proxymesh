#!/usr/bin/env python3
from pathlib import Path
import ast
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
required = [
    "README.md", "AGENT_HANDOFF.md", "SUBMISSION.md", "BUILD_STATUS.md",
    "contracts/proxymesh.py", "contracts/proxy_vote_book.py",
    "docs/ARCHITECTURE.md", "docs/SECURITY_MODEL.md", "docs/LIVE_TEST_PLAN.md", "docs/NETWORK.md",
]
for rel in required:
    if not (ROOT / rel).exists(): errors.append(f"missing {rel}")
for rel in ["contracts/proxymesh.py", "contracts/proxy_vote_book.py", "tests/test_model.py", "tests/test_source_invariants.py"]:
    try: ast.parse((ROOT / rel).read_text(encoding="utf-8"), filename=rel)
    except Exception as exc: errors.append(f"syntax {rel}: {exc}")
active_files = [
    ROOT / "contracts" / "proxymesh.py",
    ROOT / "contracts" / "proxy_vote_book.py",
    ROOT / "scripts" / "check-cli.sh",
    ROOT / "scripts" / "check-cli.ps1",
    ROOT / "docs" / "NETWORK.md",
]
active_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in active_files if p.exists())
network_text = (ROOT / "docs" / "NETWORK.md").read_text(encoding="utf-8")
if "61999" not in network_text: errors.append("Studionet chain 61999 not documented")
if "0.39.1" not in network_text: errors.append("CLI 0.39.1 not pinned")
if "https://studio.genlayer.com/api" not in network_text: errors.append("Studionet RPC not documented")
if errors:
    print("PREFLIGHT FAILED")
    for e in errors: print("-", e)
    sys.exit(1)
print("PREFLIGHT PASSED")
print("- no frontend")
print("- contracts parse as Python")
print("- network locked to Studionet 61999")
print("- CLI pinned to 0.39.1")
