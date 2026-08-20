import httpx

from app.core.settings import ORDER_SERVICE_URL


def get_order(
    order_id: int,
    token: str
):
    response = httpx.get(
        f"{ORDER_SERVICE_URL}/orders/{order_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=5.0
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()


def confirm_order(
    order_id: int,
    service_secret: str
):
    response = httpx.patch(
        f"{ORDER_SERVICE_URL}/orders/{order_id}/payment-confirm",
        headers={
            "X-Service-Secret": service_secret
        },
        timeout=5.0
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()