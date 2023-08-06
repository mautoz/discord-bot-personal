#!/usr/bin/env python3

import os
import requests
import logging
import sys
from typing import Union
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
DEFAULT_URL_SEARCH = "https://api.themoviedb.org/3/search/movie?query={0}&include_adult=false&language=en-US&page=1"
DEFAULT_URL_CAST = "https://api.themoviedb.org/3/movie/{0}/credits"
DEFAULT_URL_IMAGES = "https://api.themoviedb.org/3/movie/{0}/images"

DEFAULT_URL_SEARCH_SERIE = "https://api.themoviedb.org/3/search/tv?query={0}&include_adult=false&language=en-US&page=1"
DEFAULT_URL_CAST_SERIE = (
    "https://api.themoviedb.org/3/tv/{0}/credits?language=en-US"
)
DEFAULT_URL_IMAGES_SERIE = "https://api.themoviedb.org/3/tv/{0}/images"

DEFAULT_IMAGE_URL = "https://image.tmdb.org/t/p/original/{0}"


class TheMoviesDB:
    """
    Class used by my bots to search info from movies, tv show
    and other thing from IMDB using the free API called The Movies DB (TMDB).
    """

    def __init__(self) -> None:
        self._api_key = os.getenv("TMDB_KEY")

    def _retrive_url(self, url: str) -> Union[dict, None]:
        """
        Retrieve url with a header. Used by TMDB.

        Parameters
        ----------
        url: str
           Formatted URL used to retrieve data from TMDB.

        Returns
        -------
            JSON response.
        """
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            }
            response = requests.get(url, headers=headers, timeout=5)

        except requests.exceptions.RequestException as error:
            print(error)
            return None

        else:
            return response.json()

    def format_response(self, response: dict):
        """
        Organize the json results from TMDB as a list.

        Parameters
        ----------
        response: dict
            Raw values from TMDB.

        Returns
        -------
            A list with all results where each line contains:
            id, release date, original title and title.
        """
        results = response["results"]
        if results:
            names = []
            for result in results:
                buffer = f"{result['id']}\t{result['release_date']}\t{result['original_title']}\t{result['title']}"
                names.append(buffer)

            return names

        return None

    def format_response_tv_show(self, response: dict):
        """
        Organize the json results from TMDB as a list.
        Works for TV Show response.

        Parameters
        ----------
        response: dict
            Raw values from TMDB.

        Returns
        -------
            A list with all results where each line contains:
            id, first_air_date, original_name and name.
        """
        results = response["results"]
        if results:
            names = []
            for result in results:
                buffer = f"{result['id']}\t{result['first_air_date']}\t{result['original_name']}\t{result['name']}"
                names.append(buffer)

            return names

        return None

    def format_cast(self, response: dict):
        """
        Organize the cast names from the response.

        Parameters
        ----------
        response: dict
            Raw values from TMDB.

        Returns
        -------
            String with all cast separated by comma.
        """
        cast_crew = response["cast"]
        cast_names = []
        for cast in cast_crew:
            if cast["known_for_department"] == "Acting":
                cast_names.append(cast["name"])

        return ", ".join(cast_names)

    def get_img_links(self, response: dict):
        """
        Get only promotional images from the response.
        We use filter to get images in English or Portuguese.

        Parameters
        ----------
        response: dict
            Raw values from TMDB.

        Returns
        -------
            String with all links separated by comma.
        """
        try:
            imgs = response["backdrops"]

        except Exception as error:
            return None

        else:
            links = []
            for img in imgs:
                if img["iso_639_1"] == "en" or img["iso_639_1"] == "pt":
                    links.append(DEFAULT_IMAGE_URL.format(img["file_path"]))

            return "\n".join(links)

    def search_movie(self, title: str) -> Union[list, None]:
        """
        Search movie using the title of the movie (or part).

        Parameters
        ----------
        title: str
            String with the title or part of it to search for.
            Example: 'John Wick'

        Returns
        -------
            A list with all result for the title.
        """
        response = self._retrive_url(
            DEFAULT_URL_SEARCH.format(title.replace(" ", "%20"))
        )
        results = self.format_response(response)
        if results:
            return results

        return None

    def get_cast(self, id: int) -> Union[str, None]:
        """
        From the movie with 'id' we get all names
        from the cast.

        Parameters
        ----------
        id: int
            TMDB id for the movie.

        Returns
        -------
            String with the cast names separated by comma.
        """
        response = self._retrive_url(DEFAULT_URL_CAST.format(str(id)))
        results = self.format_cast(response)
        if results:
            return results

        return None

    def search_tv_show(self, title: str) -> str:
        """
        Search a tv show using its title (or part).

        Parameters
        ----------
        title: str
            String with the title or part of it to search for.
            Example: 'Breaking Bad'

        Returns
        -------
            A list with all result for the title.
        """
        response = self._retrive_url(
            DEFAULT_URL_SEARCH_SERIE.format(title.replace(" ", "%20"))
        )
        results = self.format_response_tv_show(response)
        if results:
            return results

        return None

    def get_cast_tv_show(self, id: int) -> Union[str, None]:
        """
        From the tv show with 'id' we get all names
        from the cast.

        Parameters
        ----------
        id: int
            TMDB id for the tv show.

        Returns
        -------
            String with the cast names separated by comma.
        """
        response = self._retrive_url(DEFAULT_URL_CAST_SERIE.format(str(id)))
        results = self.format_cast(response)
        if results:
            return results

        return None

    def get_poster_movie(self, id: int) -> Union[str, None]:
        """
        From the movie with 'id' we get all image links.

        Parameters
        ----------
        id: int
            TMDB id for the movie.

        Returns
        -------
            String with the link separated by comma.
        """
        response = self._retrive_url(DEFAULT_URL_IMAGES.format(str(id)))
        results = self.get_img_links(response)
        if results:
            return results

        return None

    def get_poster_serie(self, id: int) -> Union[str, None]:
        """
        From the tv show with 'id' we get all image links.

        Parameters
        ----------
        id: int
            TMDB id for the movie.

        Returns
        -------
            String with the link separated by comma.
        """
        response = self._retrive_url(DEFAULT_URL_IMAGES_SERIE.format(str(id)))
        results = self.get_img_links(response)
        if results:
            return results

        return None
