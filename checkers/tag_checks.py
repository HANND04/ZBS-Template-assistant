import re

# Helper to identify if a parameter represents the customer's name
def is_name_parameter(param_name):
    p = param_name.lower()
    name_terms = {'name', 'ten', 'fullname', 'hoten', 'customer', 'khachhang', 'tenkh', 'custid'}
    # Special exact matches
    if p in name_terms or p in ('tenkh', 'ten_kh', 'tenkhachhang', 'ten_khach_hang', 'customer_name', 'customername'):
        return True
    
    # Exclude terms that imply non-name entities
    exclude_terms = {'code', 'id', 'mail', 'phone', 'sdt', 'date', 'time', 'card', 'status', 'level', 'otp', 'count', 'cost', 'price', 'amount', 'wallet'}
    if any(x in p for x in exclude_terms):
        return False
        
    # Include terms that imply names
    include_terms = {'name', 'ten', 'customer', 'khach'}
    if any(x in p for x in include_terms):
        return True
        
    return False

def check_tag_requirements(extracted_data, selected_tag):
    """
    Validates structural rules based on the template tag:
    - Tag 1 (GIAO DỊCH): Name param + at least 1 transaction param (or 3 transaction params if name is missing).
    - Tag 2 (CHĂM SÓC KHÁCH HÀNG): Name param + at least 1 transaction param (or 3 transaction params if name is missing).
    - Tag 3 (HẬU MÃI): Name param is mandatory.
    - Hotline format in Tag 3: Must be 1800/1900.
    """
    violations = []
    params = extracted_data['parameters']
    
    # 1. Identify name parameter
    has_name_param = False
    name_params_found = []
    
    for param in params:
        if is_name_parameter(param):
            has_name_param = True
            name_params_found.append(param)
                
    # 2. Identify transaction parameters (parameters that are NOT name)
    transaction_params = [p for p in params if p not in name_params_found]
    
    if selected_tag in ('TRANSACTION', 'CUSTOMER_CARE'):
        tag_display = "Giao dịch (Tag 1)" if selected_tag == 'TRANSACTION' else "Chăm sóc khách hàng (Tag 2)"
        
        if has_name_param:
            if len(transaction_params) < 1:
                violations.append({
                    'type': 'Tag Compliance Error',
                    'item': f"Tag: {selected_tag}",
                    'description': f"Mẫu tin {tag_display} bắt buộc có tên khách hàng và ít nhất 1 tham số xác định giao dịch (mã đơn, mã hóa đơn, ngày mua...). Hiện tại thiếu tham số giao dịch.",
                    'suggestion': "Bổ sung thêm ít nhất một tham số định danh giao dịch cụ thể như `<ma_don_hang>`, `<ngay_giao_dich>` vao nội dung."
                })
        else:
            # If name is missing, must have at least 3 transaction/identifying parameters
            if len(transaction_params) < 3:
                violations.append({
                    'type': 'Tag Compliance Error',
                    'item': f"Tag: {selected_tag}",
                    'description': f"Do không có tham số tên khách hàng, mẫu tin {tag_display} yêu cầu tổng cộng ít nhất 3 tham số giao dịch phù hợp. Hiện tại chỉ có {len(transaction_params)} tham số: {list(transaction_params)}.",
                    'suggestion': "Bổ sung tham số tên khách hàng (như `<ten_khach_hang>`) và 1 tham số giao dịch, hoặc thêm đầy đủ ít nhất 3 tham số định danh giao dịch (như mã hóa đơn, ngày hẹn, địa điểm)."
                })
                
    elif selected_tag == 'PROMOTION':
        if not has_name_param:
            violations.append({
                'type': 'Tag Compliance Error',
                'item': f"Tag: PROMOTION",
                'description': "Mẫu tin Hậu mãi (Tag 3) bắt buộc phải có tham số tên khách hàng để cá nhân hóa tin nhắn gửi đến người dùng.",
                'suggestion': "Bổ sung tham số tên khách hàng (ví dụ: `<customer_name>`) vào phần xưng hô mở đầu tin nhắn."
            })
            
        # Hotline check in Tag 3
        for btn in extracted_data['buttons']:
            btn_text = btn.get('text', '')
            btn_data = btn.get('data', '')
            action = btn.get('action', '')
            
            is_hotline_btn = "hotline" in btn_text.lower() or "sđt" in btn_text.lower() or "gọi" in btn_text.lower() or action == 'CALL'
            if is_hotline_btn and btn_data:
                digits = re.sub(r'\D', '', btn_data)
                if digits and not (digits.startswith('1800') or digits.startswith('1900')):
                    violations.append({
                        'type': 'Tag Compliance Error',
                        'item': btn['source'],
                        'description': f"Nút hotline/SĐT trong mẫu Hậu mãi phải sử dụng đầu số tổng đài 1800 hoặc 1900. Hiện tại đang dùng số: '{btn_data}'.",
                        'suggestion': "Sử dụng số hotline 1800 hoặc 1900. Nếu dùng số bàn/di động cá nhân, doanh nghiệp phải đính kèm tài liệu chứng minh sở hữu hotline trong phần ghi chú khi đăng ký."
                    })

    return violations
