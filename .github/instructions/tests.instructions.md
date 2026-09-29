---
applyTo: "tests/**"
---
Use pytest. One behaviour per test, named `test_<what>_<expected>`.
Reuse the shared fixtures in `tests/conftest.py` (`client`, `store`, `alert_id`) and build payloads with `make_txn(**overrides)` instead of duplicating setup.
Synthetic data only: invented names, fake country codes like `XQ`, made-up references.
Run the full suite with the command in AGENTS.md before finishing.
