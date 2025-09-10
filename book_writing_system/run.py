#!/usr/bin/env python3
"""
Main entry point for the AI Book Writing System.
Supports both CLI and GUI interfaces.
"""

import sys
import asyncio
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from book_writing_system.cli import main as cli_main
from book_writing_system.gui import main as gui_main


def main():
    """Main entry point with interface selection."""
    if len(sys.argv) < 2:
        print("Usage: python run.py [cli|gui]")
        print("  cli - Command line interface")
        print("  gui - Graphical user interface")
        sys.exit(1)
    
    interface = sys.argv[1].lower()
    
    if interface == "cli":
        cli_main()
    elif interface == "gui":
        gui_main()
    else:
        print(f"Unknown interface: {interface}")
        print("Available interfaces: cli, gui")
        sys.exit(1)


if __name__ == "__main__":
    main()