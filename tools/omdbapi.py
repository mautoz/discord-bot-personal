#!/usr/bin/env python3

import os
import re
import requests
import logging
import sys
from typing import Union
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
DEFAULT_URL = "https://www.omdbapi.com/{0}={1}&apikey={2}"


class OMDBAPI:
    """
    Class used by my bots to search info from movies, tv show
    and other thing from IMDB using the free API called OMDB API.
    """

    def __init__(self) -> None:
        self._api_key = os.getenv("APIKEY")

    def _retrive_url(self, url: str) -> Union[dict, None]:
        r = requests.get(url, timeout=5)
        logging.info("Status code: %s", str(r.status_code))

        if r.status_code == 200:
            return r.json()

        return None

    def search_title(self, title: str) -> Union[list, None]:
        """
        Search for the title of the movie, tv show...

        Parameters
        ----------
        title: str
            String with the title or part of it to search for.
            Example: 'John Wick'

        Returns
        -------
            A list with all result for the title.
        """
        title_format = re.sub(r"\s+", "+", title)
        url = DEFAULT_URL.format("?s", title_format, self._api_key)

        response = self._retrive_url(url)
        results = response.get("Search", None)
        imdb_list = ["ID\t\tTítulo\t\t\t\tAno"]
        if results:
            for result in results:
                imdb_id = str(result.get("imdbID", None))[:15].ljust(15)
                title = str(result.get("Title", None))[:30].ljust(25)
                buffer = f"{imdb_id}\t{title}\t{result.get('Year', None)}"
                imdb_list.append(buffer)
            return imdb_list

        return None

    def search_imdb_id(self, imdb_id: str, is_full: bool = False) -> str:
        """
        Search for the imdb title using the imdb id.

        Parameters
        ----------
        imdb_id: str
            You can get the ID using the method search_title().
        is_full: bool (optional)
            Deafult is false and the result is not complete. With
            is_full True, you will have more information.

        Returns
        -------
            A string with info from the imdb id. We return title,
            year, director, genre, plot and a link to the poster.
        """
        url = DEFAULT_URL.format("?i", imdb_id, self._api_key)
        if is_full:
            url += "&plot=full"

        response = self._retrive_url(url)

        return f"""
            Título: {response.get('Title', None)} ({response.get('Year', None)})\n
            Diretor: {response.get('Director', None)}\n
            Elenco (parcial): {response.get('Actors', None)}\n
            Gênero: {response.get('Genre', None)}\n
            Plot: {response.get('Plot', None)}\n
            {response.get('Poster', None)}\n
        """


# if __name__ == "__main__":
#     omdbapi = OMDBAPI()
#     #     r = omdbapi.search_title("John wick")
#     #     if r:
#     #         results = "\n".join(r)
#     #         print(results)
#     #     else:
#     #         print("no result")
#     r = omdbapi.search_imdb_id("tt2911666", is_full=True)
#     print(r)
