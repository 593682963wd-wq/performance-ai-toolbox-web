"""机场 NAIP 新旧数据对比 — 网页版 (Streamlit)"""
from __future__ import annotations
import io
import os
import shutil
import tempfile
from pathlib import Path

import streamlit as st

from core.diff_engine import compare_folders, compare_pdfs, AirportDiff
from core.excel_writer import write_diff_excel

# 与桌面版同步: 改动后 PATCH +1
APP_VERSION = "V 1.0.0"
AUTHOR = "王迪"
TECH_SUPPORT = "邵小隆"

st.set_page_config(page_title="✈ 机场新旧数据对比", page_icon="✈️", layout="wide")

st.markdown(
    """
<style>
:root { --bg:#0a0e17; --panel:#0d1520; --line:#1a3a5c; --accent:#4fc3f7; --text:#c0d8f0; --muted:#6d93b2; }
.stApp { background: radial-gradient(circle at 100% -5%, #113052 0%, var(--bg) 35%); color: var(--text); }
.main .block-container { max-width: 1400px; padding-top: 1rem; }
h1, h2, h3 { color: var(--accent) !important; letter-spacing: 1px; }
.badge { display:inline-block; border:1px solid #50fa7b; color:#50fa7b; border-radius:12px; padding:2px 12px; font-size:0.8rem; letter-spacing:1px; }
.muted { color: var(--muted); font-size:0.85rem; }
.stButton > button[kind="primary"] { background:#1a5276; color:#fff; border:1px solid #4fc3f7; }
</style>
""",
    unsafe_allow_html=True,
)

col_t, col_m = st.columns([3, 1])
with col_t:
    st.markdown("# ✈ 机场 NAIP 新旧数据对比")
    st.markdown('<div class="muted">按 AD 2.x 小节自动 diff，输出 Excel 汇总+明细</div>', unsafe_allow_html=True)
with col_m:
    st.markdown(
        f'<div style="text-align:right;"><span class="badge">{APP_VERSION}</span><br>'
        f'<span class="muted">作者: {AUTHOR}　技术支持: {TECH_SUPPORT}</span></div>',
        unsafe_allow_html=True,
    )
st.divider()


# ── 输入方式: 上传文件 ──
st.markdown("### ① 上传 PDF 文件")
st.markdown(
    '<div class="muted">每个机场上传一对(旧/新) PDF。文件名前 4 个字符若为 ICAO 代码会自动识别，'
    '否则按上传顺序两两配对。</div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
with c1:
    old_files = st.file_uploader("旧数据 PDF (可多选)", type=["pdf"], accept_multiple_files=True, key="old")
with c2:
    new_files = st.file_uploader("新数据 PDF (可多选)", type=["pdf"], accept_multiple_files=True, key="new")


def _icao_of(name: str) -> str:
    base = Path(name).stem.upper()
    head = base[:4]
    if len(head) == 4 and head.isalpha():
        return head
    return base


def _pair_uploads(olds, news) -> list[tuple[str, object, object]]:
    by_old = {_icao_of(f.name): f for f in olds}
    by_new = {_icao_of(f.name): f for f in news}
    common = sorted(set(by_old) & set(by_new))
    if common:
        return [(k, by_old[k], by_new[k]) for k in common]
    # 回退: 按上传顺序
    pairs = []
    for i, (o, n) in enumerate(zip(olds, news)):
        pairs.append((_icao_of(o.name) or f"机场{i+1}", o, n))
    return pairs


run = st.button("开始对比", type="primary", disabled=not (old_files and new_files))

if run:
    pairs = _pair_uploads(old_files, new_files)
    if not pairs:
        st.error("没有可配对的新旧 PDF。请检查文件名（前 4 位 ICAO）或上传数量。")
    else:
        with tempfile.TemporaryDirectory() as td:
            diffs: list[AirportDiff] = []
            bar = st.progress(0.0, text="开始对比...")
            for idx, (icao, ofile, nfile) in enumerate(pairs):
                op = Path(td) / f"old_{icao}.pdf"
                np_ = Path(td) / f"new_{icao}.pdf"
                op.write_bytes(ofile.getbuffer())
                np_.write_bytes(nfile.getbuffer())
                bar.progress((idx) / len(pairs), text=f"对比 {icao} ...")
                diffs.append(compare_pdfs(icao, str(op), str(np_)))
            bar.progress(1.0, text="完成")
            st.session_state["diffs"] = diffs


diffs: list[AirportDiff] = st.session_state.get("diffs", [])

if diffs:
    st.markdown("### ② 汇总")
    st.dataframe(
        [
            {
                "机场": d.icao,
                "新旧数据对比结果": d.summary_text,
                "差异条数": len(d.items),
                "备注": d.error,
            }
            for d in diffs
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### ③ 明细 (按机场)")
    tabs = st.tabs([d.icao for d in diffs])
    for tab, d in zip(tabs, diffs):
        with tab:
            if d.error:
                st.error(d.error)
            elif not d.items:
                st.info("无差异")
            else:
                st.dataframe(
                    [
                        {
                            "小节": it.section,
                            "变更类型": it.change_type,
                            "旧内容": it.old_text,
                            "新内容": it.new_text,
                        }
                        for it in d.items
                    ],
                    use_container_width=True,
                    hide_index=True,
                    height=420,
                )

    st.markdown("### ④ 导出 Excel")
    out_path = Path(tempfile.gettempdir()) / "新旧数据对比.xlsx"
    write_diff_excel(diffs, out_path)
    with open(out_path, "rb") as f:
        st.download_button(
            "⬇ 下载 新旧数据对比.xlsx",
            data=f.read(),
            file_name="新旧数据对比.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
