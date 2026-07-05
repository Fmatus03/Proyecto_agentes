# Incremental traceability

| requirement | use_case | milestone | agents | tools | artifacts | validators | gates | status |
|---|---|---|---|---|---|---|---|---|
| J.12 Fundamentos | J.12 Hito 1, H, J.4, J.7, J.8 RNF-01/RNF-02 | HITO-001 | agent.intake, agent.architect_planner, agent.implementer, agent.qa, agent.security, agent.close | tool.sandbox.dev_materialize, tool.policy.static, tool.validation.artifacts, tool.security.secrets, tool.security.deps, tool.sbom.generate | contracts/permissions.json, backend/app/core/security.py, backend/app/main.py, frontend/src/App.jsx, tests/test_contracts.py | milestone.expected_artifacts, milestone.dependencies, milestone.qa_promotion, milestone.regression | milestone_validation, qa_promotion, regression | pass |
