import re
import json

def extract_content(template):
    """
    Extracts all text contents, URLs, parameters, and buttons from a ZBS template JSON.
    Returns:
        dict: {
            'texts': list of (source, text_content),
            'links': list of (source, url),
            'parameters': set of parameter names (without braces, e.g. 'customer_name'),
            'buttons': list of dict (text, url/action, source)
        }
    """
    results = {
        'texts': [],
        'links': [],
        'parameters': set(),
        'buttons': []
    }
    
    # helper to check strings for params like <param_name>
    def scan_params(text):
        if not isinstance(text, str):
            return
        # Find matches like <param_name> but exclude html tags (which have space, quotes, equals or slashes)
        matches = re.findall(r'<([^>/\s"=]+)>', text)
        for m in matches:
            results['parameters'].add(m)

    def add_text(source, text):
        if text and isinstance(text, str) and text.strip():
            results['texts'].append((source, text))
            scan_params(text)

    def add_link(source, link):
        if link and isinstance(link, str) and link.strip():
            link_clean = link.strip()
            if link_clean.startswith('{'):
                try:
                    js = json.loads(link_clean)
                    if 'url' in js:
                        add_link(source, js['url'])
                        return
                except:
                    pass
            results['links'].append((source, link_clean))

    root = template.get('root', {}) if 'root' in template else template
    sections = root.get('sections', [])
    
    for field in ['3rd_config', '3rd_info']:
        val = root.get(field)
        if val and isinstance(val, str):
            add_link(field, val)
            scan_params(val)

    for sec_idx, section in enumerate(sections):
        if not section:
            continue
        sec_type = list(section.keys())[0]
        sec_val = section[sec_type]
        if not isinstance(sec_val, dict):
            continue
            
        source_prefix = f"sections[{sec_idx}].{sec_type}"
        
        # 1. Logo / OA Info
        if sec_type in ('oa_info', 'logo'):
            img_url = sec_val.get('img', {}).get('url') if 'img' in sec_val else sec_val.get('url')
            if img_url:
                add_link(f"{source_prefix}.img_url", img_url)
            add_text(f"{source_prefix}.title", sec_val.get('title'))
            add_text(f"{source_prefix}.des", sec_val.get('des'))
            
        # 2. Banner
        elif sec_type == 'banner':
            img = sec_val.get('img')
            if img and isinstance(img, dict):
                add_link(f"{source_prefix}.img.url", img.get('url'))
            elif isinstance(img, str):
                add_link(f"{source_prefix}.img", img)
                
            title = sec_val.get('title')
            if title and isinstance(title, dict):
                add_text(f"{source_prefix}.title.text", title.get('text'))
            elif isinstance(title, str):
                add_text(f"{source_prefix}.title", title)
                
        # 3. Table / Map Info
        elif sec_type == 'map_info':
            items = sec_val.get('items', [])
            for item_idx, item in enumerate(items):
                key = item.get('key', {}).get('title', {}).get('text')
                val = item.get('value', {}).get('title', {}).get('text')
                add_text(f"{source_prefix}.items[{item_idx}].key", key)
                add_text(f"{source_prefix}.items[{item_idx}].value", val)
                
        # 4. Buttons
        elif sec_type == 'buttons':
            items = sec_val.get('items', [])
            for btn_idx, btn in enumerate(items):
                btn_text = btn.get('text')
                add_text(f"{source_prefix}.items[{btn_idx}].text", btn_text)
                
                click = btn.get('click', {})
                action = click.get('action')
                data = click.get('data')
                
                add_link(f"{source_prefix}.items[{btn_idx}].click.data", data)
                results['buttons'].append({
                    'text': btn_text,
                    'action': action,
                    'data': data,
                    'source': f"{source_prefix}.items[{btn_idx}]"
                })
                
        # 5. Carousel
        elif sec_type == 'carousel':
            cards = sec_val.get('c_card', [])
            for card_idx, card in enumerate(cards):
                card_prefix = f"{source_prefix}.c_card[{card_idx}]"
                c_items = card.get('c_items', [])
                for item in c_items:
                    item_type = list(item.keys())[0]
                    item_val = item[item_type]
                    
                    if item_type == 'c_image':
                        add_link(f"{card_prefix}.c_image", item_val)
                    elif item_type in ('c_title', 'c_paragraph'):
                        add_text(f"{card_prefix}.{item_type}", item_val)
                    elif item_type == 'c_buttons':
                        for btn_idx, btn in enumerate(item_val):
                            btn_text = btn.get('c_text')
                            add_text(f"{card_prefix}.c_buttons[{btn_idx}].text", btn_text)
                            
                            c_action = btn.get('c_action')
                            c_data = btn.get('c_data')
                            
                            add_link(f"{card_prefix}.c_buttons[{btn_idx}].click.data", c_data)
                            results['buttons'].append({
                                'text': btn_text,
                                'action': c_action,
                                'data': c_data,
                                'source': f"{card_prefix}.c_buttons[{btn_idx}]"
                            })
                            
        # 6. Rating
        elif sec_type == 'rating':
            stars = sec_val.get('stars', [])
            for star_idx, star in enumerate(stars):
                click_data = star.get('click', {}).get('data')
                add_link(f"{source_prefix}.stars[{star_idx}].click.data", click_data)
                
        # 7. Open Utility (Payment box)
        elif sec_type == 'open_utility':
            items = sec_val.get('top', {}).get('contents', {}).get('items', [])
            for item_idx, item in enumerate(items):
                add_text(f"{source_prefix}.top.contents.items[{item_idx}].text", item.get('text'))
                
        # 8. Custom section
        elif sec_type == 'custom_section':
            add_text(f"{source_prefix}.html", sec_val.get('html'))
            
    return results
