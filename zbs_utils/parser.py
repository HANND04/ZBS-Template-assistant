import re

def parse_custom_format(text):
    """
    Parses the ZBS serialized format into a standard Python dictionary.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    stack = []
    root = None
    
    def parse_value(val_str):
        if val_str == 'NULL':
            return None
        elif val_str.startswith('bool'):
            return val_str[4:] == 'true'
        elif val_str.startswith('int'):
            return int(val_str[3:])
        elif val_str.startswith('string'):
            # The value is string"something". Strip string" and the trailing "
            s = val_str[7:-1]
            return s
        return val_str

    for line_idx, line in enumerate(lines):
        is_dict_open = line.endswith('{') or ('{' in line and (line.endswith('items') or 'item' in line))
        is_list_open = line.endswith('[') or ('[' in line and (line.endswith('items') or 'item' in line))
        
        if is_dict_open or is_list_open:
            container_type = 'dict' if is_dict_open else 'list'
            new_container = {} if is_dict_open else []
            
            key = None
            if stack and stack[-1][0] == 'dict':
                m = re.match(r'^"([^"]+)":', line)
                if m:
                    key = m.group(1)
            
            if not stack:
                if line.startswith('"root"'):
                    root = {'root': new_container}
                    stack.append(('dict', root))
                    stack.append((container_type, new_container))
                else:
                    root = new_container
                    stack.append((container_type, new_container))
            else:
                parent_type, parent_obj = stack[-1]
                if parent_type == 'dict':
                    parent_obj[key] = new_container
                else:
                    parent_obj.append(new_container)
                stack.append((container_type, new_container))
                
        elif line in ('}', ']', '},', '],'):
            if stack:
                stack.pop()
                
        else:
            if line.startswith('"'):
                m = re.match(r'^"([^"]+)":\s*(.*)$', line)
                if m:
                    key = m.group(1)
                    val_str = m.group(2)
                    val = parse_value(val_str)
                    if stack:
                        stack[-1][1][key] = val
            elif re.match(r'^\d+:', line):
                m = re.match(r'^\d+:\s*(.*)$', line)
                if m:
                    val_str = m.group(1)
                    val = parse_value(val_str)
                    if stack:
                        stack[-1][1].append(val)
                
    return root
