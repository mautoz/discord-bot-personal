#!/usr/bin/env python3

import os
import requests
import logging
import sys
from typing import Union
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

BASE = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
IMAGE_ORIGINAL = "https://image.tmdb.org/t/p/original"

URL_SEARCH_MOVIE  = BASE + "/search/movie?query={0}&include_adult=false&language=pt-BR&page=1"
URL_SEARCH_TV     = BASE + "/search/tv?query={0}&include_adult=false&language=pt-BR&page=1"
URL_MOVIE_DETAILS = BASE + "/movie/{0}?language=pt-BR"
URL_TV_DETAILS    = BASE + "/tv/{0}?language=pt-BR"
URL_MOVIE_CREDITS = BASE + "/movie/{0}/credits?language=pt-BR"
URL_TV_CREDITS    = BASE + "/tv/{0}/credits?language=pt-BR"
URL_MOVIE_IMAGES  = BASE + "/movie/{0}/images"
URL_TV_IMAGES     = BASE + "/tv/{0}/images"


class TheMoviesDB:

    def __init__(self) -> None:
        self._api_key = os.getenv("TMDB_KEY")

    def _get(self, url: str) -> Union[dict, None]:
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            }
            r = requests.get(url, headers=headers, timeout=5)
            return r.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    # ── Search ──────────────────────────────────────────────────

    def search_movie(self, title: str) -> Union[list, None]:
        data = self._get(URL_SEARCH_MOVIE.format(title.replace(" ", "%20")))
        if not data or not data.get("results"):
            return None
        results = []
        for r in data["results"][:8]:
            results.append({
                "id": r.get("id"),
                "title": r.get("title", "—"),
                "original_title": r.get("original_title", "—"),
                "release_date": r.get("release_date", "—"),
                "overview": r.get("overview", ""),
                "poster_path": r.get("poster_path"),
            })
        return results

    def search_tv_show(self, title: str) -> Union[list, None]:
        data = self._get(URL_SEARCH_TV.format(title.replace(" ", "%20")))
        if not data or not data.get("results"):
            return None
        results = []
        for r in data["results"][:8]:
            results.append({
                "id": r.get("id"),
                "name": r.get("name", "—"),
                "original_name": r.get("original_name", "—"),
                "first_air_date": r.get("first_air_date", "—"),
                "overview": r.get("overview", ""),
                "poster_path": r.get("poster_path"),
            })
        return results

    # ── Details ──────────────────────────────────────────────────

    def get_movie_details(self, tmdb_id: int) -> Union[dict, None]:
        data = self._get(URL_MOVIE_DETAILS.format(tmdb_id))
        if not data or data.get("success") is False:
            return None

        credits = self._get(URL_MOVIE_CREDITS.format(tmdb_id)) or {}
        crew = credits.get("crew", [])
        cast = credits.get("cast", [])

        directors   = [c["name"] for c in crew if c.get("job") == "Director"]
        writers     = [c["name"] for c in crew if c.get("job") in ("Screenplay", "Writer", "Story")]
        cinematog   = [c["name"] for c in crew if c.get("job") == "Director of Photography"]
        composers   = [c["name"] for c in crew if c.get("department") == "Sound" and "Composer" in c.get("job", "")]
        top_cast    = [c["name"] for c in cast[:10]]

        return {
            "id": data.get("id"),
            "title": data.get("title", "—"),
            "original_title": data.get("original_title", "—"),
            "tagline": data.get("tagline", ""),
            "overview": data.get("overview", ""),
            "release_date": data.get("release_date", "—"),
            "runtime": data.get("runtime"),
            "genres": [g["name"] for g in data.get("genres", [])],
            "rating": data.get("vote_average", 0),
            "vote_count": data.get("vote_count", 0),
            "budget": data.get("budget", 0),
            "revenue": data.get("revenue", 0),
            "poster_path": data.get("poster_path"),
            "directors": directors,
            "writers": writers,
            "cinematographers": cinematog,
            "composers": composers,
            "cast": top_cast,
        }

    def get_tv_details(self, tmdb_id: int) -> Union[dict, None]:
        data = self._get(URL_TV_DETAILS.format(tmdb_id))
        if not data or data.get("success") is False:
            return None

        credits = self._get(URL_TV_CREDITS.format(tmdb_id)) or {}
        crew = credits.get("crew", [])
        cast = credits.get("cast", [])

        creators    = [c["name"] for c in data.get("created_by", [])]
        directors   = list({c["name"] for c in crew if c.get("job") == "Director"})[:5]
        writers     = list({c["name"] for c in crew if c.get("department") == "Writing"})[:5]
        top_cast    = [c["name"] for c in cast[:10]]

        return {
            "id": data.get("id"),
            "name": data.get("name", "—"),
            "original_name": data.get("original_name", "—"),
            "tagline": data.get("tagline", ""),
            "overview": data.get("overview", ""),
            "first_air_date": data.get("first_air_date", "—"),
            "last_air_date": data.get("last_air_date", "—"),
            "status": data.get("status", "—"),
            "seasons": data.get("number_of_seasons", 0),
            "episodes": data.get("number_of_episodes", 0),
            "genres": [g["name"] for g in data.get("genres", [])],
            "rating": data.get("vote_average", 0),
            "vote_count": data.get("vote_count", 0),
            "poster_path": data.get("poster_path"),
            "creators": creators,
            "directors": directors,
            "writers": writers,
            "cast": top_cast,
        }

    # ── Cast ──────────────────────────────────────────────────────

    def get_full_cast(self, tmdb_id: int, is_tv: bool = False) -> Union[dict, None]:
        url = URL_TV_CREDITS.format(tmdb_id) if is_tv else URL_MOVIE_CREDITS.format(tmdb_id)
        data = self._get(url)
        if not data:
            return None
        cast  = [c["name"] for c in data.get("cast", []) if c.get("known_for_department") == "Acting"]
        crew  = data.get("crew", [])
        directors = [c["name"] for c in crew if c.get("job") == "Director"]
        writers   = list({c["name"] for c in crew if c.get("department") == "Writing"})
        return {"cast": cast, "directors": directors, "writers": writers}

    # ── Images ────────────────────────────────────────────────────

    def get_images(self, tmdb_id: int, is_tv: bool = False) -> Union[list, None]:
        url = URL_TV_IMAGES.format(tmdb_id) if is_tv else URL_MOVIE_IMAGES.format(tmdb_id)
        data = self._get(url)
        if not data:
            return None
        backdrops = [
            IMAGE_ORIGINAL + img["file_path"]
            for img in data.get("backdrops", [])
            if img.get("iso_639_1") in ("en", "pt", None)
        ]
        return backdrops[:10] if backdrops else None

    def poster_url(self, path: str) -> str:
        return IMAGE_BASE + path if path else ""
