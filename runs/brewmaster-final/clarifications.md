# Clarifications

| decision | value | evidence |
|---|---|---|
| Runtime scope | local factory artifacts only | EV-SRC-001 |
| External write | denied by default | EV-SRC-001 |
| Deploy | denied by default | EV-SRC-001 |
| MCP | default deny / empty allowlist | EV-SRC-001 |
| Project root | `project/brewmaster` | EV-SRC-001 |
| Project memory | project-scoped only, factory memory denied | EV-SRC-001 |
| Sandboxes | DEV and QA independent local clones | EV-SRC-001 |
| Frontend contract | project-specific frontend contract is mandatory | EV-SRC-001 |
| Generated app stack | not selected in this runtime implementation | EV-SRC-001 |

No critical question remains open for the local WEBFORGE factory runtime.
