# ERP Backend

A modern, production-ready FastAPI backend for an ERP system managing quotations, jobs, measurements, and payments.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

This ERP backend manages the complete lifecycle of custom manufacturing projects—from initial customer quotation through measurement, production, installation, and payment tracking.

### Key Features

- **Customer Management** — Contact details, location tracking (Google Maps integration)
- **Product Catalog** — Categorized products with active status management
- **Quotation System** — Multi-item quotations with pricing, discounts, and status workflow
- **Job Lifecycle Tracking** — Complete production pipeline from measurement to completion
- **Measurement Management** — Multiple site visits with detailed dimension tracking
- **Payment Tracking** — Milestone-based payments (Deposit → Production → Final) with multiple payment methods
- **Activity Logging** — Complete audit trail for job activities
- **Reporting** — Generated report tracking with file path storage

---

## 🏗️ Architecture

### Technology Stack

- **Framework:** FastAPI 0.115.6
- **Database:** PostgreSQL 13+ with asyncpg
- **ORM:** SQLAlchemy 2.0 (async, typed declarative)
- **Migrations:** Alembic 1.14.0
- **Validation:** Pydantic 2.10.3
- **Testing:** pytest + pytest-asyncio
- **Container:** Docker + Docker Compose

### Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic configuration
├── app/
│   ├── api/                    # API endpoints
│   │   └── v1/                 # Version 1 API routes
│   │       ├── health.py       # Health check endpoint
│   │       └── router.py       # API router aggregator
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Application settings
│   │   ├── constants.py        # Application constants
│   │   └── logging.py          # Centralized logging
│   ├── db/                     # Database layer
│   │   ├── base.py             # Base model (2-layer design)
│   │   └── session.py          # Async session management
│   ├── database/               # Database tooling
│   │   ├── factories/          # Model factories
│   │   └── seeders/            # Data seeders
│   ├── enums/                  # Business domain enums
│   │   ├── job.py              # Job status enum
│   │   ├── payment.py          # Payment enums
│   │   └── quotation.py        # Quotation status enum
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── product_category.py
│   │   ├── quotation.py
│   │   ├── quotation_item.py
│   │   ├── job.py
│   │   ├── measurement.py
│   │   ├── measurement_item.py
│   │   ├── payment.py
│   │   ├── activity_log.py
│   │   ├── report.py
│   │   └── __init__.py         # Model registry
│   ├── repositories/           # Data access layer
│   ├── schemas/                # Pydantic schemas
│   │   └── health.py
│   ├── services/               # Business logic layer
│   ├── utils/                  # Utility functions
│   └── main.py                 # FastAPI application entry
├── docs/                       # Documentation
│   ├── CHANGELOG.md            # Business improvements log
│   ├── MIGRATION_GUIDE.md      # Complete migration docs
│   ├── MIGRATION_QUICKSTART.md # Quick reference
│   ├── MIGRATION_SUMMARY.md    # Migration overview
│   ├── MIGRATION_VERIFICATION.md # Verification checklist
│   ├── MODELS_QUICK_REFERENCE.md # Model field reference
│   ├── models_summary.md       # Detailed model docs
│   ├── schema_plan.md          # Database schema plan
│   └── verify_migration.sql    # SQL verification script
├── tests/                      # Test suite
│   └── test_health.py
├── .dockerignore               # Docker ignore patterns
├── .env.example                # Environment template
├── .gitignore                  # Git ignore patterns
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Container definition
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 📊 Database Schema

### Entity Relationship Overview

```
Customer (1) ──→ (N) Quotation
                      ├──→ (N) QuotationItem ──→ (1) Product ──→ (1) ProductCategory
                      └──→ (1) Job
                               ├──→ (N) Measurement ──→ (N) MeasurementItem
                               ├──→ (N) Payment
                               └──→ (N) ActivityLog

Report (standalone)
```

### Core Tables (11)

1. **customers** — Client information with location tracking
2. **product_categories** — Product classification
3. **products** — Sellable products linked to categories
4. **quotations** — Price estimates with status workflow
5. **quotation_items** — Line items within quotations
6. **jobs** — Approved quotations with production lifecycle
7. **measurements** — Site visit records with measurer tracking
8. **measurement_items** — Individual piece measurements
9. **payments** — Milestone-based payment tracking
10. **activity_logs** — Job audit trail
11. **reports** — Generated report metadata

### Key Design Decisions

- **Two-Layer Model Hierarchy** — `Base` (metadata) → `BaseEntity` (id, timestamps) → Business Models
- **UUID Primary Keys** — Server-generated with `gen_random_uuid()`
- **Timezone-Aware Timestamps** — All datetime columns include timezone
- **Enum Types** — PostgreSQL native enums for type safety
- **Smart Cascade Rules** — CASCADE for hierarchies, RESTRICT for lookups
- **Payment Type vs Method** — Separates business milestone from payment channel

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Docker & Docker Compose (optional but recommended)

### 1. Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Database Setup (Docker)

```bash
# Start PostgreSQL
docker compose up -d db

# Wait for database to be ready
docker compose logs -f db  # Wait for "ready to accept connections"
```

### 3. Run Migrations

```bash
# Apply database migrations
alembic upgrade head

# Verify migration
docker compose exec db psql -U erp_user -d erp_db -c "\dt"
# Should show 11 tables

# Optional: Run full verification
docker compose exec -T db psql -U erp_user -d erp_db < docs/verify_migration.sql
```

### 4. Start Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Docker
docker compose up backend
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/api/v1/health
# Expected: {"status":"ok"}

# API documentation
open http://localhost:8000/docs  # Interactive Swagger UI
open http://localhost:8000/redoc # Alternative ReDoc UI
```

---

## 🔧 Configuration

### Environment Variables

Key configuration in `.env`:

```bash
# Application
APP_NAME="ERP Backend"
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1

# Database
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=erp_password
POSTGRES_DB=erp_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Connection strings
DATABASE_URL=postgresql+asyncpg://erp_user:erp_password@db:5432/erp_db
DATABASE_URL_SYNC=postgresql+psycopg://erp_user:erp_password@db:5432/erp_db

# Server
HOST=0.0.0.0
PORT=8000
```

See `.env.example` for all available options.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_health.py -v

# Run with output
pytest -v -s
```

---

## 📚 API Documentation

### Available Endpoints

#### Health Check
```
GET /api/v1/health
```

Returns application health status.

**Response:**
```json
{
  "status": "ok"
}
```

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🗄️ Database Management

### Migrations

```bash
# Check current migration
alembic current

# View migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Rollback to beginning
alembic downgrade base

# Generate new migration (after model changes)
alembic revision --autogenerate -m "Description"

# View SQL without applying
alembic upgrade head --sql
```

### Database Access

```bash
# Connect to database
docker compose exec db psql -U erp_user -d erp_db

# Common queries
\dt              # List tables
\d table_name    # Describe table
\dT              # List custom types (enums)
\q               # Quit
```

---

## 📖 Documentation

Comprehensive documentation in `docs/`:

- **`MIGRATION_GUIDE.md`** — Complete migration documentation (3,400+ words)
- **`MIGRATION_QUICKSTART.md`** — One-page quick reference
- **`models_summary.md`** — Detailed model documentation with all fields
- **`MODELS_QUICK_REFERENCE.md`** — Quick lookup for common queries
- **`CHANGELOG.md`** — Business improvements and changes
- **`verify_migration.sql`** — PostgreSQL verification script

---

## 🏗️ Development

### Code Style

- **Type hints** — All functions use type annotations
- **Async/await** — All database operations are async
- **SQLAlchemy 2.0** — Uses modern `Mapped` and `mapped_column` syntax
- **Pydantic v2** — Latest validation and serialization

### Project Conventions

- **Models** — Inherit from `BaseEntity` (never directly from `Base`)
- **Enums** — Define in `app/enums/` as string-based enums
- **Schemas** — Pydantic models in `app/schemas/`
- **Repositories** — Data access in `app/repositories/`
- **Services** — Business logic in `app/services/`
- **Endpoints** — API routes in `app/api/v1/`

### Adding a New Model

1. Create model in `app/models/new_model.py`
2. Inherit from `BaseEntity`
3. Import in `app/models/__init__.py`
4. Generate migration: `alembic revision --autogenerate -m "Add new_model"`
5. Review and apply: `alembic upgrade head`

---

## 🐳 Docker

### Services

```yaml
services:
  db:        # PostgreSQL 16
  backend:   # FastAPI application
```

### Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend

# Restart service
docker compose restart backend

# Stop all services
docker compose down

# Remove volumes (⚠️ deletes data)
docker compose down -v
```

---

## 🔒 Security

### Best Practices Implemented

- **Environment Variables** — Secrets never committed
- **SQL Injection Protection** — Parameterized queries via SQLAlchemy
- **Type Safety** — PostgreSQL enums for valid values
- **Input Validation** — Pydantic schemas validate all input
- **Database Constraints** — Server-side validation
- **Timezone Awareness** — All timestamps use UTC

### TODO: Security Enhancements

- [ ] Authentication (JWT)
- [ ] Authorization (RBAC)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] API key management
- [ ] Request/response encryption (HTTPS)

---

## 🛠️ Troubleshooting

### Database Connection Issues

```bash
# Check database is running
docker compose ps db

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### Migration Issues

```bash
# Check migration status
alembic current

# If migration fails, rollback and retry
alembic downgrade base
alembic upgrade head

# Manual database reset (⚠️ deletes all data)
docker compose down -v
docker compose up -d db
alembic upgrade head
```

### Port Conflicts

```bash
# If port 8000 is in use
# Change in .env or docker-compose.yml
PORT=8001

# Or kill process using port
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -ti:8000 | xargs kill
```

---

## 📈 Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Project structure
- [x] Database models (11 tables)
- [x] Initial migration
- [x] Health check endpoint
- [x] Documentation

### Phase 2: CRUD Layer (Next)
- [ ] Repository pattern implementation
- [ ] Service layer with business logic
- [ ] Pydantic schemas for all models
- [ ] CRUD endpoints for all entities
- [ ] Comprehensive error handling

### Phase 3: Business Features
- [ ] Quotation workflow (draft → sent → approved)
- [ ] Job lifecycle management
- [ ] Measurement tracking
- [ ] Payment processing
- [ ] Activity log automation
- [ ] Report generation

### Phase 4: Authentication & Authorization
- [ ] User model
- [ ] JWT authentication
- [ ] Role-based access control
- [ ] Permission system
- [ ] API key management

### Phase 5: Advanced Features
- [ ] Real-time notifications (WebSockets)
- [ ] File upload/storage (for measurements, reports)
- [ ] Email notifications
- [ ] PDF generation (quotations, invoices)
- [ ] Dashboard analytics
- [ ] Backup/restore system

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for public functions
- Include tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Your Name** — Initial work

---

## 🙏 Acknowledgments

- FastAPI framework and community
- SQLAlchemy team for the excellent ORM
- Alembic for database migrations
- PostgreSQL for robust database engine

---

## 📞 Support

For issues, questions, or contributions:

- **Issues:** [GitHub Issues](repository-url/issues)
- **Documentation:** [Wiki](repository-url/wiki)
- **Email:** your-email@example.com

---

## 📊 Project Status

**Status:** 🟢 Active Development  
**Version:** 0.1.0 (Initial Release)  
**Last Updated:** 2026-07-16

### Current Capabilities

✅ Database schema complete (11 tables)  
✅ Initial migration ready  
✅ Health check endpoint  
✅ Docker setup complete  
✅ Comprehensive documentation  

### In Progress

🔄 CRUD endpoints for all entities  
🔄 Business logic services  
🔄 Data validation schemas  

---

**Built with ❤️ using FastAPI and Python**
