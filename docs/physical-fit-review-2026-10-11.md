# Conditional physical-fit review — 11 October 2026

Supplement version **1.0.0**. This adds results for two already published signals;
it leaves their historical dossier versions, first disclosures, warnings and
unclassified assessments intact. It is not a new-candidate or planet announcement.

[Recorded results, units, conditional quantiles, covariance and receipt hashes](../reviews/physical-fit-review-2026-10-11-v1.json).

| Signal | Retained steps per independent ensemble | Retained draws | Original sampling checks | Scientific assessment |
|---|---:|---:|---|---|
| [TIC 261119502](../candidates/tic-261119502-s01/README.md) | 10,000 | 640,000 | Passed | Unclassified; prior report and adverse evidence retained |
| [TIC 339451799](../candidates/tic-339451799-s01/README.md) | 10,250 | 656,000 | Passed | Unclassified; odd/even warning retained; model concerns below |

The initial physical pilot was sampling-unqualified. These extensions retain its
data, priors, noise and geometry, adding sampling effort. Qualification still uses
50 estimated autocorrelation times, independent-ensemble agreement and the original
acceptance limits. The first extension uses a newly declared random stream because
the original random state was not saved; later checkpoints preserve exact state.
Each completed history was reconstructed exactly, including its original samples.
For each signal, 319 saved likelihoods replayed with zero differences. Geometry was
derived for all retained draws and checked against the model on that subset.
These integrity checks do not establish that the physical hypothesis is adequate.

## TIC 339451799: sampling checks can pass while the model remains strained

Under the assumed catalogue host, circular orbit and white-noise model, the median
log10 stellar density is **1.9293**, compared with the catalogue-based prior centre
**0.3090** (density in g/cm³ before taking log10). The conditional fitted density
is about **42 times** the prior centre. The difference spans **16.2 declared prior
widths**; that is a model-tension diagnostic, not a calibrated rejection significance.

**99.96%** of retained limb-darkening q1 draws lie in the declared lower boundary
region (the lowest 2% of its allowed range). Longer sampling therefore did not
remove the earlier density/limb-darkening concerns.

Exposure integration also needs scrutiny. Across nine fixed retained vectors,
the largest absolute log-likelihood changes were **8.85** for quadrature factor
7→21, **2.29** for 21→63, and **0.53** for 63→127. These comparisons neither refit
the model nor reweight its posterior. The original factor-7 summaries should not
be treated as a numerically settled physical inference.

An incorrect host, inadequate orbital/noise/shape assumptions, photometric or
timing effects, and a nonplanetary explanation remain possibilities. This review
does not establish which applies. The odd/even warning stays in place; no
false-positive classification or planetary promotion follows automatically.

## TIC 261119502: sampling improved; adverse source evidence remains

The white-noise model passes the same sampling and integrity checks. This does
not resolve its attributed external adverse report or the uncorrected secondary-
phase warning. It remains previously reported and is not a novel qualifier.
The other physical/noise scenarios and source attribution require further work.

## Scope and reproducibility

The JSON supplies conditional radius ratio, impact parameter, a/Rstar and timing
covariance with explicit assumptions and units. These are parameters of a dark-
occultor hypothesis, not verified planetary properties. No absolute planet radius
or planet probability is assigned. Conditional intervals are not calibrated total
uncertainties, and a shared fitted ephemeris does not prove timing consistency.

The supplement is **evidence inspection only**: readers can inspect recorded values
and hashes, but a public numerical reproduction capsule for these fits is not
yet available. Source attribution, correlated-noise calibration, astrophysical
alternatives/FPP/NFPP, full-search reliability and scientific review remain open.
The dated initial-screen census and browsing counts are unchanged.
