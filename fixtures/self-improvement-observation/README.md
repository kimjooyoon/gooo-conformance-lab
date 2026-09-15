# Self-improvement observation fixture

This fixture uses the real Gooo `observe` and `propose` commands. The
authority file declares a pure, read-only semantic operation and the input
file supplies a small domain program. Repeated evaluation produces a
deterministic observation candidate and a proposal-only artifact.

The CI lane does not invent human approval. It also submits a structurally
invalid denied authorization to `gooo adopt` and requires fail-closed
rejection without an adoption result. A real authorization must come from a
separate explicit caller-controlled authority path.

The separate `Gooo authorized self-improvement adoption` workflow is the
positive path. It is `workflow_dispatch` only and requires an explicit
authorization flag and caller-provided authority id. The workflow binds that
authorization to its freshly generated proposal, then lets the compiler
verify every digest before bounded in-memory reuse. Its output is uploaded as
an artifact; it never writes the repository.

The authorization proposal binding intentionally uses the proposal file's
raw-byte digest because that is the current `gooo adopt` CLI boundary. This is
distinct from the compiler's internal canonical proposal digest and is kept
visible in the workflow rather than silently approximated.
