# Result — acoustic-IMGL0400

## Scope

This result records the first end-to-end verified development trace in Experiment 001.

It describes one Lightroom Classic 15.5.1 catalog fixture and is an experimental observation of that implementation, not a Core semantic contract.

## Identity trace

- fixture: `acoustic-IMGL0400`
- RAW: `IMGL0400.CR2`
- RAW SHA-256: `45e317daeb6b238055aca7a5e5f27caa849315c870f3a86bb85a053666af4afe`
- JPEG: `260923_191504_IMGL0400.jpg`
- JPEG SHA-256: `be83738fcdaec78cd65ee5b66d024a1479db4a694406bc4f2ee8c15de7982341`
- catalog: `_20260923_Acoustic ANGA feat.手話.lrcat`
- AgLibraryFile.id_local: 5476
- Adobe_images.id_local: 819
- Adobe_imageDevelopSettings.id_local: 5509

## Verified history payload encoding

For the tested history rows, `Adobe_libraryImageDevelopHistoryStep.text` is a BLOB with:

1. a four-byte big-endian declared uncompressed length;
2. a zlib stream beginning immediately after the four-byte prefix.

All tested rows decompressed successfully and the declared length matched the actual decompressed payload length.

Observed examples:

| History row | Event | Compressed bytes | Declared/actual decoded bytes |
| --- | --- | ---: | ---: |
| 5515 | Import | 1030 | 2646 |
| 19012 | Preset: `_Fundamental` | 1212 | 3765 |
| 22040 | Sync settings | 1348 | 4094 |
| 25154 | Sync settings | 1278 | 3231 |
| 29810 | Export to disk | 1278 | 3231 |

The last sync and export payloads decode to the same inspected development values, so the export event is a strong reference for the settings used to produce the JPEG.

## Development state at `_Fundamental`

The decoded preset-history state contains:

| Parameter | Value |
| --- | ---: |
| Exposure2012 | +0.50 |
| Highlights2012 | -70 |
| Shadows2012 | +70 |
| Whites2012 | 0 |
| Blacks2012 | 0 |
| Contrast2012 | 0 |
| Vibrance | +20 |
| Saturation | 0 |
| Texture | 0 |
| Clarity2012 | 0 |
| Dehaze | 0 |
| Temperature | 4400 |
| Tint | +1 |

The preset itself is known not to explicitly define Temperature/Tint. Therefore the history snapshot must be treated as the complete post-preset develop state, not as a literal list of only values written by the preset.

## Development state at export

The decoded export-history state contains:

| Parameter | Value |
| --- | ---: |
| Exposure2012 | +1.50 |
| Highlights2012 | -70 |
| Shadows2012 | +70 |
| Whites2012 | 0 |
| Blacks2012 | 0 |
| Contrast2012 | 0 |
| Vibrance | +20 |
| Saturation | 0 |
| Temperature | 2700 |
| Tint | 0 |
| CropAngle | -3.01 |
| CropLeft | 0.020308 |
| CropRight | 0.979692 |
| CropTop | 0.073108 |
| CropBottom | 0.926892 |
| CropConstrainAspectRatio | true |

Catalog develop dimensions are 6237 x 4158, exactly matching the JPEG fixture dimensions.

## Baseline-relative human decision

For the inspected parameters, the human development change from the `_Fundamental` post-preset state to the exported state is:

| Dimension | Baseline | Export | Delta / change |
| --- | ---: | ---: | --- |
| Exposure2012 | +0.50 | +1.50 | **+1.00 EV** |
| Temperature | 4400 | 2700 | **-1700 K** |
| Tint | +1 | 0 | **-1** |
| Highlights2012 | -70 | -70 | unchanged |
| Shadows2012 | +70 | +70 | unchanged |
| Whites2012 | 0 | 0 | unchanged |
| Blacks2012 | 0 | 0 | unchanged |
| Contrast2012 | 0 | 0 | unchanged |
| Vibrance | +20 | +20 | unchanged |
| Saturation | 0 | 0 | unchanged |
| Crop | none observed in selected baseline fields | explicit crop | added |
| CropAngle | none observed in selected baseline fields | -3.01 | added |

This is the first concrete Experiment 001 Human Development Decision reference.

It is not a universal correct development. It is the recorded human decision that produced this fixture's exported result.

## Consequence for RDA

The experiment now has one real example of:

```text
RAW Source Artifact
  -> _Fundamental Development Context
  -> post-preset state
  -> human development change
  -> export-time development state
  -> JPEG Rendered Result
```

This is enough to begin testing whether candidate RAW observations can explain a baseline-relative exposure decision.

Before promoting any RAW measurement definition, the same extraction should be automated across the remaining catalog-matched fixtures.
