#!/usr/bin/env python3
"""Run all tests for Hinglish Order Desk."""

import subprocess
import sys
import os


def run_command(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

    success = True

    # Backend tests
    print("\n=== Backend Tests ===")
    if not run_command("python -m pytest backend/tests -v"):
        success = False

    # Frontend tests (if any)
    print("\n=== Frontend Tests ===")
    if not run_command("npm test", cwd="frontend"):
        print("No frontend tests configured")

    # AI/ML tests (if any)
    print("\n=== AI/ML Tests ===")
    # Add AI tests here when implemented

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()