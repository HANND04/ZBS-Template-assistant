import os
import pandas as pd
import json

from zbs_utils.parser import parse_custom_format
from zbs_utils.extractor import extract_content
import checkers.param_checks as param_checks
import checkers.content_checks as content_checks
import checkers.tag_checks as tag_checks

def main():
    csv_path = "sample_data.csv"
    if not os.path.exists(csv_path):
        scratch_path = r"C:\Users\Admin\.gemini\antigravity-ide\brain\b44b3994-94c3-45e6-af3a-009bd4f65459\scratch\sample_data.csv"
        if os.path.exists(scratch_path):
            csv_path = scratch_path
        else:
            print(f"Error: Could not find sample_data.csv in current directory or scratch folder.")
            return

    print("==================================================")
    print(">>> Running Automated Moderation Checks on 6 Sample Templates")
    print("==================================================")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print("Error loading CSV:", e)
        return

    # Map templates to standard tags for validation
    tag_mapping = {
        0: "TRANSACTION", # payment
        1: "PROMOTION",   # voucher
        2: "TRANSACTION", # rating
        3: "TRANSACTION", # OTP / verification
        4: "PROMOTION",   # carousel
        5: "TRANSACTION"  # custom (Bridgestone survey)
    }

    for idx, row in df.iterrows():
        name = row.iloc[2]
        raw_data = row.iloc[4]
        
        if pd.isna(name) or pd.isna(raw_data):
            continue
            
        # Safe print name
        safe_name = str(name).encode('ascii', errors='replace').decode('ascii')
        print(f"\n[TEST CASE {idx + 1}] {safe_name}")
        
        # 1. Parsing
        try:
            parsed = json.loads(raw_data)
        except json.JSONDecodeError:
            parsed = parse_custom_format(raw_data)
            
        if not parsed:
            print("  [ERROR] Parsing Error: Failed to parse tree format.")
            continue
            
        # 2. Extract content
        extracted = extract_content(parsed)
        
        # 3. Determine tag
        tag = tag_mapping.get(idx, "TRANSACTION")
        print(f"  [TAG] Evaluated under Tag: {tag}")
        
        # 4. Run basic checker
        violations = []
        violations.extend(param_checks.check_parameters(extracted))
        violations.extend(content_checks.check_addressing(extracted))
        violations.extend(content_checks.check_body_links_and_phones(extracted))
        violations.extend(content_checks.check_cta_links(extracted))
        violations.extend(tag_checks.check_tag_requirements(extracted, tag))
        
        # 5. Output results
        if violations:
            print(f"  [VIOLATIONS] Found {len(violations)} basic violations:")
            for v in violations:
                safe_desc = v['description'].encode('ascii', errors='replace').decode('ascii')
                safe_sugg = v['suggestion'].encode('ascii', errors='replace').decode('ascii')
                print(f"    - [{v['type']}] in '{v['item']}': {safe_desc}")
                print(f"      -> Suggestion: {safe_sugg}")
        else:
            print("  [PASS] Passed all basic structural checks successfully!")

    print("\n==================================================")
    print(">>> Automated test run complete.")
    print("==================================================")

if __name__ == "__main__":
    main()
