import json
import sys
from pathlib import Path


catalog = json.loads(Path("fixtures/best-practices/catalog.json").read_text())
if catalog.get("schema") != "gooo/best-practice-corpus/v1":
    raise SystemExit("unexpected best-practice catalog schema")
cases = {item["id"]: item for item in catalog.get("cases", [])}

if len(sys.argv) == 2 and sys.argv[1] == "--count":
    print(len(cases))
    raise SystemExit(0)
if len(sys.argv) != 2 or sys.argv[1] not in cases:
    raise SystemExit("unknown best-practice catalog case")

case = cases[sys.argv[1]]
if case.get("generation") not in {"PASS", "FAIL_CLOSED"}:
    raise SystemExit("unsupported best-practice generation state")
print(case["generation"], case["root"], case["target"], case["entity_count"], case["activity_count"])
