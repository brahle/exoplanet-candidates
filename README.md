# Exoplanet candidate dossiers

Independent transit detections, dated research and inspectable evidence by Bruno Rahle.
Each entry identifies a **signal**, records what was checked and retains what remains uncertain.
An entry is an attributable research record; its presence here does not establish a planet,
scientific priority or an official TESS designation.

**[Browse by vetting progress, scientific assessment and warning flags](browse/README.md).**
The [classification guide](docs/classification.md) separates work performed from
confidence in a planetary explanation. Dossiers keep stable paths as findings change.
The [outstanding-work folders](browse/README.md#outstanding-work) group records by
source attribution, timing, physical alternatives, search reliability and review.
These overlapping groups describe the work still needed, not planet likelihood.

[Vetting update, 11 October 2026](docs/vetting-findings-2026-10-11.md): among the
156 signals without prior-report overlaps, 116 have initial warnings, 33 have no
warnings in those initial checks, and seven have incomplete diagnostics. Later
pixel warnings are recorded separately. All 172 scientific assessments remain
unclassified; the shortlist is not a count of likely planets.
Three initial-shortlist signals now carry off-target warnings, leaving
[30 without currently published warnings for follow-up](browse/shortlist/README.md).

[Supplementary physical-fit review](docs/physical-fit-review-2026-10-11.md): longer
chains pass sampling checks for two public signals, while TIC 339451799 retains
substantial density, limb-darkening and exposure-integration concerns. These
conditional results do not change the unclassified assessments.

A [separate exposure-integration review](docs/exposure-integration-review-2026-10-11.md)
and numerical replay package show that changing the averaging rule leaves
TIC339451799's point-fit density concern in place. No corrected posterior or
stronger classification is claimed.

A [source-control quality review](docs/source-control-review-2026-10-11.md) finds
that extra centroid starts help one selected control, while background/source
modelling remains limiting. Source attribution stays unresolved.

A [joint temporal source/noise pilot](docs/temporal-source-review-2026-10-11.md)
attempted24 source records and retained missing-event and nominal-interval issues.
It remains a conditional method experiment, with no stronger scientific assessments.

A [mode-dependent temporal covariance review](docs/mode-temporal-source-review-2026-10-12.md)
replays the same 24-record cohort. It reduces three selected nominal interval
mismatches to two; remaining mismatches and correlation-bound clipping leave
source attribution unresolved.

A [held-out prediction review](docs/heldout-source-review-2026-10-12.md) tests
training-only noise models against unseen transit-duration OOT blocks. Prediction
improvements are mixed, and many timescales remain at a bound; this does not qualify
source attribution or promote any signal.

An [independent-sector noise review](docs/independent-sector-noise-review-2026-10-12.md)
tests finite-prior fast/slow variability predictions on each target's next available
sector. Twenty targets support the test; improvements are mixed, leaving source
qualification unresolved.

A [contributor-truth review](docs/contributor-truth-review-2026-10-12.md) distinguishes
an added source from the whole composite image in known forward controls. Joint
contribution estimates handle signed blends under the declared model, while position
mismatches retain substantial failures. Existing source warnings remain intact.

An [observed-star position review](docs/observed-position-review-2026-10-12.md)
measures disjoint early/late images across 24 source records. Most selected positions
are stable within a sector despite catalogue-relative offsets; boundary and rank
failures remain explicit. Field ranks are descriptive, with no adopted host exclusions.

An [early-profile transfer review](docs/profile-transfer-review-2026-10-12.md)
compares those profiles on late images and joint transit contrasts. Most learned
cores remain unusable; TIC 21694454 shows substantial target-contribution sensitivity
to the profile model. The failed case and missing windows remain explicit, with no
host or planetary promotion.

A [source-profile resampling review](docs/profile-bootstrap-review-2026-10-12.md)
propagates early pixel-block variation through position/profile refits into late
transit contributions. Within-family scatter is small for TIC 21694454 compared
with the persistent structural difference between families; the bootstrap cannot
qualify that host assignment. Missing windows and rejected baseline controls remain.

A [background-search fitting repair](docs/contact-faces-review-2026-10-12.md)
addresses a numerical repeatability failure in the independent search-control pilot.
The contact-face experiment is stable on its saved inputs and finds better objectives;
the failed first version is retained. The repair is not adopted and the full campaign
remains held. The separate source wave has finished all 42 executions, still unresolved.

A [full diagnostic replay](docs/trapezoid-interface-review-2026-10-12.md) now connects
that experimental fit to all original light-curve diagnostics. All 36 saved-input
replays are stable, including conditional covariance; native-input repeatability
and interval qualification remain open. No dossier assessment changes.

A [native-input repeatability review](docs/native-fit-repeatability-2026-10-12.md)
expands the experiment to 32 presampled targets and 480 complete searches. Available
measurements repeat within the declared tolerances, while nine trial groups retain
undefined diagnostics. The method remains experimental and all assessments unchanged.

| Signal | Period | Source localisation | Timing consistency | Novelty check |
|---|---:|---|---|---|
| [TIC 464547401 / S01](candidates/tic-464547401-s01/README.md) | 13.24437854 d | unresolved | unresolved | No match in checked sources, 2026-10-10 |

The first dossier was **publicly disclosed on 2026-10-10** as an evidence-only record.
Its [disclosure receipt](candidates/tic-464547401-s01/publication-receipt.json) identifies the
initial commit and observed GitHub push timestamp. No versioned release or DOI is assigned yet.
Its tables and plots can be inspected and hash-verified; a public numerical rerun
is not yet available. See its [reproducibility statement](candidates/tic-464547401-s01/REPRODUCIBILITY.md).

[Run 5: 171 provisional signal dossiers](batches/run5-v1/README.md) includes the full 229-record outcome ledger, catalog coverage, adverse diagnostics and unresolved checks. These are unclassified evidence records with no planet or discovery-priority claim.

[Later source review](docs/external-reports.md) records matching independent aperture reports for
16 run-5 dossiers, including Eumemic's binary/blend warnings and downgraded records.
Their novelty status is now `previously_reported`; their physical classifications remain unresolved.
Earlier versions and dated no-match queries remain available.

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
