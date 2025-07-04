#!/usr/bin/env python3
"""
Entry point script for Novel Notify Bot
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from novel_notify.main import run

if __name__ == "__main__":
    run()
