import json
import hashlib
from pathlib import Path


comparison = json.loads(Path("receipts/corpus-metric-comparison.json").read_text())
comparison_bytes = Path("receipts/corpus-metric-comparison.json").read_bytes()
comparison_digest = "sha256:" + hashlib.sha256(comparison_bytes).hexdigest()
results = [metric["result"] for metric in comparison.get("metrics", {}).values()]
if comparison.get("state") != "CLOSED":
    decision = "DEFER"
    next_operation = "REESTABLISH_EXACT_BASELINE"
elif "IMPROVED" in results:
    decision = "OBSERVED_IMPROVEMENT_CANDIDATE"
    next_operation = "PRESERVE_CANDIDATE_FOR_INDEPENDENT_REVIEW"
elif "REGRESSED" in results:
    decision = "REJECT_CANDIDATE"
    next_operation = "PROFILE_AND_REDUCE_OBSERVER_OVERHEAD"
else:
    decision = "NO_CHANGE"
    next_operation = "NO_PERFORMANCE_ACTION_REQUIRED"

receipt = {
    "schema": "gooo/improvement-decision/v1",
    "comparison_state": comparison.get("state"),
    "comparison_reason": comparison.get("reason"),
    "comparison_digest": comparison_digest,
    "decision": decision,
    "next_operation": next_operation,
    "improved_metrics": [name for name, metric in comparison.get("metrics", {}).items() if metric.get("result") == "IMPROVED"],
    "regressed_metrics": [name for name, metric in comparison.get("metrics", {}).items() if metric.get("result") == "REGRESSED"],
    "unknown_metrics": [name for name, metric in comparison.get("metrics", {}).items() if metric.get("result") == "UNKNOWN"],
    "review_required": decision == "OBSERVED_IMPROVEMENT_CANDIDATE",
    "execution_allowed": False,
    "repository_writes": 0,
    "evidence": "receipts/corpus-metric-comparison.json",
}
output = Path("receipts/improvement-decision.json")
output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print("### Improvement decision")
for key in ("decision", "next_operation", "execution_allowed", "repository_writes"):
    print(f"- {key}: `{receipt[key]}`")
