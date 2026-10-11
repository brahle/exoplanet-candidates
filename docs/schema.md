# Dossier schema versions

`schema_version` describes the data contract. The per-signal `version` describes a
particular dossier revision. Evidence manifests and other artifacts have their own
formats; their version numbers do not select the candidate contract.

| Contract | Meaning |
|---|---|
| [1.0](../schemas/candidate-1.0.schema.json) | Gaia DR3 ID is a decimal string; every measurement has a positive numerical error. Preserves the pre-run-5 contract. |
| [1.1](../schemas/candidate-1.1.schema.json) | Gaia DR3 ID may be null when an association has not been established. Duration/depth errors may be null only for unclassified signals with an explicit unavailable-uncertainty limit. Epoch and period errors remain positive and numerical. |

[candidate.schema.json](../schemas/candidate.schema.json) dispatches to either known
version. The repository validator resolves these references from checked-in files
without network requests. Consumers can validate against the single versioned file
matching a record's `schema_version`, or download all three files together and use
the dispatcher. Reject unknown versions rather than substituting a current schema.

The 171 run-5 records originally changed null semantics while incorrectly claiming
`1.0`. This was a publication compatibility error. Their corrected live dossiers use
`1.1`, with a patch revision and history entry; the original TIC 464547401 dossier
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
