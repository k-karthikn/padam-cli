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

    def test_media_url_is_canonical_and_vlc_argv_keeps_query_tokens(self):
        raw = ("https://open.southbytes.xyz/files/Tamil 2026 Movies/Sshhh (2026)/"
               "Sshhh 2026 Epi 04).mp4?htag=a95b81e&etag=1796050186")
        with patch("src.media.shutil.which", return_value="/usr/bin/vlc"), \
             patch("src.media.subprocess.run") as run:
            media = Media(raw, "Sshhh")
            self.assertTrue(media.stream())
        expected = ("https://open.southbytes.xyz/files/Tamil%202026%20Movies/Sshhh%20(2026)/"
                    "Sshhh%202026%20Epi%2004).mp4?htag=a95b81e&etag=1796050186")
        self.assertEqual(expected, media.url)
        argv = run.call_args.args[0]
        self.assertEqual("vlc", argv[0])
        self.assertEqual(expected, argv[1])
        self.assertIn("?htag=a95b81e&etag=1796050186", argv[1])
        self.assertFalse(any(argument.startswith("--http-header-fields") for argument in argv))

    def test_vlc_receives_dedicated_user_agent_and_referrer_flags(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "Referer": "https://movies.downloadpage.xyz/download/page/99789",
        }
        with patch("src.media.shutil.which", return_value="/usr/bin/vlc"), \
             patch("src.media.subprocess.run") as run:
            Media("https://cdn.example/movie.mp4?htag=a&etag=b", headers=headers).stream()
        argv = run.call_args.args[0]
        self.assertEqual("https://cdn.example/movie.mp4?htag=a&etag=b", argv[1])
        self.assertEqual(f":http-user-agent={headers['User-Agent']}", argv[2])
        self.assertEqual(f":http-referrer={headers['Referer']}", argv[3])
        self.assertFalse(any(argument.startswith("--http-header-fields") for argument in argv))
        self.assertFalse(any(argument.startswith("--http-user-agent") for argument in argv))

    def test_unsupported_headers_are_skipped_with_a_warning(self):
        with patch("src.media.shutil.which", return_value="/usr/bin/vlc"), \
             patch("src.media.subprocess.run") as run, \
             patch("src.media.console.print") as printed:
            Media("https://cdn.example/movie.mp4", headers={"Cookie": "a=1, b=2"}).stream()
        argv = run.call_args.args[0]
        self.assertEqual(["vlc", "https://cdn.example/movie.mp4"], argv)
        self.assertTrue(any("Cookie" in str(call) for call in printed.call_args_list))


if __name__ == "__main__":
    unittest.main()
