import httpx, re

# Formatos soportados de Google Maps:
#   .../@31.6904,-106.4245,15z
#   ...?q=31.6904,-106.4245
#   ...!3d31.6904!4d-106.4245   (URLs de "place" con data=)
PATRONES = [
    re.compile(r'@(-?\d+\.\d+),(-?\d+\.\d+)'),
    re.compile(r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)'),
    re.compile(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)'),
]

IS_SHORT_LINK = re.compile(r'https?://(maps\.app\.goo\.gl|goo\.gl/maps)/\S+')

def extract(url):
    for patron in PATRONES:
        match = patron.search(url)
        if match:
            return float(match.group(1)), float(match.group(2))
    return None

def handle_short_link(url, max_jumps):
    actual = url
    with httpx.Client(follow_redirects=False, timeout=5.0) as client:
        for _ in range(max_jumps):
            response = client.get(actual)
            if response.status_code in (301, 302, 303, 307, 308) and "location" in response.headers:
                actual = response.headers("location")
                if extract(actual):
                    return actual
            else:
                break
    return actual

def extract_coords_from_url(url):
    url = url.strip()
    coords = extract(url)
    if coords:
        return coords

    if IS_SHORT_LINK.match(url):
        large_url = handle_short_link(url)
        return extract(large_url)

    return None
