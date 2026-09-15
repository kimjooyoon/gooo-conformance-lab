import hashlib
import json
from pathlib import Path


root = Path("review-artifact")
comparison_path = root / "receipts" / "corpus-metric-comparison.json"
decision_path = root / "receipts" / "improvement-decision.json"
baseline_candidate_path = root / "receipts" / "baseline-candidate.json"
comparison = json.loads(comparison_path.read_text())
decision = json.loads(decision_path.read_text())
baseline_candidate = json.loads(baseline_candidate_path.read_text())
expected_digest = "sha256:" + hashlib.sha256(comparison_path.read_bytes()).hexdigest()
if decision.get("comparison_digest") != expected_digest:
    raise SystemExit("improvement candidate comparison digest mismatch")
if decision.get("execution_allowed") is not False or decision.get("repository_writes") != 0:
    raise SystemExit("independent review found execution authority")
if decision.get("comparison_state") != comparison.get("state"):
    raise SystemExit("improvement candidate comparison state drifted")
if baseline_candidate.get("promotion_allowed") is not False or baseline_candidate.get("repository_writes") != 0:
    raise SystemExit("baseline candidate unexpectedly grants promotion authority")
if baseline_candidate.get("source_comparison_state") == "UNKNOWN":
    baseline_review = "READY_FOR_EXPLICIT_PROMOTION"
    baseline_next_operation = "PROMOTE_BASELINE_WITH_EXPLICIT_POLICY_CHANGE"
else:
    baseline_review = "NO_BASELINE_PROMOTION_REQUIRED"
    baseline_next_operation = "NO_PERFORMANCE_ACTION_REQUIRED"
baseline_receipt = {
    "schema": "gooo/best-practice-baseline-review/v1",
    "candidate_source_commit": baseline_candidate.get("source_commit"),
    "candidate_source_run_id": baseline_candidate.get("source_run_id"),
    "candidate_catalog_digest": baseline_candidate.get("catalog_digest"),
    "decision": baseline_review,
    "next_operation": baseline_next_operation,
    "promotion_allowed": False,
    "repository_writes": 0,
}
(root / "receipts" / "baseline-review.json").write_text(json.dumps(baseline_receipt, indent=2, sort_keys=True) + "\n")
if decision.get("decision") == "OBSERVED_IMPROVEMENT_CANDIDATE":
    if decision.get("review_required") is not True:
        raise SystemExit("improvement candidate does not require review")
    if not decision.get("improved_metrics"):
        raise SystemExit("improvement candidate has no improved metrics")
print(f"independent review: {decision.get('decision')}")
print(f"comparison digest: {expected_digest}")
print("execution_allowed: false")
print("repository_writes: 0")
print(f"baseline review: {baseline_review}")
