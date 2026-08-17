from slowapi import Limiter

# Solo Nginx (dentro de la red Docker stem-net) puede establecer X-Forwarded-For de confianza.
# Valores de la red interna Docker bridge (172.16.0.0/12) + loopback.
_TRUSTED_PROXIES = {"127.0.0.1", "::1", "172.17.0.1", "172.18.0.1", "172.19.0.1"}


def get_real_ip(request) -> str:
    client_host = request.client.host if request.client else "unknown"
    if client_host in _TRUSTED_PROXIES:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return client_host


limiter = Limiter(key_func=get_real_ip)
