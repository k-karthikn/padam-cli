import httpx
import re
import sys

from rich.console import Console
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from src.logger import Logger
from src.utils import is_valid

console = Console()

class Scraper:
    def __init__(self):
        self.selected_domain = None
        self.resolver_current_href = None
        self.headers = None

    # Fetch the pages
    async def fetch_page(self,client: httpx.AsyncClient, url: str) -> BeautifulSoup | None:

        try:
            response = await client.get(url)
            response.raise_for_status()

            return BeautifulSoup(response.text, "lxml")
        except Exception as e:
            Logger.log(f"Failed to fetch {url}: {e}")
            return None
        
    # Extract the links from pages
    async def extract_links(self, client: httpx.AsyncClient, url: str) -> list[tuple[str,str]]:
        soup = await self.fetch_page(client, url) 

        if not soup:
            console.print("[bold yellow]There is a problem in extracting links[/bold yellow]")
            Logger.log("Soup Not Found: scaraper.py extract_links method")
        return [ ( a.get_text(strip=True) or "[No Text]", a["href"] ) for a in soup.find_all("a", href=True) ]
        Logger.log("Links Extracted sucessfuly")

    #Page navigation
    async def get_pagination_pages(self, client:httpx.AsyncClient, url:str) -> list[str]:
        links = await self.extract_links(client, url)
        pages = {url}

        for text, href in links:
            if text.isdigit():
                pages.add(urljoin(self.selected_domain,href))
        Logger.log(f"{len(pages)} pages found")
        return sorted(pages)

    # Resolve when something failed in scraping
    async def resolver(self, href: str):
        self.resolver_current_href = href
        async with httpx.AsyncClient(follow_redirects=True, timeout=30,headers=self.headers)as client:
            links = await self.extract_links(client, urljoin(self.selected_domain, href))
            results = [(text, href) for text, href in links if is_valid(text,href)]
            return results


    #fetch the downloable mp3 or m3u8 urls
    async def get_download_links(self, download_page_link: str) -> list[str]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30,headers=self.headers)as client:
            soup = await self.fetch_page(client, download_page_link)
            links = [link["href"] for link in soup.select("div.dlink a")]
            Logger.log(f"Links found : {links} in scraper.py get_dowlnoad_links method")

            dlinks = await self.fetch_page(client, links[0])
            download_links = [link["href"] for link in dlinks.select("div.dlink a")]
            Logger.log(f"download_links = {download_links}")
            
            filtered_download_links = list(set([link for link in download_links if link.endswith((".mp4", ".m3u8")) or "cdn" in link or "dub" in link]))
            Logger.log(f"filtered = {filtered_download_links}")
            
            return filtered_download_links
        
    #used to crawling to the downloadpage
    async def get_download_informations(self, quality_href) -> list[str]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30, headers=self.headers) as client:
            Logger.log(f"processing href : {quality_href} in scraper.py get_download_information method")
            soup = await self.fetch_page(client, urljoin(self.selected_domain, quality_href))
            download_info_page_link = soup.find("a", class_ = "coral")
            
            if download_info_page_link:
                Logger.log(f"download_info_page_link found : {download_info_page_link}")
                dlinks = await self.fetch_page(client, urljoin(self.selected_domain, download_info_page_link["href"]))
            else:
                Logger.log(f"download_info_page_link Not found : {download_info_page_link}")
                Logger.log(f"Now using resolver_current_href: {self.resolver_current_href}")
                dlinks = await self.fetch_page(client, urljoin(self.selected_domain, self.resolver_current_href))

            file_download_page_links = [link["href"] for link in dlinks.select("div.dlink a")]
            movie_download_links = await self.get_download_links(file_download_page_links[0])

            return movie_download_links