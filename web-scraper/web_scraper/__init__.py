import requests
from bs4 import BeautifulSoup
import sys

def main() -> int:
    """Echo the input arguments to standard output"""
    URL = "https://www.backerkit.com/c/admin/projects/honey-s-hose-inclusive-tights-for-performers"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    csrf_token = soup.find("input", {"name": "_token"})["value"]

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
