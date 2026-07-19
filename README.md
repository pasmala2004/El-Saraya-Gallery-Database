# Gallery ERP System

A modern ERP (Enterprise Resource Planning) system built for a manufacturing and gallery business that produces and sells custom products such as windows, doors, kitchens, shower cabins, and smart locks.

The system replaces Excel-based workflows with a centralized web application that manages customers, quotations, jobs, measurements, payments, and business operations.

---

## Features

### Customer Management
- Create, edit, and search customers
- Store phone numbers, addresses, and locations
- Quick customer lookup

### Product Management
- Product Categories
- Product Catalog
- Active/Inactive products
- Product descriptions

### Quotation Management
- Create quotations
- Add multiple quotation items
- Automatic total calculation
- Discounts
- Status management
- Customer quotation history

### Job Management
- Convert approved quotations into jobs
- Track production workflow
- Measurement tracking
- Installation scheduling

### Payment Management
- Record payments
- Payment status tracking
- Installment support
- Outstanding balances

### Dashboard
- Business overview
- Customer statistics
- Quotation statistics
- Quick navigation

---

# Tech Stack

## Backend

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Docker
- AsyncPG
- Pydantic

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Axios
- Lucide Icons
- Sonner Toasts

---

# Project Structure

```
backend/
│
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── database/
│   ├── enums/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── utils/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── lib/
│   └── public/
│
└── docker-compose.yml
```

---

# Database Design

The system currently includes the following entities:

- Customers
- Product Categories
- Products
- Quotations
- Quotation Items
- Jobs
- Measurements
- Measurement Items
- Payments
- Reports
- Activity Logs

---

# Installation

## Clone

```bash
git clone https://github.com/YOUR_USERNAME/gallery-erp.git
cd gallery-erp
```

---

## Backend

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure environment variables

```bash
cp .env.example .env
```

Run migrations

```bash
alembic upgrade head
```

Start the API

```bash
uvicorn app.main:app --reload
```

Backend

```
http://localhost:8000
```

Swagger

```
http://localhost:8000/docs
```

---

## Frontend

Install packages

```bash
npm install
```

Run development server

```bash
npm run dev
```

Frontend

```
http://localhost:3000
```

---

# API

Interactive API documentation is available at

```
http://localhost:8000/docs
```

---

# Current Status

### Completed

- Database architecture
- PostgreSQL schema
- Alembic migrations
- Customer module
- Product module
- Quotation module
- Dashboard
- React frontend foundation
- Customer UI
- Product UI
- Quotation UI

### In Progress

- Jobs module
- Payments module

### Planned

- Reports
- Analytics Dashboard
- Export to Excel/PDF
- Authentication
- Notifications
- Role-based permissions

---

# Screens

- Dashboard
- Customers
- Products
- Quotations
- Jobs
- Payments

---

# Development Principles

- Repository Pattern
- Service Layer Architecture
- Async Database Operations
- Clean Architecture
- RESTful API Design
- Type Safety with TypeScript
- Responsive UI
- Production-ready structure

---

# Future Improvements

- Multi-user authentication
- Role-based access control
- PDF quotation generation
- Excel import/export
- Email & WhatsApp integration
- Inventory management
- Production planning
- Advanced reporting
- Dashboard analytics
- AI assistant integration

---

# License

This project is intended for educational and business use.

---

# Author

**Basmala Emad**

Computer Science Student  
Minia University

GitHub:
https://github.com/pasmala2004