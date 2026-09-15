import json
from pathlib import Path


metrics = json.loads(Path("receipts/corpus-metrics.json").read_text())
comparison = json.loads(Path("receipts/corpus-metric-comparison.json").read_text())
candidate = {
    "schema": "gooo/best-practice-baseline-candidate/v1",
    "source_commit": __import__("os").environ.get("GITHUB_SHA", ""),
    "source_run_id": int(__import__("os").environ.get("GITHUB_RUN_ID", "0")),
    "compiler_ref": metrics.get("compiler_ref"),
    "catalog_digest": metrics.get("catalog_digest"),
    "metrics": {
        key: metrics[key]
        for key in (
            "corpus_wall_ms",
            "generated_compile_wall_ms",
            "fixture_count",
            "fixture_gooo_physical_lines",
            "catalog_case_count",
            "pass_case_count",
            "fail_closed_case_count",
            "compiler_go_files",
            "compiler_go_physical_lines",
            "compiler_gooo_files",
            "compiler_gooo_physical_lines",
            "generated_go_files",
            "lab_regular_files",
            "lab_descendant_dirs",
        )
    },
    "source_comparison_state": comparison.get("state"),
    "promotion_allowed": False,
    "repository_writes": 0,
    "next_operation": "PRESERVE_BASELINE_CANDIDATE_FOR_INDEPENDENT_REVIEW",
}
output = Path("receipts/baseline-candidate.json")
output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
print("### Baseline candidate")
print(f"- source comparison state: `{candidate['source_comparison_state']}`")
print(f"- promotion allowed: `{candidate['promotion_allowed']}`")
print(f"- next operation: `{candidate['next_operation']}`")
