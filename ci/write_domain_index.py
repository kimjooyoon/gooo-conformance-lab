import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--observation", required=True)
parser.add_argument("--metrics", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

observation_path = Path(args.observation)
metrics_path = Path(args.metrics)
observation = json.loads(observation_path.read_text())
metrics = json.loads(metrics_path.read_text())
if observation.get("schema") != "gooo/domain-observation/v1":
    raise SystemExit("unexpected domain observation schema")
if metrics.get("schema") != "gooo/best-practice-corpus-metrics/v1":
    raise SystemExit("unexpected corpus metrics schema")

cases = []
for item in sorted(observation.get("observations", []), key=lambda value: value["case_id"]):
    state = item["state"]
    if state == "CLOSED":
        next_operation = "COMPARE_AGAINST_EXACT_BASELINE"
    elif state == "FAIL_CLOSED":
        next_operation = "PRESERVE_BOUNDARY_AND_EXTEND_RUNTIME_SUPPORT"
    else:
        next_operation = "CLASSIFY_DOMAIN_OBSERVATION_STATE"
    cases.append(
        {
            "case_id": item["case_id"],
            "source": item["source"],
            "state": state,
            "entity_count": item["entity_count"],
            "activity_count": item["activity_count"],
            "bind_count": item["bind_count"],
            "declaration_count": item["entity_count"] + item["activity_count"],
            "graph_complexity": item["entity_count"] + item["activity_count"] + item["bind_count"],
            "next_operation": next_operation,
            "source_digest": item["source_digest"],
            "observation_evidence": item["evidence"],
        }
    )

state_counts = {}
for item in cases:
    state_counts[item["state"]] = state_counts.get(item["state"], 0) + 1

index = {
    "schema": "gooo/domain-index/v1",
    "catalog_digest": observation["catalog_digest"],
    "observation_digest": digest(observation_path),
    "metrics_digest": digest(metrics_path),
    "case_count": len(cases),
    "state_counts": {key: state_counts[key] for key in sorted(state_counts)},
    "total_entity_count": sum(item["entity_count"] for item in cases),
    "total_activity_count": sum(item["activity_count"] for item in cases),
    "total_bind_count": sum(item["bind_count"] for item in cases),
    "cases": cases,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
print(f"### Domain index ({len(cases)} cases)")
for state, count in index["state_counts"].items():
    print(f"- `{state}`: {count}")
