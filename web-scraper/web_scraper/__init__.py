import json
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple
from io import StringIO
import pytz

from playwright.async_api import async_playwright
import pandas as pd

class LoadRequestData:

    @staticmethod
    def load_from_json(curl_request_file_as_json: str) -> Tuple[str, List[Dict[str, str]], Dict[str, str]]:
        """
        Reads the cURL request data from the given JSON file and returns the URL, cookies, and headers.

        Args:
            curl_request_file: Path to the JSON file containing curl request, headers, and cookies.

        Returns:
            A tuple containing the URL, cookies, and headers.
        """
        with open(curl_request_file_as_json, 'r') as f:
            curl_request = json.load(f)
        url = curl_request["url"]
        cookies = [{'url': url, 'name': name, 'value': value} for name, value in curl_request["cookies"].items()]
        headers = curl_request["headers"]
        return url, cookies, headers

    @staticmethod
    def load_curl_str(curl_request_file_as_curl: str) -> Tuple[str, List[Dict[str, str]], Dict[str, str]]:
        """
        Reads the cURL request data from the given cURL string file and returns the URL, cookies, and headers. The data is formatted with each parameter on a separate line.

        Args:
            curl_request_file: Path to the file containing a valid multi-line cURL request string.

        Returns:
            A tuple containing the URL, cookies, and headers.
        """
        with open(curl_request_file_as_curl, 'r') as f:
            curl_str = f.read()

        url = curl_str.split("'", 1)[1].split("'")[0]  # Extract URL between single quotes
        headers = {}
        cookies = {}

        for line in curl_str.splitlines():
            line = line.strip()
            if line.startswith("-H"):
                heade_parts = line.split("'", 2)
                if len(heade_parts) == 3:
                    hname, hvalue = heade_parts[1].split(": ")
                    headers[hname] = hvalue
            elif line.startswith("-b"):
                cookie_parts = line.split("'", 2)
                if len(cookie_parts) == 3:
                    for cookie_pair in cookie_parts[1].split(";"):
                        if cookie_pair:
                            name, value = cookie_pair.strip().split("=", 1)
                            cookies[name] = value

        cookies = [{'url': url, 'name': name, 'value': value} for name, value in cookies.items()]

        return url, cookies, headers

    @staticmethod
    def load(curl_request_file: str) -> Tuple[str, List[Dict[str, str]], Dict[str, str]]:
        """
        Reads the cURL request data from the given file and returns the URL, cookies, and headers.

        Automatically determines the file type (JSON or cURL string) based on the file extension.

        Args:
            curl_request_file: Path to the file containing cURL request data.

        Returns:
            A tuple containing the URL, cookies, and headers.
        """
        if curl_request_file.lower().endswith(".json"):
            return LoadRequestData.load_from_json(curl_request_file)
        elif curl_request_file.lower().endswith(".curl"):  # Or any other extension you want to support
            return LoadRequestData.load_curl_str(curl_request_file)
        else:
            raise ValueError("Unsupported file type. Please provide a JSON or cURL file.")

class AsyncBrowser:
    def __init__(self, cookies, headers):
        self.__p = None
        self.__browser = None
        self.__context = None
        self.__cookies = cookies
        self.__headers = headers
        self.__page = None

    async def __aenter__(self):
        if self.__p is None:
            self.__p = await async_playwright().start()
        if self.__browser is None:
            self.__browser = await self.__p.chromium.launch(headless=True)
        if self.__context is None:
            self.__context = await self.__browser.new_context()
        if self.__page is None:
            await self.__context.add_cookies(self.__cookies)
            self.__page = await self.__context.new_page()
            await self.__page.set_extra_http_headers(self.__headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__context is not None:
            await self.__context.close()
            self.context = None
        if self.__browser is not None:
            await self.__browser.close()
            self.__browser = None
        if self.__p is not None:
            await self.__p.stop()
            self.__p = None

    async def get_html_content_as_str(self, url: str) -> str:
        """
        Fetches the HTML content from the given URL using the class's Playwright browser,
        with specified cookies and headers.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content as a string.
        """
        await self.__page.goto(url)
        await self.__page.wait_for_load_state("domcontentloaded")

        # Get the current UTC time
        utc_time = datetime.now(pytz.utc)

        # Format the timestamp as ISO 8601
        iso_timestamp = utc_time.strftime("%Y-%m-%dT%H-%M-%SZ")

        await self.__page.screenshot(path=f"example/{url}/{iso_timestamp}.png")
        html_content: str = await self.__page.content()
        return html_content
    
    async def get_html_content(self, url: str) -> StringIO:
        """
        Fetches the HTML content from the given URL using the class's Playwright browser,
        with specified cookies and headers.

        Args:
            url: The URL to fetch.

        Returns:
            A StringIO object containing the HTML content.
        """
        html_content = await self.get_html_content_as_str(url)
        return StringIO(html_content)

def extract_pledges_data(html_io: StringIO) -> pd.DataFrame:
    """
    Extracts backer data from the given HTML content (StringIO object).

    Args:
        html_io: StringIO object containing the HTML content.

    Returns:
        A Pandas DataFrame containing the extracted backer data.
    """
    df: pd.DataFrame = pd.read_html(html_io, attrs={"id": "backers_table"})[0]
    df = df.iloc[:-1,:4]  # Remove last row and unnecessary columns
    df.columns = ["Pledge", "Pledge Level", "Pledged", "Status"]  # Rename columns

    # Split the "Pledge" column into "Pledge ID" and "Backer"
    df[["Pledge ID", "Backer"]] = df["Pledge"].str.split(n=1, expand=True)
    df = df.drop(columns=["Pledge"])  # Remove original "Pledge" column
    return df

def extract_stats_data(html_io: StringIO) -> List[pd.DataFrame]:  # Updated return type
    """
    Extracts all tables from the given HTML content (StringIO object) as a list of DataFrames.

    Args:
        html_io: StringIO object containing the HTML content.

    Returns:
        A list of Pandas DataFrames extracted from the HTML.
    """
    # Find all tables within the HTML
    df_list: List[pd.DataFrame] = pd.read_html(html_io)

    # TODO: get the table headings from the page and assign them to the different tables

    # Extract headings from each DataFrame
    for i, df in enumerate(df_list):
        print(f"Table {i + 1} headings:")
        print(df.columns)  # Print the column names (headings)
        print("---")

    return df_list  # Return the list of DataFrames


async def main(curl_request_file: str) -> None:
    """
    Main function to run the scraper and print the output.
    """
    url, cookies, headers = LoadRequestData.load(curl_request_file)
    async with AsyncBrowser(cookies, headers) as browser:  # Use the AsyncBrowser class

        # Extract project name from URL
        project_name = url.split("/c/admin/projects/")[1].split("/")[0]

        html_io = await browser.get_html_content(f"https://www.backerkit.com/c/admin/projects/{project_name}/pledges")
        df = extract_pledges_data(html_io)
        print(df)

        html_io2 = await browser.get_html_content(f"https://www.backerkit.com/c/admin/projects/{project_name}/stats")
        df_list = extract_stats_data(html_io2)
        print(df_list)

if __name__ == "__main__":
    import sys
    if len(sys.argv)!= 2:
        print("Usage: python script.py <curl_request_file>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
