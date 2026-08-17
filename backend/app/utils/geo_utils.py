import httpx
import re
import ipaddress
import urllib.parse

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

_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def _es_host_privado(host: str) -> bool:
    try:
        addr = ipaddress.ip_address(host)
        return any(addr in net for net in _PRIVATE_NETS)
    except ValueError:
        return False


def extract(url):
    for patron in PATRONES:
        match = patron.search(url)
        if match:
            return float(match.group(1)), float(match.group(2))
    return None


def handle_short_link(url: str, max_jumps: int = 5) -> str:
    actual = url
    with httpx.Client(follow_redirects=False, timeout=5.0) as client:
        for _ in range(max_jumps):
            parsed = urllib.parse.urlparse(actual)
            if parsed.scheme not in ("http", "https"):
                break
            if _es_host_privado(parsed.hostname or ""):
                break
            response = client.get(actual)
            if response.status_code in (301, 302, 303, 307, 308) and "location" in response.headers:
                actual = response.headers["location"]
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
