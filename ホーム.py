# main.py  ― Notionライクなトップページ
# ==============================================
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

# （以下、既存のst.set_page_configやCSS、ページ内容はそのまま続けてOK）

st.set_page_config(
    page_title="AI経営コンサルタントLite（β版）",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- グローバル CSS  --------------------------------
st.markdown(
    """
<style>
/* ========= Google Font (Inter & Noto Sans JP) ========== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+JP:wght@400;600&display=swap');

/* ========= カラートークン (Notion風) ========== */
:root {
  --bg:          #f6f7f9;
  --card-bg:     #ffffff;
  --border:      #e0e0e0;
  --shadow:      rgba(0,0,0,0.06);
  --text:        #37352f;
  --text-sub:    #6e6e6e;
  --accent:      #0b5fff;
}

/* ========= ベーススタイル ========== */
html, body, .stApp, .main { 
  background-color: var(--bg) !important;
  color: var(--text);
  font-family: 'Inter', 'Noto Sans JP', sans-serif;
  font-size: 16px;
}

/* ========= カード (Notionページ風) ========== */
.main-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2.2rem 2.7rem 2rem;
  margin: 2.2rem auto;
  max-width: 1800px;
  box-shadow: 0 4px 12px var(--shadow);
}

/* ========= 見出し ========== */
.main-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  letter-spacing: 0.4px;
  text-align: center;
  color: var(--text);
}
.main-sub {
  font-size: 1.05rem;
  color: var(--text-sub);
  text-align: center;
  margin-bottom: 2.2rem;
}

/* ========= ステップリスト ========== */
.step-list {
  list-style: none; padding-left: 0;
}
.step-list li {
  margin: 0.4rem 0 0.4rem 0;
  padding-left: 1.6rem;
  position: relative;
}
.step-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--accent);
  font-size: 1.1rem;
  line-height: 1;
}

/* ========= ノートブロック  ========== */
.note-block {
  background: #eef3ff;
  border-left: 4px solid var(--accent);
  padding: 1rem 1.3rem;
  border-radius: 6px;
  color: var(--text);
  margin-top: 1.8rem;
  font-size: 0.95rem;
}

/* ========= フッター (固定) ========== */
.footer {
  position: fixed;
  bottom: 0; left: 0; width: 100%;
  background: var(--bg);
  border-top: 1px solid var(--border);
  padding: 0.7rem 0;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-sub);
  z-index: 99;
}
.footer a { color: var(--accent); text-decoration: none; margin: 0 1rem; }
.footer a:hover { text-decoration: underline; }

/* ========= レスポンシブ ========== */
@media (max-width: 640px){
  .main-card { padding: 1.5rem 1.2rem; margin: 1.2rem auto; }
  .main-title { font-size: 1.6rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- ページ内容  --------------------------------
st.markdown(
    """
<div class="main-card">
  <div class="main-title">AI経営コンサルタントLite（β版）</div>
  <div class="main-sub">
経営者・個人事業主の “最も身近な経営アドバイザー”。<br>
3ステップで、<b>現状の課題も、未来のチャンスも “見える化”</b>。<br>
<span style="font-weight:bold; color:#0b5fff;">
AIがあなたの会社専用の経営改善策を提案し、<br>
“分かりやすい経営レポート”として自動生成します。
</span>

</div>

  <h4 style="margin-top:1.2rem;">🚀 ご利用ステップ</h4>
  <ul class="step-list">
    <li><b>Step&nbsp;1：</b>「基本情報入力」タブで会社プロフィールと問題点を入力</li>
    <li><b>Step&nbsp;2：</b>「AI経営診断」タブでAIが経営改善策の提案</li>
    <li><b>Step&nbsp;3：</b>「PDF出力」タブでレポートをダウンロード</li>
  </ul>

<div style="background-color:#f0f4ff; padding: 1em; border-left: 5px solid #1e90ff; border-radius: 6px;">
  <ul style="margin: 0; padding-left: 1.2em;">
    <li>入力したデータはセッション内でのみ保持され、サーバー側へ保存されることはありません。</li>
    <li>AIの回答は必ずしも正確とは限りません。重要な情報はご自身でご確認ください。</li>
    <li>
      <strong>もっと成果を出したい方へ：</strong>
      AIチャットによる実行サポート、業務進捗管理、さらに高度な経営分析やレポート出力など、
      ワンランク上の機能を備えた<b>Starter版・Pro版</b>もご用意しています。<br>
      本格的な経営支援をお求めの方はぜひご検討ください。
    </li>
  </ul>
</div>



""",
    unsafe_allow_html=True,
)

# ---------- フッター  ----------------------------------
st.markdown(
    """
<div class="footer">
  <a href="/プライバシーポリシー" target="_self">プライバシーポリシー</a>
  <a href="/利用規約" target="_self">利用規約</a>
  <a href="/お問い合わせ" target="_self">お問い合わせ</a><br>
  © 2025 AI経営コンサルティング
</div>
""",
    unsafe_allow_html=True,
)
