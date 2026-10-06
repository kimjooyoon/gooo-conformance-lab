import json
import sys
from pathlib import Path


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


if len(sys.argv) != 4:
    fail("usage: verify_runtime_scaffold.py GENERATE_RECEIPT SOURCE EXPECTED_BINDS")

receipt_path, source_path, expected_binds = sys.argv[1:]
try:
    receipt = json.loads(Path(receipt_path).read_text())
    source = Path(source_path).read_text()
except (OSError, json.JSONDecodeError) as error:
    fail("missing or invalid scaffold input: " + str(error))

if receipt.get("command") != "generate" or receipt.get("status") != "ok":
    fail("typed composition scaffold generation did not succeed")
def artifact_path(value):
    path = Path(value)
    if path.is_absolute():
        return path
    return Path("meta-ontology-go") / path


output_path = artifact_path(receipt.get("output", ""))
plan_path = artifact_path(receipt.get("runtime_plan", ""))
if not output_path.is_file() or not plan_path.is_file():
    fail("generated Go or runtime-plan artifact is missing")

try:
    generated = output_path.read_text()
    plan = json.loads(plan_path.read_text())
except (OSError, json.JSONDecodeError) as error:
    fail("invalid generated scaffold or runtime plan: " + str(error))

declared_binds = sum(line.startswith("bind ") for line in source.splitlines())
if declared_binds != int(expected_binds) or declared_binds <= 0:
    fail("source bind count does not match the catalog")
if plan.get("runtime_binding_count") != declared_binds:
    fail("runtime plan does not preserve every declared bind")
if len(plan.get("binding_edge_order", [])) != declared_binds:
    fail("runtime plan is missing deterministic bind-edge order")
if "GoooCompose" not in generated:
    fail("generated Go is missing its explicit composition scaffold")

print(
    "SCAFFOLD: generated typed composition and runtime plan for "
    f"{declared_binds} declared bind(s); activity bodies require runtime support evidence"
)
