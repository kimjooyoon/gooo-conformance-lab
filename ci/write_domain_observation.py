import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True)
args = parser.parse_args()

catalog_path = Path("fixtures/best-practices/catalog.json")
catalog = json.loads(catalog_path.read_text())
observations = []
for case in catalog["cases"]:
    source = Path("fixtures/best-practices") / case["source"]
    generation_receipt = Path("receipts") / f"{case['id']}.json"
    query_receipt = Path("receipts") / f"{case['id']}-query.json"
    for evidence in (source, generation_receipt, query_receipt):
        if not evidence.is_file():
            raise SystemExit(f"missing observation evidence: {evidence}")
    generation = json.loads(generation_receipt.read_text())
    query = json.loads(query_receipt.read_text())
    query_ok = (
        query.get("schema") == "gooo-query/v1"
        and query.get("status") == "ok"
        and query.get("request", {}).get("operation") == "exact"
        and query.get("request", {}).get("relation") == "used"
        and bool(query.get("result", {}).get("deterministic_matches"))
    )
    if not query_ok:
        raise SystemExit(f"query receipt did not close for {case['id']}")
    if case["generation"] == "PASS":
        generation_ok = (
            generation.get("command") == "generate"
            and generation.get("status") == "ok"
            and bool(generation.get("output"))
            and bool(generation.get("manifest"))
        )
    else:
        generation_ok = (
            generation.get("command") == "generate"
            and generation.get("status") == "error"
            and any(
                item.get("code") == "generator.generate"
                and "runtime bindings are unsupported" in item.get("message", "")
                for item in generation.get("diagnostics", [])
            )
        )
    if not generation_ok:
        raise SystemExit(f"generation receipt did not match catalog state for {case['id']}")
    generation_reason = (
        "GENERATION_SUCCESS"
        if case["generation"] == "PASS"
        else "RUNTIME_BINDINGS_UNSUPPORTED"
    )
    observations.append(
        {
            "case_id": case["id"],
            "source": case["source"],
            "state": "CLOSED" if case["generation"] == "PASS" else "FAIL_CLOSED",
            "generation_state": case["generation"],
            "generation_reason": generation_reason,
            "query_state": "CLOSED",
            "entity_count": case["entity_count"],
            "activity_count": case["activity_count"],
            "bind_count": case["bind_count"],
            "source_digest": digest(source),
            "generation_receipt_digest": digest(generation_receipt),
            "query_receipt_digest": digest(query_receipt),
            "evidence": [str(source), str(generation_receipt), str(query_receipt)],
        }
    )

observation = {
    "schema": "gooo/domain-observation/v1",
    "catalog_digest": digest(catalog_path),
    "observations": observations,
}
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n")
print(f"### Domain observations ({len(observations)})")
for item in observations:
    print(f"- `{item['case_id']}`: `{item['state']}` source `{item['source_digest'][:20]}...`")
