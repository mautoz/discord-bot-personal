#!/usr/bin/env python3

import os
import datetime
from typing import Union
import googleapiclient.discovery

from dotenv import load_dotenv

load_dotenv()

# API client library


CHANNELS_ID_YT = {
    "Marvel Brasil": "UCItRs-h8YU1wRRfP637614w",
    "Netflix Brasil": "UCc1l5mTmAv2GC_PXrBpqyKQ",
    "20th Century Studios Brasil": "UCTFbGAgp5L6IgUTQDW93zlQ",
    "Paramount Brasil": "UCgqD3GdUEfupsdY1kmFLIrw",
    "Prime Video Brasil": "UCuNjvqjTzw9LcD9PVpTVWRA",
    "Apple TV": "UC1Myj674wRVXB9I4c6Hm5zA",
    "Warner Channel Brasil": "UC8msOgi2CPRQKqwSK-nKwtA",
    "Warner Bros. Pictures Brasil": "UCEOVI4AmQE01FDKNFunkV2w",
    "TrailersBR": "UCF0SVZVMvkPIFGk3gu_GuNg",
    "StarPLusBr": "UC0OEW6doCsgCxVBVd4q6Rpw",
    "DisneyPlusbr": "UCApaSzvP6jM9rfs8UbcqD1g",
    "HBOMAXBR": "UCR7ZwQz60rW9dK59Dirdc8w",
    "GameSpotTrailers": "UCUnRn1f78foyP26XGkRfWsA",
    "fasdecinemabr": "UC5XG4yYM-_DQ-3HPRuam76Q",
    "gametrailers": "UCJx5KP-pCUmL9eZUv-mIcNw",
    "lionsgatemovies": "UCJ6nMHaJPZvsJ-HmUmj1SeA",
    "Universal Pictures Brasil": "UCwhVCdYsd-A32RECPqJUoPg",
    "Sony Pictures Brasil": "UC9NXpIA01HVRhYgcEbs80Nw",
    "Rotten Tomatoes Trailers": "UCi8e0iOVk1fEOogdfu4YgfA",
    "CrunchyrollBR": "UCVc-JLY3Db6-O48y7TS4N7Q",
    "parisfilmes": "UCJmCTfaqgP5AWqfQCF21fPg"
}


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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

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
                type="video",
            )
            .execute()
        )

        videos = search_response.get("items", None)

        if videos:
            return videos

        return None

    def filter_shorts(self, videos: list, max_duration_seconds: int = 65) -> list:
        """
        Filter out YouTube Shorts from a list of video items.
        Makes a single batched videos.list call to check duration.

        Parameters
        ----------
        videos: list
            List of video items from search_last_videos (across all channels).
        max_duration_seconds: int
            Videos at or below this duration are considered Shorts. Default: 65s.

        Returns
        -------
            Filtered list with Shorts removed.
        """
        if not videos:
            return []

        video_ids = [v.get("id", {}).get("videoId") for v in videos if v.get("id", {}).get("videoId")]
        if not video_ids:
            return videos

        # Batch in groups of 50 (API limit)
        durations = {}
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            response = (
                self._youtube.videos()
                .list(part="contentDetails", id=",".join(batch))
                .execute()
            )
            for item in response.get("items", []):
                vid_id = item["id"]
                duration_iso = item.get("contentDetails", {}).get("duration", "PT0S")
                durations[vid_id] = self._parse_duration(duration_iso)

        return [v for v in videos if durations.get(v.get("id", {}).get("videoId"), 999) > max_duration_seconds]

    def _parse_duration(self, iso_duration: str) -> int:
        """Convert ISO 8601 duration (e.g. PT1M30S) to total seconds."""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
        if not match:
            return 0
        hours   = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds


# if __name__ == "__main__":
#     googleytapi = GoogleYTAPI()
# channels = [
#     "Marvel Brasil",
#     "Marvel Entertainment",
#     "Netflix Brasil",
#     "20th Century Studios Brasil",
#     "Paramount Brasil",
#     "Prime Video Brasil",
#     "Apple TV ",
#     "Warner Channel Brasil",
#     "Warner Bros. Pictures Brasil",
#     "TrailersBR",
#     "HBO Brasil",
# ]

# dict_channels = {}
# for channel in channels:
#     dict_channels[channel] = googleytapi.search_channel_id(channel)

# print(dict_channels)

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


# Response Example

# [{'etag': 'oZJg1f7pFxhGjvEEN1xhgK6mrUI',
#   'id': {'kind': 'youtube#video', 'videoId': 'V51j_FKGdfU'},
#   'kind': 'youtube#searchResult',
#   'snippet': {'channelId': 'UCItRs-h8YU1wRRfP637614w',
#               'channelTitle': 'Marvel Brasil',
#               'description': 'Da produtora executiva Zoë Saldaña, #PoderM é '
#                              'uma Série Original em 4 episódios. Assista agora '
#                              'no #DisneyPlus.',
#               'liveBroadcastContent': 'none',
#               'publishTime': '2023-03-17T17:58:52Z',
#               'publishedAt': '2023-03-17T17:58:52Z',
#               'thumbnails': {'default': {'height': 90,
#                                          'url': 'https://i.ytimg.com/vi/V51j_FKGdfU/default.jpg',
#                                          'width': 120},
#                              'high': {'height': 360,
#                                       'url': 'https://i.ytimg.com/vi/V51j_FKGdfU/hqdefault.jpg',
#                                       'width': 480},
#                              'medium': {'height': 180,
#                                         'url': 'https://i.ytimg.com/vi/V51j_FKGdfU/mqdefault.jpg',
#                                         'width': 320}},
#               'title': 'Poder M | Trailer Oficial | Disney+'}},
#  {'etag': '81cqGB8pJHVRh7XZxHBfwUhvkWU',
#   'id': {'kind': 'youtube#video', 'videoId': '5BmQkV06o-I'},
#   'kind': 'youtube#searchResult',
#   'snippet': {'channelId': 'UCItRs-h8YU1wRRfP637614w',
#               'channelTitle': 'Marvel Brasil',
#               'description': 'HomemFormigaEAVespa: Quantumania, hoje nos '
#                              'cinemas e em 3D.',
#               'liveBroadcastContent': 'none',
#               'publishTime': '2023-03-15T21:00:02Z',
#               'publishedAt': '2023-03-15T21:00:02Z',
#               'thumbnails': {'default': {'height': 90,
#                                          'url': 'https://i.ytimg.com/vi/5BmQkV06o-I/default.jpg',
#                                          'width': 120},
#                              'high': {'height': 360,
#                                       'url': 'https://i.ytimg.com/vi/5BmQkV06o-I/hqdefault.jpg',
#                                       'width': 480},
#                              'medium': {'height': 180,
#                                         'url': 'https://i.ytimg.com/vi/5BmQkV06o-I/mqdefault.jpg',
#                                         'width': 320}},
#               'title': 'Homem o quê? 🤔🐜⁉ #Shorts'}},
#  {'etag': 'so1if_Ju1awbLBf0ZtaNhc4ndAM',
#   'id': {'kind': 'youtube#video', 'videoId': 'kYMNAiQDRq0'},
#   'kind': 'youtube#searchResult',
#   'snippet': {'channelId': 'UCItRs-h8YU1wRRfP637614w',
#               'channelTitle': 'Marvel Brasil',
#               'description': 'A maneira como esta trilha foi feita... dá um '
#                              'filme! #VozesEmAscensão: a música de Wakanda '
#                              'Para Sempre. Em 29 de março ...',
#               'liveBroadcastContent': 'none',
#               'publishTime': '2023-03-14T17:11:25Z',
#               'publishedAt': '2023-03-14T17:11:25Z',
#               'thumbnails': {'default': {'height': 90,
#                                          'url': 'https://i.ytimg.com/vi/kYMNAiQDRq0/default.jpg',
#                                          'width': 120},
#                              'high': {'height': 360,
#                                       'url': 'https://i.ytimg.com/vi/kYMNAiQDRq0/hqdefault.jpg',
#                                       'width': 480},
#                              'medium': {'height': 180,
#                                         'url': 'https://i.ytimg.com/vi/kYMNAiQDRq0/mqdefault.jpg',
#                                         'width': 320}},
#               'title': 'Vozes em Ascensão: A Música de Wakanda Para Sempre | '
#                        'Disney+'}}
