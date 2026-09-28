# LRCAT schema notes — Experiment 001

## Confirmed tables

The Lightroom Classic 15.5.1 catalogs used in Experiment 001 expose these relevant tables:

- `AgLibraryFile`
- `Adobe_images`
- `Adobe_imageDevelopSettings`
- `Adobe_libraryImageDevelopHistoryStep`

## Observed key fields

### AgLibraryFile

- `id_local` — primary key
- `baseName`
- `extension`
- `originalFilename`
- `folder`
- `md5`

### Adobe_images

- `id_local` — primary key
- `rootFile`
- `developSettingsIDCache`
- `masterImage`
- `fileFormat`
- `fileWidth`
- `fileHeight`
- `orientation`
- `captureTime`
- `originalCaptureTime`

### Adobe_imageDevelopSettings

- `id_local` — primary key
- `image`
- `settingsID`
- `historySettingsID`
- `beforeSettingsIDCache`
- `processVersion`
- `whiteBalance`
- `croppedWidth`
- `croppedHeight`
- `hasDevelopAdjustments`
- `hasMasks`
- `hasAIMasks`
- `text`

### Adobe_libraryImageDevelopHistoryStep

- `id_local` — primary key
- `image`
- `dateCreated`
- `name`
- `relValueString`
- `valueString`
- `text`
- `digest`

## Candidate relations to verify from data

The schema strongly suggests, but does not by itself prove, these relations:

- `Adobe_images.rootFile -> AgLibraryFile.id_local`
- `Adobe_imageDevelopSettings.image -> Adobe_images.id_local`
- `Adobe_images.developSettingsIDCache -> Adobe_imageDevelopSettings.id_local`
- `Adobe_libraryImageDevelopHistoryStep.image -> Adobe_images.id_local`

Experiment 001 MUST verify these relationships using actual fixture rows before treating them as catalog semantics.

## Research significance

If the candidate relations are confirmed, one fixture can be traced as:

```text
AgLibraryFile
  -> Adobe_images
      -> Adobe_imageDevelopSettings
      -> Adobe_libraryImageDevelopHistoryStep
```

This would allow RDA to distinguish:

- file/source identity;
- current image/develop state;
- current Lightroom development settings;
- historical human editing steps.

The history table is particularly important because it may allow the research dataset to preserve the sequence of human development decisions rather than only the final state.


## Verified relation trace: IMGL0400

Fixture `acoustic-IMGL0400` verified the candidate joins with real data:

- `AgLibraryFile.id_local = 5476`
- `Adobe_images.rootFile = 5476`
- `Adobe_images.id_local = 819`
- `Adobe_images.developSettingsIDCache = 5509`
- `Adobe_imageDevelopSettings.id_local = 5509`
- `Adobe_imageDevelopSettings.image = 819`
- `Adobe_libraryImageDevelopHistoryStep.image = 819`

Therefore, for this Lightroom Classic 15.5.1 fixture, the working relation is:

```text
AgLibraryFile.id_local
  <- Adobe_images.rootFile
Adobe_images.id_local
  <- Adobe_imageDevelopSettings.image
Adobe_images.developSettingsIDCache
  -> Adobe_imageDevelopSettings.id_local
Adobe_images.id_local
  <- Adobe_libraryImageDevelopHistoryStep.image
```

### Development state findings

For `IMGL0400.CR2`:

- RAW dimensions: 6720 x 4480.
- current develop row process version: 15.4.
- white balance mode: `Custom`.
- developed crop dimensions: 6237 x 4158.
- the exported JPEG fixture is also 6237 x 4158, providing strong evidence that this develop state corresponds spatially to the exported result.
- current settings text length: 3201 bytes/characters as reported by SQLite `length()`.
- the serialized current settings include `AutoLateralCA = 1`, `Blacks2012 = 0`, `CameraProfile = "Adobe Standard"`, `ColorNoiseReduction = 10`, `ColorNoiseReductionSmoothness = 90`, and `Contrast2012 = 0`.

### Human history findings

The develop history for the same image includes, in order:

1. import;
2. preset `_Fundamental`;
3. synchronized settings;
4. synchronized settings;
5. export to disk.

This is strong evidence that Experiment 001 can recover not only a final human development state but also the sequence of Lightroom history events that produced it.

The serialized history-step payloads still need to be extracted in full before individual decision deltas are interpreted.


## Lightroom history payload encoding finding

Experiment 001 found that `Adobe_libraryImageDevelopHistoryStep.text` is stored as a BLOB for the tested Lightroom Classic 15.5.1 catalog.

Observed payload form:

- first 4 bytes: big-endian integer matching the apparent uncompressed payload length;
- remaining bytes begin with `78 9C`, consistent with a zlib stream;
- `valueString` and `relValueString` are NULL for the tested history rows.

Examples:

- history row 19012 (`Preset: _Fundamental`) begins `00 00 0E B5 78 9C ...`;
- history row 22040 begins `00 00 0F FE 78 9C ...`;
- rows 25154 and 29810 expose the same prefix and compressed payload bytes in the inspected output, suggesting the export history event may preserve the same develop state as the immediately preceding synchronized-settings event.

This encoding is an implementation detail of the tested catalog, not an RDA semantic contract. The experiment should decode it through a catalog adapter and preserve the raw payload/digest for auditability.
