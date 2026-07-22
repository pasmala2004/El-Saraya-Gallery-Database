# Projects Module - System Architecture

**Feature ID**: `projects-module-redesign`  
**Version**: 1.0  
**Created**: 2026-07-21

---

## Architecture Overview

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Projects List│  │Project Details│  │  Dashboard   │       │
│  │     Page     │  │     Page      │  │   (Existing) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           ↓ React Query
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (REST)                         │
│  /api/v1/jobs      /api/v1/quotations                        │
│  /api/v1/payments  /api/v1/measurements                      │
│  /api/v1/customers /api/v1/activity-logs                     │
└─────────────────────────────────────────────────────────────┘
                           ↓ FastAPI
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer (Business Logic)             │
│  JobService  QuotationService  PaymentService                │
│  MeasurementService  WorkflowService  TimelineService        │
└─────────────────────────────────────────────────────────────┘
                           ↓ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────┐
│                  Data Access Layer (Repositories)             │
│  JobRepository  QuotationRepository  PaymentRepository        │
└─────────────────────────────────────────────────────────────┘
                           ↓ PostgreSQL
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                           │
│  Tables: jobs, quotations, payments, measurements,           │
│          customers, activity_logs, products, etc.            │
└─────────────────────────────────────────────────────────────┘
```

### Module Boundaries

**Projects Module** (Central):
- Aggregates data from Jobs, Quotations, Customers, Payments, Measurements
- Provides unified workspace for project operations
- Does NOT duplicate business logic
- Routes to specialized modules for global views

**Customers Module** (CRM):
- Customer management
- Customer-level analytics
- Accessed via link from Project page

**Payments Module** (Accounting):
- Global payment management across ALL projects
- Financial reports and reconciliation
- Accessed via link from Project page

**Products Module** (Catalog):
- Product and category management
- Accessed via dropdown in Quotation form

**Dashboard Module** (Overview):
- High-level KPIs
- Links filter Projects page
- Does NOT duplicate project operations


### Data Flow Architecture

**Project List Page**:
```
User visits /jobs
  ↓
ProjectsListPage component mounts
  ↓
useProjects() hook fetches data
  ↓
React Query checks cache
  ↓ (if stale or missing)
GET /api/v1/jobs (includes relationships)
  ↓
Backend: JobService.get_all()
  ↓
Backend: JobRepository.get_all_with_relationships()
  ↓
Database: SELECT jobs JOIN customers JOIN quotations
  ↓
Response: Job[] with customer, quotation
  ↓
React Query caches response (5 min)
  ↓
Frontend calculates derived data:
  - Payment progress
  - Days in stage
  - Overdue status
  - Warning badges
  ↓
Render ProjectCard components
```

**Project Details Page**:
```
User clicks project card / visits /projects/{id}
  ↓
ProjectDetailsPage component mounts
  ↓
useProjectDetails(id) hook
  ↓
Parallel React Query requests:
  - useJob(id)
  - useQuotation(quotationId)  [after job loads]
  - useCustomer(customerId)    [after job loads]
  - usePayments(jobId)
  - useMeasurements(jobId)
  - useActivityLogs(jobId)
  ↓
Each query fetches from respective endpoint:
  - GET /api/v1/jobs/{id}
  - GET /api/v1/quotations/{id}
  - GET /api/v1/customers/{id}
  - GET /api/v1/payments?job_id={id}
  - GET /api/v1/measurements?job_id={id}
  - GET /api/v1/activity-logs?job_id={id}
  ↓
React Query caches all responses
  ↓
Frontend aggregates data for header, sections
  ↓
Render collapsible sections progressively
```

**Add Payment Flow**:
```
User clicks "Add Payment"
  ↓
AddPaymentModal opens
  ↓
User fills form, clicks "Save"
  ↓
Frontend validates input
  ↓
useMutation: paymentsApi.create(payment)
  ↓
POST /api/v1/payments
Body: { job_id, payment_type, amount, due_date, ... }
  ↓
Backend: PaymentService.create()
  ↓
Backend creates Payment record
Backend creates ActivityLog entry ("Payment added")
  ↓
Response: created Payment
  ↓
React Query onSuccess:
  - Invalidate ['payments', jobId]
  - Invalidate ['timeline', jobId]
  - Invalidate ['projects'] (affects project list)
  ↓
React Query refetches invalidated queries
  ↓
UI updates automatically:
  - Payments section shows new payment
  - Timeline shows "Payment added" event
  - Header financial summary recalculates
  - Project list card updates payment progress
  ↓
Success toast notification shown
```

### State Management Architecture

**Server State** (React Query):
```typescript
// Query keys structure
['projects']                    // All projects list
['job', jobId]                  // Single job
['quotation', quotationId]      // Single quotation
['customer', customerId]        // Single customer
['payments', 'job', jobId]      // Payments for job
['measurements', 'job', jobId]  // Measurements for job
['timeline', jobId]             // Activity log for job

// Cache configuration
{
  staleTime: 5 * 60 * 1000,      // 5 minutes
  cacheTime: 10 * 60 * 1000,     // 10 minutes
  refetchOnWindowFocus: true,
  refetchOnReconnect: true
}

// Invalidation strategy
onSuccess: () => {
  // Invalidate related queries
  queryClient.invalidateQueries(['payments', 'job', jobId]);
  queryClient.invalidateQueries(['timeline', jobId]);
  queryClient.invalidateQueries(['projects']); // Refresh list
}
```

**Client State** (React useState/useReducer):
```typescript
// UI State
const [filtersPanelOpen, setFiltersPanelOpen] = useState(false);
const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
const [addPaymentModalOpen, setAddPaymentModalOpen] = useState(false);

// Form State
const [paymentForm, setPaymentForm] = useState<PaymentFormData>({
  payment_type: 'deposit',
  amount: '',
  due_date: new Date().toISOString().split('T')[0],
  // ...
});
```

**URL State** (React Router):
```typescript
// Shareable filters via URL params
/jobs?stage=measuring&priority=high&overdue=true

// Parse in component
const [searchParams] = useSearchParams();
const initialFilters = {
  stages: searchParams.getAll('stage'),
  priorities: searchParams.getAll('priority'),
  showOverdueOnly: searchParams.get('overdue') === 'true'
};
```

**Session State** (sessionStorage):
```typescript
// Persist filters across navigation
useEffect(() => {
  sessionStorage.setItem('projectFilters', JSON.stringify(filters));
}, [filters]);

const initialFilters = JSON.parse(
  sessionStorage.getItem('projectFilters') || '{}'
);
```

### Component Architecture

**Atomic Design Principles**:

```
Atoms (Basic building blocks)
├── Button
├── Input
├── Badge
├── Icon
├── Skeleton
└── Spinner

Molecules (Simple combinations)
├── StatusBadge (Badge + Icon)
├── PriorityBadge (Badge + Color)
├── ProgressBar (div + % + styling)
├── DateDisplay (Icon + formatted date)
└── PhoneLink (Icon + tel: link)

Organisms (Complex components)
├── ProjectCard (Atoms + Molecules)
├── ProjectDetailsHeader (Molecules arranged)
├── WorkflowPipeline (Multiple WorkflowStage)
├── PaymentsList (Multiple PaymentCard)
└── CollapsibleSection (Header + Content)

Templates (Page layouts)
├── ProjectsListTemplate (Header + Filters + Grid)
└── ProjectDetailsTemplate (Header + Sections)

Pages (Full pages with data)
├── JobsPage (ProjectsListTemplate + data)
└── ProjectDetailsPage (ProjectDetailsTemplate + data)
```

**Composition Pattern**:
```tsx
<ProjectDetailsPage jobId={123}>
  <ProjectDetailsHeader>
    <ProjectIdentification />
    <CustomerSummary />
    <FinancialSummary />
    <QuickActions />
  </ProjectDetailsHeader>
  
  <CollapsibleSection title="Workflow">
    <WorkflowPipeline>
      {stages.map(stage => (
        <WorkflowStage key={stage.id} stage={stage} />
      ))}
    </WorkflowPipeline>
  </CollapsibleSection>
  
  <CollapsibleSection title="Timeline">
    <ProjectTimeline events={timelineEvents} />
  </CollapsibleSection>
  
  <CollapsibleSection title="Payments">
    <PaymentsSummary />
    <PaymentsList />
    <AddPaymentButton />
  </CollapsibleSection>
  
  {/* More sections... */}
</ProjectDetailsPage>
```

### API Architecture

**RESTful Endpoints**:

```
Projects (Jobs):
  GET    /api/v1/jobs                 # List all projects
  GET    /api/v1/jobs/{id}            # Get single project
  POST   /api/v1/jobs                 # Create job (from quotation)
  PUT    /api/v1/jobs/{id}            # Update job
  PATCH  /api/v1/jobs/{id}/status     # Update status only
  DELETE /api/v1/jobs/{id}            # Soft delete (future)

Quotations:
  GET    /api/v1/quotations           # List quotations
  GET    /api/v1/quotations/{id}      # Get single quotation
  POST   /api/v1/quotations           # Create quotation
  PUT    /api/v1/quotations/{id}      # Update quotation
  PATCH  /api/v1/quotations/{id}/status # Approve/reject

Payments:
  GET    /api/v1/payments?job_id={id} # List payments for job
  POST   /api/v1/payments             # Create payment
  PATCH  /api/v1/payments/{id}/status # Mark as paid

Measurements:
  GET    /api/v1/measurements?job_id={id} # List measurements
  POST   /api/v1/measurements         # Create measurement
  PUT    /api/v1/measurements/{id}    # Update measurement

Activity Logs:
  GET    /api/v1/activity-logs?job_id={id} # Timeline events

Customers:
  GET    /api/v1/customers            # List customers
  GET    /api/v1/customers/{id}       # Get customer

Optional (Future optimization):
  GET    /api/v1/projects/{id}/summary # Aggregated project data
  POST   /api/v1/jobs/{id}/complete-stage # Complete workflow stage
```

**Response Formats**:
```json
// GET /api/v1/jobs/{id}
{
  "id": 123,
  "quotation_id": 456,
  "customer_id": 789,
  "status": "measuring",
  "priority": "high",
  "measurement_date": "2026-07-25",
  "production_start": null,
  "production_end": null,
  "installation_date": null,
  "completion_date": null,
  "expected_delivery_date": "2026-08-15",
  "notes": "Customer prefers morning installations",
  "created_at": "2026-07-21T10:00:00Z",
  "updated_at": "2026-07-21T14:30:00Z"
}

// GET /api/v1/payments?job_id=123
{
  "payments": [
    {
      "id": 1,
      "job_id": 123,
      "payment_type": "deposit",
      "payment_method": "bank",
      "percentage": 30,
      "amount": "15000.00",
      "due_date": "2026-07-20",
      "paid_date": "2026-07-19",
      "status": "paid",
      "notes": "Bank transfer",
      "created_at": "2026-07-15T09:00:00Z"
    }
  ]
}
```

### Database Schema (Existing, No Changes)

```sql
-- jobs table
CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  quotation_id INTEGER REFERENCES quotations(id),
  customer_id INTEGER REFERENCES customers(id),
  status VARCHAR(50) NOT NULL,
  priority VARCHAR(20) DEFAULT 'medium',
  measurement_date DATE,
  production_start DATE,
  production_end DATE,
  installation_date DATE,
  completion_date DATE,
  expected_delivery_date DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- quotations table
CREATE TABLE quotations (
  id SERIAL PRIMARY KEY,
  quotation_number VARCHAR(50) UNIQUE NOT NULL,
  customer_id INTEGER REFERENCES customers(id),
  status VARCHAR(50) NOT NULL,
  final_price NUMERIC(12, 2) NOT NULL,
  discount NUMERIC(5, 2) DEFAULT 0,
  valid_until DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- payments table
CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  payment_order INTEGER NOT NULL,
  payment_type VARCHAR(50) NOT NULL,
  payment_method VARCHAR(50) NOT NULL,
  percentage NUMERIC(5, 2),
  amount NUMERIC(12, 2) NOT NULL,
  due_date DATE,
  paid_date DATE,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- activity_logs table
CREATE TABLE activity_logs (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  user_id INTEGER, -- Future: REFERENCES users(id)
  action VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- measurements table
CREATE TABLE measurements (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  visit_date DATE NOT NULL,
  measured_by VARCHAR(255),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- measurement_items table
CREATE TABLE measurement_items (
  id SERIAL PRIMARY KEY,
  measurement_id INTEGER REFERENCES measurements(id),
  room VARCHAR(255),
  width NUMERIC(10, 2),
  height NUMERIC(10, 2),
  quantity INTEGER DEFAULT 1,
  notes TEXT
);

-- customers table
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  phone VARCHAR(50) NOT NULL,
  address TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Security Architecture

**Authentication**:
- JWT tokens in HTTP-only cookies (frontend)
- Token validation on every API request (backend)
- Token refresh on expiration

**Authorization** (Future):
- Role-based access control (RBAC)
- Roles: Admin, Manager, Assistant, Installer
- Permissions: view_projects, edit_projects, delete_projects, etc.

**Data Protection**:
- HTTPS only (TLS 1.3)
- Input sanitization (prevent XSS)
- SQL injection prevention (parameterized queries via SQLAlchemy)
- CORS configuration (whitelist frontend domain)

**Audit Trail**:
- ActivityLog records all significant actions
- Includes: user_id, action, timestamp, metadata
- Cannot be deleted (only view)

### Scalability Architecture

**Horizontal Scaling**:
- Stateless frontend (can deploy multiple instances)
- Stateless backend (can deploy multiple API servers)
- Database connection pooling
- Load balancer (Nginx / AWS ALB)

**Caching Strategy**:
- Frontend: React Query (in-memory)
- Backend: Redis for frequently accessed data (future)
- Database: Query result caching (PostgreSQL)

**Future Microservices** (Not in scope now):
```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
┌───▼───┐ ┌──▼───┐ ┌───▼────┐ ┌──▼──────┐
│Projects│ │Payments│ │Customers│ │Notifications│
│Service │ │Service │ │Service  │ │Service      │
└────────┘ └────────┘ └─────────┘ └──────────────┘
```

### Deployment Architecture

**Frontend**:
- Build: Vite (production build)
- Host: Static hosting (Vercel / Netlify / S3 + CloudFront)
- CDN: Cached assets (CSS, JS, fonts)

**Backend**:
- Server: Uvicorn (ASGI server)
- Container: Docker
- Orchestration: Docker Compose / Kubernetes
- Environment: Production, Staging, Development

**Database**:
- PostgreSQL 14+
- Managed service (AWS RDS / Azure Database)
- Automated backups (daily)
- Replication (read replicas for scaling)

**CI/CD Pipeline**:
```
Git Push (main branch)
  ↓
GitHub Actions / GitLab CI
  ↓
1. Run linters (ESLint, Flake8)
2. Run unit tests
3. Build frontend (Vite)
4. Build backend Docker image
5. Run integration tests
6. Deploy to staging
  ↓
Manual approval
  ↓
Deploy to production
```

---

## Architecture Decisions

### ADR-001: Use React Query for Server State

**Context**: Need efficient server state management with caching, refetching, and optimistic updates.

**Decision**: Use React Query instead of Redux or plain fetch.

**Rationale**:
- Automatic caching (reduces API calls)
- Background refetching (data stays fresh)
- Built-in loading/error states
- Optimistic updates support
- Less boilerplate than Redux

**Consequences**:
- ✅ Simpler code
- ✅ Better performance
- ❌ Learning curve for team
- ❌ Additional dependency

### ADR-002: No Database Schema Changes

**Context**: Existing schema has all required fields.

**Decision**: Reuse existing schema without modifications.

**Rationale**:
- Minimize risk
- Faster implementation
- No migration downtime
- Existing data untouched

**Consequences**:
- ✅ Zero risk to production data
- ✅ Faster development
- ❌ May need aggregation in backend (performance consideration)
- ❌ Cannot add "planned dates" fields (future requirement)

### ADR-003: Client-Side Filtering Instead of Server-Side

**Context**: Projects list needs multiple filter criteria.

**Decision**: Fetch all projects, filter on client-side.

**Rationale**:
- Instant response (no server round-trip)
- Simpler backend (no complex query building)
- Works well for <200 projects
- React Query caches data

**Consequences**:
- ✅ Instant filtering
- ✅ Simpler API
- ❌ Loads all data upfront
- ❌ May not scale to 1000+ projects (use pagination if needed)

### ADR-004: Collapsible Sections for Scalability

**Context**: Need to add 11 future features without redesigning page.

**Decision**: Use `CollapsibleSection` component for all major sections.

**Rationale**:
- Consistent UX
- Easy to add new sections
- Reduces visual clutter
- User controls what they see

**Consequences**:
- ✅ Future-proof architecture
- ✅ Scalable design
- ✅ Consistent pattern
- ❌ Slight overhead per section

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Related**: design.md, api-design.md

