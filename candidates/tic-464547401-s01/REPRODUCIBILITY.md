# Reproducibility coverage

**Current level: evidence inspection. Public end-to-end numerical reproduction is incomplete.**

From this repository, readers can validate the specification, time bookkeeping, covariance,
generated catalogue and every exported dossier file's bytes:

```bash
uv sync --frozen
uv run python scripts/catalogue.py check
uv run python -m unittest discover -s tests
```

This checks an evidence package. It does not rerun the light-curve/pixel fits, establish source
identity or validate a planetary interpretation.

The original project preserves clean source revisions, exact settings/input locks, per-run
manifests, arrays, failed checks and repeat-run comparisons. Phase 1 repeats matched fourteen
non-report outputs; Phase 2 matched forty. Original report provenance lines differ between
runs. Those repetitions used archived inputs accessible through private infrastructure.
The current public export must not claim equivalent access for an outside researcher.

`inputs.json` identifies all ten light-curve and twelve pixel products with SHA256/size,
mission/reduction/target identity, original time conventions and available public archive IDs.
It omits operational paths and private storage metadata. Exact TESScut output bytes are not
yet publicly mirrored; a new request can produce a different file hash.
`analysis-settings.json` is a settings export, not an executable replacement configuration.
Unmodified science artifacts carry their source SHA256 in `evidence-manifest.json`.

Before a **public numerical rerun** release, publish a capsule containing:

1. The exact original light-curve and pixel bytes, catalogue responses and all numerical arrays
   used by the report, with a public retrieval map and SHA256/size manifest.
2. The selected analysis source, original science configs, frozen dependency lock and software
   attribution; remove the private storage requirement without changing numerical analysis.
3. One documented command that runs both audited phases from a clean environment using only
   public URLs/files, with a fresh output manifest and comparison certificate. State whether
   agreement is byte-identical or numerical; never promise cross-platform bitwise equivalence
   without measuring it.
4. A versioned archive containing the report, code and data, with a resolvable DOI and exact
   version citation. Verify large assets are included rather than assuming integration coverage.

The capsule is an outstanding publication step. No raw-data transfer, candidate submission,
new scientific analysis or external follow-up is implied by this draft.
