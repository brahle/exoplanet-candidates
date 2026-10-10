# Publication workflow

Publish a useful, dated scientific record: the signal specification, the supporting and adverse
evidence, the exact work that can be repeated, and its author. This creates an attributable
record of a detection and assessment. It does not reserve ownership of an astronomical object
or demonstrate that no earlier report exists. Record independent recovery honestly when a
previous report is found, including after publication.

## The unit of publication

Use one directory per signal: `candidates/tic-<TIC>-s<NN>/`. A signal ID stays stable when its
period is refined, its host is questioned or its disposition changes. Check target aliases,
proper-motion-corrected positions, periods, integer harmonics and epochs before assigning a
new ID. Never assign a lowercase planet letter to an unconfirmed object.

| File | Purpose |
|---|---|
| `candidate.json` | Authoritative structured identity, ephemeris, uncertainties, assessments, provenance and publication metadata |
| `README.md` | Concise scientific report, strongest evidence and principal limitations |
| `NOVELTY.md` | Dated catalogue/literature checks, matching logic, prior reports and unresolved checks |
| `REPRODUCIBILITY.md` | What readers can actually reproduce, commands and missing dependencies |
| `inputs.json` | Mission product identifiers, reduction/exposure/time conventions and exact hashes |
| `analysis-settings.json` | Scientific choices, quality cuts, declared sensitivity matrix and random seeds |
| `evidence/` | Modest-sized plots, JSON results, event tables and negative diagnostics |
| `evidence-manifest.json` | Every dossier file's SHA256, size and export provenance |

Keep raw FITS and larger numerical arrays out of Git. Package them as per-candidate release
assets with manifests and public download URLs. Include exact TESScut bytes: fresh cutout
requests can change headers/checksums even if the scientific samples match. GitHub release
assets support individual files below 2 GiB ([release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)).

## Assessments and evidence

Source localisation and timing consistency each have a separate status: **supported**,
**contradicted** or **unresolved**, with a reason and evidence links. The astrophysical disposition
and novelty assessment are separate fields. A source/timing pass cannot automatically promote
the disposition to a planet. Failed fits, poor coverage and non-detections belong in the dossier.
Rejecting a signal is a publishable outcome; retain its identifier and previous versions.

Every specification must state units, time scale, epoch offset, model and uncertainty method.
Use the complete epoch–period covariance from the same error calculation as the displayed
uncertainties. For cycle n, `Var(Tn) = Var(T0) + 2 n Cov(T0,P) + n² Var(P)`.
Future observing times require correct barycentric-to-observer conversion; do not label
unconverted BJD_TDB predictions as UTC.

## Deliberate release sequence

1. Prepare the dossier locally. Preserve the original analysis and export only reviewed
   scientific content. Leave first-publication dates, release URL and DOI null while unpublished.
2. Check novelty against dated authoritative snapshots, using identifiers, coordinates, period,
   epoch and aliases. Recheck immediately before a novelty-sensitive release. Preserve query
   failures. A missing search result is not a novelty test.
3. Validate the schema, identity, time bookkeeping, covariance and artifact hashes. Review all
   report claims and plots against the pinned analysis. Validate public exports for private
   paths, infrastructure, credentials and unrelated personal metadata.
4. Prefer a complete public reproduction capsule: exact input bytes, selected analysis source,
   configuration, frozen dependencies, one command and output-comparison certificate. Re-run
   it from a clean environment that can access only public inputs. Until then label the release
   **evidence inspection only**; do not advertise end-to-end public reproducibility.
5. Commit the reviewed dossier. Publish a versioned candidate release such as
   `tic-464547401-s01-v0.1.0`. Enable [immutable releases](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes)
   before publishing; attach and check all assets in a draft first. GitHub locks the tag and
   assets, but the title/notes remain editable; put scientific claims in the locked files.
6. Record the actual first public disclosure from GitHub's server-visible publication history
   (the dossier commit may become public before the release). Store the release timestamp
   separately in the publication receipt. Detection dates and Git author dates are not substitutes.
   Commit a subsequent receipt if the timestamp cannot be known before the first push.
7. Deposit each candidate dossier/report and its data capsule as a versioned Zenodo record;
   use the version DOI for exact citations and link the all-versions DOI for the evolving dossier.
   See [Zenodo versions](https://help.zenodo.org/docs/deposit/manage-versions/).
   GitHub/Zenodo integration is also useful for the catalogue software, but verify which files
   were archived: do not assume separately uploaded GitHub assets are in the DOI deposit.
   A DOI establishes a citable record, not peer review or discovery priority.
8. Retrieve the public assets, verify their hashes and perform the documented public rerun.
   Append the release/DOI receipt and checks; correct errors with a new release. Never silently
   replace a published scientific file or rewrite an unfavourable classification.

Versioning is per signal: patch for corrections that do not change inference; minor for new
data/analysis; major for incompatible interpretation or record schema. Each published version
has a change description. Keep earlier releases available. Keep previously reported objects in
a separate recovery catalogue if they are useful benchmarks; do not mix them into a new-signal
claim. No wider target search is part of publication.

## Community reporting

[ExoFOP's current candidate guidelines](https://exofop.ipac.caltech.edu/tess/candidate_help.php)
require peer-reviewed online publication and approval before upload. They allow an RNAAS note
when it cites an already peer-reviewed detection/vetting methodology. A GitHub/Zenodo dossier
alone does not meet this publication requirement. Candidate upload is a separate future action;
no upload, external follow-up or journal submission is performed by this workflow.

TIC 464547401 was first publicly disclosed on 2026-10-10 as an evidence-only unclassified signal,
with source and timing both unresolved. Complete the public reproduction capsule before calling
a future release numerically reproducible. The `disclosed` state records a public Git snapshot;
the `published` state additionally requires a versioned release URL. Neither implies peer review.
