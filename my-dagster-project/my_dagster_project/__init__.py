from dagster import (
    load_assets_from_package_module,
    Definitions,
    define_asset_job,
    ScheduleDefinition,
)
from my_dagster_project import assets
import os
from googleapiclient.discovery import build
from github import Github

defs = Definitions(
    assets=load_assets_from_package_module(assets),
    schedules=[
        ScheduleDefinition(
            job=define_asset_job(name="daily_refresh", selection="*"),
            cron_schedule="@daily",
        )
    ],
    resources={
      "github_api": Github(os.environ["GITHUB_ACCESS_TOKEN"]),
      "youtube_api": build("youtube", "v3", developerKey=os.environ["GOOGLE_API_KEY"]),
      "channel_display_name": os.environ["CHANNEL_DISPLAY_NAME"]
      },
)
