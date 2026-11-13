import httpx

from .node_security import decrypt_node_token


class NodeConnectionError(Exception):
    pass


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

    token = decrypt_node_token(encrypted_token)

    url = f"http://{host}:{port}{endpoint}"

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
        host=host,
        port=port,
        encrypted_token=encrypted_token,
        endpoint="/api/v1/ping",
    )


async def get_node_metrics(
    host: str,
    port: int,
    encrypted_token: str,
):
    return await request_node(
        host=host,
        port=port,
        encrypted_token=encrypted_token,
        endpoint="/api/v1/metrics",
    )
