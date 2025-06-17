# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st
from config import _apply_global_styles


def init_session(keys: list[str]) -> None:
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = None


def show_navigation(step: int, min_step: int = 1, max_step: int = 6) -> None:
    prev_col, _, next_col = st.columns([1, 6, 1])
    with prev_col:
        if st.button("◀ 前へ", disabled=step <= min_step, key=f"nav_prev_{step}"):
            st.session_state["step"] = step - 1
            st.rerun()
    with next_col:
        if st.button("次へ ▶", disabled=step >= max_step, key=f"nav_next_{step}"):
            st.session_state["step"] = step + 1
            st.rerun()


def show_subtitle(sub: str) -> None:
    st.markdown(f"#### {sub}")


def _deep_dive_form(qs: list[dict]) -> None:
    import streamlit as st

    with st.form("deep_dive_form"):
        for i, q in enumerate(qs, 1):
            cat = q.get("category", f"カテゴリ{i}")
            st.markdown(f"### {i}. {cat}")
            st.write(
                f"**質問:** {q.get('question','')}  _(根拠: {q.get('rationale','')})_"
            )
            st.text_area(
                "回答を入力",
                key=f"qq_{i}",
                value=st.session_state.get(f"qq_{i}", ""),
            )
        # keyは不要
        if st.form_submit_button("回答を保存"):
            ans = {
                f"qq_{i}": st.session_state.get(f"qq_{i}")
                for i in range(1, len(qs) + 1)
            }
            # ここで回答を保存
            st.session_state["deep_dive_answers"] = ans
            st.success(
                "✅ 回答を保存しました上部の『次へ』ボタンでSWOT分析に進んでください。"
            )


def show_back_to_top():
    st.markdown(
        '<a href="#" style="display:inline-block;margin-top:1rem;font-size:1.1em;">▲ ページ先頭に戻る</a>',
        unsafe_allow_html=True,
    )
