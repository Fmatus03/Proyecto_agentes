# BrewMaster WEBFORGE Project Pack

This pack owns the BrewMaster domain knowledge consumed by the generic WEBFORGE factory:

- milestone roadmap from `brewmaster_especificacion_completa.md`;
- BrewMaster blueprint, coverage gates and acceptance checks;
- generated backend, frontend, contracts, docs and tests for each implemented milestone;
- project-specific frontend contract `BREWMASTER_REACT_BOOTSTRAP`.
- BrewMaster deployment contract for the approved AWS EC2 + Docker Compose target.

The `webforge/` package must remain project-agnostic. It discovers project packs through
`projects/*/webforge_pack/adapter.py` and calls the generic `ProjectAdapter` interface.
