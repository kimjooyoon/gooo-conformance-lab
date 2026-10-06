import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--operation", required=True)
parser.add_argument("--observation", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

operation_path = Path(args.operation)
observation_path = Path(args.observation)
operation = json.loads(operation_path.read_text())
observation = json.loads(observation_path.read_text())
if operation.get("schema") != "gooo/domain-next-operation/v1":
    raise SystemExit("unexpected next operation schema")
if observation.get("schema") != "gooo/domain-observation/v1":
    raise SystemExit("unexpected domain observation schema")

selected = operation["operation"]
case_id = selected.get("case_id")
matches = [item for item in observation["observations"] if item["case_id"] == case_id]
if len(matches) != 1:
    raise SystemExit("next operation did not identify exactly one observed case")
case = matches[0]
if case["state"] != "FAIL_CLOSED":
    raise SystemExit("runtime support frontier requires a FAIL_CLOSED case")
if case.get("runtime_reason") == "VALUE_PROGRAM_UNKNOWN":
    missing_capability = "REGISTERED_DOMAIN_OPERATION"
    next_operation = "IMPLEMENT_AND_CONFORM_DOMAIN_OPERATION"
    observed_reason = case["runtime_reason"] + ":" + case.get("runtime_operation", "")
elif case["generation_reason"] == "RUNTIME_BINDINGS_UNSUPPORTED":
    missing_capability = "BIND_EXECUTION"
    next_operation = "IMPLEMENT_AND_CONFORM_BIND_RUNTIME_SUPPORT"
    observed_reason = case["generation_reason"]
else:
    raise SystemExit("FAIL_CLOSED case has no observed runtime capability boundary")

receipt = {
    "schema": "gooo/runtime-support-frontier/v1",
    "operation_digest": digest(operation_path),
    "observation_digest": digest(observation_path),
    "frontier": {
        "case_id": case["case_id"],
        "source": case["source"],
        "missing_capability": missing_capability,
        "observed_reason": observed_reason,
        "next_operation": next_operation,
        "evidence": case["evidence"],
    },
    "execution_allowed": False,
    "repository_writes": 0,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(f"### Runtime support frontier: {case['case_id']}")
print(f"- missing capability: `{missing_capability}`")
