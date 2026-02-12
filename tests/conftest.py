"""Ensure project root is on sys.path so tests can import tower_params."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
