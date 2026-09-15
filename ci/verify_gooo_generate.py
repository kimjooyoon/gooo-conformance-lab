import json
import re
import sys


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def main(path, source_path, expected_entities, expected_activities, expected_binds):
    try:
        with open(path, encoding="utf-8") as handle:
            response = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        fail("generate output is not valid JSON: " + str(error))

    if response.get("command") != "generate":
        fail("unexpected command in generate envelope")
    if response.get("status") != "ok":
        fail("generate did not close successfully")
    if not response.get("output"):
        fail("generate envelope has no output path")
    if not response.get("manifest"):
        fail("generate envelope has no manifest path")
    source = open(source_path, encoding="utf-8").read()
    entities = len(re.findall(r"^entity ", source, re.MULTILINE))
    activities = len(re.findall(r"^activity ", source, re.MULTILINE))
    binds = len(re.findall(r"^bind ", source, re.MULTILINE))
    if (
        entities != int(expected_entities)
        or activities != int(expected_activities)
        or binds != int(expected_binds)
    ):
        fail(
            f"domain declaration count mismatch: entities={entities}/{expected_entities}, "
            f"activities={activities}/{expected_activities}, binds={binds}/{expected_binds}"
        )

    print(f"PASS: Gooo generated a Go output and manifest with {entities} entities, {activities} activities, and {binds} binds")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        fail("usage: verify_gooo_generate.py GENERATE_OUTPUT SOURCE ENTITY_COUNT ACTIVITY_COUNT BIND_COUNT")
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
