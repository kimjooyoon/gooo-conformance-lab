import json
import sys


receipt = json.load(open(sys.argv[1], encoding="utf-8"))
if receipt.get("schema") != "gooo/value-execution-plan/v1":
    raise SystemExit("unexpected runtime chain schema")
if receipt.get("decision") != "PASS":
    raise SystemExit("runtime chain did not pass")
execution = receipt.get("execution", {})
if execution.get("activities") != ["Produce", "Consume"]:
    raise SystemExit("runtime chain activity order is not exact")
if execution.get("apply_calls") != 2 or execution.get("deliveries") != 1:
    raise SystemExit("runtime chain execution counts are not exact")
results = execution.get("results", {})
produce = results.get("Produce", {})
consume = results.get("Consume", {})
if produce.get("value") != 2 or consume.get("value") != 3:
    raise SystemExit("runtime chain values are not exact")
if produce.get("producer_activity_id") != "runtimechain://activity/produce":
    raise SystemExit("Produce producer identity is not exact")
if consume.get("producer_activity_id") != "runtimechain://activity/consume":
    raise SystemExit("Consume producer identity is not exact")
print("verified Gooo runtime chain: Produce(1) -> Consume(2) -> 3")
