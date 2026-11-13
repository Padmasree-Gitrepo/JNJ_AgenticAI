from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_pytest(targets: list[str] | None = None) -> int:
    command = [sys.executable, "-m", "pytest"]
    if targets:
        command.extend(targets)
    return subprocess.run(command, cwd=Path(__file__).resolve().parent).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Agent Automation Framework")
    parser.add_argument("targets", nargs="*", help="Optional pytest paths or test names to run")
    args = parser.parse_args()
    raise SystemExit(run_pytest(args.targets))
