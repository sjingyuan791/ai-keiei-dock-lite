# pages/4_Settings.py
from config import init_page

init_page(title="⚙️ 設定")

import streamlit as st

st.title("⚙️ 設定")

st.markdown(
    """
こちらは **AI経営診断GPT Lite版** の  
**ユーザープロファイル設定ページ** です。 🚀✨

※ Starter版/Pro版では：
- ユーザー別パーソナライズ
- 継続利用履歴
- スコア推移  
などと連携予定です。
"""
)

# --------------------------------------------
# 3️⃣ ユーザープロファイル設定フォーム（仮）
# --------------------------------------------

st.subheader("📋 ユーザープロファイル")

company_name = st.text_input("会社名・屋号", value="")
industry = st.text_input("業種（できるだけ詳しく）", value="")
region = st.text_input("地域（例：佐賀県唐津市）", value="")
contact_email = st.text_input("ご連絡先メールアドレス", value="")
notification_opt_in = st.checkbox("📰 Push通知（気づき通知）を受け取る", value=True)

# プロファイル更新ボタン
if st.button("▶ プロファイル更新"):
    # ✅ ここに本番時は「セッション更新／DB保存」などを入れる予定
    st.success("✅ プロファイルを更新しました！（仮）")

# --------------------------------------------
# 4️⃣ 今後予定する高度機能（Starter/Pro）
# --------------------------------------------

st.markdown("---")
st.subheader("🛠️ 今後予定する高度機能（Starter/Pro 版）")

st.markdown(
    """
✅ ユーザー別ダッシュボード表示カスタマイズ  
✅ Push通知パターン選択（例：週次／月次）  
✅ AIコーチング履歴の自動記録  
✅ 診断スコアの履歴グラフ表示  
✅ アカウント管理（複数ユーザー）  
✅ データエクスポート（CSV/Excel）  
"""
)
