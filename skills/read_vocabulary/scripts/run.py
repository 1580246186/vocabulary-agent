"""Skill: 读取 Word 文档并提取英语词汇。

解析 .docx 段落（Tab/空格分隔），过滤错位单词，精简中文翻译。
"""

import re
from pathlib import Path

from docx import Document


# 词性标签正则：n. / v. / adj. / adv./prep. 等
_POS_PATTERN = re.compile(
    r"^(n|v|adj|adv|prep|conj|pron|num|art|int|aux|det|abbr|pref|suf|phr|idm)\."
    r"([/](n|v|adj|adv|prep|conj|pron|num|art|int|aux|det|abbr|pref|suf|phr|idm)\.)*$"
)


def run(filepath: str | Path) -> list[dict]:
    """解析 .docx 文件，返回清洗后的词汇列表。"""
    raw = _parse(filepath)
    return _filter(raw)


# ── 解析 ──────────────────────────────────────────────

def _parse(filepath: str | Path) -> list[dict]:
    """从 Word 文档逐段读取，识别词汇条目。"""
    doc = Document(filepath)
    entries: list[dict] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if _is_skip_line(text):
            continue

        entry = _try_parse_line(text)
        if entry is not None:
            entries.append(entry)
        elif entries and _has_chinese(text):
            # 上一行翻译的延续
            entries[-1]["translation"] += text

    return entries


def _try_parse_line(text: str) -> dict | None:
    """尝试将一行文本解析为词汇条目（单词 + 词性 + 翻译）。"""
    # 先按 Tab 分割，再按多空格，最后按任意空白
    if "\t" in text:
        parts = text.split("\t", 2)
    else:
        parts = re.split(r" {2,}", text, maxsplit=2)
        if len(parts) < 3:
            parts = text.split(None, 2)

    if len(parts) < 2:
        return None

    word = parts[0].strip()
    remainder = parts[1].strip() if len(parts) >= 2 else ""
    translation = parts[2].strip() if len(parts) >= 3 else ""

    if not _is_english_word(word):
        return None

    # 从剩余文本中提取词性标签
    tokens = remainder.split(None, 1)
    candidate_pos = tokens[0].rstrip(",;")
    if not _POS_PATTERN.match(candidate_pos):
        # 尝试"v.放弃"这种词性和翻译粘连的情况
        m = re.match(r"^([a-z]+(?:\.[/][a-z]+\.)*\.)(.*)", candidate_pos)
        if m and _POS_PATTERN.match(m.group(1)):
            candidate_pos = m.group(1)
            extra = m.group(2)
            if extra:
                translation = extra + (tokens[1] if len(tokens) > 1 else "") + translation
        else:
            return None

    if not translation and len(tokens) > 1:
        translation = tokens[1]

    return {"word": word, "pos": candidate_pos, "translation": translation}


# ── 过滤 ──────────────────────────────────────────────

def _filter(raw: list[dict]) -> list[dict]:
    """过滤错位单词，精简翻译。单词应按首字母顺序排列 A→B→C..."""
    if not raw:
        return []

    expected_letter = raw[0]["word"][0].lower()
    cleaned: list[dict] = []

    for rw in raw:
        wl = rw["word"][0].lower()
        if not wl.isalpha():
            continue
        if wl < expected_letter:
            # 错位单词（如在 C 段中出现的 A 开头词），丢弃
            continue
        elif wl > expected_letter:
            expected_letter = wl

        cleaned.append({
            "word": rw["word"],
            "pos": rw["pos"],
            "translation": _simplify(rw["translation"]),
            "first_letter": wl,
        })

    return cleaned


def _simplify(raw: str) -> str:
    """精简中文翻译：去括号注释、去多余标点、截断过长文本。"""
    text = re.sub(r'[（(][^）)]*[）)]', '', raw)
    text = text.replace('；', ';').replace('，', ',')
    text = re.sub(r'[;,]\s*[;,]', ';', text)
    text = text.rstrip(';,;，。.')
    if len(text) > 50:
        parts = re.split(r'[;；]', text)
        text = parts[0].strip()
    return text.strip()


# ── 辅助函数 ──────────────────────────────────────────

def _is_english_word(text: str) -> bool:
    """检查是否为英文单词（允许连字符和撇号）。"""
    return bool(re.match(r"^[a-zA-Z][a-zA-Z'\-]*$", text)) if text else False


def _has_chinese(text: str) -> bool:
    """检查是否包含中文字符。"""
    return bool(re.search(r"[一-鿿]", text))


def _is_skip_line(text: str) -> bool:
    """检查是否为应跳过的行（单字母标题、纯分隔符）。"""
    if re.match(r"^[A-Z]$", text):
        return True
    if re.match(r"^[-=*#]{3,}$", text):
        return True
    return False
