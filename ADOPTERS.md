# Adopters

Tools and organisations that emit or consume Agent Quality Records.

A specification with one implementation is a proposal. This list exists so that
anyone considering the format can see who else has committed to it, and at which
conformance level.

## Tools

| Tool | Maintainer | Role | Level | Notes |
|---|---|---|---|---|
| [SuperQode](https://github.com/SuperagenticAI/superqode) | Superagentic AI | Emits, checks | L2 | Coding-agent harnesses. `sq gauge run`, `gate`, `show`, `verify` |
| [SuperOptiX](https://github.com/SuperagenticAI/superoptix) | Superagentic AI | Emits | L1 | Agents across eight runtimes. `super agent evaluate --gauge-out` |

## Organisations

Teams using the format internally, listed with their permission.

_None listed yet. Open a pull request to be the first._

## Adding yourself

Open a pull request against this file with one row.

**Tools** need a link, the maintainer, whether the tool emits records, consumes
them, or both, and the highest conformance level it reaches. Run the suite
before claiming a level:

```bash
python conformance/check.py your-record.yaml
```

**Organisations** need a name and, optionally, a sentence on what you use the
format for. A logo is unnecessary and no approval is required beyond your own.

Two things worth stating. A level claimed here is self-asserted, as it is
everywhere else in this project, and anyone can reproduce it from a record you
publish. And listing here creates no obligation: the format is CC BY 4.0 and
Apache 2.0, and you can stop using it whenever it stops being useful.

## Reporting an implementation you did not write

A tool that emits valid records can be listed by anyone who has verified it.
Include a sample record in the pull request so a reviewer can run the suite
against it.
