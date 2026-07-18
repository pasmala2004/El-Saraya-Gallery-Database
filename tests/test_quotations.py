"""API tests for the Quotation module."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _seed_catalog(client: AsyncClient) -> dict:
    customer = (
        await client.post(
            "/api/v1/customers",
            json={"full_name": "Quotation Client", "phone_number": "01055556666"},
        )
    ).json()
    category = (
        await client.post("/api/v1/product-categories", json={"name": "Windows"})
    ).json()
    product = (
        await client.post(
            "/api/v1/products",
            json={
                "category_id": category["id"],
                "name": "Sliding Window",
                "active": True,
            },
        )
    ).json()
    return {"customer": customer, "category": category, "product": product}


@pytest.mark.asyncio
async def test_create_quotation(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    response = await client.post(
        "/api/v1/quotations",
        json={
            "customer_id": seed["customer"]["id"],
            "discount": "0.00",
            "notes": "Draft estimate",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["customer_id"] == seed["customer"]["id"]
    assert data["total_price"] == "0.00"
    assert data["final_price"] == "0.00"
    assert data["quotation_number"].startswith("Q-")


@pytest.mark.asyncio
async def test_add_items_and_calculate_totals(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    quotation = (
        await client.post(
            "/api/v1/quotations",
            json={"customer_id": seed["customer"]["id"]},
        )
    ).json()

    item_resp = await client.post(
        f"/api/v1/quotations/{quotation['id']}/items",
        json={
            "product_id": seed["product"]["id"],
            "quantity": 2,
            "unit_price": "1500.00",
            "description": "White aluminum\nDouble glazed",
        },
    )
    assert item_resp.status_code == 201
    item = item_resp.json()
    assert item["total_price"] == "3000.00"

    updated = await client.put(
        f"/api/v1/quotations/{quotation['id']}",
        json={"discount": "100.00"},
    )
    assert updated.status_code == 200
    assert updated.json()["final_price"] == "2900.00"

    detail = await client.get(f"/api/v1/quotations/{quotation['id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["total_price"] == "3000.00"
    assert body["discount"] == "100.00"
    assert body["final_price"] == "2900.00"
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_empty_quotation_cannot_be_sent(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    quotation = (
        await client.post(
            "/api/v1/quotations",
            json={"customer_id": seed["customer"]["id"]},
        )
    ).json()

    response = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "sent"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "quotation_requires_items"


@pytest.mark.asyncio
async def test_invalid_customer(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/quotations",
        json={"customer_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "EntityNotFoundError"


@pytest.mark.asyncio
async def test_invalid_status_transition(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    quotation = (
        await client.post(
            "/api/v1/quotations",
            json={"customer_id": seed["customer"]["id"]},
        )
    ).json()
    await client.post(
        f"/api/v1/quotations/{quotation['id']}/items",
        json={
            "product_id": seed["product"]["id"],
            "quantity": 1,
            "unit_price": "1000.00",
        },
    )

    # draft → approved is not allowed (must go through sent)
    response = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "approved"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_quotation_status_transition"


@pytest.mark.asyncio
async def test_negotiation_flow(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    quotation = (
        await client.post(
            "/api/v1/quotations",
            json={"customer_id": seed["customer"]["id"]},
        )
    ).json()
    await client.post(
        f"/api/v1/quotations/{quotation['id']}/items",
        json={
            "product_id": seed["product"]["id"],
            "quantity": 1,
            "unit_price": "2000.00",
            "description": "Custom finish",
        },
    )

    sent = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "sent"},
    )
    assert sent.status_code == 200
    assert sent.json()["status"] == "sent"

    # Renegotiate: sent → draft → sent → approved
    back = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "draft"},
    )
    assert back.status_code == 200
    assert back.json()["status"] == "draft"

    resent = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "sent"},
    )
    assert resent.status_code == 200

    approved = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "approved"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    # Terminal: cannot go back
    blocked = await client.patch(
        f"/api/v1/quotations/{quotation['id']}/status",
        json={"status": "sent"},
    )
    assert blocked.status_code == 422


@pytest.mark.asyncio
async def test_search_by_status_and_customer(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    other = (
        await client.post(
            "/api/v1/customers",
            json={"full_name": "Other Client", "phone_number": "01077778888"},
        )
    ).json()

    q1 = (
        await client.post(
            "/api/v1/quotations",
            json={"customer_id": seed["customer"]["id"]},
        )
    ).json()
    await client.post(
        f"/api/v1/quotations/{q1['id']}/items",
        json={
            "product_id": seed["product"]["id"],
            "quantity": 1,
            "unit_price": "500.00",
        },
    )
    await client.patch(
        f"/api/v1/quotations/{q1['id']}/status",
        json={"status": "sent"},
    )

    await client.post(
        "/api/v1/quotations",
        json={"customer_id": other["id"]},
    )

    by_status = await client.get("/api/v1/quotations", params={"status": "sent"})
    assert by_status.status_code == 200
    assert by_status.json()["total"] == 1
    assert by_status.json()["items"][0]["status"] == "sent"

    by_customer = await client.get(
        "/api/v1/quotations",
        params={"customer": seed["customer"]["id"]},
    )
    assert by_customer.status_code == 200
    assert by_customer.json()["total"] == 1

    nested = await client.get(
        f"/api/v1/customers/{seed['customer']['id']}/quotations"
    )
    assert nested.status_code == 200
    assert nested.json()["total"] == 1


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient) -> None:
    seed = await _seed_catalog(client)
    for _ in range(3):
        await client.post(
            "/api/v1/quotations",
            json={"customer_id": seed["customer"]["id"]},
        )

    page = await client.get(
        "/api/v1/quotations",
        params={"limit": 2, "offset": 0, "sort_by": "date", "sort_order": "desc"},
    )
    assert page.status_code == 200
    data = page.json()
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2
