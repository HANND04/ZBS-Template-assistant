import re

# Common Vietnamese diacritics / accents check regex
VIETNAMESE_ACCENTS_PATTERN = re.compile(
    r'[áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ'
    r'ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]',
    re.IGNORECASE
)

def check_parameters(extracted_data):
    """
    Validates parameter names inside extracted data.
    """
    violations = []
    params = extracted_data['parameters']
    
    for param in params:
        param_violations = []
        
        # 1. Check spaces
        if ' ' in param:
            param_violations.append("chứa khoảng trắng (spaces)")
            
        # 2. Check hyphens
        if '-' in param:
            param_violations.append("chứa dấu gạch nối (-)")
            
        # 3. Check accents
        if VIETNAMESE_ACCENTS_PATTERN.search(param):
            param_violations.append("chứa ký tự tiếng Việt có dấu")
            
        # 4. Check snake_case and case warnings
        has_uppercase = any(c.isupper() for c in param)
        has_underscore = '_' in param
        
        if has_uppercase and not has_underscore:
            param_violations.append("sử dụng chữ in hoa/CamelCase thay vì snake_case")
            
        if param_violations:
            joined_reasons = ", ".join(param_violations)
            suggested_name = param.lower().replace(' ', '_').replace('-', '_')
            suggested_name = remove_accents(suggested_name)
            
            violations.append({
                'type': 'Parameter Error',
                'item': f"<{param}>",
                'description': f"Tham số <{param}> chưa hợp lệ do {joined_reasons}.",
                'suggestion': f"Đổi tên tham số thành `<{suggested_name}>` (sử dụng chữ thường, không dấu, ngăn cách bằng dấu gạch dưới `_`)."
            })
            
    return violations

def remove_accents(input_str):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỶỷỸỹỴỵ'
    s2 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    trans = {}
    for i in range(len(s1)):
        trans[ord(s1[i])] = s2[i]
    return input_str.translate(trans)
