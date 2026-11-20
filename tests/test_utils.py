import unittest

from src.utils import canonical_url, is_secure_url, secure_url

RAW_URL = (
    "https://open.southbytes.xyz/files/Tamil 2026 Movies/Sshhh (2026)/"
    "Sshhh 2026 (Season 03) (720p HD)/Sshhh 2026 Epi 04).mp4"
    "?htag=a95b81e&etag=1796050186"
)
CANONICAL_URL = (
    "https://open.southbytes.xyz/files/Tamil%202026%20Movies/Sshhh%20(2026)/"
    "Sshhh%202026%20(Season%2003)%20(720p%20HD)/Sshhh%202026%20Epi%2004).mp4"
    "?htag=a95b81e&etag=1796050186"
)


class UtilsTests(unittest.TestCase):
    def test_failing_log_url_is_canonicalized_and_query_is_byte_identical(self):
        result = canonical_url(RAW_URL)
        self.assertEqual(CANONICAL_URL, result)
        self.assertEqual("?htag=a95b81e&etag=1796050186", result[result.index("?") :])

    def test_existing_escapes_and_reserved_query_characters_are_preserved(self):
        value = "https://cdn.example/Nanban%20%282012%29.mp4?signature=abc&dl=Zm9v%2FYmFy&path=x+y"
        self.assertEqual(value, canonical_url(value))
        self.assertEqual("https://cdn.example/a+b?x=1", canonical_url("https://cdn.example/a+b?x=1"))

    def test_non_ascii_path_is_utf8_percent_encoded(self):
        self.assertEqual(
            "https://site.example/caf%C3%A9/%E7%94%B5%E5%BD%B1.mp4?htag=a",
            canonical_url("https://site.example/café/电影.mp4?htag=a"),
        )

    def test_malformed_percent_escape_is_escaped(self):
        self.assertEqual(
            "https://cdn.example/100%25zz.mp4?x=1",
            canonical_url("https://cdn.example/100%zz.mp4?x=1"),
        )

    def test_rejections_and_fragment_stripping(self):
        self.assertIsNone(canonical_url("http://site.example/page"))
        self.assertIsNone(canonical_url("https://user:pass@site.example/page"))
        self.assertIsNone(canonical_url("https://site.example:bad/page"))
        self.assertIsNone(canonical_url("https://site.example/pa\nge"))
        self.assertEqual(
            "https://site.example/page",
            canonical_url("https://site.example/page#fragment"),
        )

    def test_secure_url_canonicalizes_relative_href(self):
        self.assertEqual(
            "https://site.example/Tamil%202026%20Movies/file.mp4?htag=a",
            secure_url("https://site.example/list", "Tamil 2026 Movies/file.mp4?htag=a"),
        )
        self.assertIsNone(secure_url("https://site.example/list", "#anchor"))
        self.assertIsNone(secure_url("https://site.example/list", "javascript:alert(1)"))

    def test_is_secure_url_is_validation_only(self):
        self.assertTrue(is_secure_url(CANONICAL_URL))
        self.assertFalse(is_secure_url("http://site.example/page"))
        self.assertFalse(is_secure_url("not a url"))


if __name__ == "__main__":
    unittest.main()
