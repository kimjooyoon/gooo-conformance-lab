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

The examples intentionally stop at the language boundary. Execution evidence,
human decisions, repository writes, and release promotion remain separate
operations in the surrounding CI system.
