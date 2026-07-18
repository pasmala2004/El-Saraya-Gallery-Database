"""API tests for the Customer module (reference ERP resource)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/customers",
        json={
            "full_name": "  Ahmed Hassan  ",
            "phone_number": "010 1234 5678",
            "city": "Cairo",
            "notes": "VIP",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Ahmed Hassan"
    assert data["phone_number"] == "+201012345678"
    assert data["city"] == "Cairo"
    assert "id" in data


@pytest.mark.asyncio
async def test_duplicate_phone_number(client: AsyncClient) -> None:
    payload = {
        "full_name": "First Customer",
        "phone_number": "01011112222",
    }
    first = await client.post("/api/v1/customers", json=payload)
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/customers",
        json={
            "full_name": "Second Customer",
            "phone_number": "+20 101 111 2222",
        },
    )
    assert second.status_code == 409
    body = second.json()
    assert body["code"] == "DuplicateEntityError"
    assert "phone_number" in body["detail"]


@pytest.mark.asyncio
async def test_get_customer(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/customers",
        json={"full_name": "Nour Ali", "phone_number": "01099998888"},
    )
    customer_id = created.json()["id"]

    response = await client.get(f"/api/v1/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "Nour Ali"

    missing = await client.get(
        "/api/v1/customers/00000000-0000-0000-0000-000000000000"
    )
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_list_customers(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/customers",
        json={"full_name": "Customer A", "phone_number": "01010000001"},
    )
    await client.post(
        "/api/v1/customers",
        json={"full_name": "Customer B", "phone_number": "01010000002"},
    )

    response = await client.get("/api/v1/customers", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_search_by_name(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/customers",
        json={"full_name": "Omar Khaled", "phone_number": "01020000001", "city": "Cairo"},
    )
    await client.post(
        "/api/v1/customers",
        json={"full_name": "Sara Ibrahim", "phone_number": "01020000002", "city": "Giza"},
    )

    response = await client.get("/api/v1/customers", params={"name": "omar"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["full_name"] == "Omar Khaled"


@pytest.mark.asyncio
async def test_search_by_city(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/customers",
        json={"full_name": "Cairo Client", "phone_number": "01030000001", "city": "Cairo"},
    )
    await client.post(
        "/api/v1/customers",
        json={"full_name": "Alex Client", "phone_number": "01030000002", "city": "Alexandria"},
    )

    response = await client.get("/api/v1/customers", params={"city": "alex"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["city"] == "Alexandria"


@pytest.mark.asyncio
async def test_update_customer(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/customers",
        json={
            "full_name": "Old Name",
            "phone_number": "01040000001",
            "city": "Cairo",
        },
    )
    customer_id = created.json()["id"]

    response = await client.put(
        f"/api/v1/customers/{customer_id}",
        json={"full_name": "New Name", "city": "Giza"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["city"] == "Giza"
    assert data["phone_number"] == "+201040000001"
