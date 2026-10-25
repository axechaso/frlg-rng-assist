"""Development uses a clean PokeLDN checkout; production uses only its documented API."""

import os
from pathlib import Path
import sys

host = os.environ.get("POKELDN_SOURCE")
if host:
    root = Path(host)
    sys.path[:0] = [str(root), str(root / "vendor" / "LDN")]
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
