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
  --destination /path/to/staging --batch campaign-name
```

No candidate IDs are hard-coded. Another compatible batch can use this command without code
edits. Existing dossiers cannot be overwritten; a revised publication requires a deliberate
versioned update. Export does not publish, set disclosure timestamps or certify numerical
reproduction. Review the provisional evidence, validate the whole catalogue, then publish
the deliberately selected dossier set and retain a server-observed disclosure receipt.
