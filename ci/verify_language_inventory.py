import json
from pathlib import Path


metrics = json.loads(Path("receipts/corpus-metrics.json").read_text())
if metrics.get("schema") != "gooo/best-practice-corpus-metrics/v1":
    raise SystemExit("unexpected corpus metrics schema")

entries = metrics.get("language_file_inventory")
if not isinstance(entries, list) or not entries:
    raise SystemExit("language file inventory is missing")

identity = [(item.get("scope"), item.get("path")) for item in entries]
if identity != sorted(identity):
    raise SystemExit("language file inventory is not deterministically sorted")
if len(identity) != len(set(identity)):
    raise SystemExit("language file inventory contains duplicate paths")

for item in entries:
    path = Path(item.get("path", ""))
    language = item.get("language")
    if language not in {"go", "gooo"} or path.suffix[1:] != language:
        raise SystemExit("language file inventory has an extension mismatch")
    if item.get("scope") not in {"compiler", "lab"}:
        raise SystemExit("language file inventory has an unknown scope")
    if not isinstance(item.get("physical_lines"), int) or item["physical_lines"] < 0:
        raise SystemExit("language file inventory has an invalid line count")
    if ".." in path.parts:
        raise SystemExit("language file inventory escapes its root")

def count(language):
    return sum(item["language"] == language for item in entries)


def lines(language):
    return sum(item["physical_lines"] for item in entries if item["language"] == language)


if metrics.get("language_go_files") != count("go"):
    raise SystemExit("Go file count disagrees with inventory")
if metrics.get("language_go_physical_lines") != lines("go"):
    raise SystemExit("Go line count disagrees with inventory")
if metrics.get("language_gooo_files") != count("gooo"):
    raise SystemExit("Gooo file count disagrees with inventory")
if metrics.get("language_gooo_physical_lines") != lines("gooo"):
    raise SystemExit("Gooo line count disagrees with inventory")

compiler = [item for item in entries if item["scope"] == "compiler"]
if metrics.get("compiler_go_files") != sum(item["language"] == "go" for item in compiler):
    raise SystemExit("compiler Go file count disagrees with inventory")
if metrics.get("compiler_go_physical_lines") != sum(item["physical_lines"] for item in compiler if item["language"] == "go"):
    raise SystemExit("compiler Go line count disagrees with inventory")
if metrics.get("compiler_gooo_files") != sum(item["language"] == "gooo" for item in compiler):
    raise SystemExit("compiler Gooo file count disagrees with inventory")
if metrics.get("compiler_gooo_physical_lines") != sum(item["physical_lines"] for item in compiler if item["language"] == "gooo"):
    raise SystemExit("compiler Gooo line count disagrees with inventory")

print(f"verified deterministic language file inventory: {len(entries)} files")
