import streamlit as st

STYLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(135deg, rgba(13, 27, 42, 0.95) 0%, rgba(27, 38, 59, 0.95) 100%);
    color: white;
}

[data-testid="stSidebar"] .stMarkdown h1, 
[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] label {
    color: #E0E1DD !important;
}

.header-container {
    background: linear-gradient(90deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%);
    padding: 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0, 82, 212, 0.25);
}

.header-container h1 {
    font-weight: 700;
    margin: 0;
    font-size: 2.5rem;
}

.header-container p {
    font-weight: 300;
    margin: 10px 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

.phone-mock {
    background-color: #E3E9F0;
    border-radius: 36px;
    padding: 40px 16px 40px 16px;
    border: 10px solid #2C3E50;
    width: 100%;
    max-width: 380px;
    margin: 0 auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.phone-screen {
    background-color: #EDF0F5;
    border-radius: 8px;
    height: 520px;
    overflow-y: auto;
    padding: 10px;
}

.phone-screen::-webkit-scrollbar {
    display: none;
}

.zalo-bubble {
    background-color: white;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    font-family: sans-serif;
    font-size: 13px;
    line-height: 1.4;
    color: #1C1C1E;
}

.zalo-logo-section {
    display: flex;
    align-items: center;
    border-bottom: 1px solid #EAEAEA;
    padding-bottom: 8px;
    margin-bottom: 8px;
}

.zalo-logo {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 8px;
    object-fit: cover;
    background-color: #F0F2F5;
}

.zalo-oa-name {
    font-weight: bold;
    font-size: 13px;
    color: #000;
}

.zalo-banner-img {
    width: 100%;
    border-radius: 8px;
    margin-bottom: 8px;
    object-fit: cover;
}

.zalo-title {
    font-weight: bold;
    font-size: 14px;
    color: #000;
    margin-bottom: 6px;
}

.zalo-text {
    margin-bottom: 8px;
    color: #4A4A4A;
    white-space: pre-line;
}

.zalo-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
}

.zalo-table td {
    padding: 4px 0;
    vertical-align: top;
    font-size: 12px;
}

.zalo-table-key {
    color: #8E8E93;
    width: 40%;
}

.zalo-table-val {
    color: #1C1C1E;
    font-weight: 500;
}

.zalo-payment-box {
    background: linear-gradient(135deg, #FBFBFB 0%, #F5F7FA 100%);
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 8px;
}

.zalo-rating-stars {
    display: flex;
    justify-content: center;
    gap: 8px;
    font-size: 20px;
    color: #FFCC00;
    margin: 8px 0;
}

.zalo-button {
    background-color: #FFFFFF;
    color: #0068FF;
    border: 1px solid #E2E8F0;
    text-align: center;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    margin-top: 6px;
    cursor: pointer;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.zalo-button-primary {
    background-color: #0068FF;
    color: white;
    border: none;
}

.violation-card {
    border-left: 5px solid #DC3545;
    background-color: #FFF5F6;
    padding: 12px 16px;
    border-radius: 4px;
    margin-bottom: 12px;
}

.violation-title {
    font-weight: 600;
    color: #DC3545;
    margin-bottom: 4px;
}

.violation-suggestion {
    font-style: italic;
    color: #6C757D;
    margin-top: 4px;
}

.success-box {
    border-left: 5px solid #28A745;
    background-color: #F4FBF6;
    padding: 15px;
    border-radius: 4px;
    font-weight: 500;
    color: #28A745;
}
</style>
"""

def inject_styles():
    st.markdown(STYLE_CSS, unsafe_allow_html=True)
