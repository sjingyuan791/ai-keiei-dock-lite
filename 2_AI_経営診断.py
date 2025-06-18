# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import io
from datetime import datetime
import streamlit as st

# ▼ Google Analytics（GA4）タグの埋め込み（unsafe_allow_html=Trueを必ず指定）
st.markdown(
    """
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TRBGYB90K3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-TRBGYB90K3');
</script>
""",
    unsafe_allow_html=True,
)

from config import init_page
from ui_components import init_session
from ai_engine import (
    show_external_environment_analysis_ai,
    deep_dive_questions_ai,
    show_swot_section_ai,
    root_cause_analysis_ai,
    action_with_eval_ai,
)
from pdf_generator import create_pdf

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ---- ページ設定・セッション初期化 ----
init_page(title="AI経営診断 – 外部環境分析")
init_session(
    [
        "user_input",
        "external_output",
        "deep_dive_questions",
        "deep_dive_answers",
        "swot_output",
        "root_cause_output",
        "action_result",
        "pdf_bytes",
    ]
)

STEP_NAMES = {
    1: "基本情報入力",
    2: "外部環境分析",
    3: "AIからの質問",
    4: "SWOT分析",
    5: "真因分析",
    6: "改善アクション提案 ＋ 統合評価",
}
TOTAL_STEPS = 6
step = st.session_state.get("step", 2)

# ここだけで本番⇔開発が切り替わる
IS_DEBUG = False  # 本番はFalse、テストしたい時だけTrueに

if IS_DEBUG:
    DEBUG_MODE = st.sidebar.toggle("🛠️ ダミーデータON", value=False)
    if DEBUG_MODE:
        st.sidebar.success("ダミーデータでテスト中！")
        st.session_state["user_input"] = {
            "会社名・屋号": "サンプル株式会社",
            "業種（できるだけ詳しく）": "自動車整備業",
            "地域": "東京都新宿区",
            "主な商品・サービス": "自動車の修理・販売",
            "主な顧客層": "地域の一般消費者",
            "年間売上高（おおよそ）": 10000000,
            "粗利率（おおよそ）": 30,
            "最終利益（税引後・おおよそ）": 1000000,
            "借入金額（だいたい）": 5000000,
            "経営の問題点": "売上の季節変動が大きく、利益率が安定しない",
        }
else:
    DEBUG_MODE = False  # 本番では必ずFalse
# 必須入力チェック＆未入力なら強制停止
user_input = st.session_state.get("user_input", {})
required_keys = [
    "会社名・屋号",
    "業種（できるだけ詳しく）",
    "地域",
    "主な商品・サービス",
    "主な顧客層",
    "経営の問題点",
]
# stepが1（基本情報入力）以外の場合にチェック
if step > 1 and not all(user_input.get(k, "").strip() for k in required_keys):
    st.error("⚠️ 基本情報の必須項目を全て入力・保存してください。")
    st.stop()


# --- 共通CSS ---
st.markdown(
    """
<style>
.step-progress-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 2.2em; margin-top: .5em;
}
.step-center-area {
    flex:1; text-align:center;
}
.step-num-label {
    color:#1976d2; font-size:1.07em; font-weight:600; letter-spacing:.5px;
}
.step-title-label {
    display:block; font-size:1.48em; font-weight:800; margin-top:.17em; color:#152e4d; letter-spacing:.04em;
}
.nav-btn {
    background: #f1f5fa; color: #1976d2; border: none; border-radius: 13px;
    font-size:1.05em; font-weight: 700; padding: .55em 1.6em;
    box-shadow: 0 2px 8px #e8eaf6; cursor: pointer;
    transition: background .18s;
}
.nav-btn:disabled {
    background:#e4e9f2; color:#b2bac8; cursor:not-allowed; opacity:.6;
}
.beauty-card {
    background:linear-gradient(100deg,#f7fafc,#e7f1fd 95%);
    border-radius:17px;padding:1.3em 1.8em;margin:1.3em 0 2em 0;
    box-shadow:0 3px 16px #e1eaf5; border-left:7px solid #1976d2;
}
.card-title {
    font-size:1.24em;font-weight:700;margin-bottom:0.32em;color:#1976d2;
}
.card-section {
    font-size:1.09em;line-height:2.04;margin:0.5em 0 0 1.1em;color:#24314d;
}
.ai-run-btn {
    display:inline-block;background:#1976d2;color:#fff;font-size:1.13em;
    font-weight:700;border-radius:13px;padding:0.65em 2.2em;margin:1.3em 0 1em;
    box-shadow:0 2px 13px #b7d0ee;cursor:pointer;transition:background .2s;
    border:none;
}
.ai-run-btn:hover { background:#154b97; }
hr.beauty-hr {
    border:none;
    height:1px;
    background:#aedbf5;
    margin:1em 0;
}
.action-title {
    font-size:1.13em;
    font-weight:900;
    color:#d32f2f;
    margin:0.5em 0 0.3em;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- ステップバー＆ナビゲーション：カラム方式 ---
col_prev, col_center, col_next = st.columns([1, 5, 1])
with col_prev:
    if st.button("◀ 前へ", disabled=step == 1):
        st.session_state["step"] = max(1, step - 1)
        st.rerun()
with col_center:
    st.markdown(
        f"""
    <div style="text-align:center;">
        <span style="color:#1976d2; font-size:1.12em; font-weight:600;">Step {step} / {TOTAL_STEPS}</span><br>
        <span style="font-size:1.55em; font-weight:800; color:#152e4d;">{STEP_NAMES.get(step, '')}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
with col_next:
    if st.button("次へ ▶", disabled=step == TOTAL_STEPS):
        st.session_state["step"] = min(TOTAL_STEPS, step + 1)
        st.rerun()

# ==== 外部環境分析カード ====
from modules.utils import extract_item


def display_external_analysis(output):
    viewpoints = {
        "政治・制度": "Politics",
        "経済": "Economy",
        "社会・文化": "Society & Culture",
        "技術": "Technology",
        "業界構造": "Industry Structure",
        "競合ポジション": "Competitive Positioning",
    }
    for jp, en in viewpoints.items():
        summary = extract_item(jp, "要約", output)
        source = extract_item(jp, "出典", output)
        st.markdown(
            f"""
<div class="beauty-card">
  <div class="card-title">{jp} <span style="font-size:0.81em;color:#566b87;">({en})</span></div>
  <ul class="card-section">
    <li><b>要約</b>: {summary}</li>
    <li><b>出典</b>: <span style="font-size:0.91em;color:#636978;">{source}</span></li>
  </ul>
</div>
""",
            unsafe_allow_html=True,
        )


# --- Markdownの整形: h3, 水平線, アクションタイトル・見出しなどをリッチHTML化 ---
def format_action_output(md_text):
    # --- を水色hr風に
    md_text = re.sub(
        r"^-{3,}$", '<hr class="beauty-hr" />', md_text, flags=re.MULTILINE
    )
    # ###（h3）や【最優先アクション】などを旗+太字に
    md_text = re.sub(
        r"^###?\s*([^\n]+)",
        r'<div class="action-title"><span style="font-size:1.2em;">🚩</span> \1</div>',
        md_text,
        flags=re.MULTILINE,
    )
    # 例: 【最優先アクション】 だけの時もタイトル強調
    md_text = re.sub(
        r"^【最優先アクション】([^\n]*)",
        r'<div class="action-title"><span style="font-size:1.2em;">🚩</span> 【最優先アクション】\1</div>',
        md_text,
        flags=re.MULTILINE,
    )
    return md_text


def format_root_cause_output(md_text):
    # 見出し（真因分析タイトル）をbeauty-cardのタイトル並に
    md_text = re.sub(
        r"^# ?真因（Root Cause）",
        r'<div style="font-size:1.18em;font-weight:900;letter-spacing:.04em;color:#1d4127;margin-bottom:.18em;font-family:\'Noto Sans JP\',sans-serif;">🔎 真因分析 <span style=\'font-size:0.95em;color:#3c3c3c;font-weight:700;\'>（Root Cause）</span></div>',
        md_text,
        flags=re.MULTILINE,
    )
    # **太字** → beauty-card本文と同じぐらい
    md_text = re.sub(
        r"\*\*(.*?)\*\*",
        r'<span style="font-weight:800;color:#202a33;font-family:\'Noto Sans JP\',sans-serif;font-size:1.09em;">\1</span>',
        md_text,
    )
    # 主な原因（中見出し）を1.09emくらいで
    md_text = re.sub(
        r"^## ?主な原因（Causes）",
        r'<div style="font-size:1.09em;font-weight:800;letter-spacing:.03em;color:#193b2e;margin:.65em 0 .2em;font-family:\'Noto Sans JP\',sans-serif;">主な原因 <span style="font-size:0.97em;color:#323b33;font-weight:700;">(Causes)</span></div>',
        md_text,
        flags=re.MULTILINE,
    )
    # -リストをbeauty-card本文と同じくらい
    md_text = re.sub(
        r"^- (.*?)$",
        r'<li style="margin-bottom:.4em;font-size:1.09em;line-height:1.7;font-family:\'Noto Sans JP\',sans-serif;">\1</li>',
        md_text,
        flags=re.MULTILINE,
    )
    # ulで囲む
    md_text = re.sub(
        r"(?:<li .*?</li>\n*)+",
        lambda m: f'<ul style="padding-left:1.6em;margin:.5em 0 1em 0;">{m.group(0)}</ul>',
        md_text,
        flags=re.DOTALL,
    )
    # 全体も同じサイズ
    return f"<div style=\"font-size:1.09em;line-height:1.8;font-family:'Noto Sans JP',sans-serif;color:#222;\">{md_text}</div>"


# ===== 各ステップの処理 =====
if step == 2:
    st.markdown(
        '<div class="beauty-card"><b>🌐 外部環境分析</b><br>AIがPEST・競合・業界などのデータをリアルタイムで自動分析します。</div>',
        unsafe_allow_html=True,
    )
    user_input = st.session_state.get("user_input")
    if not isinstance(user_input, dict) or not user_input:
        st.warning("⚠️ 先に『基本情報入力』を行ってください。")
    else:
        if st.button("▶ AI実行", key="run_extenv", help="外部環境のAI分析を開始"):
            with st.spinner("分析中…"):
                st.session_state["external_output"] = (
                    show_external_environment_analysis_ai(user_input)
                )
        output = st.session_state.get("external_output", "")
        if output:
            display_external_analysis(output)
        else:
            st.markdown(
                '<button class="ai-run-btn">▶ AI実行ボタンを押してください。</button>',
                unsafe_allow_html=True,
            )

elif step == 3:
    st.markdown(
        '<div class="beauty-card"><b>🔍 AIからの質問</b><br>経営状況を深掘りする追加ヒアリングを自動生成。</div>',
        unsafe_allow_html=True,
    )
    questions = deep_dive_questions_ai(st.session_state["user_input"])
    st.session_state["deep_dive_questions"] = questions
    st.markdown("<div style='margin:1.4em 0;'></div>", unsafe_allow_html=True)

    # ここからformでまとめる
    with st.form(key="deep_dive_form"):
        for i, q in enumerate(questions, 1):
            cat = q.get("category", f"カテゴリ{i}")
            st.markdown(
                f"""
<div class="beauty-card" style="background:linear-gradient(97deg,#f8fbff,#e9f4ff 85%);border-left:6px solid #09a7b3;">
  <div class="card-title" style="color:#089eab;">{i}. {cat}</div>
  <div style="margin-top:.45em;">
    <b>質問:</b> {q.get('question','')}<br>
    <span style="color:#607d8b;font-size:0.96em;">根拠: {q.get('rationale','')}</span>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
            st.text_area(
                "回答を入力", key=f"qq_{i}", value=st.session_state.get(f"qq_{i}", "")
            )
        submitted = st.form_submit_button("📝 回答を保存")
        if submitted:
            ans = {
                f"qq_{i}": st.session_state.get(f"qq_{i}")
                for i in range(1, len(questions) + 1)
            }
            st.session_state["deep_dive_answers"] = ans
            st.success("✅ 回答を保存しました。次のステップへお進みください。")

elif step == 4:
    st.markdown(
        '<div class="beauty-card"><b>📝 SWOT分析</b><br>あなたの会社の強み・弱み・機会・脅威をAIが自動で整理。</div>',
        unsafe_allow_html=True,
    )
    deep_dive_answers = st.session_state.get("deep_dive_answers")
    if not deep_dive_answers or not any(deep_dive_answers.values()):
        st.warning("先にAIからの質問にすべて回答してください。")
    else:
        if st.button("▶ AI実行", key="run_swot"):
            with st.spinner("SWOT分析中…"):
                st.session_state["swot_output"] = show_swot_section_ai(
                    st.session_state["user_input"]
                )
        output = st.session_state.get("swot_output")
        if output:
            st.markdown(
                f'<div class="beauty-card" style="background:#fff7ef;border-left:6px solid #f39c12;">{output}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<button class="ai-run-btn">▶ AI実行ボタンを押してください。</button>',
                unsafe_allow_html=True,
            )

# step==5 真因分析部分
elif step == 5:
    st.markdown(
        '<div class="beauty-card"><b>🔎 真因分析</b><br>問題の根本原因をAIで分解・特定します。</div>',
        unsafe_allow_html=True,
    )
    # ここで「AI実行」ボタンを実装（他stepと同じパターン）
    if st.button("▶ AI実行", key="run_rootcause"):
        with st.spinner("真因分析中…"):
            st.session_state["root_cause_output"] = root_cause_analysis_ai(
                st.session_state["user_input"]
            )
    output = st.session_state.get("root_cause_output")
    if output:
        formatted = format_root_cause_output(output)
        st.markdown(
            f'<div class="beauty-card" style="background:#f7fff6;border-left:6px solid #21a073;">{formatted}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<button class="ai-run-btn">▶ AI実行ボタンを押してください。</button>',
            unsafe_allow_html=True,
        )


elif step == 6:
    st.markdown(
        '<div class="beauty-card"><b>💡 改善アクション提案</b><br>経営改善策をAIで提案します。</div>',
        unsafe_allow_html=True,
    )
    if st.button("▶ AI実行", key="run_action"):
        if not all(
            st.session_state.get(k) for k in ("swot_output", "root_cause_output")
        ):
            st.warning("先にSWOT分析と真因分析を完了してください。")
        else:
            with st.spinner("提案＆評価中…"):
                st.session_state["action_result"] = action_with_eval_ai(
                    st.session_state["user_input"]
                )
    result = st.session_state.get("action_result", {})
    if result:
        actions_md = result.get("actions_md", "")
        if actions_md:
            formatted_md = format_action_output(actions_md)
            st.markdown(
                f'<div class="beauty-card" style="background:#eef7fe;border-left:6px solid #2574b8;">{formatted_md}</div>',
                unsafe_allow_html=True,
            )
        evaluations = result.get("evaluations", [])
        if evaluations:
            # 詳細（expander）のみ表示
            for ev in evaluations:
                with st.expander(
                    f"📝 {ev['title']} の評価根拠（クリックで詳細）", expanded=False
                ):
                    st.markdown(
                        f"""
| 項目 | 点数 | 根拠 |
|:----------|:----:|:--------------------------|
| V（経済価値）        | {ev.get('V','')} | {ev.get('root_V','')} |
| R（希少性）          | {ev.get('R','')} | {ev.get('root_R','')} |
| I（模倣困難性）      | {ev.get('I','')} | {ev.get('root_I','')} |
| O（組織適合性）      | {ev.get('O','')} | {ev.get('root_O','')} |
| 市場成長性           | {ev.get('市場成長性','')} | {ev.get('root_市場成長性','')} |
| 実行難易度           | {ev.get('実行難易度','')} | {ev.get('root_実行難易度','')} |
| 投資効率             | {ev.get('投資効率','')} | {ev.get('root_投資効率','')} |
| 顧客評価             | {ev.get('顧客評価','')} | {ev.get('root_顧客評価','')} |
| リスク               | {ev.get('リスク','')} | {ev.get('root_リスク','')} |
| **合計点数**         | **{ev['total']}** | |
"""
                    )
                    st.success(f"この案の合計点数：**{ev['total']}**")
            st.info("※同点の場合は現場状況や経営優先度に応じて決定を！")
    else:
        st.markdown(
            '<button class="ai-run-btn">▶ AI実行ボタンを押してください。</button>',
            unsafe_allow_html=True,
        )


# ==========================
# Step7: PDF 出力（ここはそのまま）
# ==========================
if step == TOTAL_STEPS:
    st.header("📄 PDFレポート出力")
    pdf_filename = f"AI経営診断レポート_{datetime.today().strftime('%Y%m%d')}.pdf"
    user_input = st.session_state.get("user_input", {})
    external_output = st.session_state.get("external_output", "")
    deep_dive_questions = st.session_state.get("deep_dive_questions", [])
    swot_output = st.session_state.get("swot_output", "")
    root_cause_output = st.session_state.get("root_cause_output", "")
    action_result = st.session_state.get("action_result") or {}
    action_eval_output = action_result.get("evaluations", [])
    report_blocks = [
        {"title": "【基本情報】", "content": str(user_input)},
        {"title": "【外部環境分析】", "content": external_output},
        {"title": "【AIからの質問】", "content": str(deep_dive_questions)},
        {"title": "【SWOT分析】", "content": swot_output},
        {"title": "【真因分析】", "content": root_cause_output},
    ]
    pdf_buffer = io.BytesIO()
    create_pdf(
        pdf_buffer,
        report_blocks=report_blocks,
        action_eval_output=action_eval_output,
        root_cause_output=root_cause_output,
    )
    pdf_buffer.seek(0)
    st.download_button(
        label="📄 PDFをダウンロード",
        data=pdf_buffer,
        file_name=pdf_filename,
        mime="application/pdf",
    )
