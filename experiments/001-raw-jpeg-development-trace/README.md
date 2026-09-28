# Experiment 001 — RAW → Human Development → JPEG Trace

## Objective

Use real Lightroom Classic work as the first end-to-end research fixture for tracing:

```text
RAW Source Artifact
  -> Human Development Decision (Lightroom catalog)
  -> JPEG Rendered Result
```

This experiment is intentionally prior to defining stable RAW tone measurements.

The first goal is to prove that RDA can reliably identify the same photograph across:

- original RAW;
- Lightroom catalog record;
- exported JPEG;

and recover enough development provenance to compare source-side observations with a human development decision.

## Local workspace

The experiment uses a non-canonical local research workspace:

```text
/Users/agent/Documents/Temporary/RAW-Development-Analysis/
├── sources/
├── extracted/
├── runs/
└── cache/
```

The local workspace is disposable/reconstructable research working space. Git remains the canonical location for experiment protocol, source identities/digests, code, findings, and promoted semantic definitions.

Git documents MUST NOT treat this absolute local path as Source Artifact identity.

## Fixture corpus

`fixtures.yml` records 13 RAW/JPEG pairs across three Lightroom catalog candidates.

Current catalog grouping is **inferred from filenames/capture dates/project names** and is not yet authoritative.

The next step is to query each LRCAT and prove which catalog record resolves to each RAW/JPEG pair.

## Protocol

### Phase A — identity

For every pair:

1. verify RAW SHA-256;
2. verify JPEG SHA-256;
3. extract source metadata from RAW/JPEG;
4. identify the matching LRCAT image record;
5. record Lightroom internal identifiers/path references;
6. distinguish exact same-source identity from basename/date inference.

### Phase B — development decision recovery

From LRCAT, recover the development state applicable to the matching image.

Record:

- process version;
- develop settings/history representation available in the catalog;
- crop/orientation;
- white balance;
- exposure/tone controls;
- presence of local masks or other nontrivial edits;
- virtual-copy/snapshot state if relevant;
- whether the exported JPEG corresponds to the catalog's current develop state.

Do not assume that every Lightroom edit maps one-to-one to a simple XMP scalar.

### Phase C — rendered-result comparison

Record JPEG properties relevant to evaluation:

- dimensions;
- orientation;
- crop relative to RAW;
- embedded output profile / color metadata;
- export/render metadata where recoverable.

A JPEG is an Evaluation Reference / Rendered Result, not photographic truth.

### Phase D — RAW probe

Run the existing experimental RAW probe over all 13 RAW files.

The probe output belongs under local `runs/` or `extracted/`, while summarized findings and stable fixture metadata are committed to Git.

### Phase E — first comparison

Only after identity + Lightroom decision recovery are proven:

1. compare source-side RAW state with human development settings;
2. identify which decision dimensions vary materially;
3. select the first candidate RAW observations;
4. define those observations precisely;
5. re-run against the corpus.

## Important characteristics of this fixture set

The corpus is useful because it is not perfectly uniform.

It includes:

- Canon EOS 5D Mark IV rendered files;
- Canon EOS 5DS rendered files;
- landscape and portrait orientation;
- exported JPEGs at full and cropped dimensions;
- food/product photography;
- event/performance photography;
- multiple independent Lightroom catalogs.

This makes it suitable for finding bad assumptions early.

## Status

- RAW/JPEG file identity: captured by SHA-256.
- Pairing by basename/export name: strong candidate, not yet catalog-verified.
- LRCAT availability: confirmed for three catalog files.
- LRCAT SQLite readability: confirmed with immutable read-only access for all three fixture catalogs.
- Copied fixture directory contains no LRCAT WAL/SHM sidecars.
- LRCAT record matching: pending.
- Development decision extraction: pending.
- RAW decoder characterization: pending.

## Batch LRCAT extraction

After the fixture files are placed in the local workspace, the catalog-matched fixtures can be traced in one command:

`rda trace-lrcat-fixtures experiments/001-raw-jpeg-development-trace/fixtures.yml --workspace /Users/agent/Documents/Temporary/RAW-Development-Analysis --out /Users/agent/Documents/Temporary/RAW-Development-Analysis/extracted/experiment-001`

The command:

- verifies catalog, RAW, and JPEG SHA-256 values before analysis;
- resolves the already-verified `AgLibraryFile.id_local` rather than trusting basename as identity;
- verifies the expected basename as a guardrail;
- follows File -> Image -> current Develop Settings -> Develop History;
- decodes the tested Lightroom Classic history BLOB form;
- identifies the last `_Fundamental` history state;
- identifies the last export history state using the tested catalog's localized event name;
- extracts selected scalar development settings without pretending to fully parse Lightroom's internal payload language;
- computes baseline-relative deltas only for unambiguous scalar values;
- writes one JSON trace per fixture plus `summary.json`.

This is an experimental Lightroom catalog adapter. Lightroom table names, history BLOB encoding, and localized history labels are implementation observations, not Core RDA semantics.
