# ZBS Template Moderation Checker 🛡️

Một ứng dụng Streamlit pair-programming giúp doanh nghiệp tự động kiểm duyệt nội dung đăng ký mẫu tin nhắn Zalo Business (ZBS) chống bị từ chối xét duyệt.

## 🌟 Tính năng nổi bật
Ứng dụng gồm 2 bộ phận chính:
1. **Bộ kiểm duyệt Cơ bản (Basic Checker - Python Logic):**
   - Kiểm tra định dạng và cấu trúc tham số (tham số viết hoa, chứa dấu cách, chứa dấu tiếng Việt có dấu, chứa gạch ngang `-`, đề xuất định dạng `snake_case`).
   - Kiểm tra lỗi xưng hô trực tiếp bị cấm `"anh/chị"`.
   - Quét nội dung văn bản (body) để phát hiện chèn trực tiếp liên kết hoặc số điện thoại (phải chuyển xuống nút CTA).
   - Kiểm duyệt nút CTA: Phát hiện liên kết rút gọn (`bit.ly`, `tinyurl.com`...) hoặc liên kết nhóm mạng xã hội/chat cá nhân (Zalo, Facebook, Telegram...).
   - Kiểm tra số lượng biến bắt buộc theo từng Tag (Tag 1 & 2 yêu cầu tên khách hàng + ít nhất 1 biến định danh, hoặc 3 biến; Tag 3 yêu cầu tên khách hàng và hotline 1800/1900).
2. **Bộ kiểm duyệt AI (AI Checker - Gemini 2.5):**
   - Quét lỗi chính tả và ngữ pháp tiếng Việt nâng cao.
   - Phát hiện trộn lẫn ngôn ngữ (Vinglish).
   - Phát hiện văn phong không chuyên nghiệp hoặc mê tín dị đoan (VD: "tín chủ", "giàu phất lên").
   - Xác minh điều kiện đặc biệt cho các dịp sinh nhật, Lễ Tết (phải kèm ưu đãi cụ thể và hình ảnh).
   - Kiểm tra tuân thủ chính sách ngành đặc biệt (VD: Thực phẩm chức năng cần tuyên bố "sản phẩm không phải là thuốc...", Rượu bia cần cảnh báo dưới 18 tuổi).
   - Phát hiện nội dung quảng cáo bị ẩn trong các Tag Giao dịch/Chăm sóc khách hàng (Tag 1 & 2).

---

## 📂 Cấu trúc thư mục
```
d:\Zalo-Intern/
├── app.py                     # Bootstrapper chính của Streamlit (<= 200 dòng)
├── components/                # Giao diện components (styles, sidebar, editor, preview...)
│   ├── styles.py
│   ├── sidebar.py
│   ├── editor.py
│   ├── preview.py
│   └── rule_map.py
├── checkers/                  # Logic kiểm duyệt (param_checks, content_checks, tag_checks, ai_checks)
│   ├── param_checks.py
│   ├── content_checks.py
│   ├── tag_checks.py
│   └── ai_checks.py
├── zbs_utils/                 # Các tiện ích chung (parser, extractor, converter)
│   ├── parser.py
│   ├── extractor.py
│   └── converter.py
├── test_runner.py             # Script chạy kiểm thử tự động trên terminal
├── sample_data.csv            # File chứa 6 mẫu template từ Google Sheet
└── README.md                  # Hướng dẫn sử dụng
```

---

## 🛠️ Hướng dẫn cài đặt

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install streamlit pandas google-genai
   ```

2. Đảm bảo file dữ liệu mẫu `sample_data.csv` nằm trong cùng thư mục với `app.py`.

---

## 🚀 Hướng dẫn sử dụng

### 1. Chạy kiểm duyệt tự động trên Terminal
Bạn có thể chạy thử nghiệm bộ lọc cơ bản trên cả 6 mẫu dữ liệu thử nghiệm bằng cách gõ:
```bash
python test_runner.py
```
Kết quả lỗi chi tiết của từng mẫu sẽ được in ra terminal.

### 2. Chạy ứng dụng Streamlit (Giao diện trực quan)
Để mở bảng điều khiển (dashboard) xem trước tin nhắn trực quan và kiểm duyệt bằng AI:
```bash
streamlit run app.py
```

Khi ứng dụng chạy, một trang web sẽ tự động mở ra. Tại đây bạn có thể:
- Chọn một trong 6 mẫu tin thử nghiệm từ thanh chọn ở khung bên trái hoặc tự dán nội dung ZBS của riêng mình.
- Xem mockup tin nhắn mô phỏng trực quan ngay trên giao diện điện thoại ở khung bên phải (Logo, Banner, Bảng thông tin, Nút CTA).
- Xem các lỗi cấu trúc được phát hiện ngay lập tức.
- Nhập **Gemini API Key** ở thanh Sidebar bên trái và click **"Chạy kiểm duyệt bằng AI"** để chạy phân tích ngôn ngữ sâu từ Gemini.
