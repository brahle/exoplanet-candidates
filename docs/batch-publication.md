# Provisional batch disclosure

The verifier separates a useful provisional signal record from the stronger `planet_candidate`
classification. Unresolved source, clock, physical-model, noise or reliability checks belong
in the preliminary dossier. They do not indefinitely prevent evidence disclosure.

`scripts/export_batch.py` accepts a sealed whole-batch report, fresh MCP receipts and dated
direct-catalogue screens. It checks scientific artifact hashes and exact ephemeris/position
agreement with the catalogue request. It records every batch outcome. Its disclosed record
selection requires an adopted diagnostic ephemeris, positive aggregate dips under both saved
baseline orders, usable events in at least two sectors and positive sector-leaveout depths.
This is a record-selection rule, not a calibrated detection threshold or planet classifier.
Match hypotheses are retained outside the no-match provisional dossier set. Failed fits,
insufficient coverage and nonpositive results remain distinct ledger outcomes.

The exporter creates one stable-ID dossier per selected signal. It retains discovery seeds,
conditional covariance, signed event/timing/alternative diagnostics, failed checks, catalogue
coverage and exact native product hashes. Missing Gaia DR3 associations and duration errors
are null. The validator permits missing duration/depth errors only for unclassified signals
with explicit limitations; epoch and period covariance are still mandatory.

```bash
uv run python scripts/export_batch.py \
  --report /path/to/sealed-batch/report.json \
  --checks /path/to/fresh-mcp-checks.jsonl \
  --screen /path/to/direct-screen/hypotheses.jsonl \
  --screen /path/to/another-direct-screen/hypotheses.jsonl \
  --reviews /path/to/assessment-bound/reviews.json \
  --destination /path/to/staging --batch campaign-name
```

No candidate IDs are hard-coded. Another compatible batch can use this command without code
edits. Existing dossiers cannot be overwritten; a revised publication requires a deliberate
versioned update. Export does not publish, set disclosure timestamps or certify numerical
reproduction. Review the provisional evidence, validate the whole catalogue, then publish
the deliberately selected dossier set and retain a server-observed disclosure receipt.

Before export, record decisions in the scientific repository:

```bash
uv run transit-search vet review --report /path/to/sealed-batch/report.json \
  --selections /path/to/review-selections.json --registry /path/to/reviews.sqlite \
  --reviewer 'Codex automated evidence review' --review-type automated
```

The selection file is a JSON array of `signal_id`, exact `assessment_sha256`, `disposition`
and `reason`. The command verifies every assessment and artifact seal before committing the
append-only review transaction. Exact repeated delivery reuses its original timestamp. Changed
science, stale artifacts and unknown selections fail; an automated review cannot promote a
planet candidate. Human review and supported scientific gates are required for that stronger
tier. The provisional exporter requires matching unclassified reviews for every batch row.

The public release helper accepts any compatible batch and does not publish:

```bash
uv run python scripts/batch_release.py prepare --root . --batch campaign-name \
  --tag campaign-v0.1.0 --output /path/to/new-assets
```

It packages clean committed source, conserving the entire ledger and binding selected signal
versions to their reviews, original assessment hashes and evidence manifests. Zero selected
records retain the ledger without manufacturing a release. It refuses overwriting assets.
After the deliberate public push, record the sampled server timestamp immediately:

```bash
uv run python scripts/batch_release.py record-disclosure --root . --batch campaign-name \
  --repo owner/repository --commit FIRST_PUBLIC_COMMIT --previous-public-commit PREVIOUS_COMMIT
```

Use `none` only for a new repository with no previous public commit. This checks the actual
public branch and prior record presence; it preserves previously recorded first disclosures.
Commit the receipt, prepare assets from that source and attach/check them in a draft before
publishing an immutable release. Publishing is an explicit GitHub action outside this helper.

Download the draft assets separately and run `batch_release.py inspect-assets --archive FILE
--manifest release-manifest.json --expected-sha256 EXPECTED --certificate draft-check.json`
before publication. This checks their full record/manifest contents, not only upload completion.

```bash
uv run python scripts/batch_release.py verify-public --repo owner/repository \
  --tag campaign-v0.1.0 --expected-sha256 EXPECTED_ARCHIVE_SHA256 \
  --certificate /path/to/public-evidence-certificate.json
uv run python scripts/batch_release.py record-release --root . --batch campaign-name \
  --repo owner/repository --tag campaign-v0.1.0 \
  --certificate /path/to/public-evidence-certificate.json
```

The verifier retrieves without authentication, checks actual immutable release/source metadata,
archive safety, checksums, every listed signal and complete dossier validation. It installs the
frozen dependency environment and runs inspection/tests in a fresh directory (offline package
cache required). It verifies older evidence-only releases too. This is **public evidence
inspection**, not a numerical rerun. Receipt recording checks current science against the locked
release, preserves first-disclosure time and appends the actual release time separately.
Repeated delivery does not create extra versions. Updated scientific inference needs a new
assessment/review/export/release; this metadata helper cannot silently attach it to an old release.

## Bounded batch packages (format v2)

`prepare` now defaults to `--format batch-evidence-v2`. It packages the selected dossiers,
the complete batch ledger and exact reviews, all batch snapshots, validation scripts/schemas,
frozen dependencies and tests. Explicit repository-file references in scientific JSON close
over shared snapshots, including snapshots stored in another batch. Missing, uncommitted or
hash-mismatched dependencies fail preparation. Scientific dossier bytes are copied from the
pinned Git commit.

The tests currently use three earlier dossiers, declared in `tests/fixture-dossiers.json`.
These unchanged test dependencies are listed separately as `support_records` with role
`validation_test_fixture`; they are not additional scientific selections. The manifest
separates `new_signal_count`, `packaged_dossier_count` (also `total_dossiers`) and
`source_catalogue_count`. Undeclared extra dossier identities are rejected.

`source_files` binds each copied file to its original repository path and SHA256. Original
source catalogue/README metadata is retained under `package-provenance/`. `derived_files`
separately binds the package README, subset catalogue/browse/gallery and scope metadata.
The extracted catalogue describes the packaged subset, not the entire source repository.
Scientific files cannot be relabelled as derived views. Unlisted files, stale hashes,
changed selections or inconsistent source/packaged counts fail inspection.

Both compressed assets and extraction retain the existing 2 GiB bounds, and extraction
retains the 100,000-member bound. Preparation checks the uncompressed size before compression;
inspection rejects traversal, duplicate members, links and special files before extraction.
A batch that exceeds these limits requires a separately designed multipart format; these
limits are not silently enlarged.

Earlier unversioned whole-repository releases remain readable as format v1.
`--format whole-repository-v1` is available for compatibility and obeys the same size bounds.
The release helpers still never publish automatically. Draft inspection, immutable publication,
anonymous public download/frozen-environment checks and timestamp receipts remain separate
steps. A passed package certificate establishes evidence integrity, not a numerical rerun,
physical host attribution or planetary validation.
