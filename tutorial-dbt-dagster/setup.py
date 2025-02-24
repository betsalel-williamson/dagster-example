from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="jaffle_shop",
        packages=find_packages(exclude=["jaffle_shop_tests"]),
        install_requires=[
            "dagster-dbt",
            "dagster-webserver",
            "dbt-duckdb",
            "pandas",
            "duckdb",
            "pyarrow",
            "plotly",
        ],
        extras_require={"dev": ["pytest"]},
    )
