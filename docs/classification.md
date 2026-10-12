# How signals are organised

Every signal keeps its existing `candidates/<signal-id>/` address, including when
it is rejected. The directory name is historical storage, not a planet claim.
[Browse](../browse/README.md) contains generated folder indexes pointing to those
records. Changing an assessment never breaks links or removes negative evidence.

We record **two independent axes**, plus warning tags and novelty. The terms below
are this project's explicit policy, not official TESS designations or probabilities.
Eumemic's A/B/N/L1 labels are specific to their selection and calibration; we do not
assign their tiers to our signals.

## Mapping the proposed folders

The proposed categories cover useful questions, but mixing them in one directory
tree would lose information. For example, a signal can have finished screening,
still have an unresolved host, and carry an odd/even warning at the same time.
Use folder **views** linking to its one permanent dossier instead.

| Proposed folder | Where to find it | Adjustment |
|---|---|---|
| Queue | `browse/process/queue/` | No initial screening started. |
| False positives | `browse/assessment/false-positive/` | Require reviewed evidence for a specific explanation; a failed calculation alone is insufficient. |
| Warnings | `browse/warnings/` | Overlapping flags, not an exclusive assessment. Keep the measurement, uncertainty and reason. |
| Candidates | `browse/assessment/candidate/` | Require a reviewed minimum policy, with supported source and timing; merely passing our currently implemented checks is insufficient. |
| Likely planets | `browse/assessment/likely-planet/` | Require qualified evidence favouring the planetary explanation; record the remaining follow-up needed. |
| Confirmed planets | `browse/assessment/confirmed-planet/` | Require published confirmation evidence; checklist completion does not confer confirmation. |

Two additions fill the gaps: **unclassified** for detections whose explanation is
still open, and **validated planet** for a documented statistical validation.
An observing request belongs to process/follow-up needs; it does not by itself
make a detection a likely planet. A previously reported flag is independent too:
it answers whether this signal has been reported before, not whether it is real.

For practical subdivisions, use the existing stage statuses, warning tags and
`open_requirements`: needs source attribution, timing, physical alternatives,
reliability, or a classification review. Publish the specific outstanding
requirement rather than an unexplained A/B/C grade. The shortlist prioritises work;
its membership is not a probability tier. Any future probability tier needs a
declared model, a calibrated policy and published supporting evidence.

The [combined browse table](../browse/README.md) shows both axes together. It counts
each assessed record once; warning and novelty views overlap. All 172 currently
published signals remain unclassified. The dated findings and subsequent method
reviews contain useful negative evidence, but do not qualify any of them for a
stronger planetary assessment.

## Axis 1: work performed

| Stage | Meaning |
|---|---|
| Queue | Search flagged a signal; the declared screening has not started. |
| Screening | Initial diagnostics are underway or some required results are missing. |
| Screened | All results in the dated initial screen are available, including warnings. |
| Source vetting | Pixel, neighbour and timing work has started; attribution can remain unresolved. |
| Physical vetting | Physical transit/binary/dilution scenarios have been attempted. |
| Follow-up | A documented observing programme or external follow-up is underway. |
| Validation | A documented statistical-validation assessment is underway. |
| Confirmation | Evidence for a documented confirmation assessment is being reviewed. |

Each stage separately records `not_started`, `partial`, `complete` or `blocked`.
The displayed stage is the furthest work started; it does not imply that earlier
stages passed. A successful execution can still yield unqualified science.
Source vetting is complete only after attribution is supported. A physical pilot
that fails sampling qualification is blocked, not evidence that the signal is false.

The current initial screen uses light-curve odd/even and secondary-phase probes,
binary/variable catalogue matches and exact-ID Gaia RUWE. Its nominal warning
triggers are uncalibrated. “Screened” means those results were collected, not that
the signal passed a complete fast planet-vetting suite.

## Axis 2: scientific assessment

| Assessment | Required interpretation |
|---|---|
| Unclassified | Transit-like detection whose physical explanation remains unresolved. |
| Candidate | A reviewed planetary hypothesis meeting a declared minimum vetting policy, including supported source and timing. More tests remain. |
| Likely planet | A reviewed candidate with qualified physical/scenario and reliability evidence strongly favouring a planet. The model, coverage, caveats and follow-up needs must be published. |
| False positive | Reviewed evidence supports a nonplanetary or instrumental explanation for this signal. Record the mechanism and decisive evidence. |
| Validated planet | Documented statistical validation that considers relevant false-positive scenarios and the possibility of a false alarm. Cite the validation study and its assumptions. |
| Confirmed planet | A documented planet confirmation with appropriate independent evidence and a cited publication/catalogue decision. |
| Known signal | Recovery of an already reported signal; its source's disposition remains separately attributed. |

Passing every implemented test is insufficient when important tests are missing.
An unavailable test is not a pass. A failed fit or incomplete catalogue is not a
false-positive classification. An elevated RUWE or nearby eclipsing binary is a
warning until its connection to the detected dips is established.

For `candidate` and stronger planetary classifications, the existing dossier
validator requires supported source localisation and timing consistency. A
stronger sidecar assessment must also agree with the dossier and cite a documented
classification review. This importer only publishes findings; it cannot promote
signals. All current records remain unclassified.

Confirmation is not the last box in an automated checklist. Statistical validation
can also establish a planet without a mass measurement, but requires a defensible
validation analysis. The NASA Exoplanet Archive distinguishes candidates, false
positives and confirmed/validated planets and requires adequate follow-up or
validation and published evidence for inclusion:
[archive criteria](https://exoplanetarchive.ipac.caltech.edu/docs/exoplanet_criteria.html),
[TOI dispositions](https://exoplanetarchive.ipac.caltech.edu/docs/API_TOI_columns.html).

TRICERATOPS's authors define method-specific FPP/NFPP criteria for likely and
validated planets. Those conditional astrophysical probabilities are not a total
probability that a search detection is a planet; false-alarm reliability must also
be assessed. We have not adopted a numeric likelihood tier or imported someone
else's rates. See [the method paper](https://arxiv.org/abs/2002.00691) and
[Eumemic's pipeline](https://github.com/eumemic/exoplanets).

## Warnings, shortlist and novelty

Warnings are flags, not a third scientific disposition. They can coexist with any
progress stage. Current flags include odd/even contrast, phase-half secondary,
uncorrected secondary-phase scan, catalogue binary matches, elevated RUWE,
attributed external adverse reports and reviewed off-target diagnostics.
Individual measurements and qualifications are in each dossier's
`evidence/vetting-findings.json`.

The dated **initial-screen** folders preserve the original mutually exclusive
groups: warnings, no initial warnings, and incomplete without an existing warning.
The **current warnings** folder additionally includes later source warnings and
external adverse reports. The views overlap and their counts must not be added.
A warning group can contain incomplete checks too.

Novelty stays independent: a previously reported signal can be promising, false,
or unresolved. The 16 external overlaps are attributed reports, not 16 automatic
rejections. Earlier dated no-match checks and original disclosure dates are retained.

For now, a useful candidate subdivision is the explicit work completed and open
requirements, rather than A/B/C scores or unsupported numerical odds. If we later
introduce ranked tiers, they need a versioned policy, a representative calibration
population and an independent evaluation set.

## Machine records and maintenance

`candidate.json` retains its declared 1.0–1.3 scientific contract. A separately
versioned `vetting.json` uses [vetting schema 1.0](../schemas/vetting-1.0.schema.json).
This avoids silently changing existing dossier semantics. `catalogue.json` remains
the scientific catalogue; [vetting-catalogue.json](../vetting-catalogue.json) joins
the new progress, assessment, warnings and provenance by stable signal ID.

Publish new dated findings with `scripts/record_vetting_findings.py`. It verifies
successful terminal input manifests, output hashes, cohort identities, adopted
periods and existing novelty before changing any dossier. The initial importer
refuses different findings for an existing snapshot; a later assessment needs an
explicitly reviewed versioned amendment. Preserve old assessments and evidence.

Run `uv run python scripts/catalogue.py build` to regenerate browsing views and
`uv run python scripts/catalogue.py check` to detect stale indexes, changed evidence,
missing-check passes or inconsistent classifications. Validation never pushes or
creates releases. Neither browse folders nor queue entries confer an official TOI.
