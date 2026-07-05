import streamlit as st
import json

from zbs_utils.parser import parse_custom_format
from zbs_utils.extractor import extract_content
from zbs_utils.converter import deconstruct_template, construct_template

# Mapping helper for sidebar sync
TAG_KEYS = {
    "TRANSACTION": "Tag 1 - GIAO DỊCH (TRANSACTION)",
    "CUSTOMER_CARE": "Tag 2 - CHĂM SÓC KHÁCH HÀNG (CUSTOMER_CARE)",
    "PROMOTION": "Tag 3 - HẬU MÃI (PROMOTION)"
}

def render_editor(sample_templates, selected_tag):
    st.markdown("### 📝 Nội dung đăng ký ZBS")
    
    sample_options = [t['name'] for t in sample_templates]
    selected_example = st.selectbox(
        "💡 Chọn một mẫu thử nghiệm (Từ bảng dữ liệu mẫu):",
        options=["Tùy chỉnh (Tự nhập dữ liệu)"] + sample_options
    )
    
    default_text = ""
    if selected_example != "Tùy chỉnh (Tự nhập dữ liệu)":
        for t in sample_templates:
            if t['name'] == selected_example:
                default_text = t['data']
                name_lower = t['name'].lower()
                # Auto tag helper
                if 'payment' in name_lower or 'rating' in name_lower or 'xác thực' in name_lower or 'x?c th?c' in name_lower:
                    selected_tag = "TRANSACTION"
                elif 'voucher' in name_lower or 'carousel' in name_lower:
                    selected_tag = "PROMOTION"
                break
                
    input_mode = st.radio("Chế độ nhập liệu:", ["Form dễ dùng (No-Code)", "Dán mã JSON/Serialized (Developer)"], horizontal=True)
    
    parsed_template = None
    extraction_results = None
    parse_error = None
    
    # Deconstruct sample if selected to pre-populate form
    sample_deconstructed = {}
    if selected_example != "Tùy chỉnh (Tự nhập dữ liệu)" and default_text:
        try:
            p_sample = json.loads(default_text)
        except json.JSONDecodeError:
            p_sample = parse_custom_format(default_text)
        if p_sample:
            sample_deconstructed = deconstruct_template(p_sample)

    if input_mode == "Form dễ dùng (No-Code)":
        st.markdown("##### 🏢 Thông tin OA & Banner")
        col_oa1, col_oa2 = st.columns(2)
        oa_name = col_oa1.text_input("Tên OA hiển thị:", value=sample_deconstructed.get('oa_name', "Tên OA của bạn"))
        logo_url = col_oa2.text_input("Đường dẫn Logo OA:", value=sample_deconstructed.get('logo_url', "https://stc-oa.zdn.vn/uploads/2026/06/04/1e58bd98c5d120838b461e86c93e1331.png"))
        banner_url = st.text_input("Đường dẫn Ảnh Banner (Tùy chọn):", value=sample_deconstructed.get('banner_url', ""))
        
        st.markdown("##### 📝 Nội dung văn bản")
        title_text = st.text_input("Tiêu đề tin nhắn:", value=sample_deconstructed.get('title_text', "Thông báo"))
        body_text = st.text_area("Nội dung tin nhắn (Dùng <tên_biến> để chèn biến):", value=sample_deconstructed.get('body_text', "Xin chào <customer_name>, mã xác nhận của bạn là <otp>."))
        
        st.markdown("##### 📊 Bảng thông tin chi tiết (Table rows)")
        defaults_rows = sample_deconstructed.get('table_rows', [])
        has_table = st.checkbox("Hiển thị bảng chi tiết", value=len(defaults_rows) > 0)
        
        table_rows = []
        if has_table:
            for r_idx in range(3):
                col_k, col_v = st.columns(2)
                def_k = defaults_rows[r_idx][0] if r_idx < len(defaults_rows) else ""
                def_v = defaults_rows[r_idx][1] if r_idx < len(defaults_rows) else ""
                
                k_val = col_k.text_input(f"Tên trường {r_idx + 1}", value=def_k, key=f"tbl_k_{r_idx}")
                v_val = col_v.text_input(f"Giá trị trường {r_idx + 1}", value=def_v, key=f"tbl_v_{r_idx}")
                if k_val.strip():
                    table_rows.append((k_val, v_val))
                    
        st.markdown("##### 🔘 Nút bấm thao tác (CTA Buttons)")
        default_btns = sample_deconstructed.get('buttons', [])
        
        # Button 1
        st.markdown("**Nút bấm 1**")
        def_btn1 = default_btns[0] if len(default_btns) > 0 else {}
        col_b1_t, col_b1_a = st.columns(2)
        b1_text = col_b1_t.text_input("Chữ hiển thị (Nút 1)", value=def_btn1.get('text', ""))
        
        act1_map = {"action.open.inapp": "Mở liên kết (URL)", "CALL": "Gọi hotline", "action.copy.clipboard": "Sao chép mã"}
        b1_act_def = act1_map.get(def_btn1.get('action', ''), "Mở liên kết (URL)")
        b1_action = col_b1_a.selectbox("Hành động (Nút 1)", ["Mở liên kết (URL)", "Gọi hotline", "Sao chép mã"], index=["Mở liên kết (URL)", "Gọi hotline", "Sao chép mã"].index(b1_act_def))
        b1_val = st.text_input("Giá trị (URL/Số điện thoại/Nội dung copy) (Nút 1):", value=def_btn1.get('data', ""))
        
        # Button 2
        st.markdown("**Nút bấm 2 (Tùy chọn)**")
        def_btn2 = default_btns[1] if len(default_btns) > 1 else {}
        col_b2_t, col_b2_a = st.columns(2)
        b2_text = col_b2_t.text_input("Chữ hiển thị (Nút 2)", value=def_btn2.get('text', ""))
        
        b2_act_def = act1_map.get(def_btn2.get('action', ''), "Mở liên kết (URL)")
        b2_action = col_b2_a.selectbox("Hành động (Nút 2)", ["Mở liên kết (URL)", "Gọi hotline", "Sao chép mã"], index=["Mở liên kết (URL)", "Gọi hotline", "Sao chép mã"].index(b2_act_def), key="b2_action_select")
        b2_val = st.text_input("Giá trị (URL/Số điện thoại/Nội dung copy) (Nút 2):", value=def_btn2.get('data', ""), key="b2_val_input")
        
        buttons = []
        if b1_text.strip():
            buttons.append({'text': b1_text, 'action': b1_action, 'data': b1_val})
        if b2_text.strip():
            buttons.append({'text': b2_text, 'action': b2_action, 'data': b2_val})
            
        parsed_template = construct_template(
            oa_name, logo_url, banner_url, title_text, body_text, table_rows, buttons
        )
        extraction_results = extract_content(parsed_template)
        
        with st.expander("🛠️ Xem mã JSON đăng ký tự động tạo ra từ Form:"):
            st.code(json.dumps(parsed_template, indent=2, ensure_ascii=False), language="json")
            
    else:
        raw_template_input = st.text_area(
            "Nhập mã đăng ký template ZBS (Hỗ trợ cả JSON chuẩn và Định dạng serialized của Zalo):",
            value=default_text,
            height=320,
            help="Hãy dán JSON đăng ký của bạn vào đây."
        )
        
        if raw_template_input.strip():
            try:
                parsed_template = json.loads(raw_template_input)
            except json.JSONDecodeError:
                try:
                    parsed_template = parse_custom_format(raw_template_input)
                    if not parsed_template:
                        parse_error = "Dữ liệu nhập không khớp với cấu trúc ZBS JSON hoặc Zalo serialization."
                except Exception as e:
                    parse_error = f"Lỗi phân tách (Parsing Error): {str(e)}"
                    
            if parsed_template:
                extraction_results = extract_content(parsed_template)

    return parsed_template, extraction_results, parse_error, selected_tag
