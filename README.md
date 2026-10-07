# Gooo Conformance Lab

Gooo Conformance Lab is an independent public CI surface for checking
machine-readable language evidence. It does not mirror the compiler source,
replace the main repository, or declare whole-language completion.

## What this repository proves

The first contract checks that a development-story observation has:

- a stable story identifier;
- an immutable source digest and artifact digest;
- an explicit state (`CLOSED`, `UNKNOWN`, or `REFUTED`);
- a stage, step, reason, next operation, and blocked frontier for `UNKNOWN`;
- no claim of success when the evidence is incomplete.

The workflow validates the contract in GitHub Actions and publishes a
human-readable summary plus the normalized observation as an artifact.

When manually dispatched with a public artifact URL and its expected
SHA-256, the independent consumer job verifies byte identity before any
future semantic interpretation. Missing inputs skip that optional consumer;
malformed or mismatched inputs fail closed.

The same consumer job is exposed as a reusable workflow, so a producer
repository can invoke this lab after publishing an immutable public artifact
without copying the validator into the producer repository.

The language job checks out an immutable `meta-ontology-go` commit, executes a
real `.gooo` query through `go run ./cmd/gooo`, and validates the returned
query envelope. Digest verification alone is not treated as Gooo
functionality.

The generation job uses the same pinned compiler to run `gooo generate`,
checks the JSON generation envelope, and requires a generated Go file in the
output directory. A `SCAFFOLD` result means the typed bind graph and Go
composition wrapper were generated and type-checked; it does not mean the
activity bodies are implemented. The catalog records runtime observations as a
separate dimension: supported value chains must execute in declared order, and
unsupported operations must fail closed before an activity is applied. Query,
scaffold generation, and runtime execution are separate observations. A second runtime exercise uses the pinned compiler's
`body-compose` command to compile and execute a three-activity Gooo body graph.
It checks both typed edges, nine finite record-field and value expectations, and
identical output hashes across two native runs. An incompatible edge is rejected
during plan validation, before body generation or native execution. This measures
source-body composition separately from the registered-operation `run` path.

## What it does not prove

A passing contract check does not prove compiler correctness, user utility,
performance improvement, or adoption. Those claims require independently
bound evidence from the relevant Gooo CI run.

## Planned inputs

Later workflows may consume a released Gooo artifact by URL and SHA-256. The
consumer will never treat a URL, title, cache hit, or green check alone as
semantic or adoption authority.

## Local execution policy

The repository is designed to be validated by GitHub Actions. No local Go
build, test, generator, formatter, or repair is required for this contract.
