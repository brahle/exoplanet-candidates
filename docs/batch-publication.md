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
