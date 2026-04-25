import sys
from pathlib import Path

# 把 repo 根目录加入 sys.path, 否则 Streamlit Cloud 上找不到 _toolbox_loader
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _toolbox_loader import render_tool  # noqa: E402

render_tool("tools_obstacle")
