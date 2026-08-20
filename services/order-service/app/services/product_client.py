import httpx

from app.core.settings import PRODUCT_SERVICE_URL


def get_product(product_id: int, token: str):

    response = httpx.get(
        f"{PRODUCT_SERVICE_URL}/products/{product_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=5.0
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()

def update_product_stock(
    product_id: int,
    quantity: int,
    token: str
):
    response = httpx.patch(
        f"{PRODUCT_SERVICE_URL}/products/{product_id}/stock",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "quantity": quantity
        },
        timeout=5.0
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()

def restore_product_stock(
    product_id: int,
    quantity: int,
    token: str
):
    response = httpx.patch(
        f"{PRODUCT_SERVICE_URL}/products/{product_id}/restore-stock",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "quantity": quantity
        },
        timeout=5.0
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()