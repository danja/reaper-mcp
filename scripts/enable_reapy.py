#!/usr/bin/env python3
"""
Enable the reapy distant API in REAPER.

Run this script from within REAPER:
  1. Open REAPER
  2. Go to Actions > Run ReaScript
  3. Select this file

After running, restart REAPER for the changes to take effect.
"""

import sys
from pathlib import Path


# REAPER embeds Python rather than activating this project's virtual
# environment. Add the matching venv site-packages directory explicitly so
# that ``import reapy`` resolves to the installation used by the MCP server.
repo_root = Path(__file__).resolve().parent.parent
site_packages = (
    repo_root
    / "venv"
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages"
)

if not site_packages.is_dir():
    raise RuntimeError(
        f"Could not find the reaper-mcp virtual environment at {site_packages}. "
        "Create the venv with the same Python version configured in REAPER."
    )

sys.path.insert(0, str(site_packages))

import reapy

reapy.config.enable_dist_api()
print("reapy distant API enabled. Please restart REAPER.")
