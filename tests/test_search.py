import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

from src.config import Config
from src.scraper import Link, ScrapeError
from src.search import Search, choose_link


class SearchTests(unittest.IsolatedAsyncioTestCase):
    async def test_picker_returns_original_link_instead_of_dictionary(self):
        links = [Link("First", "https://site.example/first"),
                 Link("Second", "https://site.example/second")]
        with patch("src.search.inquirer.fuzzy") as fuzzy:
            fuzzy.return_value.execute_async = AsyncMock(return_value=1)
            selected = await choose_link("Choose:", links)
        self.assertIs(selected, links[1])
        self.assertEqual([0, 1], [choice.value for choice in fuzzy.call_args.kwargs["choices"]])

    async def test_latest_result_selection_uses_original_link(self):
        chosen = Link("Movie", "https://site.example/movie")
        media = Link("Movie", "https://site.example/file.mp4", chosen.url)
        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            search = Search(config)
            search.list_latest = True
            with patch("src.search.inquirer.fuzzy") as fuzzy, \
                 patch.object(search, "latest_movies", new=AsyncMock(return_value=[chosen])), \
                 patch.object(search, "resolve", new=AsyncMock(return_value=media)) as resolver:
                fuzzy.return_value.execute_async = AsyncMock(return_value=0)
                self.assertTrue(await search.show_results_tui())
            self.assertIs(resolver.await_args.args[1], chosen)
            self.assertEqual({"title": "Movie", "movie_url": chosen.url}, search.selected_movie)
            self.assertEqual(media.url, search.selected_server_url)

    async def test_multiple_servers_use_original_link(self):
        def handler(request):
            if request.url.path == "/start":
                return httpx.Response(200, text="""<div class=dlink>
                    <a href='/server1'>Server 1</a><a href='/server2'>Server 2</a></div>""")
            return httpx.Response(200, headers={"Content-Type": "video/mp4"}, content=b"x")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                with patch("src.search.inquirer.fuzzy") as fuzzy:
                    fuzzy.return_value.execute_async = AsyncMock(return_value=1)
                    media = await Search(config).resolve(client, Link("Movie", "https://site.example/start"))
        self.assertEqual("https://site.example/server2", media.url)
        self.assertEqual([0, 1], [choice.value for choice in fuzzy.call_args.kwargs["choices"]])

    async def test_failed_server_uses_another_server(self):
        def handler(request):
            if request.url.path == "/start":
                return httpx.Response(200, text="""<div class=dlink>
                    <a href='/server1'>Download Server 1</a>
                    <a href='/server2'>Download Server 2</a></div>""")
            if request.url.path == "/server1":
                return httpx.Response(404)
            return httpx.Response(200, headers={"Content-Type": "video/mp4"}, content=b"x")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                with patch("src.search.inquirer.fuzzy") as fuzzy:
                    fuzzy.return_value.execute_async = AsyncMock(return_value=0)
                    media = await Search(config).resolve(client, Link("Movie", "https://site.example/start"))
        self.assertEqual("https://site.example/server2", media.url)

    async def test_series_episodes_include_later_pages(self):
        calls = []

        def handler(request):
            calls.append(str(request.url))
            if request.url.path == "/show":
                return httpx.Response(200, text="<div class=f><a href='/season'>Season 01</a></div>")
            if request.url.path == "/season":
                number = request.url.params.get("page", "1")
                if number == "1":
                    body = """<div class=f><a href='/episode4'>Epi 4</a></div>
                        <div class=f><a href='/episode3'>Epi 3</a></div>
                        <div class=pagination><a href='?page=2'>2</a></div>"""
                elif number == "2":
                    body = """<div class=f><a href='/episode2'>Epi 2</a></div>
                        <div class=pagination><a href='?page=3'>3</a></div>"""
                else:
                    body = "<div class=f><a href='/episode1'>Epi 1</a></div>"
                return httpx.Response(200, text=body)
            if request.url.path == "/episode1":
                return httpx.Response(302, headers={"Location": "https://cdn.example/episode1.mp4"})
            raise AssertionError("Unexpected URL or attempted media download")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                with patch("src.search.inquirer.fuzzy") as fuzzy:
                    fuzzy.return_value.execute_async = AsyncMock(return_value=3)
                    media = await Search(config).resolve(client, Link("Show", "https://site.example/show"))
                    again = await Search(config).resolve(client, Link("Show", "https://site.example/show"))
        self.assertEqual("https://cdn.example/episode1.mp4", media.url)
        self.assertEqual(media.url, again.url)
        self.assertIn("https://site.example/season?page=2", calls)
        self.assertIn("https://site.example/season?page=3", calls)
        self.assertEqual(1, calls.count("https://site.example/season?page=2"))
        self.assertEqual(4, len(fuzzy.call_args.kwargs["choices"]))

    async def test_older_movie_gateway_chain_reaches_redirected_file(self):
        steps = {
            "/nanban": "<div class=f><a href='/format'>Mp4 HQ (Single Part)</a></div>",
            "/format": "<div class=dlink><a href='/download'>Nanban (2012) Single Part</a></div>",
            "/download": "<div class=dlink><a href='/gateway1'>Download Server 1</a></div>",
            "/gateway1": "<div class=dlink><a href='/gateway2'>Download Server 1</a></div>",
            "/gateway2": "<div class=dlink><a href='/final'>Download Server 1</a></div>",
        }

        def handler(request):
            if request.url.path == "/final":
                return httpx.Response(302, headers={
                    "Location": "https://cdn.example/Nanban%20%282012%29.mp4?signature=abc"})
            if request.url.path in steps:
                return httpx.Response(200, text=steps[request.url.path])
            raise AssertionError("The movie file should not be fetched")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                media = await Search(config).resolve(client, Link("Nanban (2012)", "https://site.example/nanban"))
        self.assertEqual("https://cdn.example/Nanban%20%282012%29.mp4?signature=abc", media.url)

    async def test_dubbed_search_discovers_other_host_and_later_page(self):
        calls = []

        def handler(request):
            calls.append(str(request.url))
            path = request.url.path
            if request.url.host == "isaiidub.com":
                return httpx.Response(200, text="""
                    <a href='https://catalogue.example/tamil-atoz-dubbed-movies/'>Tamil A-Z Dubbed Movies</a>""")
            if request.url.query:
                return httpx.Response(200, text="<div class=f><a href='/virus/'>Virus (1999)</a></div>")
            return httpx.Response(200, text="""
                <div class=f><a href='/other/'>Other (1999)</a></div>
                <div class=pagination><a href='?page=2'>2</a></div>""")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                result = await Search(config).search_movies(client, "virus", dubbed=True)
        self.assertEqual("https://catalogue.example/virus/", result[0].url)
        self.assertIn("https://catalogue.example/tamil-atoz-dubbed-movies/v?page=2", calls)

    async def test_resolver_follows_choices_to_verified_media(self):
        def handler(request):
            if request.url.path == "/start":
                return httpx.Response(200, text="<div class=folder><a href='/quality'>720p</a></div>")
            if request.url.path == "/quality":
                return httpx.Response(200, text="<div class=dlink><a href='/file'>Download server</a></div>")
            return httpx.Response(200, headers={"Content-Type": "video/mp4"}, content=b"x")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                media = await Search(config).resolve(client, Link("Movie", "https://site.example/start"))
        self.assertEqual("https://site.example/file", media.url)
        self.assertEqual("https://site.example/quality", media.referer)

    async def test_first_page_failure_propagates(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache")
            async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:
                    httpx.Response(503))) as client:
                with self.assertRaises(ScrapeError):
                    await Search(config).search_movies(client, "leo")

    async def test_complete_catalogue_is_reused_for_repeat_search(self):
        calls = []

        def handler(request):
            calls.append(str(request.url))
            return httpx.Response(200, text="<div class=f><a href='/leo/'>Leo (2023)</a></div>")

        with tempfile.TemporaryDirectory() as directory:
            config = Config(Path(directory) / "missing", Path(directory) / "cache.json")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                first = await Search(config)._collect(client, "https://site.example/catalogue", "leo")
                second = await Search(config)._collect(client, "https://site.example/catalogue", "leo")
        self.assertEqual(first, second)
        self.assertEqual(1, len(calls))


if __name__ == "__main__":
    unittest.main()
