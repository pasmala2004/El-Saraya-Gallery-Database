"""API tests for the Product module."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _create_category(client: AsyncClient, name: str = "Windows") -> dict:
    response = await client.post("/api/v1/product-categories", json={"name": name})
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/product-categories",
        json={"name": "  Doors  "},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Doors"
    assert "id" in data

    duplicate = await client.post(
        "/api/v1/product-categories",
        json={"name": "Doors"},
    )
    assert duplicate.status_code == 409


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient) -> None:
    category = await _create_category(client, "Windows")
    response = await client.post(
        "/api/v1/products",
        json={
            "category_id": category["id"],
            "name": "  Sliding Window  ",
            "active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sliding Window"
    assert data["category_id"] == category["id"]
    assert data["active"] is True


@pytest.mark.asyncio
async def test_duplicate_product(client: AsyncClient) -> None:
    category = await _create_category(client, "Windows")
    payload = {
        "category_id": category["id"],
        "name": "Casement Window",
        "active": True,
    }
    first = await client.post("/api/v1/products", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/products", json=payload)
    assert second.status_code == 409
    assert second.json()["code"] == "DuplicateEntityError"


@pytest.mark.asyncio
async def test_filter_by_category(client: AsyncClient) -> None:
    windows = await _create_category(client, "Windows")
    doors = await _create_category(client, "Doors")

    await client.post(
        "/api/v1/products",
        json={"category_id": windows["id"], "name": "Fixed Window", "active": True},
    )
    await client.post(
        "/api/v1/products",
        json={"category_id": doors["id"], "name": "French Door", "active": True},
    )

    response = await client.get(
        "/api/v1/products",
        params={"category": windows["id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Fixed Window"
    assert data["items"][0]["category_id"] == windows["id"]


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient) -> None:
    category = await _create_category(client, "Windows")
    created = await client.post(
        "/api/v1/products",
        json={
            "category_id": category["id"],
            "name": "Awning Window",
            "active": True,
        },
    )
    product_id = created.json()["id"]

    response = await client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Awning Window XL", "active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Awning Window XL"
    assert data["active"] is False


@pytest.mark.asyncio
async def test_list_active_products(client: AsyncClient) -> None:
    category = await _create_category(client, "Smart Locks")
    await client.post(
        "/api/v1/products",
        json={"category_id": category["id"], "name": "Active Lock", "active": True},
    )
    await client.post(
        "/api/v1/products",
        json={"category_id": category["id"], "name": "Retired Lock", "active": False},
    )

    response = await client.get("/api/v1/products", params={"active": True})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Active Lock"
    assert data["items"][0]["active"] is True
