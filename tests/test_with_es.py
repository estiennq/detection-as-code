import requests
import json
import yaml
import subprocess
import sys
import time
from pathlib import Path

ES_URL = "http://localhost:9200"
INDEX = "test-detections"

def wait_for_es():
    for i in range(10):
        try:
            requests.get(ES_URL)
            return
        except:
            print("Attente ES...")
            time.sleep(3)
    print("ES non disponible")
    sys.exit(1)

def reset_index():
    requests.delete(f"{ES_URL}/{INDEX}")
    requests.put(f"{ES_URL}/{INDEX}", json={
        "mappings": {
            "properties": {
                "Message":     {"type": "keyword"},
                "Hostname":    {"type": "keyword"},
                "ProcessName": {"type": "keyword"}
            }
        }
    })

def index_event(event):
    requests.post(f"{ES_URL}/{INDEX}/_doc?refresh=true",
        json=event)

def convert_rule(rule_file):
    result = subprocess.run(
        ["sigma", "convert", "-t", "lucene", "--without-pipeline", str(rule_file)],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def search(query):
    response = requests.get(f"{ES_URL}/{INDEX}/_search",
        params={"q": query})
    return response.json()["hits"]["total"]["value"]

errors = 0
wait_for_es()

for rule_file in Path("detections").rglob("*.yml"):
    test_dir = Path("tests") / rule_file.parent.name / rule_file.stem

    if not test_dir.exists():
        print(f"SKIP {rule_file} — pas de dossier de test")
        continue

    query = convert_rule(rule_file)

    # True positive
    reset_index()
    with open(test_dir / "true_positive.json") as f:
        index_event(json.load(f))

    hits = search(query)
    if hits > 0:
        print(f"OK   {rule_file} — true positive détecté ({hits} hit)")
    else:
        print(f"FAIL {rule_file} — true positive non détecté")
        errors += 1

    # False positive
    reset_index()
    with open(test_dir / "false_positive.json") as f:
        index_event(json.load(f))

    hits = search(query)
    if hits == 0:
        print(f"OK   {rule_file} — false positive ignoré")
    else:
        print(f"FAIL {rule_file} — false positive déclenche la règle")
        errors += 1

sys.exit(errors)
