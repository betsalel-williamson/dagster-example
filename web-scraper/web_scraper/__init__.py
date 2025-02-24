import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
from io import StringIO

async def scrape_backerkit_pledge_data(curl_request_file: str) -> pd.DataFrame:
    """
    Scrapes backer data from the given URL using Playwright, with specified cookies and headers.

    To get the header and cookies, manually login to the website in Chrome, load the url: https://www.backerkit.com/ navigate to pledges and get the cURL request headers and cookies as json objects.

    Args:
        curl_request_file: Path to the JSON file containing curl request, headers, and cookies.

    Returns:
        A Pandas DataFrame containing the scraped backer data.
    """
    # Load request information from JSON file
    with open(curl_request_file, 'r') as f:
        curl_request = json.load(f)    

    url = curl_request["url"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await context.add_cookies([{'url': url, 'name': name, 'value': value} for name, value in curl_request["cookies"].items()])

        await page.set_extra_http_headers(curl_request["headers"])

        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        html_content: str = await page.content()
        await browser.close()

        html_io = StringIO(html_content)
        df: pd.DataFrame = pd.read_html(html_io, attrs={"id": "backers_table"})[0]
        df = df.iloc[:-1,:4]  # Remove last row and unnecessary columns
        df.columns = ["Pledge", "Pledge Level", "Pledged", "Status"]  # Rename columns

        # Split the "Pledge" column into "Pledge ID" and "Backer"
        df[["Pledge ID", "Backer"]] = df["Pledge"].str.split(n=1, expand=True)
        df = df.drop(columns=["Pledge"])  # Remove original "Pledge" and "View" columns
        return df

async def main(curl_request_file: str) -> None:
    """
    Main function to run the scraper and print the output.
    """
    df = await scrape_backerkit_pledge_data(curl_request_file)
    print(df)

if __name__ == "__main__":
    import sys
    if len(sys.argv)!= 2:
        print("Usage: python script.py <curl_request_file>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
