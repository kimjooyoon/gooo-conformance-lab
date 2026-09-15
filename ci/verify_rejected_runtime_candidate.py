import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--baseline", required=True)
parser.add_argument("--candidate", required=True)
parser.add_argument("--candidate-source", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

baseline_path = Path(args.baseline)
candidate_path = Path(args.candidate)
candidate_source_path = Path(args.candidate_source)
baseline = json.loads(baseline_path.read_text())
candidate = json.loads(candidate_path.read_text())
if baseline.get("decision") != "PASS":
    raise SystemExit("rejected candidate baseline did not pass")
if candidate.get("decision") != "FAIL_CLOSED":
    raise SystemExit("overflow candidate was not fail-closed")
if candidate.get("reason") != "VALUE_INTEGER_OVERFLOW":
    raise SystemExit("overflow candidate reason was not explicit")
candidate_source_digest = digest(candidate_source_path)
if baseline.get("source_digest") == candidate_source_digest:
    raise SystemExit("rejected candidate did not change source identity")

receipt = {
    "schema": "gooo/runtime-improvement-rejection/v1",
    "baseline": {
        "receipt_digest": digest(baseline_path),
        "source_digest": baseline["source_digest"],
        "decision": baseline["decision"],
    },
    "candidate": {
        "receipt_digest": digest(candidate_path),
        "source_digest": candidate_source_digest,
        "source_path": args.candidate_source,
        "decision": candidate["decision"],
        "reason": candidate["reason"],
    },
    "decision": "CANDIDATE_REJECTED_FAIL_CLOSED",
    "next_operation": "PRESERVE_COUNTEREXAMPLE_AND_REVIEW_OPERATION_BOUND",
    "execution_allowed": False,
    "repository_writes": 0,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print("verified rejected runtime candidate: VALUE_INTEGER_OVERFLOW")
