"""按小节做行级 diff, 生成"机场→小节→旧/新"明细记录。

设计取舍:
1. NAIP PDF 的版式微差(如"-"破折号、空格)较多，统一在 pdf_extract 已做归一化。
2. 仅关注小节内增/删/改的"内容差异"，使用 difflib.ndiff。
3. 把连续的 "-"/"+" 行配对成 "改动"; 单边出现的视为 "新增"/"删除"。
"""
from __future__ import annotations
import difflib
from dataclasses import dataclass, field
from typing import Dict, List

from .pdf_extract import extract_sections


def _norm_for_compare(s: str) -> str:
    """忽略空白与中英文标点差异后用于"等同"判断。"""
    import re
    return re.sub(r"[\s\.\,\;\:。，；：·•\-_/\\()\[\]{}\"'`~!?！？]+", "", s)


@dataclass
class DiffItem:
    section: str          # 小节标题, 如 "AD 2.12 跑道..."
    change_type: str      # "新增" / "删除" / "修改"
    old_text: str
    new_text: str


@dataclass
class AirportDiff:
    icao: str
    old_pdf: str
    new_pdf: str
    items: List[DiffItem] = field(default_factory=list)
    error: str = ""

    @property
    def changed_sections(self) -> List[str]:
        seen = []
        for it in self.items:
            if it.section not in seen:
                seen.append(it.section)
        return seen

    @property
    def summary_text(self) -> str:
        return "、".join(s.split(" ", 1)[-1] for s in self.changed_sections) or "（无差异）"


def _diff_lines(old: List[str], new: List[str]) -> List[tuple[str, str]]:
    """返回 [(change_type, old_text, new_text)] 形式的列表; 这里返回三元组。"""
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    out: List[tuple[str, str, str]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        old_block = old[i1:i2]
        new_block = new[j1:j2]
        if tag == "replace":
            # 把 old_block / new_block 一一配对; 长度不齐则补空
            n = max(len(old_block), len(new_block))
            for k in range(n):
                o = old_block[k] if k < len(old_block) else ""
                nw = new_block[k] if k < len(new_block) else ""
                if o and nw:
                    out.append(("修改", o, nw))
                elif nw:
                    out.append(("新增", "", nw))
                else:
                    out.append(("删除", o, ""))
        elif tag == "delete":
            for o in old_block:
                out.append(("删除", o, ""))
        elif tag == "insert":
            for nw in new_block:
                out.append(("新增", "", nw))
    return out  # type: ignore[return-value]


def compare_pdfs(icao: str, old_pdf: str, new_pdf: str) -> AirportDiff:
    ad = AirportDiff(icao=icao, old_pdf=str(old_pdf), new_pdf=str(new_pdf))
    try:
        old_secs = extract_sections(old_pdf)
        new_secs = extract_sections(new_pdf)
    except Exception as e:  # pragma: no cover
        ad.error = f"PDF 解析失败: {e}"
        return ad

    all_sections = list(dict.fromkeys(list(old_secs.keys()) + list(new_secs.keys())))
    for sec in all_sections:
        diffs = _diff_lines(old_secs.get(sec, []), new_secs.get(sec, []))
        for ct, o, n in diffs:
            # 仅标点/空白差异 → 视为等同, 跳过
            if ct == "修改" and _norm_for_compare(o) == _norm_for_compare(n):
                continue
            ad.items.append(DiffItem(section=sec, change_type=ct, old_text=o, new_text=n))
    return ad


def compare_folders(old_root: str, new_root: str) -> List[AirportDiff]:
    """遍历 old_root/<ICAO>/ 和 new_root/<ICAO>/, 返回所有 ICAO 的差异列表。

    匹配规则:
      - 同名子目录视为同一机场 (子目录名作为 ICAO);
      - 每个 ICAO 取目录下的第一个 PDF 文件做对比。
    """
    from pathlib import Path
    old_root_p = Path(old_root)
    new_root_p = Path(new_root)
    icaos = sorted({d.name for d in old_root_p.iterdir() if d.is_dir()} &
                   {d.name for d in new_root_p.iterdir() if d.is_dir()})
    results: List[AirportDiff] = []
    for icao in icaos:
        olds = sorted(p for p in (old_root_p / icao).iterdir() if p.suffix.lower() == ".pdf")
        news = sorted(p for p in (new_root_p / icao).iterdir() if p.suffix.lower() == ".pdf")
        if not olds or not news:
            continue
        results.append(compare_pdfs(icao, str(olds[0]), str(news[0])))
    return results
