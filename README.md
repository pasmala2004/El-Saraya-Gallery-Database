# Gallery ERP System

**Production Ready** - Modern ERP system for managing gallery manufacturing and sales operations.

Complete Arabic (RTL) interface for managing customers, quotations, jobs, measurements, and payments.

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Node.js 18+ (for frontend development)
- Python 3.11+ (for local backend development)

### Start Backend (Docker - Recommended)

```bash
# 1. Ensure Docker Desktop is running

# 2. Start services
docker-compose up -d

# 3. Wait 15 seconds for services to initialize
timeout /t 15

# 4. Verify backend is running
# Open browser: http://localhost:8000/api/v1/health
```

### Start Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Open browser: http://localhost:3000
```

---

## ✅ System Status

**Backend:** 100% Complete (88/88 tests passing)  
**Frontend:** 97% Complete (all workflows functional)  
**Status:** Production Ready for single-user deployment

### Completed Modules
- ✅ Customers (العملاء)
- ✅ Product Categories (فئات المنتجات)
- ✅ Products (المنتجات)
- ✅ Quotations (عروض الأسعار)
- ✅ Jobs (الأعمال)
- ✅ Measurements (القياسات)
- ✅ Payments (المدفوعات)
- ✅ Dashboard (لوحة التحكم)

### Complete Workflow
```
Customer → Products → Quotation → Items → Approve → 
Job → Measurements → Items → Payments → Complete
```

All operations work through the UI - no database or API access needed.

---

## 🏗️ Architecture

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy 2.0** - ORM with async support
- **PostgreSQL** - Relational database
- **Alembic** - Database migrations
- **Pytest** - Testing framework (88 tests)
- **Docker** - Containerized deployment

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **TailwindCSS** - Styling
- **TanStack Query** - Data fetching
- **React Router** - Navigation
- **Complete Arabic RTL** - 250+ translation keys

---

## 📁 Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration & utilities
│   ├── db/              # Database setup
│   ├── database/        # Seeders & factories
│   ├── enums/           # Status enums
│   ├── models/          # SQLAlchemy models
│   ├── repositories/    # Data access layer
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── docs/                # Technical documentation
├── frontend/            # React application
│   └── src/
│       ├── components/  # Reusable UI components
│       ├── i18n/        # Arabic translations
│       ├── pages/       # Page components
│       ├── services/    # API clients
│       ├── types/       # TypeScript types
│       └── utils/       # Formatters & helpers
└── tests/               # Backend tests (88 tests)
```

---

## 🔧 Development

### Run Backend Tests
```bash
pytest
```

### Run Backend Locally (Without Docker)
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Seed Database
```bash
# With demo data
python seed_database.py

# Or use specific seeders
python -m app.database.seeders.reference.run_reference
python -m app.database.seeders.development.run_demo
```

---

## 📖 Documentation

- **FINAL_MVP_STATUS.md** - Production readiness assessment
- **COMMIT_MESSAGES.md** - Git commit strategies
- **docs/ARCHITECTURE.md** - System architecture
- **docs/QUICK_START.md** - Detailed startup guide
- **docs/TESTING_WORKFLOW.md** - Testing procedures
- **docs/SEEDING_GUIDE.md** - Database seeding
- **docs/JOBS_API_REFERENCE.md** - Jobs API documentation
- **docs/MEASUREMENTS_API_REFERENCE.md** - Measurements API docs
- **docs/QUOTATION_WORKFLOW.md** - Quotation workflow guide
- **frontend/README.md** - Frontend documentation

---

## 🌐 API Documentation

Interactive Swagger docs available at:
```
http://localhost:8000/docs
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_customers.py
pytest tests/test_quotations.py
pytest tests/test_jobs.py
pytest tests/test_measurements.py
pytest tests/test_payments.py

# Run with coverage
pytest --cov=app

# Current status: 88/88 tests passing ✅
```

---

## 🐛 Troubleshooting

### Backend not starting?
1. Ensure Docker Desktop is running
2. Check if port 8000 is available: `netstat -ano | findstr :8000`
3. View logs: `docker-compose logs backend`

### Frontend connection errors?
1. Verify backend is running: http://localhost:8000/api/v1/health
2. Check proxy settings in `frontend/vite.config.ts`

### Database issues?
```bash
# Restart all services
docker-compose down
docker-compose up -d

# Or reset database
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

---

## 🚢 Deployment

See **FINAL_MVP_STATUS.md** for production deployment checklist.

### Backend Deployment
1. Set environment variables (DATABASE_URL, etc.)
2. Run migrations: `alembic upgrade head`
3. Start with: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy build/ directory to web server
```

---

## 📊 Database Schema

Main entities:
- **customers** - Customer information
- **product_categories** - Product categorization
- **products** - Product catalog
- **quotations** - Sales quotations
- **quotation_items** - Line items in quotations
- **jobs** - Manufacturing jobs
- **measurements** - Site measurements
- **measurement_items** - Measurement details
- **payments** - Payment tracking
- **activity_logs** - Audit trail
- **reports** - Business reports

See **docs/ARCHITECTURE.md** for complete schema documentation.

---

## 🎯 Development Principles

- Repository Pattern for data access
- Service Layer for business logic
- Async operations throughout
- Type safety with TypeScript & Pydantic
- RESTful API design
- Comprehensive testing
- Clean architecture
- Production-ready code

---

## 📝 Future Enhancements

Post-MVP improvements:
- Multi-user authentication
- Role-based access control
- PDF generation for quotations
- Excel export functionality
- Email notifications
- Reports and analytics
- Mobile application
- Advanced filtering
- Bulk operations

---

# License

This project is intended for educational and business use.

---

# Author

**Basmala Hesham**

Computer Science Student  
Minia University

GitHub:
https://github.com/pasmala2004