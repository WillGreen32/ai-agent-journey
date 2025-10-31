import requests

def paginate(url, session, cache=None):
    """Generator that yields each page of results."""
    while url:
        if cache and (cached := cache.get(url)):
            yield cached
            next_link = None
        else:
            r = session.get(url)
            data = r.json()
            yield data

            # Extract 'next' page URL from GitHub's Link header if it exists
            links = r.headers.get("Link")
            next_link = None
            if links:
                parts = [p.strip() for p in links.split(",")]
                for part in parts:
                    if 'rel="next"' in part:
                        next_link = part[part.find("<") + 1 : part.find(">")]
                        break

        url = next_link
