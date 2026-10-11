# Batch catalogue enrichment

The scientific pipeline command queries exact TIC IDs and the official
`gaiadr3.dr2_neighbourhood` table. Gaia DR2 identifiers from TIC are never copied
into the DR3 field. Integer identifiers never pass through floating point.
The pinned `stellar-v2.toml` policy requires exactly one row with separation below
100 mas and absolute G-band difference below 0.2 mag. It retains all rows and the
quality decision for each. Multiple qualifying rows, or a competitor with missing
quality information, remain ambiguous; it never merely selects the nearest row.
This is a catalogue-association policy, not source localisation. The earlier v1
policy required uniqueness before quality filtering; its results remain archived.

TIC JSON completion/pagination and Gaia VOTable query status, overflow and field
units are checked. Query failures, missing, ambiguous and quality-limited results
remain separate outcomes. One acquisition serves all signals on the same target.
Each run records request bodies, query parameters, retrieval UTC, raw response
bytes and hashes. A snapshot replay checks all seals and runs without the network.

```bash
# Scientific repository, with an imported batch:
uv run --extra agent transit-search vet --root /path/to/batches stellar \
  --batch campaign --science-config configs/vetting/stellar-v2.toml \
  --output /path/to/new-stellar.json
# Offline repeat from the printed run directory:
uv run --extra agent transit-search vet --root /path/to/batches stellar \
  --batch campaign --output /path/to/repeat.json --snapshot results/runs/RUN
# New policy applied to the same complete raw responses, as a separate run:
uv run --extra agent transit-search vet --root /path/to/batches stellar \
  --batch campaign --science-config configs/vetting/stellar-v2.toml \
  --output /path/to/reassessed.json --snapshot results/runs/OLD_RUN --reassess
# This public repository; prepares changes without publishing:
uv run python scripts/enrich_batch.py --root . --batch campaign \
  --report /path/to/scientific/results/runs/RUN/stellar.json
```

The public helper requires the complete batch ledger and a manifest-bound report,
validates before updating dossiers, and refuses different already-attached context.
Exact repeated delivery does not change versions/history. The response snapshot
is copied with a public provenance receipt; private manifest hostnames and paths
are excluded. The validator ties structured parameters and association back to
the per-dossier context. A new catalogue assessment needs a deliberate versioned
update rather than replacement of an earlier snapshot. Reassessment retains the
original acquisition run and raw hashes; incompatible acquisition settings are rejected.

Schema 1.2 records five TIC catalogue values and their reported errors in an
explicit aperture-target host context. Catalogue row `version` is preserved
separately from the service's TIC release identifier. Temperature/radius/mass/
distance calculation flags, missing uncertainties and large errors are retained.
The [TIC release notes](https://outerspace.stsci.edu/spaces/TESS/pages/111023212/TIC%2Bv8.2%2Band%2BCTL%2Bv8.xx%2BData%2BRelease%2BNotes)
document catalogue caveats, including unreliable properties for some subgiants.

Aperture-star catalogue association does not identify the eclipsed source. The
existing source, timing, novelty and disposition assessments are preserved;
the physical host and dilution remain unresolved. Duration uncertainty and
physical transit parameters require separate fits and are not supplied by this
catalogue stage. Published updates follow the existing deliberate release process.
