import argparse
import json
import time
import hashlib
from pathlib import Path


def physical_lines(path):
    return len(path.read_text().splitlines())


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def files_under(root, excluded):
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in excluded for part in path.parts)
    ]


def language_inventory(root, compiler_files, lab_files):
    entries = []
    for path in compiler_files:
        if path.suffix not in {".go", ".gooo"}:
            continue
        entries.append(
            {
                "scope": "compiler",
                "path": (Path(root.name) / path.relative_to(root)).as_posix(),
                "language": path.suffix[1:],
                "physical_lines": physical_lines(path),
            }
        )
    for path in lab_files:
        if path.suffix not in {".go", ".gooo"}:
            continue
        entries.append(
            {
                "scope": "lab",
                "path": path.relative_to(root).as_posix(),
                "language": path.suffix[1:],
                "physical_lines": physical_lines(path),
            }
        )
    return sorted(entries, key=lambda item: (item["scope"], item["path"]))


parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True)
parser.add_argument("--started-at-ms", required=True, type=int)
parser.add_argument("--generated-compile-wall-ms", required=True, type=int)
parser.add_argument("--generation-query-wall-ms", required=True, type=int)
parser.add_argument("--runtime-provenance-wall-ms", required=True, type=int)
args = parser.parse_args()

root = Path(".")
fixture_root = root / "fixtures" / "best-practices"
catalog = json.loads((fixture_root / "catalog.json").read_text())
cases = catalog["cases"]
compiler_files = files_under(root / "meta-ontology-go", {".git"})
lab_files = files_under(root, {".git", "meta-ontology-go", "generated", "receipts", "repair"})
fixture_files = sorted(fixture_root.glob("*.gooo"))
generated_files = files_under(root / "generated", {".git"})
language_files = language_inventory(root, compiler_files, lab_files)

metrics = {
    "schema": "gooo/best-practice-corpus-metrics/v1",
    "compiler_ref": __import__("os").environ.get("GOOO_REF", ""),
    "catalog_digest": digest(fixture_root / "catalog.json"),
    "corpus_wall_ms": max(0, int(time.time() * 1000) - args.started_at_ms),
    "generation_query_wall_ms": args.generation_query_wall_ms,
    "runtime_provenance_wall_ms": args.runtime_provenance_wall_ms,
    "generated_compile_wall_ms": args.generated_compile_wall_ms,
    "fixture_count": len(fixture_files),
    "fixture_gooo_physical_lines": sum(physical_lines(path) for path in fixture_files),
    "catalog_case_count": len(cases),
    "pass_case_count": sum(case["generation"] == "PASS" for case in cases),
    "fail_closed_case_count": sum(case["generation"] == "FAIL_CLOSED" for case in cases),
    "compiler_go_files": sum(path.suffix == ".go" for path in compiler_files),
    "compiler_go_physical_lines": sum(physical_lines(path) for path in compiler_files if path.suffix == ".go"),
    "compiler_gooo_files": sum(path.suffix == ".gooo" for path in compiler_files),
    "compiler_gooo_physical_lines": sum(physical_lines(path) for path in compiler_files if path.suffix == ".gooo"),
    "generated_go_files": sum(path.suffix == ".go" for path in generated_files),
    "lab_regular_files": len(lab_files),
    "language_file_inventory": language_files,
    "language_go_files": sum(item["language"] == "go" for item in language_files),
    "language_go_physical_lines": sum(item["physical_lines"] for item in language_files if item["language"] == "go"),
    "language_gooo_files": sum(item["language"] == "gooo" for item in language_files),
    "language_gooo_physical_lines": sum(item["physical_lines"] for item in language_files if item["language"] == "gooo"),
    "lab_descendant_dirs": sum(
        1
        for path in root.rglob("*")
        if path.is_dir() and ".git" not in path.parts and path.name not in {"meta-ontology-go", "generated", "receipts", "repair"}
    ),
}

output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
print("### Corpus metrics")
for key, value in metrics.items():
    if key not in {"schema", "language_file_inventory"}:
        print(f"- {key}: `{value}`")
print("### Language file inventory")
for item in language_files:
    if item["language"] == "gooo":
        print(f"- {item['scope']}/{item['path']}: `{item['language']}` `{item['physical_lines']}` physical lines")
