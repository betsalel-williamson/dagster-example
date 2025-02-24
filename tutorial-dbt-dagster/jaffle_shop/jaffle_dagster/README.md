# Jaffle Dagster

Follow steps in tutorial until https://docs.dagster.io/integrations/libraries/dbt/using-dbt-with-dagster/load-dbt-models

```bash
cd tutorial-dbt-dagster/jaffle_shop/jaffle_dagster
mkdir -p "$PWD/.tmpdata"
export DAGSTER_HOME="$PWD/.tmpdata"
dagster dev
```
