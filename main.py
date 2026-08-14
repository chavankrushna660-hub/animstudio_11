#!/usr/bin/env python3
"""
AnimStudio 7 - Standalone Python Application Entry Point
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from animstudio.gui_pyqt import run_app

if __name__ == "__main__":
    run_app()
