import json
import tempfile
import unittest
from pathlib import Path

from src.config import Config


class ConfigTests(unittest.TestCase):
    def test_refresh_applies_new_domains_before_search_and_caches_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local = root / "local.json"
            cache = root / "cache.json"
            local.write_text(json.dumps({
                "domains": {"moviesda": "https://old.example", "isaidub": "https://old-dub.example"},
                "download_path": "~/Movies",
            }))
            remote = {"domains": {"moviesda": "https://new.example", "isaidub": "https://new-dub.example/"}}
            config = Config(local, cache, lambda _: json.dumps(remote).encode())
            self.assertTrue(config.fetch_config())
            self.assertEqual("https://new.example/home.html", config.moviesda_home_endpoint)
            self.assertEqual("https://new-dub.example", config.isaidub)
            self.assertEqual("~/Movies", config.download_path)
            offline = Config(local, cache, lambda _: (_ for _ in ()).throw(OSError("offline")))
            self.assertEqual("https://new.example", offline.moviesda)

    def test_invalid_update_never_replaces_last_good_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "cache.json"
            cache.write_text(json.dumps({"domains": {
                "moviesda": "https://good.example", "isaidub": "https://good-dub.example"}}))
            config = Config(root / "missing.json", cache,
                            lambda _: b'{"domains":{"moviesda":"http://bad.example"}}')
            self.assertFalse(config.fetch_config())
            self.assertEqual("https://good.example", config.moviesda)
            self.assertEqual("https://good.example", json.loads(cache.read_text())["domains"]["moviesda"])

    def test_local_settings_work_without_domain_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local = root / "local.json"
            local.write_text(json.dumps({"download_path": "~/Movies"}))
            config = Config(local, root / "cache.json")
            self.assertEqual("~/Movies", config.download_path)
            self.assertEqual("https://moviesda.ski", config.moviesda)


if __name__ == "__main__":
    unittest.main()
