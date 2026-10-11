# Dated external aperture reports

An external report can be scientifically useful even when its author excluded it
from a planet-candidate list. Our initial database checks indexed Eumemic's counted
candidates, while their complete all-sky table also contained downgraded and rejected
signals. A dated no-match database response is retained as historical evidence; it
does not override a matching row found subsequently in a wider source inventory.

The source is Eumemic, [exoplanets](https://github.com/eumemic/exoplanets/tree/f3dd74abec5879661d76bcfcae2ce6744ba18aad),
commit `f3dd74abec5879661d76bcfcae2ce6744ba18aad`. Their results, tables and figures
are **CC BY 4.0**. Source rows and available supporting files are copied without
modification and credited individually. Our review metadata and narrative identify
our additions; their FPP/NFPP, fitted parameters and tiers remain attributed results.

Sixteen run-5 dossiers have matching same-TIC, direct-period external reports:
12 labelled `likely nearby FP`, two `likely EB` and two `C`. The saved nominal event
centres also align with the external ephemeris. These are reference centres of our
adopted hypothesis, not independently measured individual transit times. The external
epoch uncertainty and joint covariance are unavailable in the table; the diagnostic
does not establish calibrated timing consistency, source attribution or discovery priority.

Their novelty status is now `previously_reported`: an independent matching aperture
report exists. Their physical disposition remains `unclassified_transit_like_signal`;
source and timing statuses remain unresolved. A reported high FPP or binary label is
adverse evidence, not an independently reproduced probability or falsification.
Earlier public versions, first-disclosure dates, measurements and signed diagnostics
are retained. The original outcome ledger records the earlier review; later amendments
do not rewrite that history. A current source-review receipt lists the affected records.

Each affected dossier's `evidence/external-report.json` retains the full table row,
source table hash/commit/logical CSV row, nominal event residuals, reported metrics,
uncertainty limits and previous novelty block. Both C-tier dossiers have supporting
JSON and vetting images under `evidence/external-source/`; the other 14 have no
matching per-signal supporting files in the pinned public repository. One published
C-tier neighbour query failed with HTTP 429; that failure remains in the copied evidence.

The staging helper checks the complete manifest-bound review before any dossier
mutation, refuses changed science/source bytes or private paths, preserves scientific
and publication blocks, adds a minor dossier version and reseals the index. Repeating
the identical review makes no record changes. It never publishes automatically:

```bash
uv run python scripts/record_external_reports.py \
  --root . --batch run5-v1 --review /absolute/path/to/review.json
uv run python scripts/catalogue.py check
uv run python -m unittest discover -s tests
```

The review is evidence inspection. It does not rerun external fits, source/FPP
models or our photometry. Their full source inventory should also be retained by
catalogue services so absence from a candidate-only API is not mistaken for
absence of a prior report.
