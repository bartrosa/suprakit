# Deferred work

This directory tracks items that were scoped for bootstrap but deferred to keep the initial commit clean. Each file describes one deferred item in enough detail for another agent or human to pick it up without rediscovery.

## Open items

- [TODO-anionfit-esp-implementation.md](TODO-anionfit-esp-implementation.md) — Full ESP-at-bowl-center extraction via tblite (deferred pending verified Python API usage).

## How to close an item

1. Implement the work.
2. Remove any `NotImplementedError` stub (if applicable).
3. Delete the corresponding `TODO-*.md`.
4. Remove the entry from this README.
5. Add a conventional-commit `feat:` or `fix:` referencing the removed TODO file.
