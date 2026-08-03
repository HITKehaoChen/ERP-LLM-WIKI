"""Run the full test baseline: unit tests + in-process smoke + real-process E2E."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    ("unit_tests.py", "python scripts/unit_tests.py"),
    ("test_app.py", "python scripts/test_app.py"),
    ("e2e_test.py", "python scripts/e2e_test.py"),
    ("lint_wiki.py", "python scripts/lint_wiki.py"),
]


def main() -> int:
    failed = []
    for name, cmd in STEPS:
        print(f"\n===== {name} =====")
        r = subprocess.run(cmd.split(), cwd=ROOT)
        if r.returncode != 0:
            failed.append(name)
    if failed:
        print("\nFAILED:", ", ".join(failed))
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
