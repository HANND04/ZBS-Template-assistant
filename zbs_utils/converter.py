def deconstruct_template(template):
    if not template:
        return {}
    res = {
        'oa_name': 'Tên OA của bạn',
        'logo_url': 'https://stc-oa.zdn.vn/uploads/2026/06/04/1e58bd98c5d120838b461e86c93e1331.png',
        'banner_url': '',
        'title_text': '',
        'body_text': '',
        'table_rows': [],
        'buttons': []
    }
    
    root = template.get('root', {}) if 'root' in template else template
    sections = root.get('sections', [])
    
    for sec in sections:
        if not sec:
            continue
        sec_type = list(sec.keys())[0]
        sec_val = sec[sec_type]
        if not isinstance(sec_val, dict):
            continue
            
        if sec_type in ('oa_info', 'logo'):
            img_url = sec_val.get('img', {}).get('url') if 'img' in sec_val else sec_val.get('url')
            if img_url:
                res['logo_url'] = img_url
            if 'title' in sec_val and sec_val['title']:
                res['oa_name'] = sec_val['title']
        elif sec_type == 'banner':
            img = sec_val.get('img')
            if img:
                img_url = img.get('url') if isinstance(img, dict) else img
                if img_url:
                    res['banner_url'] = img_url
            title = sec_val.get('title')
            if title:
                txt = title.get('text') if isinstance(title, dict) else title
                txt_type = title.get('type') if isinstance(title, dict) else None
                if txt_type == 'text-title':
                    res['title_text'] = txt
                else:
                    if res['body_text']:
                        res['body_text'] += "\n" + txt
                    else:
                        res['body_text'] = txt
        elif sec_type == 'map_info':
            items = sec_val.get('items', [])
            for item in items:
                key = item.get('key', {}).get('title', {}).get('text', '')
                val = item.get('value', {}).get('title', {}).get('text', '')
                res['table_rows'].append((key, val))
        elif sec_type == 'buttons':
            items = sec_val.get('items', [])
            for btn in items:
                click_info = btn.get('click') or {}
                res['buttons'].append({
                    'text': btn.get('text', '') or '',
                    'action': click_info.get('action', '') or '',
                    'data': click_info.get('data', '') or ''
                })
        elif sec_type == 'carousel':
            cards = sec_val.get('c_card', [])
            if cards:
                c_items = cards[0].get('c_items', [])
                for item in c_items:
                    itype = list(item.keys())[0]
                    ival = item[itype]
                    if itype == 'c_image':
                        res['banner_url'] = ival or ''
                    elif itype == 'c_title':
                        res['title_text'] = ival or ''
                    elif itype == 'c_paragraph':
                        res['body_text'] = ival or ''
                    elif itype == 'c_buttons':
                        for btn in ival:
                            res['buttons'].append({
                                'text': btn.get('c_text', '') or '',
                                'action': btn.get('c_action', '') or '',
                                'data': btn.get('c_data', '') or ''
                            })
                            
    return res

def construct_template(oa_name, logo_url, banner_url, title_text, body_text, table_rows, buttons):
    parsed_template = {
        "root": {
            "oa_id": "123456789",
            "extend_info": "123456789",
            "sections": []
        }
    }
    sections = parsed_template["root"]["sections"]
    
    # 1. OA Info
    sections.append({
        "oa_info": {
            "show": True,
            "vertical": True,
            "horizontal": False,
            "pos": "1",
            "img": {
                "url": logo_url,
                "light": "width: 60%; data-width:400;data-height:96; margin-bottom:0dp;",
                "dark": f"src:{logo_url}"
            },
            "title": oa_name,
            "des": None
        }
    })
    
    pos_counter = 2
    
    # 2. Banner Img
    if banner_url.strip():
        sections.append({
            "banner": {
                "show": True,
                "pos": str(pos_counter),
                "img": {
                    "url": banner_url,
                    "light": f"src:{banner_url};",
                    "dark": f"src:{banner_url}"
                },
                "title": None,
                "click": None
            }
        })
        pos_counter += 1
        
    # 3. Title Text
    if title_text.strip():
        sections.append({
            "banner": {
                "show": True,
                "pos": str(pos_counter),
                "img": None,
                "title": {
                    "click": None,
                    "id": "",
                    "icon": None,
                    "text": title_text,
                    "light": "",
                    "dark": "",
                    "type": "text-title",
                    "wrapper": None
                },
                "click": None
            }
        })
        pos_counter += 1
        
    # 4. Body Text
    if body_text.strip():
        sections.append({
            "banner": {
                "show": True,
                "pos": str(pos_counter),
                "img": None,
                "title": {
                    "click": None,
                    "id": "",
                    "icon": None,
                    "text": body_text,
                    "light": "",
                    "dark": "",
                    "type": "text-normal",
                    "wrapper": None
                },
                "click": None
            }
        })
        pos_counter += 1
        
    # 5. Table rows
    if table_rows:
        table_items = []
        for k, v in table_rows:
            if k.strip():
                table_items.append({
                    "pos": f"row_{len(table_items)}_{pos_counter}",
                    "show": True,
                    "row": None,
                    "value": {
                        "type": "table-effect-default",
                        "title": { "text": v }
                    },
                    "key": {
                        "title": { "text": k }
                    }
                })
        if table_items:
            sections.append({
                "map_info": {
                    "show_all": True,
                    "items": table_items
                }
            })
            pos_counter += 1
            
    # 6. Buttons
    buttons_list = []
    for btn in buttons:
        b_text = btn.get('text', '')
        b_action = btn.get('action', 'Mở liên kết (URL)')
        b_val = btn.get('data', '')
        
        if b_text.strip():
            action_type = "action.open.inapp"
            if b_action == "Gọi hotline" or b_action == "CALL":
                action_type = "CALL"
            elif b_action == "Sao chép mã" or b_action == "action.copy.clipboard":
                action_type = "action.copy.clipboard"
                
            buttons_list.append({
                "pos": pos_counter,
                "text": b_text,
                "type": "button-primary" if len(buttons_list) == 0 else "button-neutral",
                "click": {
                    "id": str(len(buttons_list)),
                    "click_extend_info": b_val if action_type == "action.copy.clipboard" else "",
                    "action": action_type,
                    "data": b_val if action_type != "action.copy.clipboard" else f"{{\\\"content\\\":\\\"{b_val}\\\"}}",
                    "data_detail": f"{{\\\"url\\\":\\\"{b_val}\\\",\\\"h5_src_open\\\":1110}}" if action_type == "action.open.inapp" else None
                },
                "icon_info": None
            })
            pos_counter += 1
            
    if buttons_list:
        sections.append({
            "buttons": {
                "show_all": True,
                "items": buttons_list
            }
        })
        
    return parsed_template
