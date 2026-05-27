"""科幻模式 · 全息粒子系统 + 手势交互。

独立沉浸界面，不影响其它工具页面。引入与 Flask 工具台同一份 HTML，
通过 Streamlit components.html 全屏嵌入。

文件来源：performance-ai-toolbox-web/assets/scifi_mode.html
（与 New project/static/scifi_mode.html 保持同步）
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="科幻模式 · 全息粒子",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 让组件占满整屏
st.markdown(
    """
<style>
.main .block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: rgba(0,0,0,0); }
section[data-testid="stSidebar"] { display: none; }
iframe { border: 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

HTML_PATH = Path(__file__).resolve().parent.parent / "assets" / "scifi_mode.html"

if not HTML_PATH.exists():
    st.error(
        "未找到科幻模式 HTML。请同步：\n\n"
        f"`{HTML_PATH}`\n\n"
        "可执行：`rsync -av /Users/amanda/Documents/New\\ project/static/scifi_mode.html "
        "/Users/amanda/Desktop/performance-ai-toolbox-web/assets/`"
    )
    st.stop()

html = HTML_PATH.read_text("utf-8")
# 嵌入；高度铺满视窗
components.html(html, height=900, scrolling=False)
