import json
from pathlib import Path


current_path = Path("receipts/corpus-metrics.json")
baseline_path = Path("fixtures/best-practices/baseline-metrics.json")
current = json.loads(current_path.read_text())
baseline = json.loads(baseline_path.read_text())
identity_fields = ("schema", "compiler_ref", "catalog_digest")
same_identity = all(current.get(field) == baseline.get(field) for field in identity_fields)
integer_fields = ("corpus_wall_ms", "generated_compile_wall_ms")
comparison = {
    "schema": "gooo/best-practice-corpus-metric-comparison/v1",
    "baseline_source_run_id": baseline.get("source_run_id"),
    "baseline_source_commit": baseline.get("source_commit"),
    "identity": {field: current.get(field) for field in identity_fields},
    "state": "CLOSED" if same_identity else "UNKNOWN",
    "reason": "EXACT_BEFORE_AFTER_TUPLE" if same_identity else "BEFORE_AFTER_IDENTITY_MISMATCH",
    "metrics": {},
}
for field in integer_fields:
    before = baseline.get(field)
    after = current.get(field)
    valid_pair = same_identity and isinstance(before, int) and isinstance(after, int)
    delta = before - after if valid_pair else None
    comparison["metrics"][field] = {
        "before": before,
        "after": after,
        "delta_before_minus_after": delta,
        "result": (
            "IMPROVED" if delta and delta > 0 else
            "REGRESSED" if delta and delta < 0 else
            "UNCHANGED" if delta == 0 else
            "UNKNOWN"
        ),
    }

output = Path("receipts/corpus-metric-comparison.json")
output.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n")
print("### Corpus metric comparison")
print(f"- state: `{comparison['state']}`")
print(f"- reason: `{comparison['reason']}`")
for field, metric in comparison["metrics"].items():
    print(f"- {field}: `{metric['result']}` before `{metric['before']}` after `{metric['after']}`")
