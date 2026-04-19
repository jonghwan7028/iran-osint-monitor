from __future__ import annotations

import hashlib
import posixpath
import re
from datetime import datetime
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "oc",
    "ved",
    "usg",
    "at_medium",
    "at_campaign",
    "at_platform",
    "at_ptr_name",
    "at_ptr_type",
    "at_campaign_type",
    "rss",
    "output",
}

KNOWN_PLACE_COORDS: dict[str, tuple[str, float, float]] = {
    # Specific bases and facilities
    "prince sultan air base": ("Prince Sultan Air Base", 24.0620, 47.5800),
    "al udeid": ("Al Udeid Air Base", 25.1170, 51.3140),
    "ali al salem": ("Ali Al Salem Air Base", 29.3467, 47.5211),
    "king fahd causeway": ("King Fahd Causeway", 26.12, 50.33),
    "akrotiri": ("RAF Akrotiri, Cyprus", 34.5907, 32.9878),
    # Iran nuclear and military sites
    "fordow": ("Fordow", 34.8840, 50.9960),
    "natanz": ("Natanz", 33.7250, 51.7250),
    "isfahan": ("Isfahan", 32.6546, 51.6680),
    "khondab": ("Khondab (Arak)", 34.38, 49.24),
    "parchin": ("Parchin", 35.52, 51.78),
    # Iran cities
    "tehran": ("Tehran", 35.6892, 51.3890),
    "tabriz": ("Tabriz", 38.0962, 46.2738),
    "bandar abbas": ("Bandar Abbas", 27.1832, 56.2666),
    "bushehr": ("Bushehr", 28.9234, 50.8203),
    "kharg island": ("Kharg Island", 29.2610, 50.3300),
    "kermanshah": ("Kermanshah", 34.3142, 47.0650),
    "shiraz": ("Shiraz", 29.5918, 52.5836),
    "kashan": ("Kashan", 33.98, 51.43),
    "karaj": ("Karaj", 35.8400, 50.9391),
    "qom": ("Qom", 34.6416, 50.8746),
    "dezful": ("Dezful", 32.3836, 48.4036),
    "yazd": ("Yazd", 31.8974, 54.3569),
    "khorramshahr": ("Khorramshahr", 30.4264, 48.1661),
    "chabahar": ("Chabahar", 25.2919, 60.6430),
    # Other key locations
    "baghdad": ("Baghdad", 33.3152, 44.3661),
    "damascus": ("Damascus", 33.5138, 36.2765),
    "tel aviv": ("Tel Aviv", 32.0853, 34.7818),
    "haifa": ("Haifa", 32.7940, 34.9896),
    "jerusalem": ("Jerusalem", 31.7683, 35.2137),
    "beersheba": ("Beersheba", 31.2518, 34.7913),
    "sanaa": ("Sanaa", 15.3694, 44.1910),
    "dubai": ("Dubai", 25.2048, 55.2708),
    "fujairah": ("Fujairah", 25.1288, 56.3264),
    "istanbul": ("Istanbul", 41.0082, 28.9784),
    "dortyol": ("Dortyol, Hatay", 36.85, 36.22),
    "galle": ("Galle, Sri Lanka", 6.0535, 80.2210),
    "manama": ("Manama, Bahrain", 26.2285, 50.5860),
    "kuwait": ("Kuwait", 29.3759, 47.9774),
    # Water bodies and regions
    "red sea": ("Red Sea", 20.0000, 38.0000),
    "persian gulf": ("Persian Gulf", 26.0000, 52.0000),
    "gulf of oman": ("Gulf of Oman", 23.7000, 58.0000),
    "strait of hormuz": ("Strait of Hormuz", 26.5667, 56.2500),
    # Countries
    "saudi arabia": ("Saudi Arabia", 23.8859, 45.0792),
    "saudi": ("Saudi Arabia", 23.8859, 45.0792),
    "iran": ("Iran", 32.4279, 53.6880),
    "iraq": ("Iraq", 33.2232, 43.6793),
    "syria": ("Syria", 34.8021, 38.9968),
    "qatar": ("Qatar", 25.3548, 51.1839),
    "israel": ("Israel", 31.0461, 34.8516),
    "yemen": ("Yemen", 15.5527, 48.5164),
    "oman": ("Oman", 21.5126, 55.9233),
    "uae": ("United Arab Emirates", 23.4241, 53.8478),
    "united arab emirates": ("United Arab Emirates", 23.4241, 53.8478),
    "jordan": ("Jordan", 30.5852, 36.2384),
    "lebanon": ("Lebanon", 33.8547, 35.8623),
    "bahrain": ("Bahrain", 26.0667, 50.5577),
    "cyprus": ("Cyprus", 35.1264, 33.4299),
    "turkey": ("Turkey", 38.9637, 35.2433),
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def safe_parse_date(date_text: str | None) -> datetime | None:
    if not date_text:
        return None
    try:
        from dateutil import parser
        return parser.parse(date_text)
    except Exception:
        return None


def first_match(text: str, candidates: Iterable[str]) -> str | None:
    lowered = text.lower()
    for c in candidates:
        if c.lower() in lowered:
            return c
    return None


def _normalize_netloc(netloc: str) -> str:
    netloc = (netloc or "").lower().strip()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def canonicalize_url(url: str) -> str:
    raw = normalize_whitespace(url)
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
    except Exception:
        return raw
    scheme = parsed.scheme.lower() or "https"
    netloc = _normalize_netloc(parsed.netloc)
    path = parsed.path or "/"
    path = posixpath.normpath(path)
    if not path.startswith("/"):
        path = f"/{path}"
    query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=False):
        if key.lower() in TRACKING_PARAMS:
            continue
        query_pairs.append((key, value))
    query_pairs.sort()
    query = urlencode(query_pairs, doseq=True)
    fragment = ""
    canonical = urlunparse((scheme, netloc, path, "", query, fragment))
    return canonical.rstrip("/") if canonical.endswith("/") and path != "/" else canonical


def publisher_domain(url: str) -> str:
    try:
        return _normalize_netloc(urlparse(url).netloc)
    except Exception:
        return ""


def infer_location_from_text(text: str) -> tuple[str | None, float | None, float | None]:
    lowered = normalize_whitespace(text).lower()
    if not lowered:
        return None, None, None

    # longest-key-first matching so specific places beat countries
    for key in sorted(KNOWN_PLACE_COORDS.keys(), key=len, reverse=True):
        if key in lowered:
            label, lat, lon = KNOWN_PLACE_COORDS[key]
            return label, lat, lon

    # generic patterns that often appear in headlines
    patterns = [
        (r"\bsaudi\s+base\b", "Saudi Arabia"),
        (r"\biranian\b", "Iran"),
        (r"\biran\b", "Iran"),
        (r"\bsaudi\b", "Saudi Arabia"),
        (r"\bisraeli?\b", "Israel"),
        (r"\bqatari?\b", "Qatar"),
        (r"\biraqi?\b", "Iraq"),
        (r"\byemeni?\b", "Yemen"),
    ]
    for pattern, label in patterns:
        if re.search(pattern, lowered):
            for key, (name, lat, lon) in KNOWN_PLACE_COORDS.items():
                if name == label:
                    return name, lat, lon

    return None, None, None


REGIONAL_FALLBACKS: dict[str, tuple[str, float, float]] = {
    "middle east": ("Middle East", 29.5, 47.5),
    "gulf region": ("Gulf Region", 26.0, 51.0),
    "arabian gulf": ("Persian Gulf", 26.0, 52.0),
}


def choose_fallback_location(*texts: str) -> tuple[str | None, float | None, float | None]:
    merged = normalize_whitespace(" ".join([t for t in texts if t]))
    name, lat, lon = infer_location_from_text(merged)
    if lat is not None and lon is not None:
        return name, lat, lon
    lowered = merged.lower()
    for key, value in REGIONAL_FALLBACKS.items():
        if key in lowered:
            return value
    return ("Middle East", 29.5, 47.5) if merged else (None, None, None)
