# Contributor-truth review — 12 October 2026

The existing real-background controls test an added signal in a field that can
already contain variability. The known added coordinate is not automatically the
sole source or the effective position of the combined image. Existing ellipse
misses remain diagnostic adverse evidence; this review neither erases them nor
turns them into passes. **Source attribution remains unresolved.**

The new joint estimator fits signed contributions at the declared catalogue
profiles plus a spatial sky plane, with full conditional pixel covariance.
Negative nuisance contributions represent brightenings. Its coefficient intervals
answer a different question from a one-source winner or a free-centroid position.
No contribution estimate alone establishes an astrophysical host or a planet.

All 24 original records were attempted. Twenty-two have usable fixed geometry;
two remain unavailable. For each geometry, create known forward scenes with an
added source and a neighbour at -1/0/0.5/1/2 times its declared full-source loss.
Use 128 Gaussian draws per scene, with covariance explicitly known in the simulation.
Also shift the generating profiles by 0.2 pixels along each axis while fitting the
original positions. These are deterministic mismatch stresses, not an observed
astrometric-error distribution or a real-data coverage test.

| Generating profiles | Source coefficients | Draws | Joint injected-coefficient misses | Single-target amplitude misses |
|---|---|---:|---:|---:|
| Match the fitted profiles | Sole source | 2,816 | 37 | 35 |
| Match the fitted profiles | Multiple signed contributors | 11,264 | 109 | 9,987 |
| Shifted by 0.2 pixels | Sole source | 5,632 | 1,016 | 617 |
| Shifted by 0.2 pixels | Multiple signed contributors | 22,528 | 5,222 | 19,879 |

Misses use nominal 99% scalar intervals for the known contribution. The single-target
amplitude fit omits other source profiles; it is not the old free-centroid ellipse.
These counts must not be compared as coverage of the same quantity. The joint
calculation behaves as expected under its declared matched Gaussian model, while
forcing a single source introduces strong bias in composite scenes. Position
mismatch substantially undermines even the joint intervals.

One-source selection also sometimes chooses a different catalogue profile. That
does not make every injected contributor absent: selection, coefficient inference
and the dominant observable signal are distinct questions. Declared full-flux
amplitude dominance can differ from ROI-captured flux or the best one-source fit.
Real observed backgrounds do not have the fully known coefficients used here.

All 330 scenes and 42,240 simulated image draws have been numerically replayed.
This verifies conditional synthetic estimates; it does not establish empirical
host/position coverage, source reliability or a complete public numerical capsule.
The supplement is **evidence inspection only**.

The [anonymous aggregate record](../reviews/contributor-truth-review-2026-10-12-v1.json)
retains the recipe, counts and originating batch hash. Existing dossiers, warning
flags and negative evidence remain unchanged; all 172 assessments are unclassified.

Fixed/bounded source profiles, covariance estimation, physical eclipse feasibility,
PRF/position uncertainty and omitted hosts remain unqualified. Adequate empirical
calibration, timing, physical alternatives, search reliability and review remain
required before candidate promotion.
