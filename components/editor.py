import streamlit as st
import json
import re

from zbs_utils.parser import parse_custom_format
from zbs_utils.extractor import extract_content
from zbs_utils.converter import deconstruct_template, construct_template

import checkers.param_checks as param_checks
import checkers.content_checks as content_checks

# Mapping helper for sidebar sync
TAG_KEYS = {
    "TRANSACTION": "Tag 1 - GIAO DỊCH (TRANSACTION)",
    "CUSTOMER_CARE": "Tag 2 - CHĂM SÓC KHÁCH HÀNG (CUSTOMER_CARE)",
    "PROMOTION": "Tag 3 - HẬU MÃI (PROMOTION)"
}

# --- VALIDATION HELPERS ---

def show_validation_result(is_valid, error_msg, optional=False, value=""):
    if not is_valid:
        st.markdown(
            f'<div style="color: #dc3545; font-size: 13px; margin-top: -8px; margin-bottom: 12px; font-weight: 500; display: flex; align-items: center; gap: 4px;">'
            f'<span>❌</span> {error_msg}</div>', 
            unsafe_allow_html=True
        )
    else:
        if optional and not value.strip():
            st.markdown(
                f'<div style="color: #6c757d; font-size: 13px; margin-top: -8px; margin-bottom: 12px; font-weight: 400; display: flex; align-items: center; gap: 4px;">'
                f'<span>⚪</span> Trống (Tùy chọn)</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="color: #28a745; font-size: 13px; margin-top: -8px; margin-bottom: 12px; font-weight: 500; display: flex; align-items: center; gap: 4px;">'
                f'<span>✅</span> Nhập đúng</div>', 
                unsafe_allow_html=True
            )

def validate_oa_name(name):
    if not name or not name.strip():
        return False, "Tên OA hiển thị không được để trống."
    return True, ""

def validate_logo_url(url):
    if not url or not url.strip():
        return False, "Đường dẫn Logo OA không được để trống."
    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "Đường dẫn Logo OA phải bắt đầu bằng http:// hoặc https://"
    return True, ""

def validate_banner_url(url):
    if not url or not url.strip():
        return True, ""
    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "Đường dẫn Ảnh Banner phải bắt đầu bằng http:// hoặc https://"
    return True, ""

def check_text_params(text):
    if not text:
        return True, ""
    matches = re.findall(r'<([^>/\s"=]+)>', text)
    for param in matches:
        param_violations = []
        if ' ' in param:
            param_violations.append("khoảng trắng")
        if '-' in param:
            param_violations.append("dấu gạch nối")
        if param_checks.VIETNAMESE_ACCENTS_PATTERN.search(param):
            param_violations.append("ký tự tiếng Việt có dấu")
            
        has_uppercase = any(c.isupper() for c in param)
        has_underscore = '_' in param
        if has_uppercase and not has_underscore:
            param_violations.append("chữ in hoa/CamelCase thay vì snake_case")
            
        if param_violations:
            joined = ", ".join(param_violations)
            suggested = param.lower().replace(' ', '_').replace('-', '_')
            suggested = param_checks.remove_accents(suggested)
            return False, f"Tham số <{param}> chưa hợp lệ do chứa {joined}. Gợi ý: `<{suggested}>`"
    return True, ""

def check_forbidden_addressing(text):
    if not text:
        return True, ""
    forbidden_terms = [r'\banh/chị\b', r'\banh / chị\b', r'\bAnh/Chị\b', r'\bAnh / Chị\b']
    for term in forbidden_terms:
        if re.search(term, text, re.IGNORECASE):
            found_term = re.findall(term, text, re.IGNORECASE)[0]
            return False, f"Nội dung chứa cụm từ xưng hô bị cấm: '{found_term}'. Hãy sử dụng '<gender>' hoặc 'quý khách'."
    return True, ""

def check_body_links_and_phones(text):
    if not text:
        return True, ""
    url_pattern = re.compile(
        r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(com|vn|net|org|edu|gov)\b)', 
        re.IGNORECASE
    )
    phone_pattern = re.compile(
        r'(\b(0|84|\+84)[35789]\d{8}\b|\b1[89]00\d{4}\b)', 
        re.IGNORECASE
    )
    urls = url_pattern.findall(text)
    if urls:
        found_url = urls[0][0]
        return False, f"Chứa đường dẫn trực tiếp: '{found_url}'. Hãy chuyển xuống Nút thao tác (CTA button)."
    phones = phone_pattern.findall(text)
    if phones:
        found_phone = phones[0][0]
        return False, f"Chứa số điện thoại trực tiếp: '{found_phone}'. Hãy chuyển xuống Nút thao tác (CTA button)."
    return True, ""

def validate_title_text(text):
    if not text or not text.strip():
        return False, "Tiêu đề tin nhắn không được để trống."
    ok, err = check_text_params(text)
    if not ok:
        return False, err
    ok, err = check_forbidden_addressing(text)
    if not ok:
        return False, err
    return True, ""

def validate_body_text(text):
    if not text or not text.strip():
        return False, "Nội dung tin nhắn không được để trống."
    ok, err = check_text_params(text)
    if not ok:
        return False, err
    ok, err = check_forbidden_addressing(text)
    if not ok:
        return False, err
    ok, err = check_body_links_and_phones(text)
    if not ok:
        return False, err
    return True, ""

def validate_table_key(key, val):
    if not key.strip() and val.strip():
        return False, "Tên trường không được để trống khi có giá trị."
    if key.strip():
        ok, err = check_text_params(key)
        if not ok:
            return False, err
        ok, err = check_forbidden_addressing(key)
        if not ok:
            return False, err
    return True, ""

def validate_table_value(key, val):
    if key.strip() and not val.strip():
        return False, "Giá trị không được để trống khi có tên trường."
    if val.strip():
        ok, err = check_text_params(val)
        if not ok:
            return False, err
        ok, err = check_forbidden_addressing(val)
        if not ok:
            return False, err
    return True, ""

def validate_button_text(btn_text, btn_val, btn_idx):
    if not btn_text.strip() and btn_val.strip():
        return False, f"Chữ hiển thị của Nút {btn_idx} không được để trống khi có giá trị."
    return True, ""

def validate_button_value(btn_text, btn_action, btn_val, btn_idx, selected_tag):
    if btn_text.strip() and not btn_val.strip():
        return False, f"Giá trị (URL/SĐT/Mã copy) của Nút {btn_idx} không được để trống."
    
    if btn_text.strip() and btn_val.strip():
        if btn_action == "Mở liên kết (URL)":
            if not (btn_val.startswith("http://") or btn_val.startswith("https://")):
                return False, f"Đường dẫn Nút {btn_idx} phải bắt đầu bằng http:// hoặc https://"
            for domain in content_checks.SHORTENER_DOMAINS:
                if re.search(domain, btn_val, re.IGNORECASE):
                    return False, f"Nút {btn_idx} chứa liên kết rút gọn bị cấm ({domain}). Hãy dùng đường dẫn đầy đủ."
            for group in content_checks.GROUP_PATTERNS:
                if re.search(group, btn_val, re.IGNORECASE):
                    return False, f"Nút {btn_idx} chứa liên kết nhóm chat/mạng xã hội bị cấm."
        elif btn_action == "Gọi hotline":
            digits = re.sub(r'\D', '', btn_val)
            if not digits:
                return False, f"Giá trị Nút {btn_idx} phải là số điện thoại."
            if selected_tag == 'PROMOTION' and not (digits.startswith('1800') or digits.startswith('1900')):
                return False, f"Nút hotline trong mẫu Hậu mãi phải dùng đầu số 1800 hoặc 1900. Hiện tại: '{btn_val}'."
        elif btn_action == "Sao chép mã":
            if not btn_val.strip():
                return False, f"Nội dung copy của Nút {btn_idx} không được để trống."
    return True, ""

# --- END VALIDATION HELPERS ---

def render_editor(sample_templates, selected_tag):
    st.markdown("### Nội dung đăng ký ZBS")
    
    sample_options = [t['name'] for t in sample_templates]
    selected_example = st.selectbox(
        "Chọn một mẫu thử nghiệm (Từ bảng dữ liệu mẫu):",
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
        st.markdown("##### Thông tin OA & Banner")
        col_oa1, col_oa2 = st.columns(2)
        oa_name = col_oa1.text_input("Tên OA hiển thị:", value=sample_deconstructed.get('oa_name', "Tên OA của bạn"))
        logo_url = col_oa2.text_input("Đường dẫn Logo OA:", value=sample_deconstructed.get('logo_url', "https://stc-oa.zdn.vn/uploads/2026/06/04/1e58bd98c5d120838b461e86c93e1331.png"))
        
        # Validation for OA Name
        v_oa_ok, v_oa_err = validate_oa_name(oa_name)
        with col_oa1:
            show_validation_result(v_oa_ok, v_oa_err)
            
        # Validation for Logo URL
        v_logo_ok, v_logo_err = validate_logo_url(logo_url)
        with col_oa2:
            show_validation_result(v_logo_ok, v_logo_err)
            
        banner_url = st.text_input("Đường dẫn Ảnh Banner (Tùy chọn):", value=sample_deconstructed.get('banner_url', ""))
        v_banner_ok, v_banner_err = validate_banner_url(banner_url)
        show_validation_result(v_banner_ok, v_banner_err, optional=True, value=banner_url)
        
        st.markdown("##### Nội dung văn bản")
        title_text = st.text_input("Tiêu đề tin nhắn:", value=sample_deconstructed.get('title_text', "Thông báo"))
        v_title_ok, v_title_err = validate_title_text(title_text)
        show_validation_result(v_title_ok, v_title_err)
        
        body_text = st.text_area("Nội dung tin nhắn (Dùng <tên_biến> để chèn biến):", value=sample_deconstructed.get('body_text', "Xin chào <customer_name>, mã xác nhận của bạn là <otp>."))
        v_body_ok, v_body_err = validate_body_text(body_text)
        show_validation_result(v_body_ok, v_body_err)
        
        st.markdown("##### Bảng thông tin chi tiết (Table rows)")
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
                
                # Inline validation for each column input in columns
                if k_val.strip() or v_val.strip():
                    vk_ok, vk_err = validate_table_key(k_val, v_val)
                    vv_ok, vv_err = validate_table_value(k_val, v_val)
                    with col_k:
                        show_validation_result(vk_ok, vk_err)
                    with col_v:
                        show_validation_result(vv_ok, vv_err)
                        
                if k_val.strip():
                    table_rows.append((k_val, v_val))
                    
        st.markdown("##### Nút bấm thao tác (CTA Buttons)")
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
        
        # Validation for Button 1 Text and Value
        vb1_t_ok, vb1_t_err = validate_button_text(b1_text, b1_val, 1)
        vb1_v_ok, vb1_v_err = validate_button_value(b1_text, b1_action, b1_val, 1, selected_tag)
        
        if b1_text.strip() or b1_val.strip():
            # Show text validation below b1_text in its column
            with col_b1_t:
                show_validation_result(vb1_t_ok, vb1_t_err)
            # Show value validation below value input
            show_validation_result(vb1_v_ok, vb1_v_err)
            
        # Button 2
        st.markdown("**Nút bấm 2 (Tùy chọn)**")
        def_btn2 = default_btns[1] if len(default_btns) > 1 else {}
        col_b2_t, col_b2_a = st.columns(2)
        b2_text = col_b2_t.text_input("Chữ hiển thị (Nút 2)", value=def_btn2.get('text', ""))
        
        b2_act_def = act1_map.get(def_btn2.get('action', ''), "Mở liên kết (URL)")
        b2_action = col_b2_a.selectbox("Hành động (Nút 2)", ["Mở liên kết (URL)", "Gọi hotline", "Sao chép mã"], index=["Mở liên kết (URL)", "Gọi hotline", "Sao chép mã"].index(b2_act_def), key="b2_action_select")
        b2_val = st.text_input("Giá trị (URL/Số điện thoại/Nội dung copy) (Nút 2):", value=def_btn2.get('data', ""), key="b2_val_input")
        
        # Validation for Button 2 Text and Value
        vb2_t_ok, vb2_t_err = validate_button_text(b2_text, b2_val, 2)
        vb2_v_ok, vb2_v_err = validate_button_value(b2_text, b2_action, b2_val, 2, selected_tag)
        
        if b2_text.strip() or b2_val.strip():
            # Show text validation below b2_text in its column
            with col_b2_t:
                show_validation_result(vb2_t_ok, vb2_t_err)
            # Show value validation below value input
            show_validation_result(vb2_v_ok, vb2_v_err)
            
        buttons = []
        if b1_text.strip():
            buttons.append({'text': b1_text, 'action': b1_action, 'data': b1_val})
        if b2_text.strip():
            buttons.append({'text': b2_text, 'action': b2_action, 'data': b2_val})
            
        parsed_template = construct_template(
            oa_name, logo_url, banner_url, title_text, body_text, table_rows, buttons
        )
        extraction_results = extract_content(parsed_template)
        
        with st.expander("Xem mã JSON đăng ký tự động tạo ra từ Form:"):
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
