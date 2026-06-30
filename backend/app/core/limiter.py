from slowapi import Limiter


def get_real_ip(request) -> str:
    # Render (y la mayoría de proxies) pasan la IP real en X-Forwarded-For
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host or "unknown"


limiter = Limiter(key_func=get_real_ip)
