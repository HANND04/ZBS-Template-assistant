import streamlit as st

def render_rule_map():
    st.markdown("""
    ### 📜 Tóm tắt bộ quy định duyệt mẫu ZBS Zalo
    
    #### 1. Quy định về Tham số (Parameters)
    - Phải được đặt trong cụm `<...>`, không dùng dấu tiếng Việt, không dùng khoảng trắng hay dấu gạch ngang (`-`).
    - Các từ ngăn cách bằng dấu gạch dưới `_` (snake_case).
    - Không được xưng hô trực tiếp bằng "anh/chị" trong văn bản, thay bằng các cụm từ trung tính (Quý khách, Bạn) hoặc sử dụng biến giới tính.
    
    #### 2. Quy định về Liên kết & Hotline (Links & Buttons)
    - Không chèn SĐT hoặc URL trực tiếp vào nội dung tin nhắn, phải di chuyển xuống nút bấm (CTA).
    - Cấm sử dụng link rút gọn (`bit.ly`, `tinyurl.com`...).
    - Cấm dẫn link vào kịch bản chatbot, chatgroup (Zalo, Facebook, Telegram...).
    - Tên miền trong CTA phải khớp với tên OA hoặc thương hiệu sở hữu.
    
    #### 3. Quy định theo Tag (Mục đích)
    - **Tag Giao dịch (Tag 1) & Chăm sóc khách hàng (Tag 2)**: Cấm chèn các thông tin mang tính chất quảng cáo, voucher khuyến mãi không liên quan, upsell. Bắt buộc có tên khách hàng + ít nhất 1 tham số giao dịch (hoặc 3 tham số nếu không có tên).
    - **Tag Hậu mãi (Tag 3)**: Bắt buộc phải có tên khách hàng. Hotline phải dùng đầu số 1800/1900. Không được viết tắt.
    
    #### 4. Nhóm ngành đặc biệt
    - **Thực phẩm chức năng**: Bắt buộc có câu tuyên bố phủ nhận: *"Sản phẩm không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh"*.
    - **Rượu bia dưới 5.5 độ**: Bắt buộc có câu tuyên bố: *"Sản phẩm không dành cho người dưới 18 tuổi"*.
    - **Các ngành cấm quảng bá**: Sữa cho trẻ dưới 24 tháng, thuốc kê đơn, sản phẩm người lớn/tình dục, get-rich-quick, crypto/forex.
    """)
