# -*- coding: utf-8 -*-
from __future__ import annotations
import io
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Flowable,
)

# フォント設定
_FONT = "Helvetica"
font_path = Path(__file__).parent / "fonts" / "ipag.ttf"
if font_path.exists():
    pdfmetrics.registerFont(TTFont("IPAGothic", str(font_path)))
    _FONT = "IPAGothic"

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName=_FONT,
    fontSize=22,
    leading=26,
    alignment=TA_CENTER,
    spaceAfter=24,
)
H1 = ParagraphStyle(
    "Heading1",
    parent=styles["Heading1"],
    fontName=_FONT,
    fontSize=14,
    leading=20,
    spaceBefore=12,
    spaceAfter=12,
    textColor=colors.HexColor("#0D2E5A"),
)
BODY = ParagraphStyle(
    "BodyText",
    parent=styles["Normal"],
    fontName=_FONT,
    fontSize=11,
    leading=18,
    spaceAfter=10,
    alignment=TA_LEFT,
)


# タイトル中の絵文字・特殊記号を除去
def clean_title(text):
    for mark in ["🚩", "🟥", "▶", "□", "■"]:
        text = text.replace(mark, "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# 強調（色付きボックス）を作るFlowable
class HighlightBox(Flowable):
    def __init__(self, text, width=420, height=45, color="#E0F7FA"):
        Flowable.__init__(self)
        self.text = text
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(colors.HexColor(self.color))
        self.canv.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=0)
        self.canv.setFillColor(colors.HexColor("#0D2E5A"))
        self.canv.setFont(_FONT, 12)
        self.canv.drawString(16, self.height - 28, clean_title(self.text))
        self.canv.restoreState()


# Markdown→HTML変換
_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC = re.compile(r"\*(.+?)\*")


def _md_to_html(text: str) -> str:
    text = _MD_BOLD.sub(r"<b>\1</b>", text)
    text = _MD_ITALIC.sub(r"<i>\1</i>", text)
    return text


# 本文ブロック追加
def _add_body_block(story: list, text: str):
    for line in text.strip().splitlines():
        l = line.rstrip()
        if not l:
            continue
        html = _md_to_html(l)
        if l.startswith("###"):
            story.append(Paragraph(f"<b>{html[3:].strip()}</b>", H1))
        elif l.startswith("- "):
            story.append(Paragraph(html[2:].strip(), BODY, bulletText="•"))
        else:
            story.append(Paragraph(html, BODY))


def _build_eval_tbl(evals: List[Dict[str, Any]]):
    if not evals:
        return Paragraph("※ アクション統合評価なし", BODY)

    header = ["アクション", "総合", "ランク"]
    data = [header]
    for r in evals:
        data.append(
            [
                Paragraph(_md_to_html(clean_title(r.get("title", ""))), BODY),
                r.get("total", ""),
                r.get("rank", ""),
            ]
        )
    tbl = Table(data, repeatRows=1, colWidths=[200, 40, 40], hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#555555")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#AAAAAA")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D2E5A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 1), (-2, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, -1), _FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#F5F7FA"), colors.white],
                ),
            ]
        )
    )
    return tbl


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor("#0D2E5A"))
    canvas.setLineWidth(0.6)
    canvas.line(50, h - 55, w - 50, h - 55)
    canvas.setStrokeColor(colors.HexColor("#888888"))
    canvas.setLineWidth(0.3)
    canvas.line(50, 45, w - 50, 45)
    canvas.setFont(_FONT, 8)
    canvas.drawRightString(w - 50, 30, str(doc.page))
    canvas.restoreState()


def create_pdf(
    filename: io.BytesIO | str,
    *,
    report_blocks: List[Dict[str, str]],
    action_eval_output: List[Dict[str, Any]] | None = None,
    root_cause_output: str | None = None,
    action_best: str | None = None,
    ai_questions_answers: List[Dict[str, str]] | None = None,
):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=70,
        bottomMargin=60,
        title="AI経営診断レポート",
    )
    story: list = []

    # Cover
    story.append(Paragraph("AI経営診断レポート", TITLE))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"発行日: {datetime.today().strftime('%Y-%m-%d')}", BODY))
    story.append(PageBreak())

    # ① 改善提案（最優先アクション＋統合評価テーブル）
    if action_best:
        story.append(Paragraph("■ 改善提案・最優先アクション", H1))
        story.append(Spacer(1, 2))
        story.append(HighlightBox(action_best, width=420, height=45, color="#FFE082"))
        story.append(Spacer(1, 18))
    if action_eval_output:
        story.append(Paragraph("アクション統合評価 (VRIO + 5軸)", H1))
        story.append(Spacer(1, 8))
        story.append(_build_eval_tbl(action_eval_output))
        story.append(Spacer(1, 18))

    # ② 真因分析（report_blocks内の真因分析ブロックは出力しない）
    if root_cause_output:
        story.append(Paragraph("■ 真因分析（Root Cause）", H1))
        _add_body_block(story, root_cause_output)
        story.append(Spacer(1, 14))

    # ③ SWOT分析（タイトルにSWOT含むブロックのみ中間に）
    for blk in report_blocks:
        title_upper = blk["title"].upper()
        if "SWOT" in title_upper:
            story.append(Paragraph(blk["title"], H1))
            _add_body_block(story, blk["content"])
            story.append(Spacer(1, 14))

    # ④ AIからの質問・回答（新設）
    if ai_questions_answers:
        story.append(Paragraph("■ AIによるヒアリング質問・回答", H1))
        for i, qa in enumerate(ai_questions_answers, 1):
            q = qa.get("question", "")
            a = qa.get("answer", "")
            story.append(Paragraph(f"{i}. <b>質問:</b> {q}", BODY))
            story.append(Paragraph(f"<b>回答:</b> {a}", BODY))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 14))

    # ⑤ 根拠ブロック（SWOTと真因分析以外をまとめて。重複防止）
    for blk in report_blocks:
        title_upper = blk["title"].upper()
        # 「基本情報」「AIからの質問」はPDF出力から除外
        if ("SWOT" not in title_upper) and ("真因" not in blk["title"]):
            if "基本情報" in blk["title"] or "AIからの質問" in blk["title"]:
                continue  # ← ここでスキップ！
            story.append(Paragraph(blk["title"], H1))
            _add_body_block(story, blk["content"])
            story.append(Spacer(1, 14))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
