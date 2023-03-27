from dotenv import load_dotenv
import os
import datetime
from typing import Union

load_dotenv()

# API client library
import googleapiclient.discovery


class GoogleYTAPI:
    """
    Fill
    """

    def __init__(self) -> None:
        self._youtube = googleapiclient.discovery.build(
            os.getenv("API_SERVICE_NAME"),
            os.getenv("API_VERSION"),
            developerKey=os.getenv("DEVELOPER_KEY"),
        )

    def search_channel_id(self, channel_name: str) -> Union[str, None]:
        """
        Fill
        """
        search_response = (
            self._youtube.search()
            .list(
                part="id",
                q=channel_name,
                type="channel",
                fields="items(id(channelId))",
                maxResults=1,
            )
            .execute()
        )

        if search_response:
            print(search_response)
            return search_response["items"][0]["id"]["channelId"]

        return None

    def search_last_videos(self, channel_id: str):
        """
        Fill
        """
        search_response = (
            self._youtube.search()
            .list(
                part="id,snippet",
                order="date",
                channelId=channel_id.strip(),
                publishedAfter=(
                    datetime.datetime.now() - datetime.timedelta(days=1)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            .execute()
        )

        videos = search_response.get("items", None)

        if videos:
            return videos

        return None


if __name__ == "__main__":
    googleytapi = GoogleYTAPI()
    channels = [
        "Marvel Brasil",
        "Marvel Entertainment",
        "Netflix Brasil",
        "20th Century Studios Brasil",
        "Paramount Brasil",
        "Prime Video Brasil",
        "Apple TV ",
        "Warner Channel Brasil",
        "Warner Bros. Pictures Brasil",
        "TrailersBR",
        "HBO Brasil",
    ]

    dict_channels = {}
    for channel in channels:
        dict_channels[channel] = googleytapi.search_channel_id(channel)

    print(dict_channels)

    # channels_id = {
    #     "Marvel Brasil": "UCItRs-h8YU1wRRfP637614w",
    #     "Marvel Entertainment": "UCvC4D8onUfXzvjTOM-dBfEA",
    #     "Netflix Brasil": "UCc1l5mTmAv2GC_PXrBpqyKQ",
    # }

    # for channel, yt_id in channels_id.items():
    #     print(f"Current: {channel}")
    #     response = googleytapi.search_last_videos(yt_id)

    #     import pprint as pp

    #     pp.pprint(response)

    #     videos = response.get("items", None)

    #     if videos:
    #         for video in videos:
    #             channel = video.get("snippet", None).get("channelTitle", None)
    #             publish_time = video.get("snippet", None).get(
    #                 "publishTime", None
    #             )
    #             thumbnails = (
    #                 video.get("snippet", None)
    #                 .get("thumbnails", None)
    #                 .get("default", None)
    #             )
    #             title = video.get("snippet", None).get("title", None)
    #             print(f"{channel}\t{title}\t{publish_time}\t{thumbnails}")
