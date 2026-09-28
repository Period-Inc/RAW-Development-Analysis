from __future__ import annotations

from dataclasses import dataclass

from rda_toolchain.raw_probe import snapshot_rawpy_object


class FakeArray:
    def __init__(self, shape, dtype, values=None):
        self.shape = shape
        self.dtype = dtype
        self._values = values

    def tolist(self):
        return self._values


@dataclass
class FakeSizes:
    raw_height: int = 110
    raw_width: int = 210
    height: int = 100
    width: int = 200
    top_margin: int = 5
    left_margin: int = 5
    iheight: int = 100
    iwidth: int = 200
    pixel_aspect: float = 1.0
    flip: int = 0


class FakeRaw:
    raw_image_visible = FakeArray((100, 200), "uint16")
    raw_colors_visible = FakeArray((100, 200), "uint8")
    black_level_per_channel = [512, 512, 512, 512]
    white_level = 16383
    camera_white_level_per_channel = [16000, 16100, 16050, 16100]
    raw_pattern = FakeArray((2, 2), "uint8", [[0, 1], [3, 2]])
    color_desc = b"RGBG"
    num_colors = 3
    sizes = FakeSizes()


def test_snapshot_rawpy_object_records_unprocessed_decoder_state():
    result = snapshot_rawpy_object(FakeRaw(), decoder_version="0.test")

    assert result["probe_profile"] == "rda.experimental.rawpy-unpacked-sensor-state/0.1"
    assert result["decoder"] == {
        "implementation": "rawpy",
        "version": "0.test",
        "postprocess_called": False,
    }
    assert result["visible_sensor_array"] == {
        "shape": [100, 200],
        "dtype": "uint16",
    }
    assert result["sensor_metadata"]["black_level_per_channel"] == [512, 512, 512, 512]
    assert result["sensor_metadata"]["white_level"] == 16383
    assert result["sensor_metadata"]["raw_pattern"] == [[0, 1], [3, 2]]
    assert result["sensor_metadata"]["color_desc"] == "RGBG"
    assert result["sizes"]["top_margin"] == 5
