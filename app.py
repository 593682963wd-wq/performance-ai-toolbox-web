"""性能 AI 工具台 — 入口页 (landing)。

将 3 个独立 Streamlit 工具汇总到同一个 Web 站点：
  1. 机场障碍物分析    (tools_obstacle)
  2. 机场新旧数据对比  (tools_compare)
  3. 航线载量分析      (tools_routeload)

每个工具放在 pages/ 下作为独立页面，独立的 core/ 通过 sys.modules 隔离。
"""
from __future__ import annotations

import streamlit as st

APP_VERSION = "V 1.0.0"
AUTHOR = "王迪"

st.set_page_config(
    page_title="性能 AI 工具台",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "性能 AI 工具台 — 汇总『机场障碍物分析』『机场新旧数据对比』"
                 "『航线载量分析』三大工具。作者: 王迪"
    },
)

st.markdown(
    """
<style>
:root{
  --bg:#0a0e17; --panel:#0d1520; --panel-strong:#0d2137;
  --line:#1a3a5c; --line-strong:#1a5276;
  --accent:#4fc3f7; --text:#c0d8f0; --muted:#6d93b2;
}
.stApp { background: radial-gradient(circle at 100% -5%, #113052 0%, var(--bg) 35%); color: var(--text); }
.main .block-container { max-width: 1280px; padding-top: 1.2rem; }
h1, h2, h3 { color: var(--accent) !important; letter-spacing: 1px; }
.badge { display:inline-block; border:1px solid #50fa7b; color:#50fa7b; border-radius:12px;
         padding:2px 14px; font-size:0.78rem; letter-spacing:2px; font-family:monospace; font-weight:700; }
.tool-card {
    background: linear-gradient(135deg, rgba(79,195,247,.10) 0%, rgba(13,33,55,.55) 100%);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 22px 26px 18px 26px;
    margin-bottom: 14px;
    transition: all .2s;
}
.tool-card:hover { border-color: var(--accent); box-shadow: 0 0 22px rgba(79,195,247,.18); }
.tool-card .icon { font-size: 2.2rem; }
.tool-card .title { color: var(--accent); font-size: 1.25rem; font-weight: 700; letter-spacing: 1px; margin-bottom: 6px; }
.tool-card .summary { color: var(--text); font-size: 0.9rem; line-height: 1.55; }
.tool-card .tag { display:inline-block; background:rgba(79,195,247,.12); color:var(--accent);
                  border:1px solid var(--line); border-radius: 10px;
                  padding:1px 10px; font-size:0.72rem; margin-right:6px; margin-top:8px; }
section[data-testid="stSidebar"] { background: #0d1520 !important; border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] a { color: var(--accent) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── 顶部 ──
top_l, top_r = st.columns([3, 1])
with top_l:
    st.markdown("# ✈ 性能 AI 工具台")
    st.caption("Performance AI Toolbox · 一站式签派性能分析工具")
with top_r:
    st.markdown(
        f'<div style="text-align:right;margin-top:10px;">'
        f'<span class="badge">{APP_VERSION}</span><br>'
        f'<span style="color:#6d93b2;font-size:0.8rem;">作者: {AUTHOR}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

st.divider()

st.markdown("### 🧰 工具列表")
st.caption("点击左侧边栏的页面名称进入对应工具。")

st.markdown(
    """
<div class="tool-card">
    <div style="display:flex;align-items:center;gap:14px;">
        <div class="icon">🗼</div>
        <div>
            <div class="title">机场障碍物分析</div>
            <div class="summary">
                解析 AIP PDF/TXT，按 ICAO Annex 14 / PANS-OPS 计算障碍物对起降的影响，
                导出 PEP 兼容 Excel 与 TXT。支持手动复核、遮蔽规则、离场参数配置。
            </div>
            <div>
                <span class="tag">PDF</span><span class="tag">TXT</span>
                <span class="tag">PEP</span><span class="tag">PANS-OPS</span>
            </div>
        </div>
    </div>
</div>

<div class="tool-card">
    <div style="display:flex;align-items:center;gap:14px;">
        <div class="icon">📊</div>
        <div>
            <div class="title">机场新旧数据对比</div>
            <div class="summary">
                上传新旧版 NAIP PDF（按 ICAO 自动配对），按 AD 2.x 小节自动 diff，
                输出『新旧数据对比.xlsx』汇总+明细，颜色高亮新增/删除/修改。
            </div>
            <div>
                <span class="tag">NAIP</span><span class="tag">差异</span>
                <span class="tag">Excel</span><span class="tag">多机场</span>
            </div>
        </div>
    </div>
</div>

<div class="tool-card">
    <div style="display:flex;align-items:center;gap:14px;">
        <div class="icon">📦</div>
        <div>
            <div class="title">航线载量分析</div>
            <div class="summary">
                上传 CFP/计划文件，自动算出可用业载、油量分配、配平裕度，输出 Word 分析报告与 PPT。
            </div>
            <div>
                <span class="tag">CFP</span><span class="tag">业载</span>
                <span class="tag">Word</span><span class="tag">PPT</span>
            </div>
        </div>
    </div>
</div>

<div class="tool-card" style="background:linear-gradient(135deg,rgba(139,92,246,.16) 0%,rgba(79,195,247,.10) 100%);border-color:rgba(139,92,246,.45);">
    <div style="display:flex;align-items:center;gap:14px;">
        <div class="icon">🌌</div>
        <div>
            <div class="title">科幻模式 · 全息粒子</div>
            <div class="summary">
                Three.js + MediaPipe 全息粒子交互系统。通过摄像头单手张合控制粒子缩放扩散，
                支持土星 / 圆球 / 山脉 / 烟花 / DNA / 文字 6 套模型，滑动切换、双手缩放、捏合点击。
                <span style="color:#bf6bff;font-weight:600">独立沉浸界面，不影响其它工具。</span>
            </div>
            <div>
                <span class="tag">Three.js</span><span class="tag">MediaPipe</span>
                <span class="tag">手势</span><span class="tag">WebGL</span>
            </div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()
st.caption("👉 在左侧 **Pages** 选择具体工具进入使用。所有工具数据仅在浏览器/会话中处理，不上传服务器存档。")
