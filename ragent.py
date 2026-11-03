#!/usr/bin/env python3
"""
Launcher script for RAgent.
Can be executed directly: ./ragent.py
"""

from pathlib import Path
import sys

# Ensure package directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ragent.cli import main

if __name__ == "__main__":
    sys.exit(main())

