#!/usr/bin/env python3
"""Download the Academic Vocabulary List (AVL) / COCA-Academic word lists.

These lists come from https://www.academicvocabulary.info (Mark Davies and Dee
Gardner), built from the 120-million-word COCA-Academic corpus.

LICENSING -- READ BEFORE RUNNING
--------------------------------
The publisher's download page states:

  "Note that these lists are strictly for academic use. For commercial use,
   please contact us. Also, please do not place these lists on another website
   -- even for student use. Just link to our site so that other people can
   download the files for themselves."

Consequences for this repository:
  * the downloaded file is NOT committed (see .gitignore),
  * do not ship it in the app or republish it; link to the source instead,
  * a commercial release of the app should contact the publisher first.

The app asset only stores individual words with our own generated translations
and definitions, no list content, but confirm this with the publisher before a
commercial release.

Usage:
  python fetch_academic_lists.py --out data/academic_lists.json
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


BASE = "https://www.academicvocabulary.info/download"
SOURCES = {
    "acadCore.xlsx": f"{BASE}/acadCore.xlsx",
    "families.xlsx": f"{BASE}/families.xlsx",
    "allWords.xlsx": f"{BASE}/allWords.xlsx",
}
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; TOEFL-Coach-vocabulary-builder)"}


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(request, timeout=120) as response:
        dest.write_bytes(response.read())


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.iter(f"{NS}t"))
        for item in root.findall(f"{NS}si")
    ]


def rows(archive: zipfile.ZipFile, name: str, strings: list[str]) -> list[list[str]]:
    root = ET.fromstring(archive.read(name))
    output = []
    for row in root.iter(f"{NS}row"):
        cells = []
        for cell in row.findall(f"{NS}c"):
            value = cell.find(f"{NS}v")
            if value is None or value.text is None:
                cells.append("")
            elif cell.get("t") == "s":
                cells.append(strings[int(value.text)])
            else:
                cells.append(value.text)
        output.append(cells)
    return output


def extract(workbook: Path, sheet: str, word_col: int, pos_col: int | None) -> list[dict]:
    with zipfile.ZipFile(workbook) as archive:
        strings = shared_strings(archive)
        out = []
        for row in rows(archive, sheet, strings):
            if len(row) <= word_col:
                continue
            word = row[word_col].strip().lower()
            if not re.fullmatch(r"[a-z][a-z\- ']{1,30}", word):
                continue
            out.append({"word": word, "pos": row[pos_col].strip() if pos_col is not None and len(row) > pos_col else ""})
        return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "data/academic_lists.json")
    parser.add_argument("--workdir", type=Path, default=Path("/private/tmp/avl-download"))
    args = parser.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        dest = args.workdir / name
        if dest.exists() and dest.stat().st_size > 0:
            print(f"cached  {name}")
            continue
        print(f"fetch   {url}")
        download(url, dest)
        print(f"  saved {dest} ({dest.stat().st_size} bytes)")

    result = {
        # The 3,000 core academic lemmas (sheet 2 of acadCore.xlsx).
        "avl_core": extract(args.workdir / "acadCore.xlsx", "xl/worksheets/sheet2.xml", 1, 2),
        # Every member of the AVL word families (sheet 4 of families.xlsx).
        "avl_family": extract(args.workdir / "families.xlsx", "xl/worksheets/sheet4.xml", 3, 4),
        # The COCA-Academic top 20,000 (sheet 2 of allWords.xlsx).
        "coca_academic": extract(args.workdir / "allWords.xlsx", "xl/worksheets/sheet2.xml", 3, 4),
    }
    for key, value in result.items():
        print(f"{key}: {len(value)} words")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    print()
    print("NOTE: the publisher requires that these lists are used for academic")
    print("purposes only and are not reposted elsewhere. Do not commit this file.")


if __name__ == "__main__":
    main()
