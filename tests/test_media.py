import tempfile
import unittest
from unittest.mock import patch

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


    def test_media_url_is_canonical_and_mpv_argv_keeps_query_tokens(self):
        raw = ("https://open.southbytes.xyz/files/Tamil 2026 Movies/Sshhh (2026)/"
               "Sshhh 2026 Epi 04).mp4?htag=a95b81e&etag=1796050186")
        with patch("src.media.shutil.which", return_value="/usr/bin/mpv"), \
             patch("src.media.subprocess.run") as run:
            media = Media(raw, "Sshhh")
            self.assertTrue(media.stream())
        expected = ("https://open.southbytes.xyz/files/Tamil%202026%20Movies/Sshhh%20(2026)/"
                    "Sshhh%202026%20Epi%2004).mp4?htag=a95b81e&etag=1796050186")
        self.assertEqual(expected, media.url)
        argv = run.call_args.args[0]
        self.assertEqual("mpv", argv[0])
        self.assertEqual(expected, argv[-1])
        self.assertIn("?htag=a95b81e&etag=1796050186", argv[-1])

    def test_comma_containing_headers_are_not_passed_to_mpv(self):
        with patch("src.media.shutil.which", return_value="/usr/bin/mpv"), \
             patch("src.media.subprocess.run") as run:
            Media("https://cdn.example/movie.mp4?signature=abc", headers={"Cookie": "a,b"}).stream()
        argv = run.call_args.args[0]
        self.assertFalse(any("a,b" in argument for argument in argv))


if __name__ == "__main__":
    unittest.main()
