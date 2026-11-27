#!/usr/bin/env python3
"""Regenerate a zh-tw body from its zh-cn source, or check the result.

Usage:
    scripts/convert-zh-tw.py <zh-cn file> <zh-tw file>
    scripts/convert-zh-tw.py --check <zh-tw file>...

The zh-tw file keeps its front matter, because those titles were chosen by hand.

OpenCC (s2twp) supplies the character set. Three shields run before it, because
the manual documents literal column names and flags (`样本编号`, `--skip-envs`)
and a conversion inside those would stop them matching the software.

Two dictionaries surround OpenCC. PRE rewrites phrases whose machine rendering
would collide with another term; POST records where OpenCC's Taiwan form is not
the one this site uses, or where the domain has an established rendering. The
home page under data/home/zh-tw.yaml was corrected by hand earlier and is the
reference for both.
"""
import pathlib
import re
import subprocess
import sys

# `文档` (documentation) and `文件` (file) are distinct in zh-cn, but OpenCC's
# s2twp renders both as 文件. Documentation is shielded before conversion and
# restored as 文檔 afterwards, so 文件 keeps meaning "file" and renders 檔案.
DOC_TOKEN = "@@OTDOC@@"
DOC_TERM = "文檔"

# Applied to the Chinese text before OpenCC. "runner" is the CI machine; OTTER's
# own executor is 執行器 in both languages, so the two must not merge.
PRE = {
    "文档": DOC_TOKEN,
    # 构建 splits two ways: a software build is 建置 in Taiwan, but constructing a
    # matrix is 建構. Shield the construction phrases before the 構建 -> 建置 rule.
    "甲基化矩阵构建": "甲基化矩陣建構",
    "构建 CpG": "建構 CpG",
    "矩阵构建": "矩陣建構",
    "在原生运行器上": "在原生 runner 上",
    "原生运行器": "原生 runner",
    "运行器": "runner",
}

# Applied after OpenCC, longest key first so 校驗和 survives the 校驗 rule.
POST = {
    # terms with their own form (shielded from the shorter rules below)
    "校驗和": "校驗和",
    # OpenCC form -> the form data/home/zh-tw.yaml already uses
    "校驗": "驗證",
    "質量": "品質",
    "許可權": "權限",
    "自定義": "自訂",
    "倉庫": "儲存庫",
    "示例": "範例",
    "軟體包": "軟體套件",
    "分割槽": "分區",
    "引數": "參數",
    "發佈": "釋出",
    "註冊表": "登錄檔",
    "算子": "運算子",
    "安裝器": "安裝程式",
    "賬戶": "帳戶",
    "後臺": "後台",
    "繫結": "綁定",
    "字段": "欄位",
    "全域性": "全域",
    "運行環境": "執行環境",
    "運行時": "執行時",
    "運行": "執行",
    # Taiwan technical usage: 運算元 is "operand"; an operator is 運算子.
    "運算元": "運算子",
    # 建置 is the Taiwan term for a build; 建構 means "to construct" and stays.
    "構建": "建置",
    # 二進位 is the Taiwan short form; 二進位制 is a mainland calque.
    "二進位制": "二進位",
    # Taiwan bioinformatics usage: genome is 基因體, transcriptome 轉錄體,
    # sequencing 定序, and QC 品管. 質控/測序/基因組 are mainland renderings.
    "基因組": "基因體",
    "轉錄組": "轉錄體",
    "測序": "定序",
    "質控": "品管",
    # Normalisation is 正規化 in Taiwan; 歸一化 is the mainland term.
    "歸一化": "正規化",
    # Configuration is 設定 in Taiwan (noun and verb alike); 配置 is a mainland
    # rendering. 註釋 (annotation) is 註解 in Taiwan.
    "配置檔案": "設定檔",
    "配置": "設定",
    "註釋": "註解",
}

SHIELD = re.compile(r"@@OT(\d+)OT@@")


class Shield:
    def __init__(self):
        self.items = []

    def __call__(self, match):
        self.items.append(match.group(0))
        return f"@@OT{len(self.items) - 1}OT@@"

    def restore(self, text):
        out = SHIELD.sub(lambda m: self.items[int(m.group(1))], text)
        if SHIELD.search(out):
            raise SystemExit("unrestored shield placeholder")
        return out


def apply_post(text):
    """Longest key first, and a no-op entry shields its own term.

    A rule pair such as 校驗 -> 驗證 would otherwise rewrite the 校驗 inside
    校驗和, so that entry is registered with itself as the target and the term is
    swapped for a token while the shorter rules run.
    """
    tokens = {}
    for src, dst in sorted(POST.items(), key=lambda kv: -len(kv[0])):
        if src == dst:
            token = f"@@K{len(tokens)}K@@"
            tokens[token] = src
            text = text.replace(src, token)
        else:
            text = text.replace(src, dst)
    for token, src in tokens.items():
        text = text.replace(token, src)
    return text


def convert(body):
    shield = Shield()
    body = re.sub(r"```.*?```", shield, body, flags=re.S)
    body = re.sub(r"`[^`\n]+`", shield, body)
    body = re.sub(r"https?://[^\s)>\]\"']+", shield, body)
    for src, dst in PRE.items():
        body = body.replace(src, dst)
    out = subprocess.run(
        ["opencc", "-c", "s2twp.json"],
        input=body.encode(),
        capture_output=True,
        check=True,
    ).stdout.decode()
    return apply_post(shield.restore(out)).replace(DOC_TOKEN, DOC_TERM)


def split_front_matter(text):
    if not text.startswith("---"):
        return "", text
    end = text.index("\n---", 3)
    return text[: end + 4], text[end + 4 :]


# Characters OpenCC rewrites to a Taiwan variant that Taiwan usage also accepts
# verbatim (臺/台, 遊/游 in 上游/下游). Flagging them would report false positives.
BOTH_VALID = {"台", "游"}


def simplified_only_chars():
    """Characters OpenCC rewrites, i.e. a conservative Simplified-only set."""
    sample = "".join(chr(cp) for cp in range(0x4E00, 0xA000))
    out = subprocess.run(
        ["opencc", "-c", "s2twp.json"],
        input=sample.encode(),
        capture_output=True,
        check=True,
    ).stdout.decode()
    return {a for a, b in zip(sample, out) if a != b} - BOTH_VALID


def check(paths):
    """Report zh-tw bodies that still hold Simplified characters outside code.

    Code spans and fenced blocks are exempt on purpose: the manual documents
    literal column aliases such as `样本编号`, which must stay Simplified so they
    keep matching the software's parser.
    """
    simplified = simplified_only_chars()
    failures = []
    for path in paths:
        text = path.read_text()
        shielded = re.sub(r"```.*?```", "", text, flags=re.S)
        shielded = re.sub(r"`[^`\n]+`", "", shielded)
        found = sorted({c for c in shielded if c in simplified})
        if found:
            failures.append((path, "".join(found)))
    return failures


def main():
    args = sys.argv[1:]
    if args[:1] == ["--check"]:
        failures = check([pathlib.Path(a) for a in args[1:]])
        for path, chars in failures:
            print(f"{path}: simplified characters {chars}")
        raise SystemExit(1 if failures else 0)
    if len(args) != 2:
        raise SystemExit(__doc__)
    cn_path, tw_path = (pathlib.Path(arg) for arg in args)
    front_matter, _ = split_front_matter(tw_path.read_text())
    _, body = split_front_matter(cn_path.read_text())
    tw_path.write_text(front_matter + convert(body))


if __name__ == "__main__":
    main()
