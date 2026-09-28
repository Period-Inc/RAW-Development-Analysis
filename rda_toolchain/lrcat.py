from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sqlite3
import struct
import zlib
from typing import Any

import yaml


SELECTED_DEVELOP_KEYS = (
    "Exposure2012",
    "Highlights2012",
    "Shadows2012",
    "Whites2012",
    "Blacks2012",
    "Contrast2012",
    "Temperature",
    "Tint",
    "Vibrance",
    "Saturation",
    "Texture",
    "Clarity2012",
    "Dehaze",
    "CropAngle",
    "CropLeft",
    "CropRight",
    "CropTop",
    "CropBottom",
    "CropConstrainAspectRatio",
)

_SETTING_LINE = re.compile(
    r'^\\s*([A-Za-z][A-Za-z0-9_]*)\\s*=\\s*(.+?),?\\s*$'
)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_history_blob(blob: bytes) -> bytes:
    """Decode the tested Lightroom Classic 15.5.1 history BLOB form.

    This is an experimental catalog-adapter behavior, not an RDA Core
    serialization contract.
    """

    if len(blob) < 6:
        raise ValueError("history blob is too short")

    declared_length = struct.unpack(">I", blob[:4])[0]
    payload = zlib.decompress(blob[4:])
    if len(payload) != declared_length:
        raise ValueError(
            f"history blob length mismatch: declared={declared_length} actual={len(payload)}"
        )
    return payload


def _scalar(value: str) -> Any:
    value = value.strip()
    if value.endswith(","):
        value = value[:-1].rstrip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "nil":
        return None
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    try:
        if any(ch in value for ch in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        return value


def extract_selected_settings(text: str) -> dict[str, dict[str, Any]]:
    """Extract scalar occurrences without pretending to parse Lightroom's Lua-like payload.

    Duplicate occurrences are preserved. A normalized value is emitted only when
    all observed occurrences agree.
    """

    wanted = set(SELECTED_DEVELOP_KEYS)
    occurrences: dict[str, list[Any]] = {key: [] for key in SELECTED_DEVELOP_KEYS}

    for line in text.splitlines():
        match = _SETTING_LINE.match(line)
        if not match:
            continue
        key, raw_value = match.groups()
        if key in wanted:
            occurrences[key].append(_scalar(raw_value))

    result: dict[str, dict[str, Any]] = {}
    for key, values in occurrences.items():
        if not values:
            continue
        unique: list[Any] = []
        for value in values:
            if value not in unique:
                unique.append(value)
        result[key] = {
            "occurrences": values,
            "value": unique[0] if len(unique) == 1 else None,
            "status": "known" if len(unique) == 1 else "ambiguous",
        }
    return result


def _settings_values(settings: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        key: item["value"]
        for key, item in settings.items()
        if item.get("status") == "known"
    }


def _delta(baseline: dict[str, Any], final: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    keys = sorted(set(baseline) | set(final))
    for key in keys:
        before = baseline.get(key)
        after = final.get(key)
        item: dict[str, Any] = {"baseline": before, "final": after}
        if isinstance(before, (int, float)) and not isinstance(before, bool) and isinstance(
            after, (int, float)
        ) and not isinstance(after, bool):
            item["delta"] = after - before
        elif before == after:
            item["change"] = "unchanged"
        elif before is None:
            item["change"] = "added_or_not_observed_in_baseline"
        elif after is None:
            item["change"] = "removed_or_not_observed_in_final"
        else:
            item["change"] = "changed"
        result[key] = item
    return result


def _connect_immutable(path: pathlib.Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.resolve()}?immutable=1", uri=True)


def trace_lrcat_file(
    catalog_path: pathlib.Path,
    *,
    ag_library_file_id: int,
    expected_basename: str | None = None,
) -> dict[str, Any]:
    conn = _connect_immutable(catalog_path)
    conn.row_factory = sqlite3.Row
    try:
        file_row = conn.execute(
            """
            SELECT id_local, id_global, baseName, extension, originalFilename, folder, md5
            FROM AgLibraryFile
            WHERE id_local = ?
            """,
            (ag_library_file_id,),
        ).fetchone()
        if file_row is None:
            raise ValueError(f"AgLibraryFile {ag_library_file_id} not found")

        if expected_basename is not None and file_row["baseName"] != expected_basename:
            raise ValueError(
                f"catalog basename mismatch: expected={expected_basename!r} "
                f"actual={file_row['baseName']!r}"
            )

        images = conn.execute(
            """
            SELECT id_local, id_global, rootFile, developSettingsIDCache, masterImage,
                   fileFormat, fileWidth, fileHeight, orientation, captureTime,
                   originalCaptureTime, copyName, copyReason
            FROM Adobe_images
            WHERE rootFile = ?
            ORDER BY id_local
            """,
            (ag_library_file_id,),
        ).fetchall()

        image_results: list[dict[str, Any]] = []
        for image_row in images:
            image_id = int(image_row["id_local"])
            develop_id = image_row["developSettingsIDCache"]
            develop_row = None
            if develop_id is not None:
                develop_row = conn.execute(
                    """
                    SELECT id_local, image, processVersion, whiteBalance, fileWidth,
                           fileHeight, croppedWidth, croppedHeight, settingsID,
                           historySettingsID, beforeSettingsIDCache, snapshotID,
                           hasDevelopAdjustments, hasDevelopAdjustmentsEx, hasMasks,
                           hasAIMasks, hasRetouch, hasLensBlur, profileCorrections,
                           removeChromaticAberration, text
                    FROM Adobe_imageDevelopSettings
                    WHERE id_local = ?
                    """,
                    (int(develop_id),),
                ).fetchone()

            history_rows = conn.execute(
                """
                SELECT id_local, dateCreated, name, digest, hasBigData,
                       hasDevelopAdjustments, text
                FROM Adobe_libraryImageDevelopHistoryStep
                WHERE image = ?
                ORDER BY dateCreated, id_local
                """,
                (image_id,),
            ).fetchall()

            history: list[dict[str, Any]] = []
            for row in history_rows:
                raw_blob = row["text"]
                decoded_text = None
                decoding = None
                if isinstance(raw_blob, bytes):
                    decoded = decode_history_blob(raw_blob)
                    decoded_text = decoded.decode("utf-8")
                    decoding = {
                        "encoding": "4-byte-big-endian-length+zlib",
                        "compressed_bytes": len(raw_blob),
                        "declared_uncompressed_bytes": struct.unpack(">I", raw_blob[:4])[0],
                        "actual_uncompressed_bytes": len(decoded),
                        "sha256_compressed_blob": hashlib.sha256(raw_blob).hexdigest(),
                        "sha256_decoded_payload": hashlib.sha256(decoded).hexdigest(),
                    }
                elif isinstance(raw_blob, str):
                    decoded_text = raw_blob
                    decoding = {"encoding": "text"}

                history.append(
                    {
                        "id_local": row["id_local"],
                        "dateCreated": row["dateCreated"],
                        "name": row["name"],
                        "hasDevelopAdjustments": row["hasDevelopAdjustments"],
                        "decoding": decoding,
                        "selected_settings": (
                            extract_selected_settings(decoded_text)
                            if decoded_text is not None
                            else {}
                        ),
                    }
                )

            current_text = develop_row["text"] if develop_row is not None else None
            current_settings = (
                extract_selected_settings(current_text)
                if isinstance(current_text, str)
                else {}
            )

            baseline_candidates = [
                step
                for step in history
                if "_Fundamental" in str(step.get("name") or "")
            ]
            export_candidates = [
                step
                for step in history
                if re.search(r"(書き出し|export)", str(step.get("name") or ""), re.I)
            ]
            baseline = baseline_candidates[-1] if baseline_candidates else None
            export = export_candidates[-1] if export_candidates else None

            baseline_values = (
                _settings_values(baseline["selected_settings"]) if baseline else {}
            )
            final_values = (
                _settings_values(export["selected_settings"])
                if export
                else _settings_values(current_settings)
            )

            image_results.append(
                {
                    "image": dict(image_row),
                    "current_develop": (
                        {
                            **{key: develop_row[key] for key in develop_row.keys() if key != "text"},
                            "selected_settings": current_settings,
                        }
                        if develop_row is not None
                        else None
                    ),
                    "history": history,
                    "selection": {
                        "baseline_history_id_local": (
                            baseline["id_local"] if baseline else None
                        ),
                        "baseline_selection": (
                            "last history event whose name contains _Fundamental"
                            if baseline
                            else "not_found"
                        ),
                        "export_history_id_local": export["id_local"] if export else None,
                        "export_selection": (
                            "last history event matching /書き出し|export/i"
                            if export
                            else "not_found; current develop used for final selected values"
                        ),
                    },
                    "baseline_relative_selected_delta": _delta(
                        baseline_values, final_values
                    ),
                }
            )

        return {
            "adapter_profile": "rda.experimental.lightroom-classic-lrcat-trace/0.1",
            "catalog": {
                "locator": str(catalog_path.resolve()),
                "sha256": sha256_file(catalog_path),
            },
            "file": dict(file_row),
            "images": image_results,
        }
    finally:
        conn.close()


def trace_fixture_manifest(
    fixture_path: pathlib.Path,
    *,
    workspace: pathlib.Path,
    output_dir: pathlib.Path,
) -> dict[str, Any]:
    document = yaml.safe_load(fixture_path.read_text(encoding="utf-8")) or {}
    source_root = workspace / document.get("source_root_hint", "sources")
    catalogs = {item["catalog_id"]: item for item in document.get("catalogs") or []}

    pair_to_catalog: dict[str, dict[str, Any]] = {}
    for catalog in catalogs.values():
        for pair_id in catalog.get("fixture_pairs") or []:
            pair_to_catalog[pair_id] = catalog

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for pair in document.get("pairs") or []:
        pair_id = pair["pair_id"]
        match = pair.get("catalog_match") or {}
        file_id = match.get("ag_library_file_id_local")
        catalog = pair_to_catalog.get(pair_id)

        if catalog is None or file_id is None:
            results.append(
                {
                    "pair_id": pair_id,
                    "result": "skipped",
                    "reason": "catalog_or_verified_file_id_unavailable",
                }
            )
            continue

        catalog_path = source_root / catalog["file"]
        raw_path = source_root / pair["raw"]["file"]
        jpeg_path = source_root / pair["jpeg"]["file"]

        verification: dict[str, Any] = {}
        for role, path, expected in (
            ("catalog", catalog_path, catalog["sha256"]),
            ("raw", raw_path, pair["raw"]["sha256"]),
            ("jpeg", jpeg_path, pair["jpeg"]["sha256"]),
        ):
            if not path.exists():
                raise FileNotFoundError(f"{pair_id}: {role} file missing: {path}")
            actual = sha256_file(path)
            verification[role] = {
                "expected_sha256": expected,
                "actual_sha256": actual,
                "matches": actual == expected,
            }
            if actual != expected:
                raise ValueError(
                    f"{pair_id}: {role} SHA-256 mismatch: expected={expected} actual={actual}"
                )

        expected_basename = pathlib.Path(pair["raw"]["file"]).stem
        trace = trace_lrcat_file(
            catalog_path,
            ag_library_file_id=int(file_id),
            expected_basename=expected_basename,
        )
        record = {
            "pair_id": pair_id,
            "result": "traced",
            "verification": verification,
            "trace": trace,
        }
        (output_dir / f"{pair_id}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        results.append(
            {
                "pair_id": pair_id,
                "result": "traced",
                "images": len(trace["images"]),
                "output": str(output_dir / f"{pair_id}.json"),
            }
        )

    summary = {
        "experiment": document.get("experiment"),
        "fixture_manifest": str(fixture_path.resolve()),
        "workspace": str(workspace.resolve()),
        "output_dir": str(output_dir.resolve()),
        "results": results,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary

)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_history_blob(blob: bytes) -> bytes:
    """Decode the tested Lightroom Classic 15.5.1 history BLOB form.

    This is an experimental catalog-adapter behavior, not an RDA Core
    serialization contract.
    """

    if len(blob) < 6:
        raise ValueError("history blob is too short")

    declared_length = struct.unpack(">I", blob[:4])[0]
    payload = zlib.decompress(blob[4:])
    if len(payload) != declared_length:
        raise ValueError(
            f"history blob length mismatch: declared={declared_length} actual={len(payload)}"
        )
    return payload


def _scalar(value: str) -> Any:
    value = value.strip()
    if value.endswith(","):
        value = value[:-1].rstrip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "nil":
        return None
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    try:
        if any(ch in value for ch in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        return value


def extract_selected_settings(text: str) -> dict[str, dict[str, Any]]:
    """Extract scalar occurrences without pretending to parse Lightroom's Lua-like payload.

    Duplicate occurrences are preserved. A normalized value is emitted only when
    all observed occurrences agree.
    """

    wanted = set(SELECTED_DEVELOP_KEYS)
    occurrences: dict[str, list[Any]] = {key: [] for key in SELECTED_DEVELOP_KEYS}

    for line in text.splitlines():
        match = _SETTING_LINE.match(line)
        if not match:
            continue
        key, raw_value = match.groups()
        if key in wanted:
            occurrences[key].append(_scalar(raw_value))

    result: dict[str, dict[str, Any]] = {}
    for key, values in occurrences.items():
        if not values:
            continue
        unique: list[Any] = []
        for value in values:
            if value not in unique:
                unique.append(value)
        result[key] = {
            "occurrences": values,
            "value": unique[0] if len(unique) == 1 else None,
            "status": "known" if len(unique) == 1 else "ambiguous",
        }
    return result


def _settings_values(settings: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        key: item["value"]
        for key, item in settings.items()
        if item.get("status") == "known"
    }


def _delta(baseline: dict[str, Any], final: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    keys = sorted(set(baseline) | set(final))
    for key in keys:
        before = baseline.get(key)
        after = final.get(key)
        item: dict[str, Any] = {"baseline": before, "final": after}
        if isinstance(before, (int, float)) and not isinstance(before, bool) and isinstance(
            after, (int, float)
        ) and not isinstance(after, bool):
            item["delta"] = after - before
        elif before == after:
            item["change"] = "unchanged"
        elif before is None:
            item["change"] = "added_or_not_observed_in_baseline"
        elif after is None:
            item["change"] = "removed_or_not_observed_in_final"
        else:
            item["change"] = "changed"
        result[key] = item
    return result


def _connect_immutable(path: pathlib.Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.resolve()}?immutable=1", uri=True)


def trace_lrcat_file(
    catalog_path: pathlib.Path,
    *,
    ag_library_file_id: int,
    expected_basename: str | None = None,
) -> dict[str, Any]:
    conn = _connect_immutable(catalog_path)
    conn.row_factory = sqlite3.Row
    try:
        file_row = conn.execute(
            """
            SELECT id_local, id_global, baseName, extension, originalFilename, folder, md5
            FROM AgLibraryFile
            WHERE id_local = ?
            """,
            (ag_library_file_id,),
        ).fetchone()
        if file_row is None:
            raise ValueError(f"AgLibraryFile {ag_library_file_id} not found")

        if expected_basename is not None and file_row["baseName"] != expected_basename:
            raise ValueError(
                f"catalog basename mismatch: expected={expected_basename!r} "
                f"actual={file_row['baseName']!r}"
            )

        images = conn.execute(
            """
            SELECT id_local, id_global, rootFile, developSettingsIDCache, masterImage,
                   fileFormat, fileWidth, fileHeight, orientation, captureTime,
                   originalCaptureTime, copyName, copyReason
            FROM Adobe_images
            WHERE rootFile = ?
            ORDER BY id_local
            """,
            (ag_library_file_id,),
        ).fetchall()

        image_results: list[dict[str, Any]] = []
        for image_row in images:
            image_id = int(image_row["id_local"])
            develop_id = image_row["developSettingsIDCache"]
            develop_row = None
            if develop_id is not None:
                develop_row = conn.execute(
                    """
                    SELECT id_local, image, processVersion, whiteBalance, fileWidth,
                           fileHeight, croppedWidth, croppedHeight, settingsID,
                           historySettingsID, beforeSettingsIDCache, snapshotID,
                           hasDevelopAdjustments, hasDevelopAdjustmentsEx, hasMasks,
                           hasAIMasks, hasRetouch, hasLensBlur, profileCorrections,
                           removeChromaticAberration, text
                    FROM Adobe_imageDevelopSettings
                    WHERE id_local = ?
                    """,
                    (int(develop_id),),
                ).fetchone()

            history_rows = conn.execute(
                """
                SELECT id_local, dateCreated, name, digest, hasBigData,
                       hasDevelopAdjustments, text
                FROM Adobe_libraryImageDevelopHistoryStep
                WHERE image = ?
                ORDER BY dateCreated, id_local
                """,
                (image_id,),
            ).fetchall()

            history: list[dict[str, Any]] = []
            for row in history_rows:
                raw_blob = row["text"]
                decoded_text = None
                decoding = None
                if isinstance(raw_blob, bytes):
                    decoded = decode_history_blob(raw_blob)
                    decoded_text = decoded.decode("utf-8")
                    decoding = {
                        "encoding": "4-byte-big-endian-length+zlib",
                        "compressed_bytes": len(raw_blob),
                        "declared_uncompressed_bytes": struct.unpack(">I", raw_blob[:4])[0],
                        "actual_uncompressed_bytes": len(decoded),
                        "sha256_compressed_blob": hashlib.sha256(raw_blob).hexdigest(),
                        "sha256_decoded_payload": hashlib.sha256(decoded).hexdigest(),
                    }
                elif isinstance(raw_blob, str):
                    decoded_text = raw_blob
                    decoding = {"encoding": "text"}

                history.append(
                    {
                        "id_local": row["id_local"],
                        "dateCreated": row["dateCreated"],
                        "name": row["name"],
                        "hasDevelopAdjustments": row["hasDevelopAdjustments"],
                        "decoding": decoding,
                        "selected_settings": (
                            extract_selected_settings(decoded_text)
                            if decoded_text is not None
                            else {}
                        ),
                    }
                )

            current_text = develop_row["text"] if develop_row is not None else None
            current_settings = (
                extract_selected_settings(current_text)
                if isinstance(current_text, str)
                else {}
            )

            baseline_candidates = [
                step
                for step in history
                if "_Fundamental" in str(step.get("name") or "")
            ]
            export_candidates = [
                step
                for step in history
                if re.search(r"(書き出し|export)", str(step.get("name") or ""), re.I)
            ]
            baseline = baseline_candidates[-1] if baseline_candidates else None
            export = export_candidates[-1] if export_candidates else None

            baseline_values = (
                _settings_values(baseline["selected_settings"]) if baseline else {}
            )
            final_values = (
                _settings_values(export["selected_settings"])
                if export
                else _settings_values(current_settings)
            )

            image_results.append(
                {
                    "image": dict(image_row),
                    "current_develop": (
                        {
                            **{key: develop_row[key] for key in develop_row.keys() if key != "text"},
                            "selected_settings": current_settings,
                        }
                        if develop_row is not None
                        else None
                    ),
                    "history": history,
                    "selection": {
                        "baseline_history_id_local": (
                            baseline["id_local"] if baseline else None
                        ),
                        "baseline_selection": (
                            "last history event whose name contains _Fundamental"
                            if baseline
                            else "not_found"
                        ),
                        "export_history_id_local": export["id_local"] if export else None,
                        "export_selection": (
                            "last history event matching /書き出し|export/i"
                            if export
                            else "not_found; current develop used for final selected values"
                        ),
                    },
                    "baseline_relative_selected_delta": _delta(
                        baseline_values, final_values
                    ),
                }
            )

        return {
            "adapter_profile": "rda.experimental.lightroom-classic-lrcat-trace/0.1",
            "catalog": {
                "locator": str(catalog_path.resolve()),
                "sha256": sha256_file(catalog_path),
            },
            "file": dict(file_row),
            "images": image_results,
        }
    finally:
        conn.close()


def trace_fixture_manifest(
    fixture_path: pathlib.Path,
    *,
    workspace: pathlib.Path,
    output_dir: pathlib.Path,
) -> dict[str, Any]:
    document = yaml.safe_load(fixture_path.read_text(encoding="utf-8")) or {}
    source_root = workspace / document.get("source_root_hint", "sources")
    catalogs = {item["catalog_id"]: item for item in document.get("catalogs") or []}

    pair_to_catalog: dict[str, dict[str, Any]] = {}
    for catalog in catalogs.values():
        for pair_id in catalog.get("fixture_pairs") or []:
            pair_to_catalog[pair_id] = catalog

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for pair in document.get("pairs") or []:
        pair_id = pair["pair_id"]
        match = pair.get("catalog_match") or {}
        file_id = match.get("ag_library_file_id_local")
        catalog = pair_to_catalog.get(pair_id)

        if catalog is None or file_id is None:
            results.append(
                {
                    "pair_id": pair_id,
                    "result": "skipped",
                    "reason": "catalog_or_verified_file_id_unavailable",
                }
            )
            continue

        catalog_path = source_root / catalog["file"]
        raw_path = source_root / pair["raw"]["file"]
        jpeg_path = source_root / pair["jpeg"]["file"]

        verification: dict[str, Any] = {}
        for role, path, expected in (
            ("catalog", catalog_path, catalog["sha256"]),
            ("raw", raw_path, pair["raw"]["sha256"]),
            ("jpeg", jpeg_path, pair["jpeg"]["sha256"]),
        ):
            if not path.exists():
                raise FileNotFoundError(f"{pair_id}: {role} file missing: {path}")
            actual = sha256_file(path)
            verification[role] = {
                "expected_sha256": expected,
                "actual_sha256": actual,
                "matches": actual == expected,
            }
            if actual != expected:
                raise ValueError(
                    f"{pair_id}: {role} SHA-256 mismatch: expected={expected} actual={actual}"
                )

        expected_basename = pathlib.Path(pair["raw"]["file"]).stem
        trace = trace_lrcat_file(
            catalog_path,
            ag_library_file_id=int(file_id),
            expected_basename=expected_basename,
        )
        record = {
            "pair_id": pair_id,
            "result": "traced",
            "verification": verification,
            "trace": trace,
        }
        (output_dir / f"{pair_id}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        results.append(
            {
                "pair_id": pair_id,
                "result": "traced",
                "images": len(trace["images"]),
                "output": str(output_dir / f"{pair_id}.json"),
            }
        )

    summary = {
        "experiment": document.get("experiment"),
        "fixture_manifest": str(fixture_path.resolve()),
        "workspace": str(workspace.resolve()),
        "output_dir": str(output_dir.resolve()),
        "results": results,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary
