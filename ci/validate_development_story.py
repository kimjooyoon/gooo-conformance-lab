import json
import sys


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def main(contract_path, fixture_path):
    with open(contract_path, encoding="utf-8") as handle:
        contract = json.load(handle)
    with open(fixture_path, encoding="utf-8") as handle:
        story = json.load(handle)

    if story.get("schema") != contract.get("schema"):
        fail("schema mismatch")

    for field in contract["required"]:
        if field not in story:
            fail("missing required field: " + field)

    if story["state"] not in contract["states"]:
        fail("unknown state: " + str(story["state"]))

    for field in ("source_digest", "artifact_digest"):
        value = story[field]
        if not isinstance(value, str) or not value.startswith(contract["digest_prefix"]):
            fail("invalid digest field: " + field)

    if not isinstance(story["blocked_by"], list):
        fail("blocked_by must be an array")

    if story["state"] == "UNKNOWN":
        for field in contract["unknown_requires"]:
            if field == "blocked_by":
                continue
            if not isinstance(story[field], str) or not story[field]:
                fail("UNKNOWN requires non-empty field: " + field)

    normalized = json.dumps(story, sort_keys=True, separators=(",", ":"))
    print("PASS: development story contract")
    print(normalized)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        fail("usage: validate_development_story.py CONTRACT FIXTURE")
    main(sys.argv[1], sys.argv[2])
