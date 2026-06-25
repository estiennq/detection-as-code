from pathlib import Path
import yaml
import json
import sys

def check_match(detection, event):
    for key, value in detection.items():
        parts = key.split("|")
        field = parts[0]
        modifier = parts[1] if len(parts) > 1 else None

        if modifier == "contains":
            if isinstance(value, list):
                if not any(v in event.get(field, "") for v in value):
                    return False
            else:
                if value not in event.get(field, ""):
                    return False
    return True

errors = 0

for rule_file in Path("detections").rglob("*.yml"):
    with open(rule_file) as f:
        rule = yaml.safe_load(f)

    detection = rule["detection"]["selection"]
    test_dir = Path("tests") / rule_file.parent.name / rule_file.stem

    if not test_dir.exists():
        print(f"SKIP {rule_file} — pas de dossier de test")
        continue

    # True positive
    tp_file = test_dir / "true_positive.json"
    with open(tp_file) as f:
        event = json.load(f)

    if check_match(detection, event):
        print(f"OK   {rule_file} — true positive détecté")
    else:
        print(f"FAIL {rule_file} — true positive non détecté")
        errors += 1

    # False positive
    fp_file = test_dir / "false_positive.json"
    with open(fp_file) as f:
        event = json.load(f)

    if not check_match(detection, event):
        print(f"OK   {rule_file} — false positive ignoré")
    else:
        print(f"FAIL {rule_file} — false positive déclenche la règle")
        errors += 1

sys.exit(errors)
