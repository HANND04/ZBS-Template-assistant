import streamlit as st
import os
import pandas as pd

# Import package modules
from components.styles import inject_styles
from components.sidebar import render_sidebar
from components.editor import render_editor
from components.preview import render_preview
from components.rule_map import render_rule_map

import checkers.param_checks as param_checks
import checkers.content_checks as content_checks
import checkers.tag_checks as tag_checks
import checkers.ai_checks as ai_checks

# App page configurations
st.set_page_config(
    page_title="ZBS Template Checker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_styles()

# Render header banner
st.markdown("""
<div class="header-container">
    <h1>🛡️ ZBS Template Moderation Checker</h1>
    <p>Hỗ trợ doanh nghiệp kiểm duyệt nội dung mẫu tin nhắn Zalo Business (ZBS) tự động trước khi gửi phê duyệt.</p>
</div>
""", unsafe_allow_html=True)

# Load templates database
@st.cache_data
def load_sample_templates():
    csv_path = "sample_data.csv"
    if not os.path.exists(csv_path):
        scratch_path = r"C:\Users\Admin\.gemini\antigravity-ide\brain\b44b3994-94c3-45e6-af3a-009bd4f65459\scratch\sample_data.csv"
        if os.path.exists(scratch_path):
            csv_path = scratch_path
            
    templates = []
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            for idx, row in df.iterrows():
                name = row.iloc[2]
                raw_data = row.iloc[4]
                if pd.notna(name) and pd.notna(raw_data):
                    templates.append({
                        'name': str(name).strip(),
                        'data': str(raw_data).strip()
                    })
        except:
            pass
    return templates

sample_templates = load_sample_templates()

# Render Sidebar Configs
api_key_input, selected_tag, selected_industry = render_sidebar()

# Split panels layout
col_editor, col_preview = st.columns([7, 5])

with col_editor:
    # Render Editor UI (Form or Raw code)
    parsed_template, extraction_results, parse_error, selected_tag = render_editor(
        sample_templates, selected_tag
    )
    
    # Run checkers if parsed successfully
    if parsed_template and extraction_results:
        basic_violations = []
        basic_violations.extend(param_checks.check_parameters(extraction_results))
        basic_violations.extend(content_checks.check_addressing(extraction_results))
        basic_violations.extend(content_checks.check_body_links_and_phones(extraction_results))
        basic_violations.extend(content_checks.check_cta_links(extraction_results))
        basic_violations.extend(tag_checks.check_tag_requirements(extraction_results, selected_tag))
        
        # Tabs layout for report results
        tab_results, tab_data, tab_rules = st.tabs([
            "🔍 Kết quả Kiểm duyệt (Moderation)",
            "📊 Tham số & Dữ liệu Trích xuất",
            "📖 Bản đồ Quy định duyệt mẫu (Rule Map)"
        ])
        
        with tab_results:
            st.markdown("#### 1. Bộ kiểm duyệt cơ bản (Basic checks)")
            if basic_violations:
                for v in basic_violations:
                    st.markdown(f"""
                    <div class="violation-card">
                        <div class="violation-title">❌ {v['type']}: {v['item']}</div>
                        <div>{v['description']}</div>
                        <div class="violation-suggestion">💡 Gợi ý sửa: {v['suggestion']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-box">
                    ✅ Kiểm duyệt cơ bản: Không phát hiện lỗi cấu trúc, tham số hoặc liên kết cấm!
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("#### 2. Bộ kiểm duyệt AI (Gemini AI Support)")
            
            run_ai = st.button("🚀 Chạy kiểm duyệt bằng AI")
            
            # Input key identifier to check session state cache
            input_state_key = str(parsed_template) + selected_tag + selected_industry
            
            if run_ai or (api_key_input and "ai_violations_store" in st.session_state and st.session_state.get("prev_input") == input_state_key):
                if "ai_violations_store" in st.session_state and st.session_state.get("prev_input") == input_state_key:
                    ai_violations = st.session_state.ai_violations_store
                else:
                    with st.spinner("Gemini đang phân tích nội dung, chính tả và chính sách của mẫu tin nhắn..."):
                        ai_violations = ai_checks.check_with_ai(
                            parsed_template, 
                            selected_tag, 
                            api_key_input,
                            selected_industry
                        )
                        st.session_state.ai_violations_store = ai_violations
                        st.session_state.prev_input = input_state_key
                
                if ai_violations:
                    warnings = [v for v in ai_violations if 'warning' in v.get('type', '').lower() or 'cảnh báo' in v.get('type', '').lower()]
                    errors = [v for v in ai_violations if v not in warnings]
                    
                    if errors:
                        st.write("🔴 **Các lỗi vi phạm nội dung & chính sách phát hiện bởi AI:**")
                        for v in errors:
                            st.markdown(f"""
                            <div class="violation-card">
                                <div class="violation-title">⚠️ {v.get('type')}: {v.get('item')}</div>
                                <div>{v.get('description')}</div>
                                <div class="violation-suggestion">💡 Gợi ý sửa: {v.get('suggestion')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    if warnings:
                        st.write("⚠️ **Cảnh báo từ AI (Không bắt buộc nhưng khuyến nghị nên sửa):**")
                        for v in warnings:
                            st.markdown(f"""
                            <div class="violation-card" style="border-left-color: #FFC107; background-color: #FFFDF5;">
                                <div class="violation-title" style="color: #D39E00;">🔔 {v.get('type')}: {v.get('item')}</div>
                                <div>{v.get('description')}</div>
                                <div class="violation-suggestion">💡 Gợi ý: {v.get('suggestion')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    if not errors and not warnings:
                        st.markdown("<div class='success-box'>✅ Kiểm duyệt AI: Nội dung hoàn hảo!</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='success-box'>✅ Kiểm duyệt AI: Không phát hiện lỗi chính tả hoặc chính sách.</div>", unsafe_allow_html=True)
            else:
                st.info("Nhập Gemini API Key ở Sidebar và click nút 'Chạy kiểm duyệt bằng AI' để chạy kiểm tra nâng cao.")
                
        with tab_data:
            st.markdown("#### Tham số được trích xuất từ mẫu:")
            st.write(list(extraction_results['parameters']) if extraction_results['parameters'] else "Không có tham số.")
            st.markdown("#### Liên kết (URLs) trích xuất:")
            st.write(list(extraction_results['links']) if extraction_results['links'] else "Không có liên kết.")
            st.markdown("#### Văn bản thô trích xuất:")
            for s, text in extraction_results['texts']:
                st.markdown(f"**{s}**: `{text}`")
                
        with tab_rules:
            render_rule_map()
            
    elif parse_error:
        st.error(f"❌ Không thể phân tích mẫu tin: {parse_error}")

with col_preview:
    # Render phone mockup preview
    render_preview(parsed_template)
