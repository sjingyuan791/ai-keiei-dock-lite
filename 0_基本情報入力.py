# -*- coding: utf-8 -*-
# =====================================================================
# 0_Basic_Info_Input.py
#  AI経営診断GPT – 基本情報入力フォーム（UX抜本改善）
#  2025-06-22 | UXリニューアル版
# =====================================================================
from __future__ import annotations

import streamlit as st

st.markdown(
    """
<style>
.required-label:after {
    content: " *";
    color: #e53935;
    font-weight: bold;
}
.field-error {
    color: #e53935;
    font-size: 0.98em;
    margin-top: 2px;
    margin-bottom: 0;
}
@media (max-width: 700px) {
    .block-container {
        max-width: 98vw !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

from config import init_page
from ui_components import show_subtitle, show_back_to_top

init_page(title="AI経営診断 – 基本情報入力")

if not isinstance(st.session_state.get("user_input"), dict):
    st.session_state["user_input"] = {}
if not isinstance(st.session_state.get("errors"), dict):
    st.session_state["errors"] = {}

user_input: dict[str, any] = st.session_state["user_input"]
errors: dict[str, str] = st.session_state["errors"]

show_subtitle("🏢 基本情報入力")

# 定義
ALL_FIELDS = [
    ("会社名・屋号", True, "例）サンプル株式会社"),
    ("業種（できるだけ詳しく）", True, "例）自動車整備業、IT受託開発など"),
    ("地域", True, "例）東京都新宿区"),
    ("主な商品・サービス", True, "例）自動車修理、ケーキ販売など"),
    ("主な顧客層", True, "例）地域の一般消費者"),
    ("年間売上高（おおよそ）", False, "例）10,000,000（円）"),
    ("粗利率（おおよそ）", False, "例）30.5（％）"),
    ("最終利益（税引後・おおよそ）", False, "例）1,000,000（円）"),
    ("借入金額（だいたい）", False, "例）5,000,000（円）"),
]
INT_FIELDS = [
    "年間売上高（おおよそ）",
    "最終利益（税引後・おおよそ）",
    "借入金額（だいたい）",
]
JP_NUM_MAP = str.maketrans("０１２３４５６７８９", "0123456789")

for k, *_ in ALL_FIELDS:
    user_input.setdefault(k, "")


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


def validate_field(k: str, v: str) -> str:
    if k in [f for f, req, _ in ALL_FIELDS if req]:
        if not v.strip():
            return "必須入力です"
    if k in INT_FIELDS:
        if v and not _is_int(v):
            return "整数で入力"
    if k == "粗利率（おおよそ）":
        if v and not _is_percent(v):
            return "0〜100の数値(％)"
    return ""


def validate_all() -> dict[str, str]:
    e = {}
    for k, req, _ in ALL_FIELDS:
        v = user_input[k]
        msg = validate_field(k, v)
        if msg:
            e[k] = msg
    # 経営の問題点チェック
    if not user_input.get("経営の問題点", "").strip():
        e["経営の問題点"] = "必須入力です"
    return e


# ===== フォーム表示 =====
with st.form("form_basic_info"):
    st.markdown("### 企業情報")
    for key, required, placeholder in ALL_FIELDS:
        label = (
            f"{key}" if not required else f'<span class="required-label">{key}</span>'
        )
        user_input[key] = st.text_input(
            label=label if not required else "",
            value=str(user_input[key]),
            help=None,
            placeholder=placeholder,
            key=f"input_{key}",
            label_visibility="visible" if not required else "collapsed",
        )
        # 必須ラベル
        if required:
            st.markdown(
                f'<label class="required-label" style="font-size:1em;">{key}</label>',
                unsafe_allow_html=True,
            )
        # エラー表示
        err = errors.get(key, "")
        if err:
            st.markdown(f'<div class="field-error">{err}</div>', unsafe_allow_html=True)

    # 経営の問題点
    st.markdown(
        "### 📋 経営の問題点<span style='color:#e53935;'>*</span>",
        unsafe_allow_html=True,
    )
    user_input["経営の問題点"] = st.text_area(
        "今の経営で困っていること、悩んでいること、改善したいことがあれば、どんなことでも具体的にご記入ください。",
        value=user_input.get("経営の問題点", ""),
        key="input_経営の問題点",
        placeholder="例）月の売上変動が大きく、在庫が不足しがちでキャッシュが圧迫されています",
    )
    if errors.get("経営の問題点"):
        st.markdown(
            f'<div class="field-error">{errors["経営の問題点"]}</div>',
            unsafe_allow_html=True,
        )

    st.info("保存後、画面右上『次へ ▶』で経営診断ステップに進めます。")

    submitted = st.form_submit_button("保存")

# ===== リアルタイムバリデーション（変更検知） =====
# すべてのフィールドでvalidateを即時反映
for k, _, _ in ALL_FIELDS:
    err = validate_field(k, user_input[k])
    if err:
        errors[k] = err
    elif k in errors:
        errors.pop(k)
err_prob = validate_field("経営の問題点", user_input.get("経営の問題点", ""))
if err_prob:
    errors["経営の問題点"] = err_prob
elif "経営の問題点" in errors:
    errors.pop("経営の問題点")

# ===== 保存ボタン処理 =====
if submitted:
    errors.clear()
    errors.update(validate_all())
    if errors:
        # 最初のエラー項目へ自動スクロールJS
        first_error = next(iter(errors))
        st.markdown(
            f"""
            <script>
            var errorElem = window.parent.document.querySelector('div.field-error');
            if(errorElem){{ errorElem.scrollIntoView({{behavior:"smooth",block:"center"}}); }}
            </script>
        """,
            unsafe_allow_html=True,
        )
        st.error("⚠️ 入力内容に不備があります。赤字メッセージをご確認ください。")
        st.session_state["errors"] = errors
    else:
        # 数値正規化
        for k in INT_FIELDS:
            v = str(user_input[k]).strip()
            if v:
                user_input[k] = int(_to_half(v))
        v = str(user_input["粗利率（おおよそ）"]).strip()
        if v:
            user_input["粗利率（おおよそ）"] = float(_to_half(v).replace("%", ""))
        st.session_state["user_input"] = user_input
        st.session_state.pop("errors", None)
        st.success(
            "✅ 入力内容を保存しました。画面右上の『次へ ▶』ボタンで次ステップに進めます。"
        )

if len(ALL_FIELDS) + 1 > 8:
    show_back_to_top()
