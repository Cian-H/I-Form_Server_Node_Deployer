from pathlib import Path
from .gui import main

assets_dir = str(Path(__file__).parent.absolute() / "assets")

__all__ = ["main", "assets_dir"]
