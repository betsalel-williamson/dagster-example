# dbt with Dagster Example

This is a example project to scrape data from the BackerKit dashboard because they don't have an API.

Source: https://docs.dagster.io/integrations/libraries/dbt/using-dbt-with-dagster/

## Getting Started

```bash
cd tutorial-dbt-dagster
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Viewing HTML files

Start a simple static webserver: `python -m http.server 8000`

Navigate to the file e.g. `http://localhost:8000/jaffle_shop/order_count_chart.html`
