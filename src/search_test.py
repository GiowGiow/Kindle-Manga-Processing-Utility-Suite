from jikanpy import Jikan
from fuzzywuzzy import process


def fuzzy_search_manga(query):
    """
    Perform a fuzzy search for manga titles using JikanPy and fuzzywuzzy.
    """
    # Initialize Jikan API
    jikan = Jikan()

    # Search for manga using the Jikan search endpoint
    try:
        search_results = jikan.search("manga", query, page=1)
    except Exception as e:
        print(f"Error querying Jikan API: {e}")
        return None

    # Extract manga titles from the "data" key in the search results
    manga_list = search_results.get("data", [])
    if not manga_list:
        print("No results found.")
        return None

    # Retrieve all titles for fuzzy matching
    titles = [manga["title"] for manga in manga_list]

    # Use fuzzy matching to find the best match
    best_match, score = process.extractOne(query, titles)
    if score > 70:  # Adjust the threshold if necessary
        # Retrieve the best match's details
        for manga in manga_list:
            if manga["title"] == best_match:
                return manga  # Return the full manga data
    else:
        print("No suitable match found.")
        return None


# Example Usage
folder_name = "Monster"
result = fuzzy_search_manga(folder_name)

if result:
    print(f"Best Match: {result['title']}")
    print(f"Synopsis: {result.get('synopsis', 'No synopsis available.')}")
    print(f"Score: {result.get('score', 'No score available.')}")
    print(f"URL: {result.get('url', 'No URL available.')}")
else:
    print("No match found.")
