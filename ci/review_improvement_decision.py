import hashlib
import json
from pathlib import Path


root = Path("review-artifact")
comparison_path = root / "receipts" / "corpus-metric-comparison.json"
decision_path = root / "receipts" / "improvement-decision.json"
comparison = json.loads(comparison_path.read_text())
decision = json.loads(decision_path.read_text())
expected_digest = "sha256:" + hashlib.sha256(comparison_path.read_bytes()).hexdigest()
if decision.get("comparison_digest") != expected_digest:
    raise SystemExit("improvement candidate comparison digest mismatch")
if decision.get("execution_allowed") is not False or decision.get("repository_writes") != 0:
    raise SystemExit("independent review found execution authority")
if decision.get("comparison_state") != comparison.get("state"):
    raise SystemExit("improvement candidate comparison state drifted")
if decision.get("decision") == "OBSERVED_IMPROVEMENT_CANDIDATE":
    if decision.get("review_required") is not True:
        raise SystemExit("improvement candidate does not require review")
    if not decision.get("improved_metrics"):
        raise SystemExit("improvement candidate has no improved metrics")
print(f"independent review: {decision.get('decision')}")
print(f"comparison digest: {expected_digest}")
print("execution_allowed: false")
print("repository_writes: 0")
