# Progressive batch publication

One registered intake batch maps to one immutable `batches/phase4-scaled-bNN/`
ledger. Stable signal IDs come from the survey registry; several signals may share
a TIC. Pipeline completion and scientific classification are separate.

`export_batch.py` accepts a sealed report with `terminal_outcomes`. Each row has a
unique `row_id`, an optional assigned `signal_id`, a route and provenance. The
routes allowed into an export are completed/reviewed, carried forward, identity
hold, intake hold and exhausted execution failure. Queued/running work and failed
catalogue calls hold the entire batch open. An empty numerical signal set is
valid for a ledger containing only holds or failures.

Successful assessments still require their exact attributed review and dated
catalogue receipts. A neighbour match remains a hypothesis; it does not prove a
false positive. Ledger-only holds, failures, prior-report hypotheses and unchanged
carried-forward assessments never need invented fit parameters or stage files.
The exported occurrence ledger keeps every input row, including rows without IDs.

For a new signal selected by the existing provisional disclosure rule, export
creates a draft dossier. For an existing ID on new inputs, it stages a reviewed
replacement in `batches/<batch>/amendments/<id>/`, records `amendment_pending`, and
leaves the current dossier untouched. An exact DB match to this repository's own
stable ID is retained as `previously_reported`; it does not suppress an amendment
or become a new discovery claim. Other match hypotheses remain in the ledger.
New adverse or inconclusive assessments of an existing dossier also stage an
amendment. They retain the prior dated measurements and their original evidence,
then add the new diagnostics and catalogue hypotheses in a separate evidence
section. They explicitly state that the old values are not new fit estimates.

Apply one staged amendment deliberately:

```sh
uv run python scripts/amend_signal.py --root . --batch phase4-scaled-b001 --signal-id tic-123-s01
uv run python scripts/catalogue.py build
uv run python scripts/catalogue.py check
uv run python -m unittest discover -s tests
```

The command checks the old and staged seals, preserves the stable directory and
first public date, archives every prior byte including the prior manifest,
appends history and increments the minor analysis version. A separate immutable
amendment receipt binds the old and new manifests. A partially interrupted swap
is retained for recovery and blocks another application.

First disclosure belongs to the signal identity. The local new version remains
pending release: an earlier version's release URL and DOI are archived, not
presented as the new version's release. A previously public identity retains its
disclosure URL/date; a wholly unpublished identity remains a draft. Release
packaging refuses unapplied amendments and validates assessment/review binding.
`record-release` records the actual subsequent versioned release as before.

Follow-up cohorts with signal IDs are keyed by those IDs, allowing s01 and s02 on
one target. Legacy TIC-only cohorts retain their original uniqueness check. A
mixed cohort with missing signal IDs is refused. No ID is inferred from row order.

All preparation, amendment, validation and code commits stay in a local checkout.
A push of this public repository discloses its contents and requires owner release.
Neither export nor amendment invokes Git/network publication.

`tests/test_progressive_publication.py` exercises one seven-row acceptance batch:
new-input s01 amendment, carried-forward assessment, new s02 on the same TIC,
identity hold, intake hold, exhausted failure and external known-report hypothesis.
It checks conservation, byte preservation, first disclosure, schema/index validity
and release selection, as well as refusal of non-terminal batches.
