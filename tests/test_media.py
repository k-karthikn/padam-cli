import tempfile
import unittest

from src.media import Media


class MediaTests(unittest.TestCase):
    def test_filename_is_sanitized_and_never_overwrites_existing(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Media("https://cdn.example/file.php?path=../../danger.mp4", "Title", directory)
            self.assertEqual("danger.mp4", first.filename)
            first.output_path.write_bytes(b"existing")
            second = Media("https://cdn.example/file.php?path=../../danger.mp4", "Title", directory)
            self.assertEqual("danger (2).mp4", second.output_path.name)

    def test_title_fallback_for_hls_and_script_urls(self):
        media = Media("https://cdn.example/stream.m3u8", "A/B: Test")
        self.assertEqual("A_B_ Test.mp4", media.filename)

    def test_percent_encoded_older_movie_filename_is_readable(self):
        media = Media("https://cdn.example/Nanban%20%282012%29.mp4?signature=abc")
        self.assertEqual("Nanban (2012).mp4", media.filename)


if __name__ == "__main__":
    unittest.main()
