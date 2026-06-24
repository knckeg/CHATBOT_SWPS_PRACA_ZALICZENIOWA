"""Klient repozytorium naukowego SWPS (DSpace).

Udostępnia wyszukiwanie publikacji przez publiczne REST API DSpace
(`/server/api/discover/search/objects`). Używane jako źródło wiedzy
„na żądanie" — wywoływane przez model dopiero, gdy pytanie tego wymaga.
Korzysta wyłącznie z biblioteki standardowej (bez dodatkowych zależności).
"""

import json
import urllib.parse
import urllib.request
import requests
import os

SEARCH_URL = "https://share.swps.edu.pl/server/api/discover/search/objects"
TIMEOUT = 20
# Cloudflare przed repozytorium blokuje domyślny User-Agent urllib (403),
# dlatego podajemy nagłówek przeglądarki.
_HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
}

def search_as_text(query: str) -> str:
    """Przeszukuje Repozytorium Naukowe SWPS (API DSpace) i zwraca sformatowany tekst."""
    if os.getenv("RAG_ENABLED", "true").lower() != "true":
        return "Funkcja RAG/Wyszukiwanie w repozytorium jest wyłączona."

    # Adres API DSpace 7 Uniwersytetu SWPS
    url = "https://share.swps.edu.pl/server/api/discover/search/objects"
    params = {
        "query": query,
        "size": 3  # Pobieramy 3 najbardziej trafne publikacje
    }
    
    # Nagłówek chroniący przed blokadą 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/hal+json"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Błąd repozytorium SWPS: Serwer zwrócił status {response.status_code}"

        data = response.json()
        search_results = data.get("_embedded", {}).get("searchResult", {}).get("_embedded", {}).get("objects", [])

        if not search_results:
            return f"Brak wyników w repozytorium SWPS dla zapytania: '{query}'."

        formatted_results = []
        for obj in search_results:
            item = obj.get("_embedded", {}).get("indexableObject", {})
            metadata = item.get("metadata", {})

            # Wyciągamy kluczowe metadane publikacji
            title = metadata.get("dc.title", [{}])[0].get("value", "Brak tytułu")
            authors = [author.get("value") for author in metadata.get("dc.contributor.author", [])]
            date = metadata.get("dc.date.issued", [{}])[0].get("value", "Data nieznana")[:4]
            handle = item.get("handle", "")
            link = f"https://share.swps.edu.pl/handle/{handle}" if handle else "Brak bezpośredniego linku"

            authors_str = ", ".join(authors) if authors else "Autor nieznany"
            
            formatted_results.append(
                f"- **Tytuł**: {title}\n"
                f"  **Autorzy**: {authors_str}\n"
                f"  **Rok**: {date}\n"
                f"  **Link**: {link}\n"
            )

        return "Znalezione publikacje w Repozytorium SWPS:\n\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"Wystąpił błąd podczas próby połączenia z repozytorium SWPS: {str(e)}"

def _first(md: dict, *keys: str) -> str:
    """Pierwsza niepusta wartość spośród podanych pól metadanych."""
    for key in keys:
        for entry in md.get(key, []):
            value = (entry.get("value") or "").strip()
            if value and value.lower() != "brak":
                return value
    return ""


def _all(md: dict, *keys: str) -> list[str]:
    """Wszystkie niepuste wartości spośród podanych pól metadanych."""
    out: list[str] = []
    for key in keys:
        for entry in md.get(key, []):
            value = (entry.get("value") or "").strip()
            if value and value.lower() != "brak":
                out.append(value)
    return out


def search(query: str, size: int = 5) -> list[dict]:
    """Wyszukuje pozycje w repozytorium i zwraca uproszczone rekordy."""
    params = urllib.parse.urlencode(
        {"query": query, "size": size, "dsoType": "item"}
    )
    request = urllib.request.Request(f"{SEARCH_URL}?{params}", headers=_HEADERS)
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        data = json.load(response)

    objects = (
        data.get("_embedded", {})
        .get("searchResult", {})
        .get("_embedded", {})
        .get("objects", [])
    )

    results = []
    for obj in objects:
        item = obj.get("_embedded", {}).get("indexableObject", {})
        md = item.get("metadata", {})
        handle = item.get("handle")
        results.append(
            {
                "title": _first(md, "dc.title") or item.get("name", ""),
                "authors": _all(md, "dc.contributor.author", "dc.contributor.editor"),
                "year": _first(md, "dc.date.issued")[:4],
                "abstract": _first(
                    md, "dc.abstract.pl", "dc.description.abstract", "dc.abstract.en"
                ),
                "subjects": _all(md, "dc.subject.pl", "dc.subject.en"),
                "url": _first(md, "dc.identifier.uri")
                or (f"https://share.swps.edu.pl/handle/{handle}" if handle else ""),
            }
        )
    return results
