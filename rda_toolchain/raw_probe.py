from __future__ import annotations

import hashlib
import pathlib
from typing import Any


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tolist(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("ascii", errors="replace").rstrip("\x00")
    if isinstance(value, tuple):
        return list(value)
    return value


def snapshot_rawpy_object(raw: Any, *, decoder_version: str) -> dict[str, Any]:
    """Capture decoder-exposed RAW state without calling postprocess()."""

    visible = raw.raw_image_visible
    colors = getattr(raw, "raw_colors_visible", None)
    sizes = getattr(raw, "sizes", None)

    size_fields = {}
    if sizes is not None:
        for name in (
            "raw_height",
            "raw_width",
            "height",
            "width",
            "top_margin",
            "left_margin",
            "iheight",
            "iwidth",
            "pixel_aspect",
            "flip",
        ):
            if hasattr(sizes, name):
                size_fields[name] = _tolist(getattr(sizes, name))

    return {
        "probe_profile": "rda.experimental.rawpy-unpacked-sensor-state/0.1",
        "decoder": {
            "implementation": "rawpy",
            "version": decoder_version,
            "postprocess_called": False,
        },
        "visible_sensor_array": {
            "shape": list(visible.shape),
            "dtype": str(visible.dtype),
        },
        "visible_color_index_array": (
            {
                "shape": list(colors.shape),
                "dtype": str(colors.dtype),
            }
            if colors is not None
            else None
        ),
        "sensor_metadata": {
            "black_level_per_channel": _tolist(getattr(raw, "black_level_per_channel", None)),
            "white_level": _tolist(getattr(raw, "white_level", None)),
            "camera_white_level_per_channel": _tolist(
                getattr(raw, "camera_white_level_per_channel", None)
            ),
            "raw_pattern": _tolist(getattr(raw, "raw_pattern", None)),
            "color_desc": _tolist(getattr(raw, "color_desc", None)),
            "num_colors": _tolist(getattr(raw, "num_colors", None)),
        },
        "sizes": size_fields,
    }


def probe_raw(path: pathlib.Path) -> dict[str, Any]:
    try:
        import rawpy
    except ImportError as exc:  # pragma: no cover - exercised by installed experiment extra
        raise RuntimeError(
            'RAW probing requires the optional dependency: pip install -e ".[raw]"'
        ) from exc

    source = path.resolve()
    with rawpy.imread(str(source)) as raw:
        snapshot = snapshot_rawpy_object(raw, decoder_version=str(rawpy.__version__))

    snapshot["source"] = {
        "locator": str(source),
        "byte_length": source.stat().st_size,
        "digests": [{"algorithm": "sha256", "value": sha256_file(source)}],
    }
    return snapshot
