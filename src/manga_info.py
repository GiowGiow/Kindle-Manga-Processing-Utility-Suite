from pathlib import Path
import shutil
import tempfile
from jikanpy import Jikan
from fuzzywuzzy import process
import logging

import requests

NSFW = False
FUZZY_MATCH_THRESHOLD = 85
# Initialize the Jikan API
jikan = Jikan()
logging.basicConfig(level=logging.INFO)


def search_manga_jikan(manga_name):
    """
    Searches for a manga title using the Jikan API with fuzzy matching.
    Returns the best matching manga data if found.
    """
    try:
        # Perform a search query using Jikan
        search_results = jikan.search(
            "manga",
            manga_name,
            page=1,
            parameters={
                "limit": 5,
            },
        )
    except Exception as e:
        logging.error(f"Error fetching data from Jikan API: {e}")
        return None

    # Extract manga data from the response
    manga_list = search_results.get("data", [])
    if not manga_list:
        logging.warning(f"No matches found on Jikan for '{manga_name}'.")
        return None

    # Extract all possible titles for fuzzy matching
    titles = []
    for manga in manga_list:
        # Add main title
        titles.append((manga.get("title", ""), manga))

        # Add titles from the 'titles' list
        for title_entry in manga.get("titles", []):
            titles.append((title_entry.get("title", ""), manga))

        # Add synonyms if available
        for synonym in manga.get("title_synonyms", []):
            titles.append((synonym, manga))

        # Add English title if available
        if manga.get("title_english"):
            titles.append((manga.get("title_english"), manga))

    title_names = [title for title, _ in titles]
    # Perform fuzzy matching
    best_match, score = process.extractOne(manga_name, title_names)
    if score > FUZZY_MATCH_THRESHOLD:
        for title, manga in titles:
            if title == best_match:
                logging.info(f"Best match on Jikan: {best_match} (Score: {score})")
                return manga, best_match
    else:
        logging.warning(f"No good match found for '{manga_name}' on Jikan.")
        return None


def fetch_manga_info_jikan(manga_name):
    """
    Fetches detailed manga information using the Jikan API.
    Returns a dictionary containing relevant metadata.
    """
    # Perform fuzzy search with Jikan
    logging.debug(f"Trying to match '{manga_name}'...")
    search_result = search_manga_jikan(manga_name)
    if not search_result:
        return None

    manga_result, manga_title = search_result

    # Extract relevant details
    authors = manga_result.get("authors", [])
    author_names = (
        [author["name"] for author in authors] if authors else ["Unknown Author"]
    )
    author_str = ", ".join(author_names)

    manga_title = manga_title.strip('"') if manga_title else "Unknown Title"

    # Extract synopsis
    synopsis = manga_result.get("synopsis", "No synopsis available.")

    # Extract genres
    genres = [genre["name"] for genre in manga_result.get("genres", [])]
    genres_str = ", ".join(genres) if genres else "No genres available."

    # Extract score
    score = manga_result.get("score", "N/A")

    cover_image_url = (
        manga_result.get("images", {}).get("jpg", {}).get("large_image_url", None)
    )

    return {
        "title": manga_title,
        "author": author_str,
        "summary": synopsis,
        "genres": genres_str,
        "score": score,
        "cover_image_url": cover_image_url,
    }


def download_cover_image(cover_image_url: str, manga_name: str) -> Path | None:
    try:
        response = requests.get(cover_image_url, stream=True)
        response.raise_for_status()

        image_extension = Path(cover_image_url).suffix
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=image_extension
        ) as cover_tmp:
            cover_image_path = Path(cover_tmp.name)
            with open(cover_image_path, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)

        logging.debug(f"Cover image downloaded and saved to '{cover_image_path}'.")
        return cover_image_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading cover image: {e}")
        return None


# Example usage
if __name__ == "__main__":
    result = fetch_manga_info_jikan("Berserk Prologue")
