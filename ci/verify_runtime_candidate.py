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

baseline = json.loads(Path(args.baseline).read_text())
candidate = json.loads(Path(args.candidate).read_text())
if baseline.get("decision") != "PASS" or candidate.get("decision") != "PASS":
    raise SystemExit("runtime candidate comparison requires two passing receipts")
baseline_result = baseline.get("execution", {}).get("results", {}).get("Process", {})
candidate_result = candidate.get("execution", {}).get("results", {}).get("Process", {})
if baseline_result.get("value") != 2 or candidate_result.get("value") != 3:
    raise SystemExit("runtime candidate did not produce the exact expected delta")
if baseline.get("source_digest") == candidate.get("source_digest"):
    raise SystemExit("runtime candidate did not change the source identity")

receipt = {
    "schema": "gooo/runtime-improvement-candidate/v1",
    "baseline": {
        "receipt_digest": digest(Path(args.baseline)),
        "source_digest": baseline["source_digest"],
        "value": baseline_result["value"],
    },
    "candidate": {
        "receipt_digest": digest(Path(args.candidate)),
        "source_digest": candidate["source_digest"],
        "source_path": args.candidate_source,
        "value": candidate_result["value"],
    },
    "decision": "CANDIDATE_OBSERVED_NOT_ADOPTED",
    "next_operation": "REVIEW_RUNTIME_CANDIDATE",
    "execution_allowed": False,
    "repository_writes": 0,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print("verified runtime improvement candidate without adoption")
