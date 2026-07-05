import streamlit as st
import os

TAG_OPTIONS = {
    "Tag 1 - GIAO DỊCH (TRANSACTION)": "TRANSACTION",
    "Tag 2 - CHĂM SÓC KHÁCH HÀNG (CUSTOMER_CARE)": "CUSTOMER_CARE",
    "Tag 3 - HẬU MÃI (PROMOTION)": "PROMOTION"
}

INDUSTRY_OPTIONS = [
    "Không có / Ngành thường",
    "Rượu, bia, đồ uống có cồn dưới 5.5 độ",
    "Rượu, bia, đồ uống có cồn từ 5.5 độ trở lên",
    "Thực phẩm chức năng / Bảo vệ sức khỏe",
    "Mỹ phẩm, thẩm mỹ viện (xâm lấn / phẫu thuật)",
    "Dịch vụ phong thủy / tử vi / tâm linh",
    "Dịch vụ tang lễ và phục vụ tang lễ",
    "Thuốc không kê đơn / Kinh doanh dược"
]

def render_sidebar():
    st.sidebar.title("Cấu hình Checker")
    
    api_key_input = st.sidebar.text_input(
        "Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Nhập Gemini API Key để kiểm duyệt tự động các lỗi chính tả, văn phong, nội dung cấm và nhóm ngành đặc biệt."
    )
    
    selected_tag_label = st.sidebar.selectbox(
        "Loại Tag của mẫu tin nhắn",
        options=list(TAG_OPTIONS.keys())
    )
    selected_tag = TAG_OPTIONS[selected_tag_label]
    
    selected_industry = st.sidebar.selectbox(
        "Nhóm ngành đặc biệt",
        options=INDUSTRY_OPTIONS,
        help="Zalo quy định rất nghiêm ngặt với một số ngành nhạy cảm. Chọn đúng ngành của bạn để checker kiểm duyệt các câu tuyên bố bắt buộc (disclaimers) hoặc lệnh cấm."
    )
    
    return api_key_input, selected_tag, selected_industry
