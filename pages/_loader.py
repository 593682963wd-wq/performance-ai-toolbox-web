"""页面包装器: 隔离 sys.modules + sys.path, 加载子工具的 app.py。

各工具内部均用 `from core.xxx import ...`,  彼此会冲突;
本包装器在加载前清掉 `core` 与 `templates` 模块缓存, 确保正确分发。
同时把 `st.set_page_config` 临时换成 no-op (顶层 app.py 已配置)。
"""
from __future__ import annotations

import sys
import runpy
from pathlib import Path
import streamlit as st


_NAMES_TO_CLEAR = ("core", "templates", "usage_tracker")


def _clear_modules() -> None:
    for k in list(sys.modules):
        for name in _NAMES_TO_CLEAR:
            if k == name or k.startswith(name + "."):
                sys.modules.pop(k, None)
                break


def render_tool(tool_dir_name: str) -> None:
    """在工具目录上下文中执行该工具的 app.py。"""
    root = Path(__file__).resolve().parents[1]
    tool_dir = root / tool_dir_name
    app_file = tool_dir / "app.py"
    if not app_file.exists():
        st.error(f"找不到工具入口: {app_file}")
        return

    _clear_modules()
    sys.path.insert(0, str(tool_dir))

    # 顶层入口已经调用过 st.set_page_config; 子工具再次调用会报错, 替换为 no-op
    original_set_page_config = st.set_page_config
    st.set_page_config = lambda *a, **k: None  # type: ignore[assignment]

    cwd_before = Path.cwd()
    try:
        # 进入子工具目录, 让子工具内的相对路径(资源/模板/输出)生效
        import os
        os.chdir(tool_dir)
        runpy.run_path(str(app_file), run_name="__main__")
    finally:
        st.set_page_config = original_set_page_config  # type: ignore[assignment]
        try:
            sys.path.remove(str(tool_dir))
        except ValueError:
            pass
        try:
            import os
            os.chdir(cwd_before)
        except Exception:
            pass
