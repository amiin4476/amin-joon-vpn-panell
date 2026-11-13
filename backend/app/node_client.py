
import ipaddress

import httpx

from .node_security import decrypt_node_token


class NodeConnectionError(Exception):
    pass


def format_node_host(host: str) -> str:
    if not host:
        raise NodeConnectionError("Node host is missing")

    host = host.strip()

    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]

    try:
        address = ipaddress.ip_address(host)

        if isinstance(address, ipaddress.IPv6Address):
            return f"[{address.compressed}]"

        return address.compressed

    except ValueError:
        if any(char in host for char in "/?#@:"):
            raise NodeConnectionError("Invalid node host")

        return host


async def request_node(
    host: str,
    port: int,
    encrypted_token: str,
    endpoint: str,
    timeout: float = 10.0,
):
    if not host or not encrypted_token:
        raise NodeConnectionError(
            "Node host or credentials are missing"
        )

    if not 1 <= port <= 65535:
        raise NodeConnectionError("Invalid node port")

    if not endpoint.startswith("/") or endpoint.startswith("//"):
        raise NodeConnectionError("Invalid node endpoint")

    token = decrypt_node_token(encrypted_token)

    formatted_host = format_node_host(host)
    url = f"https://{formatted_host}:{port}{endpoint}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=False,
        ) as client:
            response = await client.get(
                url,
                headers=headers,
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as exc:
        raise NodeConnectionError(
            f"Could not connect to node: {exc}"
        ) from None


async def check_node_health(
    host: str,
    port: int,
    encrypted_token: str,
):
    return await request_node(
        host,
        port,
        encrypted_token,
        "/api/v1/ping",
    )


async def get_node_metrics(
    host: str,
    port: int,
    encrypted_token: str,
):
    return await request_node(
        host,
        port,
        encrypted_token,
        "/api/v1/metrics",
    )
