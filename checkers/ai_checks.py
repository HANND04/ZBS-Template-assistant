import json
from google import genai
from google.genai import types

AI_PROMPT = """
Bạn là một chuyên gia duyệt mẫu tin nhắn Zalo Business Template (ZBS). Nhiệm vụ của bạn là kiểm duyệt nội dung của một mẫu tin nhắn đăng ký (ZBS Template) dựa trên bộ quy định duyệt mẫu của Zalo.

Mẫu tin nhắn đăng ký được cung cấp ở định dạng JSON. Bạn cần kiểm tra các lỗi về mặt nội dung, ngữ cảnh, từ vựng và quy định ngành nghề đặc biệt.

THÔNG TIN ĐẦU VÀO:
1. JSON Mẫu đăng ký: {template_json_str}
2. Loại Tag (Mục đích gửi): {selected_tag}
3. Nhóm ngành (nếu có): {industry_name}

CÁC QUY TẮC CẦN KIỂM DUYỆT (AI CHECK):
1. CHÍNH TẢ & NGỮ PHÁP TIẾNG VIỆT:
   - Phát hiện tất cả các lỗi chính tả, lỗi đánh máy (typo), lỗi ngữ pháp hoặc câu từ tối nghĩa trong toàn bộ mẫu tin.
   - Kiểm tra các từ tiếng Việt xem có dấu đầy đủ và đúng quy chuẩn không.

2. TRỘN LẪN NGÔN NGỮ (MIXED LANGUAGE):
   - Đảm bảo mẫu tin sử dụng đồng nhất một ngôn ngữ chính. Không được pha trộn Anh - Việt một cách cẩu thả hoặc không tự nhiên (Ví dụ: "Hãy check hóa đơn ngay", "Voucher free").

3. VĂN PHONG & MÊ TÍN DỊ ĐOAN:
   - Cấm các từ ngữ mang tính chất mê tín dị đoan, thần thánh hóa sản phẩm, hoặc lừa gạt người dùng (Ví dụ: "tín chủ", "thầy pháp", "bùa ngải", "giải hạn", "giàu phất lên", "cam kết khỏi 100%").
   - Đảm bảo văn phong chuyên nghiệp, lịch sự, không dùng từ ngữ kích động hoặc thô tục.

4. QUẢNG CÁO ẨN TRONG TAG 1 & TAG 2 (TRANSACTION & CUSTOMER_CARE):
   - Nếu Tag là TRANSACTION hoặc CUSTOMER_CARE: Nội dung và liên kết CTA TUYỆT ĐỐI không được chứa quảng cáo, giới thiệu sản phẩm mới, mời gọi mua hàng, upsell/cross-sell, tặng voucher khuyến mãi không liên quan, hoặc mời tải app mới/quan tâm OA (trừ trường hợp chúc mừng sinh nhật hoặc khảo sát có quy định thể lệ cụ thể).
   - Nội dung Tag TRANSACTION phải tập trung 100% vào giao dịch. Tag CUSTOMER_CARE tập trung vào chăm sóc khách hàng.

5. QUY ĐỊNH VỀ DỊP ĐẶC BIỆT (CHÚC MỪNG SINH NHẬT / LỄ TẾT):
   - Nếu mẫu chúc mừng sinh nhật (Tag 2) hoặc Chúc mừng Lễ Tết (Tag 3):
     * BẮT BUỘC phải có hình ảnh đi kèm (nút banner hoặc logo có chứa link hình ảnh hợp lệ).
     * BẮT BUỘC phải đi kèm thông tin quà tặng/voucher/ưu đãi cụ thể (không được gửi lời chúc suông).

6. QUY ĐỊNH THEO NHÓM NGÀNH ĐẶC BIỆT:
   - Rượu, bia, đồ uống có cồn dưới 5.5 độ (Tag 3): BẮT BUỘC phải có câu: "Sản phẩm không dành cho người dưới 18 tuổi". Đồ uống trên 5.5 độ cấm chạy quảng cáo Tag 3.
   - Thực phẩm chức năng / Bảo vệ sức khỏe (Tag 3): BẮT BUỘC phải có câu: "Sản phẩm không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh". Không được dùng từ dễ gây hiểu nhầm sản phẩm là thuốc.
   - Mỹ phẩm, thẩm mỹ viện (Tag 3): Cấm quảng cáo dịch vụ xâm lấn (filler, tiêm phẫu thuật...) nếu không có giấy phép.
   - Nhóm ngành bị CẤM chạy quảng cáo (Tag 3): sữa cho bé dưới 24 tháng, thuốc kê đơn, đồ chơi người lớn/kích dục, thuốc lá, vũ khí/chất nổ, đầu tư tài chính/crypto/forex, mô hình đa cấp/kiếm tiền nhanh.

Hãy trả về kết quả dưới dạng JSON chứa danh sách các lỗi vi phạm tìm thấy (nếu không có lỗi nào, trả về danh sách rỗng).
Mỗi lỗi cần có:
- type: Thể loại lỗi (ví dụ: "Chính tả & Ngữ pháp", "Trộn ngôn ngữ", "Quảng cáo sai tag", "Thiếu điều khoản ngành", "Quy định Lễ Tết", "Nội dung cấm")
- item: Từ ngữ hoặc phần giao diện bị lỗi (ví dụ: "Đoạn văn phần 2", "Nút CTA 1")
- description: Giải thích rõ ràng lỗi vi phạm bằng tiếng Việt.
- suggestion: Gợi ý cụ thể, chi tiết cách sửa lỗi bằng tiếng Việt.

ĐỊNH DẠNG ĐẦU RA BẮT BUỘC (JSON):
{{
  "violations": [
    {{
      "type": "...",
      "item": "...",
      "description": "...",
      "suggestion": "..."
    }}
  ]
}}
"""

def check_with_ai(template_json, selected_tag, api_key, industry_name="Không có"):
    """
    Sends the template JSON and metadata to Gemini to check complex semantic and policy rules.
    """
    if not api_key:
        return [{
            'type': 'AI System Warning',
            'item': 'Gemini API Key',
            'description': 'Chưa cấu hình API Key cho Gemini. Không thể thực hiện kiểm duyệt bằng AI.',
            'suggestion': 'Vui lòng nhập Gemini API Key ở thanh bên (Sidebar) để kích hoạt tính năng kiểm duyệt AI.'
        }]
        
    try:
        template_json_str = json.dumps(template_json, indent=2, ensure_ascii=False)
        client = genai.Client(api_key=api_key)
        
        prompt = AI_PROMPT.format(
            template_json_str=template_json_str,
            selected_tag=selected_tag,
            industry_name=industry_name
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        res_data = json.loads(response.text)
        return res_data.get('violations', [])
        
    except Exception as e:
        return [{
            'type': 'AI Execution Error',
            'item': 'Gemini API',
            'description': f"Lỗi khi thực hiện kiểm duyệt bằng AI: {str(e)}",
            'suggestion': "Kiểm tra lại tính hợp lệ của API Key, kết nối mạng và định dạng JSON của bạn."
        }]
