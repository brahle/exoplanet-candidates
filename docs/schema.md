# Dossier schema versions

[Schema1.3](../schemas/candidate-1.3.schema.json) adds full conditional trapezoid
shape covariance after an exact numerical fit replay. Its duration errors have
explicit model and noise limits; physical transit geometry is marked unfitted.
See [shape uncertainty](shape-uncertainty.md). Earlier contracts remain unchanged.

`schema_version` describes the data contract. The per-signal `version` describes a
particular dossier revision. Evidence manifests and other artifacts have their own
formats; their version numbers do not select the candidate contract.

| Contract | Meaning |
|---|---|
| [1.0](../schemas/candidate-1.0.schema.json) | Gaia DR3 ID is a decimal string; every measurement has a positive numerical error. Preserves the pre-run-5 contract. |
| [1.1](../schemas/candidate-1.1.schema.json) | Gaia DR3 ID may be null when an association has not been established. Duration/depth errors may be null only for unclassified signals with an explicit unavailable-uncertainty limit. Epoch and period errors remain positive and numerical. |
| [1.2](../schemas/candidate-1.2.schema.json) | Adds a pinned target catalogue association and host context. Stellar parameters explicitly belong to the catalogue aperture target; the physical host and dilution remain unresolved. Preserves the 1.1 shape/ephemeris semantics. |

[candidate.schema.json](../schemas/candidate.schema.json) dispatches to either known
version. The repository validator resolves these references from checked-in files
without network requests. Consumers can validate against the single versioned file
matching a record's `schema_version`, or download the dispatcher and every versioned
file together. Reject unknown versions rather than substituting a current schema.

The 171 run-5 records originally changed null semantics while incorrectly claiming
`1.0`. This was a publication compatibility error. Their corrected live dossiers use
`1.1`, with a patch revision and history entry; subsequent catalogue enrichment uses
`1.2` with a minor dossier revision. The original TIC 464547401 dossier
continues using strict `1.0`. No scientific values, uncertainties, assessments or
first-disclosure timestamps change in this correction. The machine catalogue now
also carries each record's `schema_version` for ingestion routing.

The immutable `run5-v0.1.0` asset and old Git snapshots preserve the original error.
Consumers pinned to commit `180e82d` must update to the correction commit or a later
revision to obtain correctly labelled records. Do not silently redefine the legacy
1.0 contract to accept those old nulls. The batch's live publication receipt still
identifies its original evidence release; the schema correction is a subsequent
Git revision, not a replacement of its locked asset.

Any future change to field meanings or allowed values must introduce a new versioned
contract, document its migration and update the exporter and affected dossiers in
the same change. Regression tests keep both previously published versions usable.

In 1.2, `host.parameters` contains `teff_K`, `radius_Rsun`, `mass_Msun`, `tmag`
and `distance_pc`. Each value has units, catalogue field names, symmetric and
asymmetric errors, uncertainty method and missing/invalid status. Null errors do
not mean zero error. `host.parameter_scope = catalogue_aperture_target` and
`host.status = unresolved` prohibit treating these values as a verified-host
posterior. `host.dilution.target_flux_fraction` is null. No planet radius is
computed. `evidence/stellar-catalogue.json` records the raw selected TIC row,
all Gaia neighbourhood alternatives, queries, UTC retrieval, configuration and
response hashes. The complete raw batch responses accompany the batch.

## Vetting schema 1.1

Run-6 vetting records use `vetting-1.1.schema.json`. Version 1.0 remains unchanged.
Version 1.1 adds descriptive flags for weak timing-qualified-sector dips, the
13-day period cluster, conditional odd/even sensitivity, an uncorrected secondary
scan, imprecise early-only predictions and missing saved pixel competitors.
These flags are warnings, never calibrated probabilities or automatic rejection.
The generated vetting catalogue uses wrapper version 1.1 when it contains 1.1
records; individual records retain their own schema version.

All 14 new candidate records use candidate schema 1.3 with catalogue aperture
parameters and exact-replay conditional duration/ingress covariance. The physical
host and transit geometry remain unresolved.
