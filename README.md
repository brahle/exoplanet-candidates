# Exoplanet candidate dossiers

Independent transit detections, dated research and inspectable evidence by Bruno Rahle.
Each entry identifies a **signal**, records what was checked and retains what remains uncertain.
An entry is an attributable research record; its presence here does not establish a planet,
scientific priority or an official TESS designation.

| Signal | Period | Source localisation | Timing consistency | Novelty check |
|---|---:|---|---|---|
| [TIC 464547401 / S01](candidates/tic-464547401-s01/README.md) | 13.24437854 d | unresolved | unresolved | No match in checked sources, 2026-10-10 |

The first dossier was **publicly disclosed on 2026-10-10** as an evidence-only record.
Its [disclosure receipt](candidates/tic-464547401-s01/publication-receipt.json) identifies the
initial commit and observed GitHub push timestamp. No versioned release or DOI is assigned yet.
Its tables and plots can be inspected and hash-verified; a public numerical rerun
is not yet available. See its [reproducibility statement](candidates/tic-464547401-s01/REPRODUCIBILITY.md).

[Run 5: 171 provisional signal dossiers](batches/run5-v1/README.md) includes the full 229-record outcome ledger, catalog coverage, adverse diagnostics and unresolved checks. These are unclassified evidence records with no planet or discovery-priority claim.

The [machine catalogue](catalogue.json) is generated from per-signal `candidate.json` files.
Consumers must select the declared [schema version](docs/schema.md); run-5 catalogue
and shape-covariance enrichment uses `1.3` (including the nullable 1.1 semantics), while the original
non-null dossier remains on strict `1.0`.
Stable IDs such as `tic-464547401-s01` are local identifiers; they are not TOIs, cTOIs or planet names.
One star can have several signal records. Updated assessments keep the same signal ID.

```bash
uv sync --frozen
uv run python scripts/catalogue.py check
uv run python -m unittest discover -s tests
```

Read the [publication workflow](docs/publication.md), [new-candidate guide](docs/adding-candidates.md)
and [credits](docs/credits.md). The workflow uses versioned dossiers, immutable GitHub releases
and DOI archives. Validation never publishes automatically.

Repository-authored code and documentation use the existing [MIT license](LICENSE).
Third-party mission/catalogue material retains its original attribution and terms.

[Browse diagnostic figures for every dossier](gallery/README.md). Five-panel overviews, complete event pages and saved plotting vectors are described in [the rendering methods](docs/diagnostic-figures.md).
