"""Build a local HWPX submission draft from the official template.

This script intentionally creates an ignored local .hwpx file. The generated
file must still be opened in Hancom/HWP-compatible software for visual page and
layout verification before submission.
"""

from __future__ import annotations

import argparse
import copy
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


NS = {
    "ha": "http://www.hancom.co.kr/hwpml/2011/app",
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hp10": "http://www.hancom.co.kr/hwpml/2016/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hhs": "http://www.hancom.co.kr/hwpml/2011/history",
    "hm": "http://www.hancom.co.kr/hwpml/2011/master-page",
    "hpf": "http://www.hancom.co.kr/schema/2011/hpf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf/",
    "ooxmlchart": "http://www.hancom.co.kr/hwpml/2016/ooxmlchart",
    "hwpunitchar": "http://www.hancom.co.kr/hwpml/2016/HwpUnitChar",
    "epub": "http://www.idpf.org/2007/ops",
    "config": "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
}

HP = f"{{{NS['hp']}}}"


for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def read_markdown_sections(path: Path) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# 공식 제출"):
            continue
        if line.startswith("이 문서는 "):
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            if heading == "기본 정보":
                current = None
            elif heading == "제출 전 확인 필요":
                current = None
            else:
                current = heading
                sections[current] = []
            continue
        if current is None:
            continue
        converted = convert_markdown_line(line)
        if converted:
            sections[current].extend(converted)

    return sections


def convert_markdown_line(line: str) -> list[str]:
    if line.startswith("|"):
        cells = [cell.replace("`", "").strip() for cell in line.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"-+", cell.replace(" ", "")) for cell in cells):
            return []
        if len(cells) >= 3:
            return [f"- {cells[0]}: {cells[1]} / {cells[2]}"]
        return ["- " + " / ".join(cells)]
    if line.startswith("> "):
        return [line[2:].strip()]
    if line.startswith("- "):
        return ["- " + line[2:].strip()]
    return [line]


def set_cell_text(root: ET.Element, row: str, col: str, text: str) -> bool:
    for tc in root.findall(".//hp:tc", NS):
        addr = tc.find("hp:cellAddr", NS)
        if addr is None or addr.get("rowAddr") != row or addr.get("colAddr") != col:
            continue
        p = tc.find(".//hp:p", NS)
        if p is None:
            return False
        replace_paragraph_text(p, text, char_pr_id="14")
        return True
    return False


def replace_paragraph_text(p: ET.Element, text: str, char_pr_id: str = "17") -> None:
    for run in list(p.findall("hp:run", NS)):
        p.remove(run)
    run = ET.SubElement(p, HP + "run", {"charPrIDRef": char_pr_id})
    t = ET.SubElement(run, HP + "t")
    t.text = text


def make_paragraph(text: str, kind: str) -> ET.Element:
    if kind == "heading":
        char_pr = "20"
        para_pr = "1"
        text = text
    elif kind == "summary-heading":
        char_pr = "20"
        para_pr = "1"
        text = "<요약>"
    elif kind == "bullet":
        char_pr = "17"
        para_pr = "1"
    else:
        char_pr = "17"
        para_pr = "1"

    p = ET.Element(
        HP + "p",
        {
            "id": "0",
            "paraPrIDRef": para_pr,
            "styleIDRef": "0",
            "pageBreak": "0",
            "columnBreak": "0",
            "merged": "0",
        },
    )
    run = ET.SubElement(p, HP + "run", {"charPrIDRef": char_pr})
    t = ET.SubElement(run, HP + "t")
    t.text = text
    lines = ET.SubElement(p, HP + "linesegarray")
    ET.SubElement(
        lines,
        HP + "lineseg",
        {
            "textpos": "0",
            "vertpos": "0",
            "vertsize": "1300",
            "textheight": "1300",
            "baseline": "1105",
            "spacing": "780",
            "horzpos": "0",
            "horzsize": "48188",
            "flags": "393216",
        },
    )
    return p


def build_section_xml(template_xml: bytes, sections: dict[str, list[str]]) -> bytes:
    root = ET.fromstring(template_xml)
    original_children = list(root)
    if len(original_children) < 2:
        raise ValueError("Unexpected HWPX template: not enough root paragraphs")

    first_title = copy.deepcopy(original_children[0])
    metadata_table = copy.deepcopy(original_children[1])

    for child in list(root):
        root.remove(child)
    root.append(first_title)
    root.append(metadata_table)

    set_cell_text(root, "0", "8", "●")
    set_cell_text(root, "1", "2", "MedIT Agent Lab")
    set_cell_text(root, "2", "2", "Clinical Trial Protocol Review Agent / 임상시험 프로토콜 사전검토 에이전트")
    set_cell_text(root, "3", "4", "임상시험 프로토콜, 의료정보, 병원 데이터, 근거 기반 검토, 에이전트 AI")
    set_cell_text(root, "4", "4", "Clinical Trial Protocol, Medical IT, Hospital Data Readiness, Evidence-Based Review, Agentic AI")

    order = [
        "요약",
        "1. 신약개발 과정에서의 에이전트 활용 필요성 및 배경",
        "2. 에이전트 설계, 독창성 및 창의성",
        "3. 기술적 실현 가능성",
        "4. 에이전트 평가 계획",
        "5. 최종 라운드 데모 시나리오",
        "6. 기대효과, 윤리 및 적용 경계",
        "참고문헌",
    ]

    for heading in order:
        if heading not in sections:
            continue
        if heading == "요약":
            root.append(make_paragraph("", "summary-heading"))
        else:
            root.append(make_paragraph(heading, "heading"))
        for line in sections[heading]:
            kind = "bullet" if line.startswith("- ") or re.match(r"^\d+\. ", line) else "body"
            root.append(make_paragraph(line, kind))

    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + ET.tostring(root, encoding="utf-8")


def extract_plain_text_from_hwpx(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("Contents/section0.xml"))
    lines = []
    for p in root.findall(".//hp:p", NS):
        text = "".join(t.text or "" for t in p.findall(".//hp:t", NS)).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def build_hwpx(template_path: Path, source_path: Path, output_path: Path) -> None:
    sections = read_markdown_sections(source_path)
    if not sections:
        raise ValueError(f"No sections parsed from {source_path}")

    with zipfile.ZipFile(template_path, "r") as zin:
        section_xml = build_section_xml(zin.read("Contents/section0.xml"), sections)
        with zipfile.ZipFile(output_path, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "Contents/section0.xml":
                    data = section_xml
                elif item.filename == "Preview/PrvText.txt":
                    data = "\n".join(
                        ["MedIT Agent Lab", "Clinical Trial Protocol Review Agent"]
                        + [heading for heading in sections.keys()]
                    ).encode("utf-8")
                zout.writestr(item, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", default="proposal/template.hwpx")
    parser.add_argument("--source", default="proposal/submission_form_condensed_ko.md")
    parser.add_argument("--output", default="proposal/MedIT_Agent_Lab_submission_draft.hwpx")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    template = Path(args.template)
    source = Path(args.source)
    output = Path(args.output)

    build_hwpx(template, source, output)
    plain_text = extract_plain_text_from_hwpx(output)
    required_terms = [
        "MedIT Agent Lab",
        "Clinical Trial Protocol Review Agent",
        "임상시험 승인",
        "규제 적합성 보증",
        "실제 환자 데이터",
    ]
    missing = [term for term in required_terms if term not in plain_text]
    if missing:
        raise ValueError(f"Generated HWPX is missing expected text: {missing}")

    print(f"generated={output}")
    print(f"bytes={output.stat().st_size}")
    print(f"paragraphs={plain_text.count(chr(10)) + 1}")
    if args.preview:
        print("--- preview ---")
        print("\n".join(plain_text.splitlines()[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
