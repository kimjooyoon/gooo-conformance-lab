#!/usr/bin/env python3
"""Verify one deterministic semantic query against a best-practice fixture."""

import json
import sys


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verify_gooo_query_case.py RESPONSE SUBJECT OBJECT")
    response_path, subject, object_id = sys.argv[1:]
    with open(response_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema") != "gooo-query/v1":
        raise SystemExit("unexpected query schema")
    if payload.get("status") != "ok":
        raise SystemExit("query did not complete successfully")
    request = payload.get("request", {})
    if request.get("operation") != "exact" or request.get("relation") != "used":
        raise SystemExit("query request is not the expected exact used relation")
    matches = payload.get("result", {}).get("deterministic_matches", [])
    expected = {"subject": subject, "predicate": "used", "object": object_id}
    if not any(all(match.get(key) == value for key, value in expected.items()) for match in matches):
        raise SystemExit("expected deterministic semantic match is missing")
    print(f"verified deterministic match: {subject} used {object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
