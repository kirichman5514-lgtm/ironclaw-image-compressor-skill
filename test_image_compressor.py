"""Tests for image_compressor.py.

Uses Python's built-in unittest and Pillow to create throwaway images,
so no external test framework or fixture files are required.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import image_compressor  # noqa: E402


class ImageCompressorTests(unittest.TestCase):
    def setUp(self):
        self._tmp = Path(tempfile.mkdtemp(prefix="imgcomp_test_"))
        from PIL import Image

        # Create a small test image.
        self.src = self._tmp / "source.png"
        Image.new("RGB", (100, 80), (200, 100, 50)).save(self.src)

    def tearDown(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _run(self, argv):
        """Run the CLI and return the exit code."""
        try:
            return image_compressor.main(argv)
        except SystemExit as exc:
            return exc.code

    def test_convert_png_to_jpg(self):
        out_dir = self._tmp / "out_jpg"
        code = self._run(
            [str(self.src), "-f", "jpg", "-q", "85", "-o", str(out_dir)]
        )
        self.assertEqual(code, 0)
        outputs = list(out_dir.glob("*.jpg"))
        self.assertEqual(len(outputs), 1)
        self.assertGreater(outputs[0].stat().st_size, 0)

    def test_convert_png_to_webp(self):
        out_dir = self._tmp / "out_webp"
        code = self._run([str(self.src), "-f", "webp", "-o", str(out_dir)])
        self.assertEqual(code, 0)
        self.assertEqual(list(out_dir.glob("*.webp")).__len__(), 1)

    def test_compress_mode_keeps_format(self):
        # compress mode with an explicit -f png keeps the png output format.
        out_dir = self._tmp / "out_compress"
        code = self._run(
            [str(self.src), "-m", "compress", "-f", "png", "-q", "50", "-o", str(out_dir)]
        )
        self.assertEqual(code, 0)
        self.assertEqual(list(out_dir.glob("*.png")).__len__(), 1)

    def test_quality_validation_rejected(self):
        # quality outside 1-100 should be rejected (non-zero exit).
        code = self._run([str(self.src), "-q", "101", "-o", str(self._tmp)])
        self.assertNotEqual(code, 0)

    def test_missing_input_reports_error(self):
        # an unknown input format choice should be rejected.
        code = self._run([str(self.src), "-f", "bogus"])
        self.assertEqual(code, 2)

    def test_max_dimension_resizes(self):
        from PIL import Image

        out_dir = self._tmp / "out_resize"
        code = self._run(
            [str(self.src), "-f", "png", "-s", "50", "-o", str(out_dir)]
        )
        self.assertEqual(code, 0)
        out_path = list(out_dir.glob("*.png"))[0]
        with Image.open(out_path) as img:
            self.assertLessEqual(max(img.size), 50)


if __name__ == "__main__":
    unittest.main()