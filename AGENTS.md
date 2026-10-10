# Candidate publication rules

This repository publishes candidate dossiers. Read README.md and docs/publication.md first.

- Keep target identity, signal identity, novelty, source localisation and timing consistency separate.
- Never promote an unresolved transit-like signal to a planet or invent an official designation.
- Tie measurements to versioned evidence, units, uncertainty methods and input hashes.
- Preserve negative evidence, failed checks, previous releases and rejected signals.
- Do not replace dated catalogue responses with live responses without a new assessment/version.
- Do not backdate public disclosure to detection, author dates or unpublished analysis commits.
- Public exports must exclude credentials, private infrastructure, unrelated task context and personal metadata.
- A checksum verifies an artifact; it does not establish scientific validity or discovery priority.
- State public reproducibility coverage honestly. Inspection of saved evidence is not a fresh numerical rerun.
- Keep publication a deliberate release step. Validation and index generation must not publish automatically.
- Before delivery run `uv sync --frozen`, `uv run python scripts/catalogue.py check`
  and `uv run python -m unittest discover -s tests`.
