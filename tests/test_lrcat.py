import pathlib
import sqlite3
import struct
import zlib

from rda_toolchain.lrcat import (
    decode_history_blob,
    extract_selected_settings,
    trace_lrcat_file,
)


def _history_blob(text: str) -> bytes:
    payload = text.encode("utf-8")
    return struct.pack(">I", len(payload)) + zlib.compress(payload)


def test_decode_history_blob_checks_declared_length():
    text = 's = { Exposure2012 = 0.5, }'
    blob = _history_blob(text)
    assert decode_history_blob(blob) == text.encode("utf-8")


def test_extract_selected_settings_preserves_duplicate_occurrences():
    result = extract_selected_settings(
        """
        Exposure2012 = 0.5,
        Exposure2012 = 0.5,
        Temperature = 4400,
        CropConstrainAspectRatio = true,
        """
    )
    assert result["Exposure2012"]["value"] == 0.5
    assert result["Exposure2012"]["occurrences"] == [0.5, 0.5]
    assert result["Temperature"]["value"] == 4400
    assert result["CropConstrainAspectRatio"]["value"] is True


def test_trace_lrcat_file_recovers_baseline_export_delta(tmp_path: pathlib.Path):
    db = tmp_path / "catalog.lrcat"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE AgLibraryFile (
          id_local INTEGER PRIMARY KEY,
          id_global,
          baseName,
          extension,
          originalFilename,
          folder,
          md5
        );
        CREATE TABLE Adobe_images (
          id_local INTEGER PRIMARY KEY,
          id_global,
          rootFile,
          developSettingsIDCache,
          masterImage,
          fileFormat,
          fileWidth,
          fileHeight,
          orientation,
          captureTime,
          originalCaptureTime,
          copyName,
          copyReason
        );
        CREATE TABLE Adobe_imageDevelopSettings (
          id_local INTEGER PRIMARY KEY,
          image,
          processVersion,
          whiteBalance,
          fileWidth,
          fileHeight,
          croppedWidth,
          croppedHeight,
          settingsID,
          historySettingsID,
          beforeSettingsIDCache,
          snapshotID,
          hasDevelopAdjustments,
          hasDevelopAdjustmentsEx,
          hasMasks,
          hasAIMasks,
          hasRetouch,
          hasLensBlur,
          profileCorrections,
          removeChromaticAberration,
          text
        );
        CREATE TABLE Adobe_libraryImageDevelopHistoryStep (
          id_local INTEGER PRIMARY KEY,
          dateCreated,
          name,
          digest,
          hasBigData,
          hasDevelopAdjustments,
          image,
          text
        );
        """
    )
    conn.execute(
        "INSERT INTO AgLibraryFile VALUES (1, 'f', 'IMGL0400', 'CR2', 'IMGL0400.CR2', 0, NULL)"
    )
    conn.execute(
        "INSERT INTO Adobe_images VALUES (2, 'i', 1, 3, NULL, 'RAW', 6720, 4480, 'AB', NULL, NULL, NULL, NULL)"
    )
    final = """
    Exposure2012 = 1.5,
    Temperature = 2700,
    Tint = 0,
    CropAngle = -3.01,
    """
    conn.execute(
        """
        INSERT INTO Adobe_imageDevelopSettings
        VALUES (3, 2, '15.4', 'Custom', 6720, 4480, 6237, 4158,
                NULL, 'hist', NULL, NULL, 1, NULL, 0, 0, NULL, 0, 1, 1, ?)
        """,
        (final,),
    )
    baseline = """
    Exposure2012 = 0.5,
    Temperature = 4400,
    Tint = 1,
    """
    conn.execute(
        "INSERT INTO Adobe_libraryImageDevelopHistoryStep VALUES (10, 1, 'Preset: _Fundamental', NULL, 0, 1, 2, ?)",
        (_history_blob(baseline),),
    )
    conn.execute(
        "INSERT INTO Adobe_libraryImageDevelopHistoryStep VALUES (11, 2, 'Export to disk', NULL, 0, 1, 2, ?)",
        (_history_blob(final),),
    )
    conn.commit()
    conn.close()

    result = trace_lrcat_file(db, ag_library_file_id=1, expected_basename="IMGL0400")
    image = result["images"][0]
    delta = image["baseline_relative_selected_delta"]

    assert image["selection"]["baseline_history_id_local"] == 10
    assert image["selection"]["export_history_id_local"] == 11
    assert delta["Exposure2012"]["delta"] == 1.0
    assert delta["Temperature"]["delta"] == -1700
    assert delta["Tint"]["delta"] == -1
