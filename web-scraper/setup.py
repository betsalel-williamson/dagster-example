from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="web_scraper",
        packages=find_packages(exclude=["web_scraper_tests"]),
        install_requires=[
            "playwright",
            "pytest-playwright",
            "asyncio",
            "pandas",
            "lxml",
        ],
        extras_require={"dev": ["pytest"]},
    )
