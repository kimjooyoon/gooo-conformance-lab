# Gooo best-practice corpus

These fixtures are intentionally small and executable. The public conformance
workflow runs the pinned Gooo compiler against every file and verifies the
generated response and a deterministic semantic query. They are not pseudocode
and they do not claim that the whole language is complete.

## Practices represented

1. Declare domain entities with stable, explicit identifiers.
2. Use activities to make input and output provenance visible.
3. Keep a candidate, a baseline, and a decision as separate entities when a
   change is bounded by comparison.
4. Prefer several small declarations over one opaque natural-language claim.
5. Treat generated Go as an artifact to inspect, not as permission to adopt a
   change.
6. Query the declared input relation instead of inferring it from the source
   text or from the generated file name.

## Progressive domain scenarios

The first three fixtures establish the language shape. The next three are
small problem-solving scenarios that use the same shape:

- inventory consistency: reconcile an order line with a stock snapshot;
- deployment contract: validate a plan against a service contract;
- change review: review a repair candidate against a reported problem.
- self-improvement loop: observe a problem, compare a repair candidate with a
  baseline, and record a human decision.
- counterexample-guided repair: preserve a failure observation, compare a
  candidate with baseline behavior, retain a counterexample, and decide the
  next run.

The compiler observes the declared relationships and the CI observes the
generated/query results. It does not claim that these declarations execute a
warehouse, deploy a service, or approve a repair by themselves.

The self-improvement fixture is deliberately incomplete as an automation
promise: candidate generation, independent evaluation, adoption, and the next
run are separate operations. The fixture only makes their semantic boundary
observable.

The examples intentionally stop at the language boundary. Execution evidence,
human decisions, repository writes, and release promotion remain separate
operations in the surrounding CI system.
