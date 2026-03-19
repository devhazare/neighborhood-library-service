#!/usr/bin/env python3
"""
Test Runner Script - Runs all API tests and generates HTML reports.

Usage:
    python scripts/run_tests.py           # Run all tests with HTML report
    python scripts/run_tests.py --quick   # Run tests without coverage
    python scripts/run_tests.py --module auth  # Run specific module tests
"""
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Ensure we're in the backend directory
BACKEND_DIR = Path(__file__).parent.parent
os.chdir(BACKEND_DIR)

# Create reports directory
REPORTS_DIR = BACKEND_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def run_tests(module: str = None, quick: bool = False):
    """Run tests and generate HTML report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if module:
        report_name = f"test_report_{module}_{timestamp}.html"
        test_path = f"tests/test_api_{module}.py"
    else:
        report_name = f"test_report_full_{timestamp}.html"
        test_path = "tests/"

    report_path = REPORTS_DIR / report_name

    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        f"--html={report_path}",
        "--self-contained-html",
    ]

    if not quick:
        cmd.extend([
            "--cov=app",
            "--cov-report=html:reports/coverage",
            "--cov-report=term-missing",
        ])

    print(f"\n{'='*60}")
    print(f"🧪 Running API Tests")
    print(f"{'='*60}")
    print(f"Module: {module or 'All'}")
    print(f"Report: {report_path}")
    print(f"{'='*60}\n")

    # Run tests
    result = subprocess.run(cmd)

    print(f"\n{'='*60}")
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print(f"📊 HTML Report: {report_path}")
    if not quick:
        print(f"📈 Coverage Report: {REPORTS_DIR}/coverage/index.html")
    print(f"{'='*60}\n")

    return result.returncode


def main():
    args = sys.argv[1:]

    quick = "--quick" in args
    if quick:
        args.remove("--quick")

    module = None
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            module = args[idx + 1]

    sys.exit(run_tests(module=module, quick=quick))


if __name__ == "__main__":
    main()

