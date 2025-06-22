# pages/3_Report_History.py
from config import init_page

init_page(title="📄 レポート履歴")

import streamlit as st
import os


# --------------------------------------------
# 2️⃣ レポート履歴ページ
# --------------------------------------------
st.title("📄 レポート履歴")

st.markdown(
    """
こちらは **AI経営診断GPT Lite版** における  
これまで出力した **PDFレポート履歴（仮）** を確認するページです。 🚀✨

※ 将来的には：
- 出力日時
- 会社名・分析対象期間
- PDFファイルダウンロード
- コメント記録
- 差分比較（Starter版/Pro版用）

などを搭載予定です。
"""
)

# --------------------------------------------
# 3️⃣ 【仮】 PDF履歴ファイルリスト表示（ダミー）
# --------------------------------------------

# 仮想的な履歴（Starter版なら → データベース連携予定）
dummy_reports = [
    {
        "date": "2025-06-06",
        "company": "株式会社テストカンパニー",
        "filename": "AI_Dock_Report_20250606.pdf",
    },
    {
        "date": "2025-06-01",
        "company": "株式会社サンプル製作所",
        "filename": "AI_Dock_Report_20250601.pdf",
    },
    {
        "date": "2025-05-25",
        "company": "合同会社デモ商会",
        "filename": "AI_Dock_Report_20250525.pdf",
    },
]

# 表示
st.subheader("📑 出力済みレポート一覧（仮）")

for report in dummy_reports:
    st.write(f"📅 {report['date']} | 🏢 {report['company']} | 📄 {report['filename']}")
    st.button(
        f"📥 ダウンロード（{report['filename']}）", key=f"download_{report['filename']}"
    )

# --------------------------------------------
# 4️⃣ 今後予定する高度機能（Starter/Pro）
# --------------------------------------------

st.markdown("---")
st.subheader("🛠️ 今後予定する高度機能（Starter/Pro 版）")

st.markdown(
    """
✅ PDF自動保存（クラウド or DB）  
✅ 履歴にタグ付け・コメント記録  
✅ 過去レポートとの差分比較  
✅ グラフ表示（診断スコア推移）  
✅ レポート検索・フィルター  
✅ CSVエクスポート  
"""
)
