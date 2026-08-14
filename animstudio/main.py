#!/usr/bin/env python3
"""
AnimStudio 7 - Python PyQt6 & Pygame Entrypoint
Run this script to launch the standalone desktop application in Python.
"""

import sys
import os

# Add local path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from animstudio.gui_pyqt import run_app

if __name__ == "__main__":
    run_app()
