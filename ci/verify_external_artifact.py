import hashlib
import json
import sys


def fail(message):
    print(json.dumps({"state": "REFUTED", "reason": message}, sort_keys=True))
    raise SystemExit(1)


def main(path, expected):
    if not expected.startswith("sha256:") or len(expected) != len("sha256:") + 64:
        fail("expected digest must be sha256:<64 hex characters>")
    try:
        expected_hex = bytes.fromhex(expected.removeprefix("sha256:"))
    except ValueError:
        fail("expected digest is not hexadecimal")

    with open(path, "rb") as handle:
        payload = handle.read()
    actual = hashlib.sha256(payload).digest()
    result = {
        "state": "CLOSED" if actual == expected_hex else "REFUTED",
        "bytes": len(payload),
        "actual_digest": "sha256:" + actual.hex(),
        "expected_digest": expected,
    }
    print(json.dumps(result, sort_keys=True))
    if actual != expected_hex:
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        fail("usage: verify_external_artifact.py FILE sha256:<digest>")
    main(sys.argv[1], sys.argv[2])
