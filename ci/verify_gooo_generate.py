import json
import sys


def fail(message):
    print("FAIL: " + message)
    raise SystemExit(1)


def main(path):
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

    print("PASS: Gooo generated a Go output and manifest")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: verify_gooo_generate.py GENERATE_OUTPUT")
    main(sys.argv[1])
