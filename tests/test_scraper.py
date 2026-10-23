import unittest

import httpx

from src.scraper import Link, ScrapeError, Scraper


class ScraperTests(unittest.IsolatedAsyncioTestCase):
    async def test_follows_final_host_and_discovers_numeric_pagination(self):
        def handler(request):
            if request.url.host == "start.example":
                return httpx.Response(302, headers={"Location": "https://catalogue.example/tamil-movies/l/"})
            return httpx.Response(200, text="""
                <div class=f><a href='/leo/'>Leo (2023)</a></div>
                <div class=pagination><a href='?page=2'>2</a>
                  <a href='https://evil.example/page'>3</a></div>
            """)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
            page = await Scraper().fetch_page(client, "https://start.example/list")
        self.assertEqual("https://catalogue.example/leo/", Scraper().entries(page)[0].url)
        self.assertEqual(["https://catalogue.example/tamil-movies/l/?page=2"], Scraper().pages(page))

    async def test_http_error_is_not_reported_as_empty_results(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(
                lambda _: httpx.Response(503))) as client:
            with self.assertRaises(ScrapeError):
                await Scraper().fetch_page(client, "https://site.example/page")

    async def test_rejects_insecure_redirect(self):
        def handler(request):
            if request.url.scheme == "https":
                return httpx.Response(302, headers={"Location": "http://site.example/page"})
            return httpx.Response(200, text="insecure")
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
            with self.assertRaisesRegex(ScrapeError, "insecure or missing URL"):
                await Scraper().fetch_page(client, "https://site.example/page")

    async def test_redirect_to_movie_file_does_not_open_the_large_file(self):
        calls = []

        def handler(request):
            calls.append(str(request.url))
            if request.url.path == "/gateway":
                return httpx.Response(302, headers={
                    "Location": "https://cdn.example/Nanban%20(2012).mp4?signature=abc"})
            raise AssertionError("The media response must not be opened while resolving")

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
            page = await Scraper().fetch_page(client, "https://site.example/gateway")
        self.assertTrue(page.is_media)
        self.assertEqual("https://cdn.example/Nanban%20(2012).mp4?signature=abc", page.url)
        self.assertEqual(["https://site.example/gateway"], calls)

    async def test_transient_timeout_is_retried_with_clear_error_if_exhausted(self):
        calls = []

        def handler(request):
            calls.append(str(request.url))
            if len(calls) == 1:
                raise httpx.ReadTimeout("temporary timeout", request=request)
            return httpx.Response(200, text="<div class=f><a href='/movie'>Movie</a></div>")

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            page = await Scraper().fetch_page(client, "https://site.example/catalogue")
        self.assertEqual(2, len(calls))
        self.assertEqual("Movie", Scraper().entries(page)[0].title)

    async def test_rejects_unsafe_links_and_preserves_multiple_servers(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                text="""<div class=dlink><a href='/server1'>Server 1</a>
                <a href='/server2'>Server 2</a><a href='javascript:bad()'>Bad</a>
                <a href='http://site.example/bad'>Insecure</a>
                <a href='https://site.example:bad/file'>Malformed</a></div>"""))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/movie")
        self.assertEqual(["https://site.example/server1", "https://site.example/server2"],
                         [item.url for item in Scraper().choices(page)])

    async def test_alternate_download_button_and_media_tag(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                text="<a class='download-btn' href='/get?id=42'>Get file</a>"))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/page")
        self.assertEqual("https://site.example/get?id=42", Scraper().choices(page)[0].url)

        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                text="<video><source src='https://cdn.example/movie.mp4'></video>"))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/page")
        self.assertEqual("https://cdn.example/movie.mp4", Scraper().choices(page)[0].url)

    async def test_html_at_mp4_path_is_treated_as_a_page(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                headers={"Content-Type": "text/html"},
                text="<a class='download' href='/real-file'>Download</a>"))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/pretend.mp4")
        self.assertFalse(page.is_media)
        self.assertEqual("https://site.example/real-file", Scraper().choices(page)[0].url)

    async def test_script_redirect_and_social_links(self):
        markup = """<div class='f'><a href='/page'>Facebook</a></div>
                    <script>window.location.href = '/get-file?id=42';</script>"""
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                text=markup))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/page")
        self.assertEqual("https://site.example/get-file?id=42", Scraper().choices(page)[0].url)

    async def test_get_form_and_meta_redirect_are_discovered(self):
        form = """<form action='/get' method='get'>
            <input type='hidden' name='id' value='42'><button>Download file</button></form>"""
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                text=form))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/page")
        self.assertEqual("https://site.example/get?id=42", Scraper().choices(page)[0].url)

        refresh = "<meta http-equiv='refresh' content='0; URL=/continue'>"
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
                text=refresh))) as client:
            page = await Scraper().fetch_page(client, "https://site.example/page")
        self.assertEqual("https://site.example/continue", Scraper().choices(page)[0].url)


if __name__ == "__main__":
    unittest.main()
