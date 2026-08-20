from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
import httpx

from app.core.security import get_current_user, require_admin


app = FastAPI(
    title="E-Commerce API Gateway"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SECURITY
# ============================================================


# ============================================================
# SERVICE URLs
# ============================================================

USER_SERVICE_URL = "http://ecommerce-user-service:8000"
PRODUCT_SERVICE_URL = "http://ecommerce-product-service:8001"
ORDER_SERVICE_URL = "http://ecommerce-order-service:8002"
PAYMENT_SERVICE_URL = "http://ecommerce-payment-service:8003"

# ============================================================
# GENERIC PROXY
# ============================================================

async def proxy_request(
    request: Request,
    service_url: str,
    path: str = ""
):
    
    url = f"{service_url}/{path}"

    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {service_url}"
            )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {
                "content-encoding",
                "transfer-encoding",
                "content-length"
            }
        },
        media_type=response.headers.get("content-type")
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
async def root():
    return {"message": "E-Commerce API Gateway is running"}


# ============================================================
# AUTH — PUBLIC 
# ============================================================

@app.post("/auth/register")
async def auth_register(request: Request):
    return await proxy_request(request, USER_SERVICE_URL, "auth/register")


@app.post("/auth/login")
async def auth_login(request: Request):
    return await proxy_request(request, USER_SERVICE_URL, "auth/login")


# ============================================================
# USERS — token header required, actual verification downstream
# ============================================================

@app.api_route(
    "/users",
    methods=["GET"],
    dependencies=[Depends(get_current_user)]
)
async def users(request: Request):
    return await proxy_request(request, USER_SERVICE_URL, "users/")


@app.api_route(
    "/users/me",
    methods=["GET"],
    dependencies=[Depends(get_current_user)]
)
async def user_me(request: Request):
    return await proxy_request(request, USER_SERVICE_URL, "users/me")


@app.api_route(
    "/users/{user_id}",
    methods=["GET", "PUT", "DELETE"],
    dependencies=[Depends(get_current_user)]
)
async def user_by_id(user_id: int, request: Request):
    return await proxy_request(request, USER_SERVICE_URL, f"users/{user_id}")


# ============================================================
# PRODUCTS — token header required, role check downstream
# ============================================================

@app.get(
    "/products",
    dependencies=[Depends(get_current_user)]
)
async def get_products_route(request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, "products/")


@app.post(
    "/products",
    dependencies=[Depends(require_admin)]
)
async def create_product_route(request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, "products/")


@app.get(
    "/products/{product_id}",
    dependencies=[Depends(get_current_user)]
)
async def get_product_route(product_id: int, request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, f"products/{product_id}")


@app.put(
    "/products/{product_id}",
    dependencies=[Depends(require_admin)]
)
async def update_product_route(product_id: int, request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, f"products/{product_id}")


@app.delete(
    "/products/{product_id}",
    dependencies=[Depends(require_admin)]
)
async def delete_product_route(product_id: int, request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, f"products/{product_id}")


@app.patch(
    "/products/{product_id}/stock",
    dependencies=[Depends(get_current_user)]
)
async def product_stock(product_id: int, request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, f"products/{product_id}/stock")


@app.patch(
    "/products/{product_id}/restore-stock",
    dependencies=[Depends(get_current_user)]
)
async def product_restore_stock(product_id: int, request: Request):
    return await proxy_request(request, PRODUCT_SERVICE_URL, f"products/{product_id}/restore-stock")

# ============================================================
# ORDERS — token header required, ownership/role check downstream
# ============================================================
 
@app.post(
    "/orders",
    dependencies=[Depends(get_current_user)]
)
async def create_order_route(request: Request):
    return await proxy_request(request, ORDER_SERVICE_URL, "orders/")
 
 
@app.get(
    "/orders/my",
    dependencies=[Depends(get_current_user)]
)
async def get_my_orders_route(request: Request):
    return await proxy_request(request, ORDER_SERVICE_URL, "orders/my")
 
 
@app.get(
    "/orders/{order_id}",
    dependencies=[Depends(get_current_user)]
)
async def get_order_route(order_id: int, request: Request):
    return await proxy_request(request, ORDER_SERVICE_URL, f"orders/{order_id}")
 
 
@app.patch(
    "/orders/{order_id}/status",
    dependencies=[Depends(require_admin)]
)
async def update_order_status_route(order_id: int, request: Request):
    return await proxy_request(request, ORDER_SERVICE_URL, f"orders/{order_id}/status")
 
 
@app.patch(
    "/orders/{order_id}/cancel",
    dependencies=[Depends(get_current_user)]
)
async def cancel_order_route(order_id: int, request: Request):
    return await proxy_request(request, ORDER_SERVICE_URL, f"orders/{order_id}/cancel")
 
 

 
 
# ============================================================
# PAYMENTS — token header required, ownership check downstream
# ============================================================
 
@app.post(
    "/payments",
    dependencies=[Depends(get_current_user)]
)
async def create_payment_route(request: Request):
    return await proxy_request(request, PAYMENT_SERVICE_URL, "payments/")
 
 
@app.get(
    "/payments/my",
    dependencies=[Depends(get_current_user)]
)
async def get_my_payments_route(request: Request):
    return await proxy_request(request, PAYMENT_SERVICE_URL, "payments/my")
 
 
@app.get(
    "/payments/{payment_id}",
    dependencies=[Depends(get_current_user)]
)
async def get_payment_route(payment_id: int, request: Request):
    return await proxy_request(request, PAYMENT_SERVICE_URL, f"payments/{payment_id}")