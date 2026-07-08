const fs = require("fs");
const path = require("path");

let docx;
try {
  docx = require("docx");
} catch (_err) {
  docx = require("C:/Users/neo62/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/docx");
}

const {
  AlignmentType,
  BorderStyle,
  Document,
  Footer,
  HeadingLevel,
  LevelFormat,
  Packer,
  PageNumber,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} = docx;

const sourcePath = process.argv[2] || "proposal/submission_form_condensed_ko.md";
const outputPath = process.argv[3] || "proposal/MedIT_Agent_Lab_submission_working.docx";

function convertMarkdownLine(line) {
  const trimmed = line.trim();
  if (!trimmed) return null;
  if (trimmed.startsWith("|")) {
    const cells = trimmed
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((cell) => cell.replace(/`/g, "").trim());
    if (cells.every((cell) => /^-+$/.test(cell.replace(/\s/g, "")))) return null;
    if (cells.length >= 3) return { type: "bullet", text: `${cells[0]}: ${cells[1]} / ${cells[2]}` };
    return { type: "bullet", text: cells.join(" / ") };
  }
  if (trimmed.startsWith("> ")) return { type: "quote", text: trimmed.slice(2).trim() };
  if (trimmed.startsWith("- ")) return { type: "bullet", text: trimmed.slice(2).trim() };
  if (/^\d+\.\s/.test(trimmed)) return { type: "number", text: trimmed.replace(/^\d+\.\s/, "") };
  return { type: "body", text: trimmed };
}

function parseMarkdown(filePath) {
  const lines = fs.readFileSync(filePath, "utf8").split(/\r?\n/);
  const metadata = {
    field: "3번 분야: 규제 대응 및 지능형 임상시험 설계",
    team: "MedIT Agent Lab",
    agent: "Clinical Trial Protocol Review Agent / 임상시험 프로토콜 사전검토 에이전트",
    koKeywords: "임상시험 프로토콜, 의료정보, 병원 데이터, 근거 기반 검토, 에이전트 AI",
    enKeywords: "Clinical Trial Protocol, Medical IT, Hospital Data Readiness, Evidence-Based Review, Agentic AI",
  };
  const sections = [];
  let current = null;
  let skip = true;

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("# 공식 제출")) continue;
    if (trimmed.startsWith("이 문서는 ")) continue;
    if (trimmed === "## 기본 정보") {
      skip = true;
      current = null;
      continue;
    }
    if (trimmed === "## 제출 전 확인 필요") {
      skip = true;
      current = null;
      continue;
    }
    if (trimmed.startsWith("## ")) {
      skip = false;
      current = { title: trimmed.slice(3).trim(), blocks: [] };
      sections.push(current);
      continue;
    }
    if (skip || !current) continue;
    const converted = convertMarkdownLine(line);
    if (converted) current.blocks.push(converted);
  }

  return { metadata, sections };
}

function run(text, options = {}) {
  return new TextRun({
    text,
    font: "함초롬돋움",
    size: options.size || 22,
    bold: options.bold || false,
    italics: options.italics || false,
  });
}

function paragraph(text, options = {}) {
  return new Paragraph({
    children: [run(text, options)],
    heading: options.heading,
    alignment: options.alignment,
    numbering: options.numbering,
    spacing: { before: options.before || 0, after: options.after || 120, line: 276 },
  });
}

function metadataTable(metadata) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "777777" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const labelWidth = 2500;
  const valueWidth = 7200;
  const rows = [
    ["선택분야", metadata.field],
    ["팀 명", metadata.team],
    ["에이전트명", metadata.agent],
    ["국문 키워드", metadata.koKeywords],
    ["영문 키워드", metadata.enKeywords],
  ];

  return new Table({
    width: { size: labelWidth + valueWidth, type: WidthType.DXA },
    columnWidths: [labelWidth, valueWidth],
    rows: rows.map(([label, value]) =>
      new TableRow({
        children: [
          new TableCell({
            width: { size: labelWidth, type: WidthType.DXA },
            borders,
            shading: { fill: "E8EEF7", type: ShadingType.CLEAR },
            margins: { top: 100, bottom: 100, left: 120, right: 120 },
            children: [paragraph(label, { bold: true, after: 0 })],
          }),
          new TableCell({
            width: { size: valueWidth, type: WidthType.DXA },
            borders,
            margins: { top: 100, bottom: 100, left: 120, right: 120 },
            children: [paragraph(value, { after: 0 })],
          }),
        ],
      })
    ),
  });
}

function buildDocument(parsed) {
  const children = [
    paragraph("제 4회 인공지능(AI) 신약개발 경진대회 예선 제안서", {
      heading: HeadingLevel.HEADING_1,
      size: 30,
      bold: true,
      alignment: AlignmentType.CENTER,
      after: 240,
    }),
    paragraph("DOCX 작업본: 최종 제출은 대회 규정에 따라 HWPX로 별도 저장 필요", {
      size: 18,
      alignment: AlignmentType.CENTER,
      after: 240,
    }),
    metadataTable(parsed.metadata),
    paragraph("", { after: 120 }),
  ];

  for (const section of parsed.sections) {
    const heading = section.title === "요약" ? "요약" : section.title;
    children.push(paragraph(heading, { heading: HeadingLevel.HEADING_2, size: 26, bold: true, before: 180, after: 120 }));
    for (const block of section.blocks) {
      if (block.type === "bullet") {
        children.push(paragraph(block.text, { numbering: { reference: "bullets", level: 0 }, after: 80 }));
      } else if (block.type === "number") {
        children.push(paragraph(block.text, { numbering: { reference: "numbers", level: 0 }, after: 80 }));
      } else if (block.type === "quote") {
        children.push(paragraph(block.text, { italics: true, after: 100 }));
      } else {
        children.push(paragraph(block.text, { after: 120 }));
      }
    }
  }

  children.push(
    paragraph("최종 제출 전 확인", { heading: HeadingLevel.HEADING_2, size: 26, bold: true, before: 180 }),
    paragraph("대회 페이지는 예선 제안서 제출 파일을 HWPX로 안내하므로, 이 DOCX는 편집용 원본으로만 사용한다.", {
      numbering: { reference: "bullets", level: 0 },
    }),
    paragraph("한글 또는 HWPX 호환 프로그램에서 열어 HWPX로 저장한 뒤 10쪽 이내 여부를 확인한다.", {
      numbering: { reference: "bullets", level: 0 },
    }),
    paragraph("임상 승인, 규제 적합성 보증, 치료 추천, 실제 환자 데이터 사용을 암시하는 표현이 없는지 최종 확인한다.", {
      numbering: { reference: "bullets", level: 0 },
    })
  );

  return new Document({
    styles: {
      default: {
        document: { run: { font: "함초롬돋움", size: 22 } },
      },
      paragraphStyles: [
        {
          id: "Heading1",
          name: "Heading 1",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: "함초롬돋움", size: 30, bold: true },
          paragraph: { spacing: { before: 160, after: 160 }, outlineLevel: 0 },
        },
        {
          id: "Heading2",
          name: "Heading 2",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: "함초롬돋움", size: 26, bold: true },
          paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [
            {
              level: 0,
              format: LevelFormat.BULLET,
              text: "•",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 480, hanging: 240 } } },
            },
          ],
        },
        {
          reference: "numbers",
          levels: [
            {
              level: 0,
              format: LevelFormat.DECIMAL,
              text: "%1.",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 480, hanging: 240 } } },
            },
          ],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 },
          },
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [run("Page ", { size: 18 }), new TextRun({ children: [PageNumber.CURRENT], size: 18 })],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });
}

async function main() {
  const parsed = parseMarkdown(sourcePath);
  const document = buildDocument(parsed);
  const buffer = await Packer.toBuffer(document);
  fs.writeFileSync(outputPath, buffer);

  const stat = fs.statSync(outputPath);
  console.log(`generated=${outputPath}`);
  console.log(`bytes=${stat.size}`);
  console.log(`sections=${parsed.sections.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
