import streamlit as st

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

st.title("お問い合わせ")

st.markdown(
    """
ご質問・ご要望・不具合のご連絡は、下記メールアドレス宛にお送りください。

- お問い合わせ窓口:sjingyuan791@gmail.com

※内容によってはご返信までお時間をいただく場合がございます。  
※個人情報の取り扱いについては[プライバシーポリシー](/プライバシーポリシー)をご参照ください。
"""
)
