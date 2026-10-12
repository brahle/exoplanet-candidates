# Native-input repeatability review — 12 October 2026

The experimental [fitting repair](trapezoid-interface-review-2026-10-12.md) has now
been tested through native mission input loading, preprocessing, the complete
period search and light-curve vetting. This extends the earlier saved-array test.

The experiment uses the first32 targets in the archived random sample's draw order,
including the original two pilots. All62 public mission products were reacquired
with their original checksums; no target or input was substituted. Each target
receives five observed/control/injection variants in three independent subprocess
repetitions:96 fresh worker executions and480 full searches. The original search
settings, grids and numerical comparison tolerances remain unchanged.

| Outcome | Count |
|---|---:|
| Distinct target/variant groups |160|
| Groups with vetting outputs |74|
| Groups not selected for vetting |86|
| Groups with unavailable diagnostics |9|
| Targets affected by unavailable diagnostics |6|
| Measured numerical differences beyond the declared tolerances |0|

The nine affected groups overlap the74 vetted groups. Across repetitions,222 vet
records exist and27 contain unavailable statistics. Six groups have unavailable
local curvature errors; odd/even and out-of-transit probes are also unavailable in
some groups. These missing statistics are preserved explicitly and cannot become
passes or establish a false-positive explanation.

The audit compares full periodograms, available fitted measurements, uncertainties,
warning flags and selection/recovery decisions. It finds no measured contract
failures, but the **strict completeness audit remains unqualified**. Its85 unresolved
entries include repeated records and multiple fields; they are not85 independent
signals. The [aggregate receipt](../reviews/native-fit-repeatability-2026-10-12-v1.json)
records these scopes separately.

Resumption testing exposed a concurrent SQLite connection lifecycle deadlock after
ten cached receipts. That failed attempt was preserved. A separate serial,
cache-only verification then checked all96 original receipts with zero new
numerical executions. This is a bounded workaround; the original concurrent
resumption path has not been generally repaired.

The fitter remains experimental and the8,192-target reliability campaign remains
held. Local white-noise curvature intervals, null-model adequacy and physical/source
interpretation are still unqualified. The next review concerns the nine missing
trial groups and their information rank/event coverage; thresholds and the sample
will not be changed to erase these outcomes.

All172 published signals remain unclassified. These32 engineering controls are
separate from that catalogue. This supplement publishes aggregate evidence
inspection, with no public numerical reproduction capsule or planetary promotion.
