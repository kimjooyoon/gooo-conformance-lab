import json
import sys
from pathlib import Path


ACTIVITY_IDS = [
    "agenthandoffruntime://activity/propose-candidate",
    "agenthandoffruntime://activity/record-independent-review",
    "agenthandoffruntime://activity/commit-candidate",
]
CANDIDATE_FIELDS = [
    {"id": "agent-handoff-runtime://candidate/title", "name": "title"},
    {"id": "agent-handoff-runtime://candidate/state", "name": "state"},
]
REVIEW_FIELDS = [
    {"id": "agent-handoff-runtime://review/summary", "name": "summary"},
    {"id": "agent-handoff-runtime://review/reason", "name": "reason"},
]
DECISION_FIELDS = [
    {"id": "agent-handoff-runtime://decision/accepted", "name": "accepted"},
    {"id": "agent-handoff-runtime://decision/summary", "name": "summary"},
]


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def read_receipt(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"cannot read body composition receipt: {error}") from error


def with_values(fields, values):
    return [dict(field, value=value) for field, value in zip(fields, values)]


def verify_positive(receipt):
    composition = receipt.get("composition", {})
    runtime = receipt.get("runtime", {})
    names = ["ProposeCandidate", "RecordIndependentReview", "CommitCandidate"]
    edge_ids = [
        {
            "producer": ACTIVITY_IDS[0],
            "consumer": ACTIVITY_IDS[1],
            "producer_port": "result",
            "consumer_port": "input0",
            "entity": "agent-handoff-runtime://entity/candidate",
        },
        {
            "producer": ACTIVITY_IDS[1],
            "consumer": ACTIVITY_IDS[2],
            "producer_port": "result",
            "consumer_port": "input",
            "entity": "agent-handoff-runtime://entity/review",
        },
    ]
    cases = [
        (
            "change-42",
            True,
            {"title": "change-42", "state": "proposed"},
            {"summary": "change-42", "reason": "accepted"},
            {"accepted": True, "summary": "change-42"},
        ),
        (
            "",
            False,
            {"title": "", "state": "proposed"},
            {"summary": "", "reason": "deferred"},
            {"accepted": False, "summary": ""},
        ),
        (
            "수정안🧭",
            True,
            {"title": "수정안🧭", "state": "proposed"},
            {"summary": "수정안🧭", "reason": "accepted"},
            {"accepted": True, "summary": "수정안🧭"},
        ),
    ]

    require(receipt.get("generated_now") is True, "typed chain was not generated from its Gooo source")
    require(composition.get("stage") == "COMPLETE", "typed chain composition did not complete")
    require(composition.get("original_source_sha256") == composition.get("selected_source_sha256"), "typed chain source identity changed")
    plan = composition.get("plan", {})
    activities = plan.get("activities", [])
    require([item.get("name") for item in activities] == names, "typed activity order differs")
    require([item.get("id") for item in activities] == ACTIVITY_IDS, "typed activity identities differ")
    require([item.get("input_from") for item in activities] == [-1, 0, 1], "typed input delivery order differs")
    require(activities[0].get("input_type") == "Text" and activities[0].get("output_type") == "Candidate", "proposal signature differs")
    require(activities[1].get("inputs") == [
        {"port": "input0", "type": "Candidate", "entity_id": "agent-handoff-runtime://entity/candidate", "from": 0},
        {"port": "input1", "type": "Boolean", "entity_id": "agent-handoff-runtime://entity/boolean", "from": -1},
    ], "review input ports or their sources differ")
    require(activities[2].get("input_type") == "Review" and activities[2].get("output_type") == "Decision", "decision signature differs")
    require(plan.get("edges") == edge_ids, "declared typed edges differ")
    require(plan.get("typed_plan_sha256", "").startswith("sha256:"), "typed plan digest is missing")
    require(len(composition.get("steps", [])) == 3, "not every activity body was generated")

    require(runtime.get("stage") == "COMPLETE", "typed chain execution did not complete")
    require(runtime.get("typed_plan_sha256") == plan.get("typed_plan_sha256"), "runtime receipt does not bind the typed plan")
    require(runtime.get("finite_passed") == 9 and runtime.get("finite_total") == 9, "finite input/output cases did not all pass")
    require(runtime.get("model_calls") == 0, "unexpected model call in deterministic conformance case")
    require(runtime.get("projection_replayed") is True and runtime.get("runtime_replayed") is True, "projection or runtime replay did not close")
    runs = runtime.get("runs", [])
    require(len(runs) == 2 and all(run.get("exit_code") == 0 for run in runs), "expected two successful native executions")
    require(runs[0].get("stdout_sha256") == runs[1].get("stdout_sha256"), "native replay output changed")

    traces = runtime.get("traces", [])
    require(len(traces) == len(cases), "runtime trace count differs from declared cases")
    for case_index, (trace, case) in enumerate(zip(traces, cases)):
        root_input, review_flag, candidate, review, decision = case
        require(trace.get("case_index") == case_index, f"runtime trace index differs at {case_index}")
        deliveries = trace.get("deliveries", [])
        require(len(deliveries) == 3, f"runtime delivery count differs at case {case_index}")
        for index, delivery in enumerate(deliveries):
            require(delivery.get("activity_id") == ACTIVITY_IDS[index], f"activity identity differs at case {case_index}, step {index}")
            require(delivery.get("passed") is True, f"activity did not satisfy its finite expectation at case {case_index}, step {index}")
        proposal, independent_review, commit = deliveries
        require(proposal.get("input") == root_input, f"proposal input differs at case {case_index}")
        require(proposal.get("actual") == candidate and proposal.get("expected") == candidate, f"candidate record differs at case {case_index}")
        require(proposal.get("actual_fields") == with_values(CANDIDATE_FIELDS, [candidate["title"], candidate["state"]]), f"candidate field identity differs at case {case_index}")

        review_inputs = independent_review.get("inputs", [])
        require(len(review_inputs) == 2, f"review input count differs at case {case_index}")
        bound_candidate, external_flag = review_inputs
        require(bound_candidate.get("port") == "input0" and bound_candidate.get("entity_id") == "agent-handoff-runtime://entity/candidate", f"candidate input port identity differs at case {case_index}")
        require(bound_candidate.get("producer_id") == ACTIVITY_IDS[0] and bound_candidate.get("value") == candidate, f"candidate value was not delivered from the proposal at case {case_index}")
        require(bound_candidate.get("fields") == with_values(CANDIDATE_FIELDS, [candidate["title"], candidate["state"]]), f"delivered candidate fields differ at case {case_index}")
        require(external_flag.get("port") == "input1" and external_flag.get("entity_id") == "agent-handoff-runtime://entity/boolean" and external_flag.get("value") is review_flag, f"independent review input differs at case {case_index}")
        require(independent_review.get("actual") == review and independent_review.get("expected") == review, f"review record differs at case {case_index}")
        require(independent_review.get("actual_fields") == with_values(REVIEW_FIELDS, [review["summary"], review["reason"]]), f"review field identity differs at case {case_index}")

        require(commit.get("producer_id") == ACTIVITY_IDS[1] and commit.get("input") == review, f"review value was not delivered to decision at case {case_index}")
        require(commit.get("input_fields") == with_values(REVIEW_FIELDS, [review["summary"], review["reason"]]), f"delivered review fields differ at case {case_index}")
        require(commit.get("actual") == decision and commit.get("expected") == decision, f"decision record differs at case {case_index}")
        require(commit.get("actual_fields") == with_values(DECISION_FIELDS, [decision["accepted"], decision["summary"]]), f"decision field identity differs at case {case_index}")
    print("typed body composition: Candidate → Review → Decision, 2 declared edges, 9/9 values, 2 deterministic native runs")


def verify_negative(receipt):
    composition = receipt.get("composition", {})
    runtime = receipt.get("runtime", {})
    require(receipt.get("generated_now") is True, "negative case did not validate the supplied source")
    require(composition.get("stage") == "PLAN", "incompatible typed edge did not fail during plan validation")
    require("type mismatch" in composition.get("failure", ""), "incompatible edge failure cause was not retained")
    require(not composition.get("steps"), "body generation started before rejecting the incompatible edge")
    require(runtime.get("build", {}).get("started") is False, "native build started for an incompatible edge")
    require(runtime.get("model_calls") == 0, "model was called for an invalid graph")
    require(runtime.get("finite_passed") == 0 and runtime.get("finite_total") == 0, "invalid graph received runtime completeness credit")
    require(not runtime.get("runs"), "native execution started for an incompatible edge")
    print("incompatible Candidate → Boolean edge: FAIL_CLOSED at PLAN, before generation or native execution")


if len(sys.argv) != 3 or sys.argv[1] not in {"positive", "negative"}:
    raise SystemExit("usage: verify_body_composition.py positive|negative <receipt.json>")
receipt = read_receipt(sys.argv[2])
if sys.argv[1] == "positive":
    verify_positive(receipt)
else:
    verify_negative(receipt)
