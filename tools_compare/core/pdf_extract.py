"""从 NAIP PDF 中按 AD 2.x 小节抽取文本块。

返回结构: dict[小节标题] -> list[行文本]
小节标题示例: "AD 2.2 机场地理位置和管理资料"
若 PDF 无法识别小节, 落入 "未分类" 桶。
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pdfplumber

# 例: "ZLZW AD 2.12 跑道和停止道..."  或 "AD 2.12 跑道..."
SECTION_RE = re.compile(r"^([A-Z]{4}\s+)?AD\s*2\.(\d+(?:\.\d+)?)(\s+.*)?$")
# 页眉/页脚噪声: 资料汇编标识、页码、CAAC 生效日期戳等
PAGE_HEADER_NOISE = re.compile(
    r"^("
    r"中国民航国内航空资料汇编"
    r"|NAIP"
    r"|[A-Z]{4}\s+AD\s*2-\d+"
    r"|页码|Page\s+\d+"
    r"|\d{4}-\d{1,2}-\d{1,2}\s+中国民用航空局"  # 例: 2025-11-15 中国民用航空局 CAAC EFF...
    r"|中国民用航空局\s+CAAC"
    r")"
)
# 仅由 1~2 个非中文字符 / 标点构成的"碎片行"(PDF 抽取误差)
GARBAGE_LINE_RE = re.compile(r"^[\s\.\-_·•●○◎\©\®\*\+/\\=<>\(\)\[\]\{\}\|\?\!~`'\";:,。，；：？！]{0,3}$")


def _is_section_header(line: str) -> Tuple[bool, str]:
    s = line.strip()
    if not s:
        return False, ""
    m = SECTION_RE.match(s)
    if not m:
        return False, ""
    sec_no = m.group(2)
    rest = (m.group(3) or "").strip()
    title = f"AD 2.{sec_no} {rest}".strip()
    return True, title


def _normalize_line(line: str) -> str:
    """归一化空白和不可见字符。"""
    s = line.replace("\u3000", " ").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_sections(pdf_path: str | Path) -> Dict[str, List[str]]:
    """提取 PDF 文本, 按 AD 2.x 切分成小节。"""
    pdf_path = Path(pdf_path)
    sections: Dict[str, List[str]] = {}
    current = "AD 2.0 头部信息"
    sections[current] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw = page.extract_text() or ""
            for ln in raw.split("\n"):
                norm = _normalize_line(ln)
                if not norm:
                    continue
                if PAGE_HEADER_NOISE.match(norm):
                    continue
                if GARBAGE_LINE_RE.match(norm):
                    continue
                hit, title = _is_section_header(norm)
                if hit:
                    current = title
                    sections.setdefault(current, [])
                    continue
                sections.setdefault(current, []).append(norm)
    # 删除空节
    return {k: v for k, v in sections.items() if v}


def list_pdf_files(folder: str | Path) -> List[Path]:
    """返回文件夹下所有 PDF (按文件名排序)。"""
    folder = Path(folder)
    if not folder.exists():
        return []
    return sorted([p for p in folder.iterdir() if p.suffix.lower() == ".pdf"])
