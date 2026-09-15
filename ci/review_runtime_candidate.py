import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--candidate", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

candidate_path = Path(args.candidate)
candidate = json.loads(candidate_path.read_text())
if candidate.get("schema") != "gooo/runtime-improvement-candidate/v1":
    raise SystemExit("unexpected runtime candidate schema")
if candidate.get("decision") != "CANDIDATE_OBSERVED_NOT_ADOPTED":
    raise SystemExit("runtime candidate is not in the reviewable state")
if candidate.get("execution_allowed") is not False or candidate.get("repository_writes") != 0:
    raise SystemExit("runtime candidate has unsafe authority")
if candidate.get("baseline", {}).get("value") != 2 or candidate.get("candidate", {}).get("value") != 3:
    raise SystemExit("runtime candidate lost its exact before/after values")

review = {
    "schema": "gooo/runtime-improvement-review/v1",
    "candidate_digest": digest(candidate_path),
    "candidate_case": candidate["candidate"]["source_path"],
    "before_value": candidate["baseline"]["value"],
    "after_value": candidate["candidate"]["value"],
    "decision": "READY_FOR_EXPLICIT_ADOPTION",
    "next_operation": "PROMOTE_RUNTIME_CANDIDATE_WITH_EXPLICIT_POLICY_CHANGE",
    "promotion_allowed": False,
    "repository_writes": 0,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
print("reviewed runtime candidate: ready for explicit adoption")
