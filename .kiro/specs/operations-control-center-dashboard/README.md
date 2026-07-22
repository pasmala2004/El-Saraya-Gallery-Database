# Operations Control Center Dashboard - Spec

## Overview

This spec defines an **operational ERP dashboard** designed for gallery assistants to manage daily tasks. The dashboard prioritizes action-oriented information over analytics, with a visual pipeline board as the centerpiece.

## Quick Links

- [📋 Requirements](./requirements.md) - Comprehensive requirements with EARS-compliant acceptance criteria
- [🏗️ Design](./design.md) - Complete architecture, component specifications, and implementation plan

## Key Features

### 1. Actionable KPI Cards
Six operational metrics that answer "what needs attention today?":
- Total Active Jobs
- Quotations Waiting for Customer Response
- Measurements Scheduled Today
- Installations Scheduled Today
- Overdue Payments
- Jobs Delayed

### 2. Visual Pipeline Board (Primary Feature)
Seven-column kanban-style board showing every active job:
- **Quotation** → **Measurement** → **Deposit Received** → **Manufacturing** → **Installation** → **Completed** (auto-hide after 7 days) → **Rejected**

Each job card displays:
- Customer name
- Quotation number
- Assigned engineer
- Last activity
- Days in current stage
- Payment progress bar
- Priority indicator (high/medium/low)
- Due dates

### 3. Smart Alerts Panel
Urgency-sorted notifications:
- Quotations waiting >X days
- Measurements overdue
- Manufacturing delayed
- Installation overdue
- Payments overdue
- Jobs inactive >X days

### 4. Recent Activity Timeline
Latest 10 operations with timestamps:
- Customer created
- Quotation approved
- Measurement completed
- Payment received
- Job started
- Installation completed

## Technical Highlights

### Performance
- **Single aggregated API endpoint**: `/api/v1/dashboard`
- **Target response time**: <500ms
- **Query optimization**: SQL aggregations, no N+1 problems
- **Frontend caching**: 30-second stale time
- **Auto-refresh**: Every 30 seconds

### Architecture
- **Backend**: FastAPI + SQLAlchemy with DashboardService, DashboardRepository, and optimized SQL
- **Frontend**: React + TypeScript with reusable components (KPIGrid, PipelineBoard, JobPipelineCard, etc.)
- **Data flow**: Fetch → Process → Display in single round trip

### Future-Proof Design
Architecture supports future additions without refactoring:
- Drag & drop between pipeline stages
- Calendar view
- Engineer workload tracking
- Charts and reports
- AI recommendations

## Implementation Phases

1. **Backend Foundation** - Repository, service, schemas, router, tests
2. **Frontend Core** - KPI cards, data fetching, loading states
3. **Pipeline Board** - Job cards, columns, visual board
4. **Alerts & Activity** - Panels for alerts and recent operations
5. **Polish & Optimization** - Responsive design, caching, performance, E2E tests

## Status

- ✅ Requirements: Approved
- ✅ Design: Approved with operational focus
- ⏳ Implementation: Not started

## Key Architectural Decisions

### Why Operational Focus?
Gallery assistants need to know "what do I do today?" not business analytics. Charts and conversion metrics were removed in favor of actionable information and visual job tracking.

### Why Single API Endpoint?
Combining KPIs, pipeline data, alerts, and activities into one response eliminates multiple round trips and reduces latency from ~1500ms to <500ms.

### Why Pipeline-Centric?
The pipeline board provides the most valuable view: where every job is, what's delayed, and what needs attention. This becomes the dashboard's primary feature rather than a secondary widget.

### Why Auto-Hide Completed Jobs?
Completed jobs older than 7 days clutter the board without providing actionable information. They remain in the database but are filtered from the operational view.

## Questions for Implementation

Before starting implementation, confirm:

1. **Engineer Assignment**: Add `assigned_engineer` field to Job model now or later?
2. **Payment Progress**: Calculate based on amount paid vs total, or milestone completion?
3. **Activity Tracking**: Use existing ActivityLog model or add more granular tracking?
4. **Auto-refresh Interval**: 30 seconds confirmed?
5. **Completed Jobs**: 7-day auto-hide confirmed?

---

**Spec Version**: 1.0  
**Last Updated**: January 15, 2026  
**Entry Point**: Requirements-First
