# -*- coding: utf-8 -*-
# ======================================================================
# ai_engine.py ― AI経営診断 GPT（最高品質プロンプト＆ロジック版）
# ======================================================================
from __future__ import annotations

import json
import os
import textwrap
import traceback
from typing import Any, Dict, List

import streamlit as st
from openai import OpenAI, APIError

# ----------------------------------------------------------------------
# OpenAIクライアント設定
# ----------------------------------------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_DEFAULT_MODEL = "o3-mini"

_SYSTEM_PROMPT = (
    "あなたは超一流の経営コンサルタントです。"
    "経営者・事業責任者に対して、シンプルかつ信頼感のある表現で、"
    "現実的・実践的な戦略・改善提案を行ってください。"
    "情報は必ず全体像をふまえて統合・整理し、論拠と構造を明示してください。"
    "専門用語は必要最小限にとどめ、無駄な説明・くどい表現・ふりがなは不要です。"
)


def run_gpt(
    prompt: str,
    *,
    model: str = _DEFAULT_MODEL,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> str:
    try:
        params: Dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        if model.startswith("o3"):
            params["max_completion_tokens"] = max_tokens
        else:
            params["temperature"] = temperature
            params["max_tokens"] = max_tokens

        rsp = client.chat.completions.create(**params)
        return (rsp.choices[0].message.content or "").strip()
    except APIError as e:
        st.error(f"❌ OpenAI APIError: {e}")
        return ""


# ======================================================================
# 外部環境分析（GPT-4o推奨・Web検索なしでも安定）
# ======================================================================
import openai
import streamlit as st


def show_external_environment_analysis_ai(user_input: dict) -> str:
    c = lambda k, d="未入力": user_input.get(k, d)
    # 各観点名・英語名セット
    aspects = [
        ("政治・制度", "Politics"),
        ("経済", "Economy"),
        ("社会・文化", "Society / Culture"),
        ("技術", "Technology"),
        ("業界構造", "Industry Structure"),
        ("競合ポジション", "Competition Position"),
    ]

    # 1観点ごとのプロンプト生成関数


import openai
import streamlit as st
import time


def show_external_environment_analysis_ai(user_input: dict, max_retry=2) -> str:
    c = lambda k, d="未入力": user_input.get(k, d)
    aspects = [
        ("政治・制度", "Politics"),
        ("経済", "Economy"),
        ("社会・文化", "Society / Culture"),
        ("技術", "Technology"),
        ("業界構造", "Industry Structure"),
        ("競合ポジション", "Competition Position"),
    ]

    def build_prompt(aspect_ja, aspect_en):
        return f"""
あなたは「中小企業専門の経営コンサルタント」です。
必ず「リアルタイムの公的情報・信頼できる専門メディア」のWeb検索結果も活用し、
下記ルールで「{aspect_ja}（{aspect_en}）」に関する**経営判断に役立つ“深い洞察・現場示唆・打ち手ヒント”を含む厚い要約**を
Markdownで**200～250字で出力**してください。

- 必ず経営判断や現場実務に本当に役立つ具体的視点（なぜ重要か／何をすべきか／他社事例／リスク／数字・現場例等）を含めること
- ニュースの羅列・一般的説明・抽象論は禁止
- **補助金・助成金・給付金など特定の公的制度名や金額は一切記載しないこと。**
- 必ず信頼できる一次ソース（行政発表・日経/業界新聞・政府Web・専門媒体等）の出典URL・媒体名を2つ以上記載

【企業情報】
会社名: {c('会社名・屋号')}
業種: {c('業種（できるだけ詳しく）')}
地域: {c('地域')}
商品・サービス: {c('主な商品・サービス')}
顧客層: {c('主な顧客層')}
年間売上高: {c('年間売上高（おおよそ）')}
粗利率: {c('粗利率（おおよそ）')}
最終利益: {c('最終利益（税引後・おおよそ）')}
借入金額: {c('借入金額（だいたい）')}
経営の問題点: {c('経営の問題点')}

【Markdown出力フォーマット（例）】
## {aspect_ja} ({aspect_en})
- 要約: 季節変動リスクの高い自動車整備業では現金管理や利益率モニタリング、低利融資制度等の活用が重要。資金計画や販促施策のタイミング見直しで、繁忙期・閑散期の収益安定化が図れる。公式サイト等で最新支援情報を定期的に確認する運用が推奨される。
- 出典: 東京都中小企業振興公社 https://www.tokyo-kosha.or.jp, 日本経済新聞 https://www.nikkei.com
"""

    outputs = []
    client = openai.OpenAI()

    for aspect_ja, aspect_en in aspects:
        retry = 0
        while retry <= max_retry:
            prompt = build_prompt(aspect_ja, aspect_en)
            try:
                response = client.chat.completions.create(
                    model="gpt-4.1",  # "gpt-4.1-mini"や"gpt-4o"も可
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                    temperature=0.7,
                )
                result = response.choices[0].message.content.strip()
            except Exception as e:
                result = f"【AIエラー発生】{aspect_ja} ({aspect_en}) : {e}"

            if "【AIエラー発生】" not in result:
                outputs.append(result)
                break
            else:
                retry += 1
                time.sleep(2)  # API制限対策

        if retry > max_retry:
            outputs.append(f"【AIエラー発生】（{aspect_ja}）")

    final_markdown = "\n\n".join(outputs)
    st.session_state["external_output"] = final_markdown
    return final_markdown


# ======================================================================
# AIからの質問
# ======================================================================
def deep_dive_questions_ai(user_input: dict) -> list[dict]:
    import textwrap, json, streamlit as st

    basic_json = json.dumps(user_input, ensure_ascii=False)[:2500]
    external = st.session_state.get("external_output", "")[:1800]
    prompt = textwrap.dedent(
        f"""
あなたは「中小企業の現場・実務を熟知したプロ経営コンサルタント兼AIコーチ」です。
下記「課題」「基本・財務情報」「外部環境分析」を踏まえ、
【今まさに経営判断で迷っている経営者・現場責任者に“本質を突く・意思決定につながる鋭い質問”】だけを厳選してください。

【特に重視する指示】
- 5観点（組織・人事／財務／マーケティング／IT・DX／オペレーション）ごとに「現場ヒアリングや経営判断で本当に役立つ質問」を**必ず2問ずつ**（合計10問以上）出す
- 「現状の数字・プロセス・役割・意思決定・現場感覚」に具体的に踏み込むこと
- 抽象論や使い回しの一般論は禁止。“何が・誰に・なぜ・どう影響しているか”を聞き出す粒度に
- 「現場の数値・進捗・担当者感覚」に直結する具体質問を多く（例：●●率は？●●にどれだけ時間がかかる？●●担当は誰？）
- 各質問ごとに「今なぜそれを問うのか（根拠・30字以内）」も必ず付与（課題や外部環境との関連を明確化）
- Yes/Noや数値・現場の一次情報で答えられる質問も含めること

【さらに精度を上げるための制約】
- 業界特有の事情や直面課題（人材流出・IT化遅れ・新規顧客獲得難など）があれば、必ず反映
- 経営者が「今すぐ動く」「課題の本質に気づく」ような質問・粒度を強調
- フォーマット例：「現場で●●のKPIは明確ですか？」「●●プロジェクトは現状どこが停滞していますか？」など

【出力ルール厳守】
- 下記JSON形式でのみ出力（他の出力は禁止）
{{
  "questions": [
    {{"category":"組織・人事","question":"～","rationale":"～"}},
    ...
  ]
}}

【課題】
{user_input.get('経営の問題点','未入力')}
【基本・財務情報】
{basic_json}
【外部環境】
{external}
        """
    )

    schema = {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "question": {"type": "string"},
                        "rationale": {"type": "string"},
                    },
                    "required": ["category", "question", "rationale"],
                },
            }
        },
        "required": ["questions"],
    }
    try:
        rsp = client.chat.completions.create(
            model=_DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            functions=[{"name": "make_questions", "parameters": schema}],
            function_call={"name": "make_questions"},
        )
        return json.loads(rsp.choices[0].message.function_call.arguments)["questions"]
    except Exception as e:
        st.warning(f"⚠️ Question JSON 生成失敗: {e}")
        return []


# ======================================================================
# SWOT分析
# ======================================================================
def show_swot_section_ai(user_input: dict) -> str:
    external = st.session_state.get("external_output", "(外部環境分析 未実行)")
    deep_ans = st.session_state.get("deep_dive_questions", [])
    deep_answers = st.session_state.get("deep_dive_answers", {})
    # 質問＋ユーザー回答を集約
    question_and_answers = "\n".join(
        f"{i+1}. {q['category']}｜{q['question']} → {deep_answers.get(f'qq_{i+1}','')}"
        for i, q in enumerate(deep_ans)
    )
    prompt = textwrap.dedent(
        f"""
        下記すべての情報をもとに、S（強み）W（弱み）O（機会）T（脅威）を
        それぞれ3～5点ずつ挙げてください。強み・弱みには「課題」や「AIからの質問内容」も反映させてください。
        各項目は「要点＋根拠」のセットで、論理的かつ端的に。

        【課題】
        {user_input.get('経営の問題点','未入力')}
        【基本・財務情報】
        会社名: {user_input.get('会社名・屋号')}
        業種: {user_input.get('業種（できるだけ詳しく）')}
        地域: {user_input.get('地域')}
        年間売上高: {user_input.get('年間売上高（おおよそ）')}
        粗利率: {user_input.get('粗利率（おおよそ）')}
        最終利益: {user_input.get('最終利益（税引後・おおよそ）')}
        借入金額: {user_input.get('借入金額（だいたい）')}

        【外部環境】
        {external}

        【AIからの質問・回答】
        {question_and_answers}
        """
    )
    swot = run_gpt(prompt)
    st.session_state["swot_output"] = swot
    return swot


# ======================================================================
# 真因分析（すべての情報から）
# ======================================================================
def root_cause_analysis_ai(user_input: dict) -> str:
    import textwrap, streamlit as st
    import re

    external = st.session_state.get("external_output", "(外部環境分析 未実行)")
    swot = st.session_state.get("swot_output", "(SWOT 未実行)")
    deep_ans = st.session_state.get("deep_dive_questions", [])
    deep_answers = st.session_state.get("deep_dive_answers", {})
    question_and_answers = "\n".join(
        f"{i+1}. {q['category']}｜{q['question']} → {deep_answers.get(f'qq_{i+1}','')}"
        for i, q in enumerate(deep_ans)
    )

    prompt = textwrap.dedent(
        f"""
あなたは現場・経営に強い超一流コンサルタントです。
下記情報をもとに、必ず以下の順で構造的に出力してください。

1. # 現在の問題点
  - 箇条書きで2～5点程度、現象や症状を具体的に（できれば数字・現場証拠も）。
2. # 主な原因
  - 箇条書きで2～3点、なぜ上記問題が起こっているか、要因を簡潔に。
3. # 真因（Root Cause）
  - 一言で“最大の原因”を特定。なぜこれが真因か、理由・根拠も1文で述べる。

【出力例】
# 現在の問題点
- 売上が3期連続で減少
- 粗利率が昨年30%→今年22%に低下
- 新規顧客開拓が進んでいない

# 主な原因
- 既存顧客への値引き対応が増加
- 営業活動が属人的で新規開拓が弱い

# 真因（Root Cause）
**営業戦略の多角化不足**
なぜこれが真因か：既存顧客依存度が高く、新規市場開拓リソースが不足しているため。

---
【問題】
{user_input.get('経営の問題点','未入力')}
【基本・財務情報】
会社名: {user_input.get('会社名・屋号')}
業種: {user_input.get('業種（できるだけ詳しく）')}
地域: {user_input.get('地域')}
年間売上高: {user_input.get('年間売上高（おおよそ）')}
粗利率: {user_input.get('粗利率（おおよそ）')}
最終利益: {user_input.get('最終利益（税引後・おおよそ）')}
借入金額: {user_input.get('借入金額（だいたい）')}

【外部環境】
{external}

【AIからの質問・回答】
{question_and_answers}

【SWOT分析】
{swot}
    """
    )

    txt = run_gpt(prompt)
    # 念のためHTMLタグ除去（AIが万一タグを返しても大丈夫なように）
    clean_txt = re.sub(r"<[^>]+>", "", txt)
    st.session_state["root_cause_output"] = clean_txt
    return clean_txt


# ======================================================================
# 改善アクション提案＋統合評価
# ======================================================================
def action_with_eval_ai(user_input: dict) -> Dict[str, Any]:
    import textwrap, streamlit as st, json, traceback

    external = st.session_state.get("external_output", "")
    swot = st.session_state.get("swot_output", "")
    root = st.session_state.get("root_cause_output", "")
    deep_ans = st.session_state.get("deep_dive_questions", [])
    deep_answers = st.session_state.get("deep_dive_answers", {})
    question_and_answers = "\n".join(
        f"{i+1}. {q['category']}｜{q['question']} → {deep_answers.get(f'qq_{i+1}','')}"
        for i, q in enumerate(deep_ans)
    )
    prompt = textwrap.dedent(
        f"""
下記の全情報を統合し、「最も効果的な改善アクション（1～2個）」を【🚩最優先アクション】として必ず"最上位で目立つように"、さらに重要なアクションも加えて計3つ提案してください。
【重要】最優先アクション（is_best:true）は、必ず合計点（total）が最大のものに設定してください。
複数同点がある場合は、最も即効性・重要性が高い施策1つのみis_best:true、それ以外はis_best:falseとしてください。

各アクションごとに、下記13項目を必ずJSON形式で記述してください（空欄禁止）。

1. title（タイトル。最優先は"【🚩最優先アクション】"で始める）
2. content（現場で今すぐ着手できる具体策も明記）
3. evidence（根拠データ・業界平均・他社実例・公的出典。必ず1つはURLまたは媒体名を含める）
4. risk（やらない場合のリスク。1行で損失リスク・失敗例を具体的に）
5. kpi（必ず具体的な数値・指標。空欄禁止）
6. V（経済価値：1～10点）と root_V（その根拠を30字以内で）
7. R（希少性：1～10点）と root_R（その根拠を30字以内で）
8. I（模倣困難性：1～10点）と root_I（その根拠を30字以内で）
9. O（組織適合性：1～10点）と root_O（その根拠を30字以内で）
10. 市場成長性（1～10点）と root_市場成長性（その根拠を30字以内で）
11. 実行難易度（1～10点）と root_実行難易度（その根拠を30字以内で）
12. 投資効率（1～10点）と root_投資効率（その根拠を30字以内で）
13. 顧客評価（1～10点）と root_顧客評価（その根拠を30字以内で）
14. リスク（1～10点）と root_リスク（その根拠を30字以内で）
15. total（合計点数）, rank（A/B/C）, is_best（bool/最優先true）

【JSON出力例】
{{
  "actions": [
    {{
      "title": "【🚩最優先アクション】特定整備認証と電子整備対応体制の即時強化",
      "content": "...",
      "evidence": "...",
      "risk": "...",
      "kpi": "...",
      "V": 8, "root_V": "粗利率改善が見込める",
      "R": 7, "root_R": "他社との差別化要素",
      "I": 8, "root_I": "専門ノウハウが必要",
      "O": 8, "root_O": "既存組織で実行可能",
      "市場成長性": 9, "root_市場成長性": "関連市場が拡大中",
      "実行難易度": 7, "root_実行難易度": "既存人員で対応可能",
      "投資効率": 8, "root_投資効率": "ROI高い",
      "顧客評価": 8, "root_顧客評価": "顧客満足度向上に寄与",
      "リスク": 6, "root_リスク": "法規制リスク低い",
      "total": 41,
      "rank": "A",
      "is_best": true
    }},
    ...
  ]
}}

【外部環境】
{external}

【AIからの質問・回答】
{question_and_answers}

【SWOT分析】
{swot}

【真因分析】
{root}
        """
    )
    schema = {
        "type": "object",
        "properties": {
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "evidence": {"type": "string"},
                        "risk": {"type": "string"},
                        "kpi": {"type": "string"},
                        "V": {"type": "integer"},
                        "root_V": {"type": "string"},
                        "R": {"type": "integer"},
                        "root_R": {"type": "string"},
                        "I": {"type": "integer"},
                        "root_I": {"type": "string"},
                        "O": {"type": "integer"},
                        "root_O": {"type": "string"},
                        "市場成長性": {"type": "integer"},
                        "root_市場成長性": {"type": "string"},
                        "実行難易度": {"type": "integer"},
                        "root_実行難易度": {"type": "string"},
                        "投資効率": {"type": "integer"},
                        "root_投資効率": {"type": "string"},
                        "顧客評価": {"type": "integer"},
                        "root_顧客評価": {"type": "string"},
                        "リスク": {"type": "integer"},
                        "root_リスク": {"type": "string"},
                        "total": {"type": "integer"},
                        "rank": {"type": "string"},
                        "is_best": {"type": "boolean"},
                    },
                    "required": [
                        "title",
                        "content",
                        "evidence",
                        "risk",
                        "kpi",
                        "V",
                        "root_V",
                        "R",
                        "root_R",
                        "I",
                        "root_I",
                        "O",
                        "root_O",
                        "市場成長性",
                        "root_市場成長性",
                        "実行難易度",
                        "root_実行難易度",
                        "投資効率",
                        "root_投資効率",
                        "顧客評価",
                        "root_顧客評価",
                        "リスク",
                        "root_リスク",
                        "total",
                        "rank",
                        "is_best",
                    ],
                },
            }
        },
        "required": ["actions"],
    }
    try:
        rsp = client.chat.completions.create(
            model=_DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            functions=[{"name": "make_actions", "parameters": schema}],
            function_call={"name": "make_actions"},
        )

        raw = json.loads(rsp.choices[0].message.function_call.arguments)["actions"]

        # 合計点最大のものだけ is_best=True に補正（複数あれば最初の1つのみTrue）
        max_score = max(a.get("total", 0) for a in raw)
        first_flag = False
        for a in raw:
            if a.get("total", 0) == max_score and not first_flag:
                a["is_best"] = True
                first_flag = True
            else:
                a["is_best"] = False

    except Exception as e:
        st.session_state["action_error_trace"] = traceback.format_exc()
        st.error(f"⚠️ Action+Eval 生成失敗: {e}")
        return {"actions_md": "", "evaluations": []}

    # Markdown用出力（最優先アクションをアイコン強調！）
    md = []
    for a in raw:
        if a.get("is_best"):
            md.append(
                f"---\n### 🚩【最優先アクション】{a['title'].replace('【🚩最優先アクション】','')}\n"
            )
        else:
            md.append(f"---\n### {a.get('title','')}\n")
        md.append(a.get("content", ""))
        md.append(f"- **根拠データ・実例**: {a.get('evidence','')}")
        md.append(f"- **やらない場合のリスク**: {a.get('risk','')}")
        md.append(f"- **KPI**: {a.get('kpi','')}")
        md.append(f"- **総合点**: {a.get('total','')} / **Rank**: {a.get('rank','')}")
    return {"actions_md": "\n".join(md), "evaluations": raw}


# ----------------------------------------------------------------------
# 公開シンボル
# ----------------------------------------------------------------------
__all__ = [
    "show_external_environment_analysis_ai",
    "deep_dive_questions_ai",
    "show_swot_section_ai",
    "root_cause_analysis_ai",
    "action_with_eval_ai",
    "run_gpt",
]
