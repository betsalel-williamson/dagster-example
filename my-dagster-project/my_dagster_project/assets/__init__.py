import pandas as pd
from dagster import asset
import nbformat
import jupytext
import pickle
from nbconvert.preprocessors import ExecutePreprocessor
import datetime
from github import InputFileContent

# Global variables (can be refactored as resources in Dagster)
@asset(required_resource_keys={"youtube_api", "channel_display_name"})
def channel_id(context) -> str:
    """Gets the YouTube channel ID using the channel's display name."""
    youtube = context.resources.youtube_api  # Access the youtube resource
    channelDisplayName = context.resources.channel_display_name

    request = youtube.search().list(part="snippet", type="channel", q=channelDisplayName)
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        channelId = response["items"][0]["snippet"]["channelId"]
        context.log.info(f"channelId {channelId} found for {channelDisplayName}")
        return channelId
    else:
        raise ValueError(f"Channel '{channelDisplayName}' not found.")


@asset(required_resource_keys={"youtube_api"})
def uploads_playlist_id(context, channel_id: str):
    """Gets the uploads playlist ID for the given channel ID."""
    youtube = context.resources.youtube_api  # Access the youtube resource

    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()

    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


@asset(required_resource_keys={"youtube_api"})
def video_data(context, uploads_playlist_id):
    """Fetches video data (views, title, published date) for videos in the uploads playlist."""
    youtube = context.resources.youtube_api
    video_data = []
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)

    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        for item in response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]

            video_request = youtube.videos().list(part="statistics,snippet", id=video_id)
            video_response = video_request.execute()

            if "items" in video_response and len(video_response["items"]) > 0:
                video_info = video_response["items"][0]
                published_at = datetime.datetime.strptime(
                    video_info["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                ).date()

                if start_date <= published_at <= end_date:
                    views = int(video_info["statistics"].get("viewCount", 0))
                    title = video_info["snippet"]["title"]
                    video_data.append([video_id, title, published_at, views])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_data


@asset
def video_views_dataframe(context, video_data) -> pd.DataFrame:
    """Creates a Pandas DataFrame from the video data."""
    df = pd.DataFrame(video_data, columns=["Video ID", "Title", "Published At", "Views"])
    context.log.info(f"DataFrame created with {len(df)} rows.")
    return df

@asset
def video_views_notebook(video_views_dataframe: pd.DataFrame):
    markdown = f"""
# Video Data

```python
import pickle
video_views_dataframe = pickle.loads({pickle.dumps(video_views_dataframe)!r})
```

## Video Views
```python
video_views_dataframe.reset_index().plot.bar(x="Published At", y="Views")
```
    """
    nb = jupytext.reads(markdown, "md")
    ExecutePreprocessor().preprocess(nb)
    return nbformat.writes(nb)

@asset(required_resource_keys={"github_api"})
def youtube_notebook_gist(context, video_views_notebook):
    gist = context.resources.github_api.get_user().create_gist(
        public=False,
        files={
            "youtube.ipynb": InputFileContent(video_views_notebook),
        },
    )
    context.log.info(f"Notebook created at {gist.html_url}")
    return gist.html_url
