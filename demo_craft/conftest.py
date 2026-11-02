"""
Pytest configuration for the demo_craft test suite.

The swxsoc package selects its per-mission configuration from the
``SWXSOC_MISSION`` environment variable. ``demo_craft/__init__.py`` forces it
to ``demo`` on import; setting it here as well makes the choice explicit for
tests that run before the package is imported (for example the docs doctests).
"""

import os

os.environ.setdefault("SWXSOC_MISSION", "demo")
