import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


wrapper_source = (Path(__file__).resolve().parents[2] / "build" / "emby-ffmpeg").read_text()
with TemporaryDirectory() as tmp:
    root = Path(tmp)
    sysfs = root / "drm"
    device = sysfs / "renderD128" / "device"
    device.mkdir(parents=True)
    (device / "vendor").write_text("0x8086\n")
    (device / "device").write_text("0x4908\n")

    ffmpeg = root / "ffmpeg"
    ffmpeg.write_text("#!/usr/bin/env python3\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\n")
    ffmpeg.chmod(0o755)
    wrapper = root / "emby-ffmpeg"
    wrapper.write_text(
        wrapper_source.replace("/usr/bin/ffmpeg", str(ffmpeg)).replace("/sys/class/drm", str(sysfs))
    )

    render_node = "/dev/dri/renderD128"
    qsv = ["-init_hw_device", f"qsv=dev1:hw_any,child_device={render_node}"]
    derived = [
        "-init_hw_device", f"vaapi=emby_va_dev1:{render_node}",
        "-init_hw_device", "qsv=dev1@emby_va_dev1",
    ]
    media = ["-i", "/data0/样例 (HDR).mkv"]
    hdr = ["-filter_complex", "[0:v]hwmap@f3=mode=+read:derive_device=opencl,tonemap_opencl@f4=tonemap=hable[out]"]
    sdr = ["-vf", "vpp_qsv=width=1280:height=532"]
    subtitles = ["-filter_complex", f"{hdr[1]};[out][0:4]overlay[out_with_subtitles]"]

    def assert_arguments(original, expected):
        result = subprocess.check_output(["bash", str(wrapper), *original], text=True)
        actual = json.loads(result)
        assert actual == expected, (expected, actual)

    assert_arguments(["-version"], ["-version"])
    assert_arguments(qsv + media + hdr, derived + media + hdr)
    assert_arguments(qsv + media + subtitles, derived + media + subtitles)
    assert_arguments(qsv + media + sdr, qsv + media + sdr)
    (device / "device").write_text("0x56a0\n")
    assert_arguments(qsv + media + hdr, qsv + media + hdr)
    (device / "device").unlink()
    assert_arguments(qsv + media + hdr, qsv + media + hdr)
