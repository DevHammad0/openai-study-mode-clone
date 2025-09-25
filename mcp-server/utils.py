import httpx
from bs4 import BeautifulSoup, Tag 
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import urllib.parse
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import time
import re



import os, glob
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from pydantic import SecretStr


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set")



@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str
    position: int


class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests: list[Any] = []

    async def acquire(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req for req in self.requests if now - req < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Wait until we can make another request
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.requests.append(now)


class DuckDuckGoSearcher:
    BASE_URL = "https://html.duckduckgo.com/html"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self):
        self.rate_limiter = RateLimiter()

    def format_results_for_llm(self, results: List[SearchResult]) -> str:
        """Format results in a natural language style that's easier for LLMs to process"""
        if not results:
            return "No results were found for your search query. This could be due to DuckDuckGo's bot detection or the query returned no matches. Please try rephrasing your search or try again in a few minutes."

        output = []
        output.append(f"Found {len(results)} search results:\n")

        for result in results:
            output.append(f"{result.position}. {result.title}")
            output.append(f"   URL: {result.link}")
            output.append(f"   Summary: {result.snippet}")
            output.append("")  # Empty line between results

        return "\n".join(output)

    async def search(
        self, query: str, max_results: int = 10
    ) -> List[SearchResult]:
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()

            # Create form data for POST request
            data = {
                "q": query,
                "b": "",
                "kl": "",
            }

            print(f"Searching DuckDuckGo for: {query}")
            print(f"Using URL: {self.BASE_URL}")

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        self.BASE_URL, data=data, headers=self.HEADERS, timeout=30.0
                    )
                    response.raise_for_status()
                    print(f"Request successful. Status code: {response.status_code}")
                except httpx.ConnectError as e:
                    print(f"Connection error: {e}")
                    raise
                except httpx.TimeoutException as e:
                    print(f"Timeout error: {e}")
                    raise

            # Parse HTML response
            soup = BeautifulSoup(response.text, "html.parser")
            if not soup:
                print("Failed to parse HTML response")
                return []

            results = [] # type: ignore
            for result in soup.select(".result"):
                title_elem = result.select_one(".result__title")
                if not title_elem:
                    continue

                link_elem = title_elem.find("a")
                if not link_elem or not isinstance(link_elem, Tag):
                    continue

                title = link_elem.get_text(strip=True)
                link_attr = link_elem.get("href", "")
                
                # Ensure link is a string
                link = str(link_attr) if link_attr else ""
                
                # Skip if no link found
                if not link:
                    continue

                # Skip ad results
                if "y.js" in link:
                    continue

                # Clean up DuckDuckGo redirect URLs
                if link.startswith("//duckduckgo.com/l/?uddg="):
                    try:
                        link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                    except (IndexError, ValueError):
                        continue

                snippet_elem = result.select_one(".result__snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                results.append(
                    SearchResult(
                        title=title,
                        link=link,
                        snippet=snippet,
                        position=len(results) + 1,
                    )
                )

                if len(results) >= max_results:
                    break

            print(f"Successfully found {len(results)} results")
            return results

        except httpx.TimeoutException:
            print("Search request timed out")
            return []
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error during search: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return []


class WebContentFetcher:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=20)

    async def fetch_and_parse(self, url: str) -> str:
        """Fetch and parse content from a webpage"""
        try:
            await self.rate_limiter.acquire()

            print(f"Fetching content from: {url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    follow_redirects=True,
                    timeout=30.0,
                )
                response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Get the text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text).strip()

            # Truncate if too long
            if len(text) > 8000:
                text = text[:6000] + "... [content truncated]"

            print(f"Successfully fetched and parsed content ({len(text)} characters)")
            return text

        except httpx.TimeoutException:
            print(f"Request timed out for URL: {url}")
            return "Error: The request timed out while trying to fetch the webpage."
        except httpx.HTTPError as e:
            print(f"HTTP error occurred while fetching {url}: {str(e)}")
            return f"Error: Could not access the webpage ({str(e)})"
        except Exception as e:
            print(f"Error fetching content from {url}: {str(e)}")
            return f"Error: An unexpected error occurred while fetching the webpage ({str(e)})"
        
        
        

searcher = DuckDuckGoSearcher()
fetcher = WebContentFetcher()


async def search(query: str, max_results: int = 5):
    """
    Search DuckDuckGo and return formatted results.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        ctx: MCP context for logging
    """
    try:
        results = await searcher.search(query, max_results)
        return results
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"



async def fetch_content(url: str) -> str:
    """
    Fetch and parse content from a webpage URL.

    Args:
        url: The webpage URL to fetch content from
    """
    return await fetcher.fetch_and_parse(url)




def build_vector_store(input_dir: str = "knowledge-base/"):
    # load docs
    documents = []
    folders = glob.glob(input_dir)
    for folder in folders:
        docs_loader = DirectoryLoader(folder, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        docs_folder = docs_loader.load()
        for doc in docs_folder:
            file_name = os.path.basename(doc.metadata["source"])
            doc.metadata["page_title"] = os.path.splitext(file_name)[0]
            documents.append(doc)

    print(f"[INFO] Loaded {len(documents)} documents")

    # split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=gemini_api_key
    )

    ds_name = os.path.join("..", "shared_data", "vector_store")
    
    # Create the shared_data directory if it doesn't exist
    os.makedirs(os.path.dirname(ds_name), exist_ok=True)
    
    if os.path.exists(ds_name):
        import shutil
        shutil.rmtree(ds_name)
        print(f"[INFO] Removed old vector store at {ds_name}")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=ds_name,
        client_settings=Settings(anonymized_telemetry=False)
    )
    print(f"Vector store created with {vector_store._collection.count()} chunks")
