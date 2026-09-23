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
        fail("query output is not valid JSON: " + str(error))

    if response.get("schema") != "gooo-query/v1":
        fail("unexpected query schema")
    if response.get("status") != "ok":
        fail("query did not close successfully")
    if response.get("request", {}).get("operation") != "exact":
        fail("query operation was not exact")

    matches = response.get("result", {}).get("deterministic_matches", [])
    matching = [
        match.get("subject") == "billing://activity/pay-order"
        and match.get("predicate") == "used"
        and match.get("object") == "billing://entity/order"
        for match in matches
    ]
    if len(matching) != 1:
        fail(f"deterministic Order match count is {len(matching)}, expected exactly one")

    print("PASS: Gooo query executed and returned a deterministic match")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: verify_gooo_query.py QUERY_OUTPUT")
    main(sys.argv[1])
