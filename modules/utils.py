def calc_finance_metrics(user_input: dict) -> dict:
    try:
        sales = float(user_input.get("年間売上高", "0") or "0")
        profit = float(user_input.get("営業利益／事業所得", "0") or "0")
        cash = float(user_input.get("現預金残高", "0") or "0")
        loan = float(user_input.get("借入金残高", "0") or "0")
        repay = float(user_input.get("年間借入返済額", "0") or "0")

        profit_margin = round((profit / sales) * 100, 1) if sales > 0 else 0
        cash_months = round((cash / (sales / 12)), 1) if sales > 0 else 0
        burden_ratio = round((repay / sales) * 100, 1) if sales > 0 else 0

        return {
            "profit_margin": profit_margin,
            "cash_months": cash_months,
            "burden_ratio": burden_ratio,
        }
    except Exception as e:
        return {
            "profit_margin": 0,
            "cash_months": 0,
            "burden_ratio": 0,
            "error": str(e),
        }


# utils.py

import re


def extract_item(section_jp, field, text):
    """
    指定セクション内の指定ラベルを抜き出す
    section_jp ... 例: '政治・制度'
    field ... 例: '要約' or '動向' or '出典'
    text ... AI応答の全体（Markdown）
    """
    # セクション（## 観点名 (English)）から下を抽出
    pattern_section = rf"^##\s*{re.escape(section_jp)}[^\n]*\n(.*?)(?=^##|\Z)"
    m_section = re.search(pattern_section, text, re.MULTILINE | re.DOTALL)
    if not m_section:
        return ""
    section_body = m_section.group(1)
    # セクション内の - ラベル: 値 を抜く
    pattern_field = rf"-\s*{re.escape(field)}[:：]\s*(.*)"
    m_field = re.search(pattern_field, section_body)
    return m_field.group(1).strip() if m_field else ""
