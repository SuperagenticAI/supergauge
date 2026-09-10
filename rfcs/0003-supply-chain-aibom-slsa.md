---
rfc: 0003
title: Supply-chain AIBOM and SLSA digests on the record
status: draft          # draft | accepted | rejected | superseded
surface: spec
author: Superagentic AI
created: 2026-09-10
---

# RFC 0003: Supply-chain AIBOM and SLSA digests on the record

## Summary

Add an optional top-level `supply_chain` block so an Agent Quality Record can
carry digests and references for AI/ML bills of materials (AIBOM), SLSA or
in-toto provenance, MCP server pins, and model or tool artifact digests.
SuperGauge records what was attested at ship time; it does not generate BOMs
or provenance. Light SPEC and schema patches keep status at `0.1.0-draft`.

## Problem

Release decisions for agents increasingly face the same questions as classical
software supply chain reviews: which models and tools were in the loop, which
MCP servers were reachable, and whether a signed bill of materials and
provenance exist. Procurement and security programmes (including OWASP ASI
guidance around supply-chain risk) ask for attestation evidence. Today an AQR
pins `subject.harness_digest` and optional `code_digest`, but has nowhere to
put an AIBOM digest, an SLSA provenance digest, or the set of MCP servers the
agent was measured against. Teams either omit the evidence or paste it into
unstructured rationale, which auditors cannot verify.

## Proposal

### Optional `supply_chain` block

Additive and optional. The eight required AQR blocks are unchanged. When an
emitter has attestation artifacts, it MAY include:

```yaml
supply_chain:
  aibom_digest: sha256:...                 # CycloneDX ML-BOM / AIBOM document
  aibom_format: "cyclonedx-1.6+aibom"      # OPTIONAL label of the BOM profile
  slsa_provenance_digest: sha256:...       # SLSA provenance or in-toto statement
  provenance_format: "slsa/v1"             # OPTIONAL; or in-toto/v1, etc.
  model_digests:                           # OPTIONAL pins beyond subject.model
    - {provider: anthropic, id: claude-opus-5, digest: sha256:...}
  tool_digests:                            # OPTIONAL tool / plugin artifacts
    - {name: repo-grep, digest: sha256:...}
  mcp_servers:
    - name: github
      version: "2.1.0"
      digest: sha256:...                   # server distribution / image digest
      endpoint_digest: sha256:...          # OPTIONAL digest of endpoint config
```

| Field | Required when block present | Meaning |
|---|---|---|
| `aibom_digest` | recommended when models or tools are in scope | Digest of the AIBOM / CycloneDX AI-ML BOM document for this release |
| `aibom_format` | optional | Short label of the BOM spec/profile (e.g. CycloneDX with AI/ML extensions) |
| `slsa_provenance_digest` | recommended when claiming verifiable build provenance | Digest of the SLSA provenance predicate or enclosing in-toto attestation |
| `provenance_format` | optional | `slsa/v1`, `in-toto/v1`, or another documented attestation shape |
| `model_digests[]` | optional | Content digests for model artifacts when not already implied by `subject.model` |
| `tool_digests[]` | optional | Digests for tool binaries, plugins, or packed tool definitions |
| `mcp_servers[]` | optional | MCP servers available during measurement |

Each `mcp_servers[]` entry:

| Field | Required | Meaning |
|---|---|---|
| `name` | required | Stable server name as configured for the run |
| `version` | recommended | Version string when the server publishes one |
| `digest` | recommended | Digest of the server distribution, image, or package |
| `endpoint_digest` | optional | Digest of the endpoint URL plus auth-scheme descriptor (never the secret) |

**Digests.** All digests use the existing `sha256:` form (SPEC `$defs.digest`).
They MUST hash the attestation or artifact bytes used for this release, not a
description of intent (SPEC §7).

**Relation to `subject`.** `subject.model` remains the identity of the primary
model under evaluation. `supply_chain.model_digests` MAY pin content addresses
(weights, adapter archives, or vendor attestation digests) when those exist.
`subject.harness_digest` / `code_digest` continue to identify the loop and
code; they are not replaced by the AIBOM.

### Conformance guidance (no new level numbers)

| Level | Supply-chain expectation when a profile opts in |
|---|---|
| **L2** | When the profile requires supply-chain evidence, `aibom_digest` is present and covers the models and tools named on the record (including MCP servers listed under `mcp_servers[]` when used). Digests are well-formed. |
| **L4** | In addition, signed BOM and provenance are verifiable: `slsa_provenance_digest` (or equivalent in-toto attestation digest) is present, the referenced attestations verify under the emitter's published keys or transparency log, and an independent party can resolve the digests. |

Profiles choose whether supply-chain fields are mandatory for a given tier.
The core does not assert a floor (SPEC §4.3). Absence of `supply_chain` remains
valid for records that do not claim this evidence.

### Light SPEC and schema patches

- SPEC documents optional `supply_chain` after the required skeleton, with a
  pointer to this RFC.
- SPEC §5 notes the L2 / L4 guidance above when a profile requires the block.
- JSON Schema adds optional root `supply_chain` and optional
  `subject.model.digest` for a single primary model pin.
- Status remains `0.1.0-draft`.

## Deterministic or judged

This RFC defines record fields, not a graded measure. Verifying that a digest
matches retrieved bytes is deterministic. Cryptographic signature verification
for L4 is likewise deterministic given the public keys or log entries. No
model judge is involved.

## Evidence required

- The AIBOM / CycloneDX document bytes corresponding to `aibom_digest`.
- The SLSA or in-toto attestation bytes corresponding to
  `slsa_provenance_digest`, when claimed.
- Resolution paths (URL, OCI reference, or content store) sufficient for a
  third party to fetch those bytes at L4.
- MCP server distribution or config artifacts when their digests are asserted.

## Cost

No additional agent evaluation runs. Cost is whatever the organisation already
pays to produce or receive an AIBOM and provenance (often generated in CI).
Recording digests on the AQR is serialisation only.

## Failure cases

| Case | Required behaviour |
|---|---|
| `supply_chain` omitted | Valid; no supply-chain claim on this record |
| Profile requires AIBOM but `aibom_digest` missing | Do not claim the profile's supply-chain bar; conformance for that profile fails |
| Digest does not match retrieved BOM / provenance bytes | Treat as failed verification; do not claim L4 supply-chain evidence |
| `mcp_servers[]` lists a server not available during measurement | Materially false; emitters MUST list servers that were configured for the measured runs |
| Secrets embedded in endpoint descriptors | Forbidden; hash a redacted descriptor (scheme, host template, scopes) only |
| Unsigned BOM offered as L4 evidence | Insufficient for the L4 guidance above |

## Alternatives considered

- **Fold everything into `subject`.** Rejected for MCP lists and provenance:
  subject identity stays small; supply-chain attestation is optional and
  multi-artifact.
- **Require `supply_chain` on every record.** Rejected: many early adopters
  lack BOMs; optional keeps L1 reachable.
- **Generate CycloneDX or SLSA inside SuperGauge.** Rejected: out of scope;
  peer SCA and build systems already produce these artifacts.
- **Single combined RFC with Agent Card binding.** Split retained: Agent Card
  is interop/discovery; AIBOM/SLSA is attestation. Single-topic RFCs match
  `rfcs/0000-template.md` practice.

## Prior art

- [CycloneDX AI/ML BOM (AIBOM) guidance](https://cyclonedx.org/) and related
  ML-BOM profiles for models, datasets, and tools.
- ECMA-424 (CycloneDX foundational standard lineage) for BOM interchange.
- [SLSA](https://slsa.dev/) provenance levels and in-toto attestations.
- SPEC acknowledgements already cite SLSA's graded self-assertion model.
- OWASP ASI guidance on AI supply-chain risk (ASI04 and related controls) as
  the procurement pressure this block answers.

## Out of scope

- Generating, merging, or diffing BOM documents.
- Running SLSA builders, signing services, or transparency logs.
- Defining a SuperGauge-specific BOM schema.
- Declaring numeric floors or a single aggregate supply-chain score
  (forbidden by SPEC §4.2).
- Replacing `subject.authority`, ACS gates, or runtime policy engines.

## Open questions

- Whether `aibom_format` should become an enum once CycloneDX AI profiles
  stabilise under a single short name.
- Whether MCP endpoint digests should move to a dedicated measure later.
- How profiles should cite external BOM coverage requirements without
  duplicating CycloneDX field lists inside SuperGauge.

---

### Review checklist

- [ ] `id` is dotted, lowercase, and not a rename of an existing measure
- [ ] Computation is unambiguous enough for two implementations to agree
- [ ] `deterministic` / `judged` is correctly classified and defended
- [ ] Failure cases are specified
- [ ] Evidence requirements are stated
- [ ] No floor or threshold is asserted (floors are profile-scoped, SPEC §4.3)
- [ ] Commits are DCO signed off
