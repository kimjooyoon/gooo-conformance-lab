import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--index", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

index_path = Path(args.index)
index = json.loads(index_path.read_text())
if index.get("schema") != "gooo/domain-index/v1":
    raise SystemExit("unexpected domain index schema")

boundaries = [item for item in index.get("cases", []) if item.get("state") == "FAIL_CLOSED"]
if boundaries:
    selected = sorted(
        boundaries,
        key=lambda item: (-item["graph_complexity"], item["case_id"]),
    )[0]
    operation = {
        "case_id": selected["case_id"],
        "source": selected["source"],
        "reason": "FAIL_CLOSED_CASE_HAS_RUNTIME_BOUNDARY",
        "next_operation": selected["next_operation"],
        "graph_complexity": selected["graph_complexity"],
    }
else:
    operation = {
        "case_id": None,
        "source": None,
        "reason": "NO_FAIL_CLOSED_DOMAIN_CASE",
        "next_operation": "ADD_OR_REVIEW_DOMAIN_SCENARIO",
        "graph_complexity": None,
    }

receipt = {
    "schema": "gooo/domain-next-operation/v1",
    "index_digest": index["observation_digest"],
    "selection_policy": "FAIL_CLOSED_THEN_MAX_GRAPH_COMPLEXITY_THEN_CASE_ID",
    "operation": operation,
    "execution_allowed": False,
    "repository_writes": 0,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(f"### Next domain operation: {operation['next_operation']}")
if operation["case_id"]:
    print(f"- selected `{operation['case_id']}`")
