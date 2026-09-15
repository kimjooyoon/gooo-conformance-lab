import json
import sys
from pathlib import Path


source = Path(sys.argv[1])
receipt = json.loads(Path(sys.argv[2]).read_text())
diagnostics = receipt.get("diagnostics", [])
if receipt.get("status") != "error" or not any(
    item.get("code") == "generator.generate"
    and "runtime bindings are unsupported" in item.get("message", "")
    for item in diagnostics
):
    raise SystemExit(f"runtime binding generation boundary was not explicit for {source.name}")
print(f"recorded expected runtime binding generation boundary for {source.name}")
