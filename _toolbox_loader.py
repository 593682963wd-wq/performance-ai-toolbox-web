"""通用工具加载器 (放在 repo 根目录,各页面通过 sys.path 引导导入)。

要点:
1. 子工具(`tools_obstacle/` 等)各自带 `core/` 包, 名称会在 sys.modules 里冲突,
   每次切换工具前必须清掉它们的模块缓存。
2. 子工具的 `app.py` 自己会调用 `st.set_page_config`, 所以页面包装器**不要**先调用,
   也**不要**屏蔽; 直接保留它作为该页的真正 page config。
3. 把子工具目录加到 sys.path, cwd 切到子工具目录(让其相对路径资源加载正常),
   然后 runpy 执行其 app.py。
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

_NAMES_TO_CLEAR = ("core", "templates", "usage_tracker")


def _clear_modules() -> None:
    for k in list(sys.modules):
        for name in _NAMES_TO_CLEAR:
            if k == name or k.startswith(name + "."):
                sys.modules.pop(k, None)
                break


def render_tool(tool_dir_name: str) -> None:
    """以子工具目录为根, 执行其 app.py。"""
    root = Path(__file__).resolve().parent
    tool_dir = root / tool_dir_name
    app_file = tool_dir / "app.py"
    if not app_file.exists():
        import streamlit as st
        st.error(f"找不到工具入口: {app_file}")
        return

    _clear_modules()
    str_tool = str(tool_dir)
    if str_tool not in sys.path:
        sys.path.insert(0, str_tool)
    cwd_before = Path.cwd()
    try:
        os.chdir(tool_dir)
        runpy.run_path(str(app_file), run_name="__main__")
    finally:
        try:
            sys.path.remove(str_tool)
        except ValueError:
            pass
        try:
            os.chdir(cwd_before)
        except Exception:
            pass
