import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
from io import StringIO
from typing import Dict, List, Any, Tuple

def get_request_data(curl_request_file: str) -> Tuple[str, List[Dict[str, str]], Dict[str, str]]:
    """
    Reads the cURL request data from the given JSON file and returns the URL, cookies, and headers.

    Args:
        curl_request_file: Path to the JSON file containing curl request, headers, and cookies.

    Returns:
        A tuple containing the URL, cookies, and headers.
    """
    with open(curl_request_file, 'r') as f:
        curl_request = json.load(f)
    url = curl_request["url"]
    cookies = [{'url': url, 'name': name, 'value': value} for name, value in curl_request["cookies"].items()]
    headers = curl_request["headers"]
    return url, cookies, headers

async def get_html_content(url: str, cookies: List[Dict[str, str]], headers: Dict[str, str]) -> StringIO:
    """
    Fetches the HTML content from the given URL using Playwright, with specified cookies and headers.

    Args:
        url: The URL to fetch.
        cookies: A list of dictionaries representing cookies.
        headers: A dictionary of headers.

    Returns:
        A StringIO object containing the HTML content.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await context.add_cookies(cookies)
        await page.set_extra_http_headers(headers)
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        html_content: str = await page.content()
        await browser.close()

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
    url, cookies, headers = get_request_data(curl_request_file)

    # Extract project name from URL
    project_name = url.split("/c/admin/projects/")[1].split("/")[0]

    html_io = await get_html_content(f"https://www.backerkit.com/c/admin/projects/{project_name}/pledges", cookies, headers)
    df = extract_pledges_data(html_io)
    print(df)

    html_io2 = await get_html_content(f"https://www.backerkit.com/c/admin/projects/${project_name}/stats", cookies, headers)
    dfs = extract_stats_data(html_io2)
    print(dfs)

if __name__ == "__main__":
    import sys
    if len(sys.argv)!= 2:
        print("Usage: python script.py <curl_request_file>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
