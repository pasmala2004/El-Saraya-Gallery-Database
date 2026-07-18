# Backend Architecture — Repository & Service Foundation

> Status: frozen foundation for all future ERP modules.  
> Do not put domain-specific CRUD here — inherit from these bases instead.

---

## Layer responsibilities

| Layer | Owns | Does not own |
|-------|------|----------------|
| **Repository** | Queries, `add`, `delete`, `flush` | `commit` / `rollback`, business rules |
| **Service** | Business rules, validation, `commit` / `rollback`, refresh | Raw SQL / query details |
| **API route** | HTTP mapping, Depends wiring, translating domain errors → HTTP | Transactions, SQL |
| **Domain exceptions** | Business failure semantics | HTTP status codes |

### Why `commit` lives in the Service

A use-case often spans multiple repositories (e.g. Quotation + QuotationItems + Job). If a repository committed after each write, a later failure would leave partial data. The Service completes the unit of work, then commits once.

```
Route → Service.create(...)
           ├─ repository.create(parent)   # flush
           ├─ repository.create(child)    # flush
           └─ session.commit()            # one transaction
```

---

## Packages

```
app/
  core/exceptions.py      # DomainError hierarchy (not HTTPException)
  core/query.py           # Pagination, Sorting, FilterParams + apply_* helpers
  core/constants.py       # DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT, sort defaults
  api/deps.py             # get_repository / get_service factories
  repositories/base.py    # GenericRepository[+ Protocol]
  services/base.py        # BaseService[+ Protocol]
```

---

## List query helpers (`app.core.query`)

| Type | Purpose |
|------|---------|
| `Pagination` | `limit` / `offset` with defaults (50) and max (100) |
| `Sorting` | `sort_by` / `sort_order` (`asc` \| `desc`, validated) |
| `FilterParams` | Optional `name`, `phone`, `city`, `status` — subclass to extend |

Module functions `apply_pagination`, `apply_sorting`, and `apply_filters` mutate a SQLAlchemy `Select`. `GenericRepository.apply_query_options` / `get_all` call them in order: **filters → sorting → pagination**.

### How future repositories should use them

```python
from dataclasses import dataclass

from app.core.query import FilterParams, Pagination, Sorting
from app.repositories.base import GenericRepository


@dataclass(frozen=True, slots=True)
class CustomerFilters(FilterParams):
    """Extend base filters when the module needs more fields."""
    # e.g. location_url: str | None = None
    pass


class CustomerRepository(GenericRepository[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def list_customers(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: CustomerFilters | None = None,
    ) -> list[Customer]:
        return await self.get_all(
            pagination=pagination or Pagination(),
            sorting=sorting or Sorting(sort_by="created_at", sort_order="desc"),
            filters=filters,
            # Remap generic filter keys → this model's columns (no Customer
            # filter logic lives in core/query.py):
            filter_field_map={"name": "full_name", "phone": "phone_number"},
            allowed_sort_fields=frozenset({
                "full_name",
                "phone_number",
                "city",
                "created_at",
                "updated_at",
            }),
        )
```

Custom queries that are not plain `select(Model)` should still reuse the helpers:

```python
stmt = self.base_select().where(Customer.city.is_not(None))
stmt = self.apply_query_options(
    stmt,
    pagination=pagination,
    sorting=sorting,
    filters=filters,
    filter_field_map={"name": "full_name", "phone": "phone_number"},
    allowed_sort_fields=frozenset({"full_name", "city", "created_at"}),
)
```

Do **not** reimplement `offset` / `limit` / `order_by` in each repository.

---

## Example — how Customer will plug in (not implemented yet)

```python
# app/repositories/customer.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.base import GenericRepository


class CustomerRepository(GenericRepository[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    # Add customer-specific queries here, e.g. get_by_phone(...)
```

```python
# app/services/customer.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.services.base import BaseService


class CustomerService(BaseService[Customer]):
    def __init__(
        self,
        session: AsyncSession,
        repository: CustomerRepository,
    ) -> None:
        super().__init__(session, repository, entity_name="Customer")

    # Add customer-specific use-cases here
```

```python
# app/api/v1/customers.py (future)
from fastapi import APIRouter, Depends
import uuid

from app.api.deps import get_service
from app.repositories.customer import CustomerRepository
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

get_customer_service = get_service(CustomerService, CustomerRepository)


@router.get("/{customer_id}")
async def get_customer(
    customer_id: uuid.UUID,
    service: CustomerService = Depends(get_customer_service),
):
    return await service.get_by_id(customer_id)
```

No duplicated session wiring — `get_service` builds `session → repository → service` once.

---

## Customer module (reference implementation)

```
Route (api/v1/customers.py)
  → CustomerService (services/customer.py)
      → CustomerRepository (repositories/customer.py)
          → GenericRepository + query helpers
```

| Piece | Path |
|-------|------|
| Schemas | `app/schemas/customer.py` |
| Phone util | `app/utils/phone.py` |
| Exception → HTTP | `app/api/exception_handlers.py` |
| Tests | `tests/test_customers.py` |

Endpoints: `GET/POST /api/v1/customers`, `GET/PUT /api/v1/customers/{id}` (no DELETE).

---

## Domain exceptions

Defined in `app/core/exceptions.py`:

- `EntityNotFoundError`
- `DuplicateEntityError`
- `ValidationError`
- `BusinessRuleViolation`

Routes (or a global handler added later) map these to HTTP responses. Services raise them; repositories do not.
