from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="dtb_with_dagster",
        packages=find_packages(exclude=["dtb_with_dagster_tests"]),
        install_requires=[
            "dagster-dbt",
            "dagster-webserver",
            "dbt-duckdb",
        ],
        extras_require={"dev": ["pytest"]},
    )
