import streamlit as st
import re

def clean_text_for_html(text):
    if not text or not isinstance(text, str):
        return text
    # 1. Escape template parameter brackets to prevent unclosed HTML tag errors (e.g. <otp> -> &lt;otp&gt;)
    # Excludes valid styling tags like span/div
    escaped = re.sub(r'<([^>/\s"=]+)>', r'&lt;\1&gt;', text)
    # 2. Convert literal newlines to HTML line breaks to prevent Markdown parser newline glitches
    return escaped.replace('\n', '<br />')

def render_preview(parsed_template):
    st.markdown("<h3 style='text-align: center;'>📱 Giao diện xem trước tin nhắn</h3>", unsafe_allow_html=True)
    
    if parsed_template:
        root_data = parsed_template.get('root', {}) if 'root' in parsed_template else parsed_template
        sections_list = root_data.get('sections', [])
        
        logo_url = None
        oa_name = "Zalo Business Account"
        banner_img = None
        message_elements = []
        cta_buttons = []
        payment_box = None
        rating_stars = None
        
        for sec in sections_list:
            if not sec:
                continue
            sec_type = list(sec.keys())[0]
            sec_val = sec[sec_type]
            if not isinstance(sec_val, dict):
                continue
            
            if sec_type in ('oa_info', 'logo'):
                logo_url = sec_val.get('img', {}).get('url') if 'img' in sec_val else sec_val.get('url')
                if 'title' in sec_val and sec_val['title']:
                    oa_name = clean_text_for_html(sec_val['title'])
            elif sec_type == 'banner':
                img = sec_val.get('img')
                if img:
                    banner_img = img.get('url') if isinstance(img, dict) else img
                        
                title = sec_val.get('title')
                if title:
                    txt = title.get('text') if isinstance(title, dict) else title
                    txt_type = title.get('type') if isinstance(title, dict) else None
                    if txt:
                        message_elements.append({
                            'type': 'title' if txt_type == 'text-title' else 'paragraph',
                            'text': clean_text_for_html(txt)
                        })
            elif sec_type == 'map_info':
                items = sec_val.get('items', [])
                table_rows = []
                for item in items:
                    key = item.get('key', {}).get('title', {}).get('text')
                    val = item.get('value', {}).get('title', {}).get('text')
                    table_rows.append((clean_text_for_html(key), clean_text_for_html(val)))
                message_elements.append({
                    'type': 'table',
                    'rows': table_rows
                })
            elif sec_type == 'buttons':
                items = sec_val.get('items', [])
                for btn in items:
                    cta_buttons.append({
                        'text': clean_text_for_html(btn.get('text')),
                        'type': btn.get('type')
                    })
            elif sec_type == 'rating':
                rating_stars = 5
            elif sec_type == 'open_utility':
                payment_type = sec_val.get('type')
                if payment_type == 'payment':
                    items = sec_val.get('top', {}).get('contents', {}).get('items', [])
                    amount = ""
                    bank_info = ""
                    account = ""
                    for item in items:
                        itype = item.get('type')
                        itext = item.get('text')
                        if itype == 'text-money':
                            amount = clean_text_for_html(itext)
                        elif itype == 'text-subtext':
                            if "tài khoản" in itext.lower() or "số tài khoản" in itext.lower() or "tk" in itext.lower() or "công ty" in itext.lower():
                                account = clean_text_for_html(itext)
                            else:
                                bank_info = clean_text_for_html(itext)
                    payment_box = {
                        'amount': amount,
                        'bank': bank_info,
                        'account': account
                    }
            elif sec_type == 'carousel':
                cards = sec_val.get('c_card', [])
                if cards:
                    first_card = cards[0]
                    c_items = first_card.get('c_items', [])
                    card_title = ""
                    card_paragraph = ""
                    for item in c_items:
                        itype = list(item.keys())[0]
                        ival = item[itype]
                        if itype == 'c_image':
                            banner_img = ival
                        elif itype == 'c_title':
                            card_title = ival
                        elif itype == 'c_paragraph':
                            card_paragraph = ival
                        elif itype == 'c_buttons':
                            for cbtn in ival:
                                cta_buttons.append({
                                    'text': clean_text_for_html(cbtn.get('c_text')),
                                    'type': cbtn.get('c_type', 'button-primary')
                                })
                    if card_title:
                        message_elements.append({'type': 'title', 'text': clean_text_for_html(card_title)})
                    if card_paragraph:
                        message_elements.append({'type': 'paragraph', 'text': clean_text_for_html(card_paragraph)})
                        
        logo_html = f'<img class="zalo-logo" src="{logo_url}" />' if logo_url else ""
        banner_html = f'<img class="zalo-banner-img" src="{banner_img}" />' if banner_img else ""
        
        body_elements_html = ""
        for el in message_elements:
            if el['type'] == 'title':
                body_elements_html += f'<div class="zalo-title">{el["text"]}</div>'
            elif el['type'] == 'paragraph':
                body_elements_html += f'<div class="zalo-text">{el["text"]}</div>'
            elif el['type'] == 'table':
                table_rows_html = ""
                for k, v in el['rows']:
                    table_rows_html += f'<tr><td class="zalo-table-key">{k}</td><td class="zalo-table-val">{v}</td></tr>'
                body_elements_html += f'<table class="zalo-table">{table_rows_html}</table>'
                
        payment_html = ""
        if payment_box:
            payment_html = f"""
            <div class="zalo-payment-box">
                <div style="font-size: 11px; color: #8E8E93;">Số tiền cần thanh toán</div>
                <div style="font-size: 18px; font-weight: bold; color: #DC3545; margin-bottom: 4px;">{payment_box['amount']}</div>
                <div style="font-size: 11px; font-weight: 500;">{payment_box['bank']}</div>
                <div style="font-size: 11px; color: #6C757D;">{payment_box['account']}</div>
            </div>
            """
            
        rating_html = '<div class="zalo-rating-stars">⭐ ⭐ ⭐ ⭐ ⭐</div>' if rating_stars else ""
            
        buttons_html = ""
        for btn in cta_buttons:
            is_primary = "primary" in btn['type'] or "btn-primary" in btn['type']
            btn_class = "zalo-button zalo-button-primary" if is_primary else "zalo-button"
            buttons_html += f'<div class="{btn_class}">{btn["text"]}</div>'
            
        phone_html = f"""
        <div class="phone-mock">
            <div class="phone-screen">
                <div class="zalo-bubble">
                    <div class="zalo-logo-section">
                        {logo_html}
                        <span class="zalo-oa-name">{oa_name}</span>
                    </div>
                    {banner_html}
                    {body_elements_html}
                    {payment_html}
                    {rating_html}
                    {buttons_html}
                </div>
            </div>
        </div>
        """
        # Clean HTML to prevent Markdown parser from treating indented lines as code blocks
        flat_phone_html = "".join(line.strip() for line in phone_html.split('\n'))
        st.markdown(flat_phone_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Vui lòng nhập dữ liệu hợp lệ ở khung bên trái để hiển thị giao diện mô phỏng điện thoại.")
