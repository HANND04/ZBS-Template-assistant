import re

# Popular URL shorteners
SHORTENER_DOMAINS = [
    r'bit\.ly', r'tinyurl\.com', r'onelink\.me', r'goo\.gl', r't\.co', 
    r'lnk\.to', r'shorturl\.at', r'rebrand\.ly', r'is\.gd', r'buff\.ly', 
    r'ow\.ly', r'bitly\.com', r'shorte\.st', r'tiny\.cc'
]

# Social media group link patterns
GROUP_PATTERNS = [
    r'zalo\.me/g/', 
    r'facebook\.com/groups/', 
    r'facebook\.com/messages/', 
    r't\.me/joinchat',
    r't\.me/',
    r'telegram\.me/',
    r'm\.me/'
]

def check_addressing(extracted_data):
    """
    Checks if forbidden addressing terms like 'anh/chị' are used.
    """
    violations = []
    forbidden_terms = [r'\banh/chị\b', r'\banh / chị\b', r'\bAnh/Chị\b', r'\bAnh / Chị\b']
    
    for source, text in extracted_data['texts']:
        for term in forbidden_terms:
            if re.search(term, text, re.IGNORECASE):
                violations.append({
                    'type': 'Addressing Error',
                    'item': source,
                    'description': f"Nội dung chứa cụm từ xưng hô bị cấm: '{re.findall(term, text, re.IGNORECASE)[0]}'.",
                    'suggestion': "Không xưng hô bằng 'anh/chị' trực tiếp. Hãy sử dụng biến xưng hô (VD: `<gender>`) hoặc dùng các từ trung tính như 'quý khách', 'bạn', 'khách hàng'."
                })
                break
                
    return violations

def check_body_links_and_phones(extracted_data):
    """
    Checks if raw links or phone numbers are placed in the text body.
    """
    violations = []
    
    url_pattern = re.compile(
        r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(com|vn|net|org|edu|gov)\b)', 
        re.IGNORECASE
    )
    
    phone_pattern = re.compile(
        r'(\b(0|84|\+84)[35789]\d{8}\b|\b1[89]00\d{4}\b)', 
        re.IGNORECASE
    )
    
    for source, text in extracted_data['texts']:
        if text.startswith('<') and text.endswith('>'):
            continue
            
        # Check URLs
        urls = url_pattern.findall(text)
        if urls:
            found_url = urls[0][0]
            violations.append({
                'type': 'Body Content Error',
                'item': source,
                'description': f"Nội dung chứa đường dẫn (URL) trực tiếp: '{found_url}'.",
                'suggestion': "Di chuyển đường dẫn này xuống Nút thao tác (CTA button) thay vì chèn trực tiếp vào nội dung tin nhắn."
            })
            
        # Check Phone numbers
        phones = phone_pattern.findall(text)
        if phones:
            found_phone = phones[0][0]
            violations.append({
                'type': 'Body Content Error',
                'item': source,
                'description': f"Nội dung chứa số điện thoại trực tiếp: '{found_phone}'.",
                'suggestion': "Di chuyển số điện thoại này xuống Nút thao tác (CTA button) hoặc sử dụng tính năng gọi điện."
            })
            
    return violations

def check_cta_links(extracted_data):
    """
    Checks buttons / links for shortened URL domains or social media groups.
    """
    violations = []
    
    for source, url in extracted_data['links']:
        # 1. Shortener Check
        for domain in SHORTENER_DOMAINS:
            if re.search(domain, url, re.IGNORECASE):
                violations.append({
                    'type': 'CTA Link Error',
                    'item': source,
                    'description': f"Nút thao tác chứa liên kết rút gọn bị cấm: '{url}'.",
                    'suggestion': "Sử dụng đường dẫn đầy đủ (long URL) của trang web chính thức của doanh nghiệp."
                })
                break
                
        # 2. Social group check
        for group in GROUP_PATTERNS:
            if re.search(group, url, re.IGNORECASE):
                violations.append({
                    'type': 'CTA Link Error',
                    'item': source,
                    'description': f"Nút thao tác chứa liên kết dẫn đến nhóm chat/cá nhân bị cấm: '{url}'.",
                    'suggestion': "Liên kết phải dẫn về Website chính thức, Trang thông tin hoặc Mini App của doanh nghiệp. Không được dẫn về các nhóm mạng xã hội hoặc chat cá nhân."
                })
                break
                
    return violations
