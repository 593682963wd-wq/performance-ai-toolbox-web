import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _toolbox_loader import render_tool  # noqa: E402

render_tool("tools_routeload")
