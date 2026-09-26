---
id: sg/assurance-export
version: "0.1"
status: draft
kind: export-profile
---

# `sg/assurance-export@0.1`

v0 framing for **assurance export packs**: mappings from existing Agent Quality
Record evidence onto external assurance and transparency programmes.

These packs do **not** add scoring, aggregate grades, or new hard gates. They
document which AQR fields and measure classes can be projected into a named
external profile. SuperGauge remains a release-decision protocol.

## Packs in this family

| Pack | External programme | File |
|---|---|---|
| `sg/aiuc-1` | AIUC-1 (Q3 cut 2026-07-15; next cut 2026-10-15) | [`aiuc-1.md`](aiuc-1.md) |
| `sg/eu-art50` | EU AI Act Article 50 transparency (agents FAQ) | [`eu-art50.md`](eu-art50.md) |

## How to use

1. Emit a normal AQR (profile, subject, measures, deterministic gates, assurance,
   decision).
2. Optionally record which export profiles you claim coverage against under
   optional `export.profiles[]` (see SPEC / schema).
3. Use the pack tables to assemble an evidence folder or auditor checklist from
   digests and ledger pointers already on the record. Do not invent a headline
   score.

## Non-goals

- Replacing AIUC-1 certification or EU conformity assessment.
- Turning SuperGauge into a compliance engine or eval runner.
- Aggregating measure values into a single assurance grade (forbidden by SPEC
  §4.2).
