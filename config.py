# config.py
import streamlit as st


def init_page(
    *,
    title: str = "AI経営コンサルタントLite（β版）",
    layout: str = "wide",
    styles_once: bool = True,
) -> None:
    """
    - この関数を **各ページの最上段** で呼び出すだけで
      ・set_page_config
      ・共通 CSS / フォント
      を自動適用。
    - 2 回目以降の呼び出しは無視されるので重複エラーが起きない。
    """
    if "_page_initialized" in st.session_state:
        return

    st.set_page_config(page_title=title, layout=layout)

    if styles_once:
        _apply_global_styles()

    st.session_state["_page_initialized"] = True


# ---------- 共通スタイル ----------
def _apply_global_styles() -> None:
    if "_style_injected" in st.session_state:
        return
    st.markdown(
        """
<style>
html,body,[class*="css"]{font-family:"Helvetica Neue","Roboto",sans-serif;color:#212121;}
h2{color:#1F4E79;margin-top:0.8rem;}
a{color:#1F4E79;}
div[data-testid="stProgress"]>div>div>div{height:10px;}
.stButton>button{border:1px solid #1F4E79 !important;border-radius:6px !important;
                 color:#1F4E79 !important;background:#fff !important;padding:.35rem 1.2rem !important;
                 font-weight:600 !important;}
.stButton>button:hover{background:#1F4E79 !important;color:#fff !important;}
</style>
""",
        unsafe_allow_html=True,
    )
    st.session_state["_style_injected"] = True
