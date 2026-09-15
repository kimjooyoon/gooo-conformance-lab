import json
import sys


receipt = json.load(open(sys.argv[1], encoding="utf-8"))
if receipt.get("schema") != "gooo/value-execution-plan/v1":
    raise SystemExit("unexpected runtime receipt schema")
if receipt.get("decision") != "PASS":
    raise SystemExit("runtime value plan did not pass")
execution = receipt.get("execution", {})
if execution.get("apply_calls") != 1 or execution.get("deliveries") != 0:
    raise SystemExit("runtime execution counts are not exact")
result = execution.get("results", {}).get("Process", {})
if result.get("value") != 2:
    raise SystemExit(f"runtime result = {result.get('value')!r}, want 2")
if result.get("producer_activity_id") != "runtime://activity/process":
    raise SystemExit("runtime result lost producer activity identity")
print("verified Gooo runtime value: Process(1) -> 2")
