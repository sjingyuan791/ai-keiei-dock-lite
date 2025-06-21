# -*- coding: utf-8 -*-
# =====================================================================
# 0_Basic_Info_Input.py
#  AI経営診断GPT – 基本情報入力フォーム（経営改善ルート専用・UX改善版）
#  2025-06-19  |  v1.4
#     • プレースホルダーをより具体的な例に更新
#     • 「会社名・屋号」の例を「サンプル株式会社」に変更
# =====================================================================
from __future__ import annotations

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
from ui_components import show_subtitle, show_back_to_top

# 1. ページ初期化（set_page_config＋共通CSS）
init_page(title="AI経営診断 – 基本情報入力")

# 2. セッションステート初期化
if not isinstance(st.session_state.get("user_input"), dict):
    st.session_state["user_input"] = {}
if not isinstance(st.session_state.get("errors"), dict):
    st.session_state["errors"] = {}

user_input: dict[str, any] = st.session_state["user_input"]
errors: dict[str, str] = st.session_state["errors"]

show_subtitle("🏢 基本情報入力")

# 3. 企業基本情報 定義
ALL_FIELDS = [
    "会社名・屋号",
    "業種（できるだけ詳しく）",
    "地域",
    "主な商品・サービス",
    "主な顧客層",
    "年間売上高（おおよそ）",
    "粗利率（おおよそ）",
    "最終利益（税引後・おおよそ）",
    "借入金額（だいたい）",
]
REQUIRED_FIELDS = ALL_FIELDS[:5]
# 粗利率を除外した金額項目のみ
INT_FIELDS = [
    "年間売上高（おおよそ）",
    "最終利益（税引後・おおよそ）",
    "借入金額（だいたい）",
]
JP_NUM_MAP = str.maketrans("０１２３４５６７８９", "0123456789")

for k in ALL_FIELDS:
    user_input.setdefault(k, "")


# 4. バリデーションユーティリティ
def _to_half(v: str) -> str:
    return v.replace(",", "").translate(JP_NUM_MAP).strip()


def _is_int(v: str) -> bool:
    try:
        int(_to_half(v))
        return True
    except:
        return False


def _is_percent(v: str) -> bool:
    try:
        f = float(_to_half(v).replace("%", ""))
        return 0 <= f <= 100
    except:
        return False


def validate_inputs() -> dict[str, str]:
    e: dict[str, str] = {}
    # 企業基本情報必須チェック
    for k in REQUIRED_FIELDS:
        if not str(user_input[k]).strip():
            e[k] = "必須入力です"
    # 数値チェック
    for k in INT_FIELDS:
        v = str(user_input[k]).strip()
        if v and not _is_int(v):
            e[k] = "整数で入力してください"
    # 粗利率％チェック
    v = str(user_input["粗利率（おおよそ）"]).strip()
    if v and not _is_percent(v):
        e["粗利率（おおよそ）"] = "0〜100 の数値（％）で入力してください"
    # 課題入力は後段でチェック
    return e


# 5. フォーム表示＆保存処理
with st.form("form_basic_info"):
    # 5-1: 企業情報セクション
    st.markdown("### 企業情報")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        for key, label, placeholder in [
            ("会社名・屋号", "会社名・屋号*", "例）サンプル株式会社"),
            ("業種（できるだけ詳しく）", "業種*", "出来るだけ詳しく"),
            ("地域", "地域*", "例）東京都新宿区"),
            ("主な商品・サービス", "主な商品・サービス*", "出来るだけ詳しく"),
        ]:
            user_input[key] = st.text_input(
                label,
                value=str(user_input[key]),
                help=errors.get(key, ""),
                placeholder=placeholder,
            )
    with col2:
        for key, label, placeholder in [
            ("主な顧客層", "主な顧客層*", "例）地域の一般消費者"),
            ("年間売上高（おおよそ）", "年間売上高", "例）10,000,000（単位：円）"),
            ("粗利率（おおよそ）", "粗利率（％）", "例）30.5（単位：％）"),
            ("最終利益（税引後・おおよそ）", "最終利益", "例）1,000,000（単位：円）"),
            ("借入金額（だいたい）", "借入金額", "例）5,000,000（単位：円）"),
        ]:
            user_input[key] = st.text_input(
                label,
                value=str(user_input[key]),
                help=errors.get(key, ""),
                placeholder=placeholder,
            )

    # 5-2: 課題入力セクション（フォーム下部へ移動）
    st.markdown("### 📋 経営の問題点*")
    user_input["経営の問題点"] = st.text_area(
        "今の経営で困っていること、悩んでいること、改善したいことがあれば、どんなことでも具体的にご記入ください。",
        value=user_input.get("経営の問題点", ""),
        help=errors.get("経営の問題点", ""),
        placeholder="例）月の売上変動が大きく、在庫が不足しがちでキャッシュが圧迫されています",
    )

    submitted = st.form_submit_button("保存")

if submitted:
    errors.clear()
    errors.update(validate_inputs())
    # 課題は必須チェック
    if not user_input.get("経営の問題点", "").strip():
        errors["経営の問題点"] = "必須入力です"
    if errors:
        missing = "、".join(f"『{k}』" for k in errors)
        st.error(f"⚠️ 入力に不備があります → {missing} を確認してください。")
        st.session_state["errors"] = errors
    else:
        # 数値正規化
        for k in INT_FIELDS:
            v = str(user_input[k]).strip()
            if v:
                user_input[k] = int(_to_half(v))
        # 粗利率だけfloatで保存
        v = str(user_input["粗利率（おおよそ）"]).strip()
        if v:
            user_input["粗利率（おおよそ）"] = float(_to_half(v).replace("%", ""))
        st.session_state["user_input"] = user_input
        st.session_state.pop("errors", None)
        st.success("✅ 入力内容を保存しました。")

# 6. Back to Top
if len(ALL_FIELDS) + 1 > 8:
    show_back_to_top()
