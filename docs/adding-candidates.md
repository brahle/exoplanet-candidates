# Add a candidate without changing the publication system

1. Match the signal against existing records and known reports; include period aliases and
   epochs. Pick a stable local signal ID. Do not infer novelty from absence of a TIC name online.
2. Create `candidates/<id>/` with the seven dossier files described in `publication.md`.
   Use `schemas/candidate.schema.json` as the required specification. Copy the first record
   as a structural example, replacing **all** identity, scientific, provenance and publication fields.
3. Export a bounded set of evidence. Prefer one overview plot, separate older/recent folds,
   all-predicted-event table, robustness comparisons, timing and source diagnostics, and
   documented failures. Include raw-source hashes and exposure/time conventions in `inputs.json`.
4. Record each assessment independently, along with dated novelty checks. Keep uncertainty
   methods explicit. Use IDs as strings so large Gaia identifiers retain their precision.
5. Hash every dossier file except the manifest itself. The manifest must account for all files,
   including `candidate.json`, reports and input identifiers. Imported evidence should retain its
   original SHA256; identify newly derived records separately.
6. Run `uv run python scripts/catalogue.py build`, then `check`, and the tests. Update the
   human-facing README table to match the generated `catalogue.json`. Review the release as a whole.
7. Follow the deliberate release sequence; leave publication metadata null until publication.

The target-specific exporter is the worked example for this first dossier. It reads preserved
Phase 1/2 evidence and does not run a search or change scientific settings:

```bash
uv run python scripts/export_tic_464547401.py /path/to/local/transit-search
uv run python scripts/catalogue.py build
uv run python scripts/catalogue.py check
```

The source checkout is currently private. This command reproduces the **export** when that
checkout is available; it is not an end-to-end public numerical reproduction command.
Use a candidate-specific exporter or a verified upstream release capsule for later targets.
Never export a complete private run manifest indiscriminately.
