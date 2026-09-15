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
    observations.append(
        {
            "case_id": case["id"],
            "source": case["source"],
            "state": case["generation"],
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
