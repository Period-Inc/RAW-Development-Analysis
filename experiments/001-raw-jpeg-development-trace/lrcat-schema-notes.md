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
