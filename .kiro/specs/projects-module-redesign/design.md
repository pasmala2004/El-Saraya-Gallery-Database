# Projects Module Redesign - Technical Design Document

**Feature ID**: `projects-module-redesign`  
**Status**: Phase 0 - Architecture Design  
**Version**: 1.0  
**Created**: 2026-07-21  
**Owner**: Development Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Step 1: Project List Redesign](#step-1-project-list-redesign)
4. [Step 2: Project Header Redesign](#step-2-project-header-redesign)
5. [Step 3: Workflow Redesign](#step-3-workflow-redesign)
6. [Step 4: Timeline Redesign](#step-4-timeline-redesign)
7. [Step 5: Payments Integration](#step-5-payments-integration)
8. [Step 6: Measurements Integration](#step-6-measurements-integration)
9. [Step 7: Quotation Integration](#step-7-quotation-integration)
10. [Step 8: Customer Section](#step-8-customer-section)
11. [Step 9: Activity & Documents](#step-9-activity--documents)
12. [Step 10: Polish & UX Improvements](#step-10-polish--ux-improvements)
13. [Timeline Engine Design](#timeline-engine-design)
14. [Workflow Stages Design](#workflow-stages-design)
15. [Payment Design](#payment-design)
16. [Quotation Design](#quotation-design)
17. [Dashboard Integration Design](#dashboard-integration-design)
18. [Future Scalability Architecture](#future-scalability-architecture)

---

## Executive Summary

### Purpose

Transform the Projects module into the central operational workspace of the ERP system. This design provides a complete blueprint for implementing a project-centric interface where operations staff spend 80% of their time, eliminating fragmented workflows across multiple pages.

### Design Philosophy

**Project as Center**: Every piece of information aggregates to the Project. No scattered data across modules.

**Single Workspace**: 15+ operations performable in-page without navigation.

**Automatic Recording**: Timeline captures 15+ event types automatically with date/time/user.

**Real Workflow**: 8 stages with defined entry/exit conditions and automatic transitions.


**Incremental Implementation**: 10 independent steps, each production-ready before proceeding.

**Minimal Backend Changes**: Reuse existing APIs whenever possible. No database schema changes.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Card-based project list | Better information density than tables, more scannable |
| Sticky header with financial summary | Critical info always visible during scrolling |
| Automatic timeline recording | Eliminates manual entry, provides complete audit trail |
| Workflow with visual pipeline | Clear stage visualization, overdue indicators |
| Payments summary within project | Operational visibility without leaving page |
| Global payments module separate | Accounting needs remain in dedicated module |
| Collapsible sections | Scalable architecture for future features |
| Client-side filtering | Instant response, no server round-trips |
| React Query for state | Automatic caching, refetching, optimistic updates |
| Component reuse >80% | Existing components (CollapsibleSection, InlineEdit) |

### Success Criteria

- Reduce navigation between pages from 3-5 to 1
- Reduce time to check project status from 3 min to 30 sec
- Enable all operations from single workspace
- Zero backend schema changes
- Zero regressions from existing functionality
- Production-ready after each step

---

## Architecture Overview

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                        ERP System                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐      ┌─────────────────┐      ┌──────────┐   │
│  │Dashboard │─────>│Projects (Central)│<─────│Customers │   │
│  │(Overview)│      │   Workspace      │      │  (CRM)   │   │
│  └──────────┘      └─────────────────┘      └──────────┘   │
│       │                     │                      │         │
│       │                     │                      │         │
│       v                     v                      v         │
│  ┌──────────┐      ┌─────────────────┐      ┌──────────┐   │
│  │ KPIs &   │      │  Project List   │      │Payments  │   │
│  │ Filters  │      │  Project Details│      │(Accounting│   │
│  └──────────┘      └─────────────────┘      └──────────┘   │
│                             │                                │
│                             v                                │
│                    ┌─────────────────┐                      │
│                    │    Products     │                      │
│                    │   (Catalog)     │                      │
│                    └─────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

**Projects Module** (This Design):
- Project list (operational home page)
- Project details (single workspace for all operations)
- Quotation, Measurement, Payment, Customer data aggregation
- Workflow management, Timeline tracking
- In-page operations (add, edit, complete)

**Dashboard Module** (Existing):
- KPI summary cards
- Workflow pipeline overview (all projects)
- Alerts and recent activity
- **Interaction**: KPI clicks filter Projects page

**Customers Module** (Existing):
- Customer CRM management
- **Interaction**: Project links to customer profile

**Payments Module** (Existing):
- Global payment accounting
- Financial reports across all projects
- **Interaction**: Project shows THIS project's payments only

**Products Module** (Existing):
- Catalog management
- **Interaction**: Product selection in quotation forms


### Technology Stack

**Frontend**:
- React 18 (functional components, hooks)
- TypeScript 5+ (strict mode)
- React Query 4+ (server state management)
- React Router 6+ (navigation)
- Tailwind CSS (styling)
- Lucide React (icons)
- date-fns (date formatting)
- Sonner (toast notifications)

**Backend** (No Changes):
- FastAPI (Python)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Alembic (migrations - not used in this design)

**State Management Strategy**:
- Server state: React Query (jobs, quotations, payments, measurements)
- UI state: React useState (filters, modals, forms)
- URL state: React Router (active filters, shareable links)
- Session state: sessionStorage (filter persistence)
- No Redux/Zustand needed

### Component Reuse Strategy

**Existing Reusable Components**:
- `CollapsibleSection` - Used for all major sections (Workflow, Timeline, Payments, etc.)
- `InlineEdit` - Used for editable fields throughout
- `LoadingSpinner` - Loading states
- `ErrorMessage` - Error displays
- `ConfirmDialog` - Confirmation modals

**New Reusable Components** (To Create):
- `ProjectCard` - Rich card for project list
- `StatusBadge` - Colored badge for stages/statuses
- `PriorityBadge` - High/Medium/Low indicator
- `ProgressBar` - Payment progress visualization
- `Timeline Row` - Timeline event display
- `WorkflowStage` - Visual stage in pipeline
- `PaymentCard` - Payment display card


### API Strategy

**Principle**: Reuse existing endpoints wherever possible. Only create new endpoints when aggregation is required for performance.

**Existing Endpoints to Reuse**:
- `GET /api/v1/jobs` - Project list data
- `GET /api/v1/jobs/{id}` - Single project data
- `GET /api/v1/quotations?job_id={id}` - Quotation for project
- `GET /api/v1/measurements?job_id={id}` - Measurements for project
- `GET /api/v1/payments?job_id={id}` - Payments for project
- `GET /api/v1/customers/{id}` - Customer info
- `PUT /api/v1/jobs/{id}` - Update job
- `POST /api/v1/payments` - Create payment
- `PATCH /api/v1/payments/{id}/status` - Mark payment paid

**New Endpoints** (Optional, for optimization):
- `GET /api/v1/projects/{id}/summary` - Aggregated project data (if needed for performance)
- `POST /api/v1/jobs/{id}/complete-stage` - Complete workflow stage with automatic activity logging

**Decision**: Start with existing endpoints (frontend aggregation). Monitor performance. Add aggregated endpoint only if load time >2 seconds.

---

## STEP 1: Project List Redesign

### Purpose

Transform the Projects page into the **operational home page** - the primary interface where operations staff start their day. The list must provide instant visibility into all active work without requiring users to open individual projects.

### Business Problem Solved

- **Current Pain**: Simple table shows minimal info; users must open each project to understand status
- **Solution**: Rich card layout with comprehensive data (stage, priority, payment progress, warnings, activity)
- **Impact**: Reduce project status checks from 3 minutes to 30 seconds


### Components Affected

**Frontend Pages**:
- `frontend/src/pages/Jobs.tsx` - Complete redesign

**React Components** (New):
- `ProjectCard.tsx` - Rich project card
- `ProjectsFilters.tsx` - Multi-criteria filter panel
- `ProjectsSearch.tsx` - Search input with debounce
- `StatusBadge.tsx` - Stage status display
- `PriorityBadge.tsx` - Priority indicator
- `ProgressBar.tsx` - Payment progress visualization

**Hooks** (New):
- `useProjectsFilters.ts` - Filter state management
- `useProjectsSearch.ts` - Search with debounce logic

**Dialogs**: None

**Backend**: None

**Translations**:
- `projects.filters.*` - Filter labels
- `projects.search.*` - Search placeholders
- `projects.cards.*` - Card field labels
- `projects.warnings.*` - Warning badge texts

### Database Impact

**Status**: No database changes

No migrations required. All data available from existing Job, Quotation, Customer, Payment tables via existing endpoints.

### API Impact

**Existing Endpoints Reused**:

```typescript
// Fetch all projects with relationships
GET /api/v1/jobs?include=customer,quotation,payments

Response: {
  jobs: Job[]  // includes customer, quotation data
}
```

**Client-Side Aggregation**:
```typescript
// Calculate payment progress
const calculatePaymentProgress = (job: Job): number => {
  const totalPaid = job.payments
    ?.filter(p => p.status === 'paid')
    .reduce((sum, p) => sum + parseFloat(p.amount), 0) || 0;
  
  const quotationTotal = job.quotation?.final_price || 0;
  
  return quotationTotal > 0 ? (totalPaid / quotationTotal) * 100 : 0;
};

// Determine if project is overdue
const isOverdue = (job: Job): boolean => {
  if (job.status === 'completed' || job.status === 'cancelled') return false;
  
  const expectedDate = job.expected_delivery_date;
  if (!expectedDate) return false;
  
  return new Date(expectedDate) < new Date();
};

// Calculate days in current stage
const daysInStage = (job: Job): number => {
  const stageStartDate = getStageStartDate(job); // Based on workflow
  const now = new Date();
  return Math.floor((now.getTime() - stageStartDate.getTime()) / (1000 * 60 * 60 * 24));
};
```

**Performance Considerations**:
- **Initial Load**: Fetch all jobs + related data in single request
- **Caching**: React Query caches for 5 minutes, refetches on window focus
- **Filtering**: Client-side (instant response, no server round-trip)
- **Search**: Client-side with 300ms debounce
- **Pagination**: Not initially required; implement if dataset >200 projects
- **Virtualization**: Consider react-virtual if performance degrades with large datasets

### Expected Response

```typescript
interface Job {
  id: number;
  quotation_id: number;
  customer_id: number;
  status: JobStatus;
  priority: 'high' | 'medium' | 'low';
  measurement_date: string | null;
  production_start: string | null;
  production_end: string | null;
  installation_date: string | null;
  completion_date: string | null;
  expected_delivery_date: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
  
  // Relationships
  customer: {
    id: number;
    name: string;
    phone: string;
    address: string;
  };
  quotation: {
    id: number;
    quotation_number: string;
    final_price: string;
    status: QuotationStatus;
  };
  payments: Payment[];
}
```

### UI Hierarchy

```
JobsPage (Renamed from "Jobs" to "Projects" in UI)
├── PageHeader
│   ├── Title: "Projects"
│   ├── CreateButton: "New Quotation"
│   └── StatsSummary: "{count} Active Projects"
│
├── FiltersPanel (Collapsible)
│   ├── StageFilter (multi-select dropdown)
│   ├── PriorityFilter (multi-select)
│   ├── PaymentStatusFilter (multi-select)
│   ├── CustomerFilter (searchable dropdown)
│   ├── DateRangeFilter (from/to date pickers)
│   ├── OverdueToggle (checkbox)
│   └── ClearFiltersButton
│
├── SearchBar
│   ├── SearchInput (debounced 300ms)
│   └── SearchIcon
│
├── ProjectsGrid (responsive card grid)
│   └── ProjectCard (repeated)
│       ├── CardHeader
│       │   ├── ProjectID (prominent, bold)
│       │   ├── PriorityBadge
│       │   └── WarningBadges (overdue, payment due, action required)
│       │
│       ├── CardBody
│       │   ├── CustomerName (large, clickable → customer profile)
│       │   ├── StatusBadge (colored: Quotation/Measurement/Production/etc.)
│       │   ├── PaymentProgress (visual bar + percentage text)
│       │   ├── ExpectedDelivery (formatted date)
│       │   ├── DaysInStage (badge: "5 days in Measurement")
│       │   └── LatestActivity (relative time + description)
│       │
│       └── CardFooter
│           └── ViewButton ("View Project" → opens ProjectDetails)
│
└── Pagination (optional, for >200 projects)
```

### Component Specifications

#### ProjectCard Component

**Responsibilities**:
- Display comprehensive project information in scannable format
- Color-code stage badges
- Show warnings/alerts visually
- Enable quick navigation to project details

**Props**:
```typescript
interface ProjectCardProps {
  job: Job;
  onView: (jobId: number) => void;
}
```

**State**: None (stateless presentation component)

**Relationships**:
- Used by: `ProjectsGrid`
- Uses: `StatusBadge`, `PriorityBadge`, `ProgressBar`

**Visual Design**:
- Card: white background, shadow, rounded corners, hover shadow-lg
- Header: flex row, space-between, gray-50 background, padding
- Body: padding, space-y-3
- Footer: border-top, padding, flex justify-end

**Color Coding**:
- Quotation: blue-500
- Measurement: purple-500
- Deposit: yellow-500
- Production: orange-500
- Installation: indigo-500
- Completed: green-500
- Cancelled: red-500
- On Hold: gray-500


#### ProjectsFilters Component

**Responsibilities**:
- Provide all filter controls
- Manage filter state
- Persist filters to session storage
- Apply combined filters (AND logic)

**Props**:
```typescript
interface ProjectsFiltersProps {
  filters: ProjectFilters;
  onFiltersChange: (filters: ProjectFilters) => void;
  onClearFilters: () => void;
  customers: Customer[];  // for dropdown
}

interface ProjectFilters {
  stages: JobStatus[];
  priorities: ('high' | 'medium' | 'low')[];
  paymentStatuses: ('paid' | 'pending' | 'overdue')[];
  customerIds: number[];
  dateRange: { from: Date | null; to: Date | null };
  showOverdueOnly: boolean;
}
```

**State**:
- Local state for UI (dropdown open/closed)
- Filter state managed by parent via props

**Relationships**:
- Used by: `JobsPage`
- Uses: Multi-select dropdowns, date pickers, checkboxes

### State Management

**Where State Lives**:
- **Server State**: React Query (`useJobs`, `useCustomers`)
- **Filter State**: Local state in `JobsPage` with sessionStorage sync
- **UI State**: Local component state (modals, dropdowns)

**React Query Configuration**:
```typescript
const useProjects = () => {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const jobs = await jobsApi.getAll();
      const customers = await customersApi.getAll();
      const quotations = await quotationsApi.getAll();
      
      // Enrich jobs with related data
      return jobs.map(job => ({
        ...job,
        customer: customers.find(c => c.id === job.customer_id),
        quotation: quotations.find(q => q.id === job.quotation_id)
      }));
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true
  });
};
```

**Filter State Management**:
```typescript
const [filters, setFilters] = useState<ProjectFilters>(() => {
  // Load from sessionStorage on mount
  const saved = sessionStorage.getItem('projectFilters');
  return saved ? JSON.parse(saved) : defaultFilters;
});

useEffect(() => {
  // Persist to sessionStorage on change
  sessionStorage.setItem('projectFilters', JSON.stringify(filters));
}, [filters]);
```

**Derived State** (Filtered Projects):
```typescript
const filteredProjects = useMemo(() => {
  let result = projects;
  
  // Apply stage filter
  if (filters.stages.length > 0) {
    result = result.filter(p => filters.stages.includes(p.status));
  }
  
  // Apply priority filter
  if (filters.priorities.length > 0) {
    result = result.filter(p => filters.priorities.includes(p.priority));
  }
  
  // Apply search
  if (searchQuery) {
    result = result.filter(p =>
      p.customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.quotation.quotation_number.includes(searchQuery) ||
      p.id.toString().includes(searchQuery) ||
      p.customer.phone.includes(searchQuery)
    );
  }
  
  // Apply overdue filter
  if (filters.showOverdueOnly) {
    result = result.filter(p => isOverdue(p));
  }
  
  return result;
}, [projects, filters, searchQuery]);
```

### Loading Strategy

**Initial Load**:
1. Show skeleton cards (3-4 cards with loading animation)
2. Fetch projects data via React Query
3. Replace skeletons with actual cards when data loads
4. Show error message if fetch fails

**Refresh**:
- Auto-refresh every 5 minutes (React Query staleTime)
- Refresh on window focus
- Manual refresh button (forces refetch)

**Optimistic UI**: Not applicable for list (read-only)

### Error Handling

**Network Failure**:
```typescript
if (isError) {
  return (
    <ErrorMessage
      title="Failed to load projects"
      message={error.message}
      action={<Button onClick={() => refetch()}>Retry</Button>}
    />
  );
}
```

**No Results**:
```typescript
if (filteredProjects.length === 0 && !isLoading) {
  return (
    <EmptyState
      icon={<FolderOpen className="w-16 h-16 text-gray-400" />}
      title="No projects found"
      message="Try adjusting your filters or search query"
      action={filters !== defaultFilters && (
        <Button onClick={clearFilters}>Clear Filters</Button>
      )}
    />
  );
}
```

### Navigation Flows

**From Dashboard KPI** → Projects Page (Filtered):
```typescript
// Dashboard KPI Click Handler
const handleKPIClick = (kpiType: string) => {
  navigate('/jobs', {
    state: {
      filterSource: 'dashboard',
      kpiType: kpiType, // 'delayed', 'waiting-quotations', 'today-measurements'
      filters: getFiltersForKPI(kpiType)
    }
  });
};

// Jobs Page - Apply filters from navigation state
useEffect(() => {
  if (location.state?.filters) {
    setFilters(location.state.filters);
  }
}, [location.state]);
```

**From Project Card** → Project Details:
```typescript
const handleViewProject = (jobId: number) => {
  navigate(`/projects/${jobId}`);
};
```

**From Customer Name** → Customer Profile (New Tab):
```typescript
const handleViewCustomer = (customerId: number) => {
  window.open(`/customers/${customerId}`, '_blank');
};
```

### Performance Considerations

**Rendering**:
- Use `useMemo` for filtered/sorted lists
- Use `React.memo` for `ProjectCard` (prevent re-renders)
- Virtualization with `react-virtual` if >200 projects

**Data Fetching**:
- Single request with relationships included
- 5-minute cache with React Query
- Background refetch on window focus

**Filtering/Search**:
- Client-side (instant response)
- Debounced search (300ms)
- No server requests on filter changes

**Bundle Size**:
- Code-split `ProjectsFilters` if large
- Lazy-load date picker library

---

## STEP 2: Project Header Redesign

### Purpose

Create a **sticky header** that serves as the project's command center, displaying all critical information (IDs, customer, stage, financial summary, dates) without scrolling. Enable quick actions for common operations.

### Business Problem Solved

- **Current Pain**: Critical information scattered throughout page; scrolling required to understand project status
- **Solution**: Sticky header with 4-row layout showing IDs, customer info, financial summary, dates
- **Impact**: Instant visibility of project health; quick actions always accessible

### Components Affected

**Frontend Pages**:
- `frontend/src/pages/ProjectDetails.tsx` - Add header section

**React Components** (New):
- `ProjectDetailsHeader.tsx` - Main header container
- `ProjectIdentification.tsx` - IDs and badges
- `CustomerSummary.tsx` - Customer info (compact)
- `FinancialSummary.tsx` - Totals, balance, progress
- `DatesSummary.tsx` - Key dates
- `QuickActions.tsx` - Conditional action buttons

**Hooks** (Reuse):
- Existing React Query hooks for data fetching

**Dialogs**: None (action dialogs in later steps)

**Backend**: None

**Translations**:
- `projectDetails.header.*` - Header labels
- `projectDetails.financial.*` - Financial labels
- `projectDetails.dates.*` - Date labels

### Database Impact

**Status**: No database changes

### API Impact

**Existing Endpoints Reused**:

```typescript
// Option A: Multiple requests (current approach)
GET /api/v1/jobs/{id}         // Job data
GET /api/v1/quotations/{qid}  // Quotation data
GET /api/v1/customers/{cid}   // Customer data
GET /api/v1/payments?job_id={id} // Payments list

// Option B: Aggregated endpoint (future optimization if needed)
GET /api/v1/projects/{id}/summary

Response: {
  project_id: number;
  job_id: number;
  quotation_id: number;
  quotation_number: string;
  
  customer: {
    id: number;
    name: string;
    phone: string;
    address: string;
  };
  
  status: JobStatus;
  priority: 'high' | 'medium' | 'low';
  
  financial: {
    total: number;          // quotation.final_price
    paid: number;           // sum of paid payments
    remaining: number;      // total - paid
    progress: number;       // (paid / total) * 100
    overdue_amount: number; // sum of overdue payments
  };
  
  dates: {
    created: string;
    expected_delivery: string | null;
    last_updated: string;
  };
}
```

**Decision**: Start with Option A (no backend changes). Create Option B endpoint only if header load time >500ms.

**Performance Target**: Header data load <500ms

### Expected Response

*(Using existing endpoints, aggregate in frontend)*

```typescript
interface ProjectHeaderData {
  job: Job;
  quotation: Quotation;
  customer: Customer;
  payments: Payment[];
  
  // Derived (calculated in frontend)
  financialSummary: {
    total: number;
    paid: number;
    remaining: number;
    progress: number;
    hasOverduePayments: boolean;
  };
}
```


### UI Hierarchy

```
ProjectDetailsHeader (sticky, z-index: 40)
├── Row 1: Navigation & Identification
│   ├── BackButton ("← Back to Projects")
│   ├── ProjectBadge ("Project #123")
│   ├── JobIDBadge ("Job #456")
│   ├── QuotationBadge ("QT-2024-789")
│   ├── Spacer (flex-grow)
│   ├── PrintButton
│   └── MoreActionsMenu (dropdown)
│
├── Row 2: Customer & Status
│   ├── CustomerSection (flex-1)
│   │   ├── CustomerName (large, bold, clickable → profile)
│   │   ├── PhoneNumber (with icon, tel: link)
│   │   └── Address (compact, truncated)
│   │
│   ├── StatusSection (flex-1, text-center)
│   │   ├── StatusBadge (large, colored: current stage)
│   │   └── PriorityBadge (High/Medium/Low)
│   │
│   └── QuickActionsSection (flex-1, text-right)
│       └── ConditionalButtons (based on project state)
│
├── Row 3: Financial Summary
│   ├── TotalCard
│   │   ├── Label: "Total Value"
│   │   └── Amount: "EGP 50,000" (green, large)
│   │
│   ├── PaidCard
│   │   ├── Label: "Paid"
│   │   └── Amount: "EGP 30,000" (green)
│   │
│   ├── RemainingCard
│   │   ├── Label: "Remaining"
│   │   └── Amount: "EGP 20,000" (red if >0, green if 0)
│   │
│   └── ProgressCard
│       ├── Label: "Progress"
│       ├── ProgressBar (visual, 60% filled)
│       └── Percentage: "60%"
│
└── Row 4: Dates Summary
    ├── CreatedDate: "Created: 01/01/2026"
    ├── ExpectedDate: "Expected: 15/02/2026"
    └── LastUpdated: "Updated: 2 hours ago"
```

### Component Specifications

#### ProjectDetailsHeader Component

**Responsibilities**:
- Sticky positioning (always visible)
- Aggregate and display critical project data
- Provide quick action buttons
- Responsive layout (stack on mobile)

**Props**:
```typescript
interface ProjectDetailsHeaderProps {
  job: Job;
  quotation: Quotation;
  customer: Customer;
  payments: Payment[];
  onPrint: () => void;
  onBack: () => void;
}
```

**State**: None (stateless, actions delegated to parent)

**Styling**:
```css
.project-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1rem 1.5rem;
}
```

**Responsive Behavior**:
- Desktop (≥1024px): 4-row layout as shown
- Tablet (768-1023px): Stack financial cards 2x2
- Mobile (<768px): Single column, hide some secondary info

#### FinancialSummary Component

**Responsibilities**:
- Calculate payment totals
- Display financial health indicators
- Visual progress bar

**Props**:
```typescript
interface FinancialSummaryProps {
  quotationTotal: number;
  payments: Payment[];
}
```

**Calculations**:
```typescript
const totalPaid = payments
  .filter(p => p.status === 'paid')
  .reduce((sum, p) => sum + parseFloat(p.amount), 0);

const remaining = quotationTotal - totalPaid;
const progress = (totalPaid / quotationTotal) * 100;

const hasOverduePayments = payments.some(p =>
  p.status === 'pending' &&
  p.due_date &&
  new Date(p.due_date) < new Date()
);
```

### State Management

**Data Fetching**:
```typescript
const useProjectHeader = (jobId: number) => {
  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.getById(jobId)
  });
  
  const { data: quotation, isLoading: quotationLoading } = useQuery({
    queryKey: ['quotation', job?.quotation_id],
    queryFn: () => quotationsApi.getById(job.quotation_id),
    enabled: !!job?.quotation_id
  });
  
  const { data: customer, isLoading: customerLoading } = useQuery({
    queryKey: ['customer', job?.customer_id],
    queryFn: () => customersApi.getById(job.customer_id),
    enabled: !!job?.customer_id
  });
  
  const { data: payments = [], isLoading: paymentsLoading } = useQuery({
    queryKey: ['payments', 'job', jobId],
    queryFn: () => paymentsApi.getByJobId(jobId)
  });
  
  const isLoading = jobLoading || quotationLoading || customerLoading || paymentsLoading;
  
  return { job, quotation, customer, payments, isLoading };
};
```

**Derived State**:
```typescript
const financialSummary = useMemo(() => ({
  total: parseFloat(quotation?.final_price || '0'),
  paid: payments
    .filter(p => p.status === 'paid')
    .reduce((sum, p) => sum + parseFloat(p.amount), 0),
  get remaining() {
    return this.total - this.paid;
  },
  get progress() {
    return this.total > 0 ? (this.paid / this.total) * 100 : 0;
  },
  hasOverduePayments: payments.some(p =>
    p.status === 'pending' &&
    p.due_date &&
    new Date(p.due_date) < new Date()
  )
}), [quotation, payments]);
```

### Loading Strategy

**Skeleton Loading**:
```typescript
if (isLoading) {
  return (
    <ProjectDetailsHeader>
      <Skeleton className="h-8 w-48" />  {/* Project ID */}
      <Skeleton className="h-12 w-64" /> {/* Customer name */}
      <div className="grid grid-cols-4 gap-4">
        <Skeleton className="h-24" />    {/* Financial cards */}
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
    </ProjectDetailsHeader>
  );
}
```

**Progressive Loading**:
1. Show job data first (fastest)
2. Show customer data when available
3. Show quotation data when available
4. Calculate financial summary when payments load

### Error Handling

**Missing Data**:
```typescript
if (!job) {
  return <ErrorMessage title="Project not found" />;
}

if (!quotation) {
  // Show header with available data, display "Quotation loading..." in quotation badge
}

if (!customer) {
  // Show header with available data, display "Customer loading..." in customer section
}
```

### Navigation Flows

**Back Button**:
```typescript
const handleBack = () => {
  navigate('/jobs');
};
```

**View Customer Profile**:
```typescript
const handleViewCustomer = (customerId: number) => {
  window.open(`/customers/${customerId}`, '_blank');
};
```

**Call Customer**:
```typescript
<a href={`tel:${customer.phone}`} className="flex items-center gap-2">
  <Phone className="w-4 h-4" />
  {customer.phone}
</a>
```

**WhatsApp Customer**:
```typescript
<a
  href={`https://wa.me/${customer.phone.replace(/\D/g, '')}`}
  target="_blank"
  rel="noopener noreferrer"
  className="flex items-center gap-2"
>
  <MessageCircle className="w-4 h-4" />
  WhatsApp
</a>
```

**Print Project**:
```typescript
const handlePrint = () => {
  window.print(); // Uses @media print styles
};
```

### Performance Considerations

**Initial Load**:
- Target: <500ms to display header
- Parallel data fetching (React Query)
- Progressive rendering (show data as it loads)

**Sticky Header Performance**:
- Use `position: sticky` (hardware-accelerated)
- Fixed height (prevents layout shifts)
- Minimal re-renders (React.memo on financial cards)

**Responsive Images**:
- No images in header (icon-only)

---

*(Continuing with Steps 3-10 in condensed format for length...)*


## STEP 3-10: Implementation Summary

*For detailed design of Steps 3-10, see specialized documents:*
- `workflow-stages-design.md` - Step 3: Workflow visual pipeline with stage completion
- `timeline-engine-design.md` - Step 4: Automatic event recording system
- `payments-integration-design.md` - Step 5: Payment summary within project
- `measurements-design.md` - Step 6: Measurement cards and operations
- `quotation-integration-design.md` - Step 7: Quotation section within project
- `customer-section-design.md` - Step 8: Customer info and quick actions
- `activity-documents-design.md` - Step 9: Activity feed and document placeholders
- `polish-ux-design.md` - Step 10: Final UX improvements

### Steps 3-10 Quick Overview

**Step 3: Workflow Section** - Visual pipeline showing 8 stages (Quotation → Measurement → Deposit → Production → Installation → Completed → Cancelled → On Hold), with completion buttons, overdue indicators, and automatic stage transitions.

**Step 4: Timeline Section** - Automatic timeline recording 15+ event types (project created, quotation approved, measurement completed, payments received, etc.) with planned vs actual dates, duration calculations, delay warnings.

**Step 5: Payments Integration** - Payment summary cards (total/paid/remaining/progress), payment history list, add payment modal, mark as paid action. Global Payments module remains separate for accounting.

**Step 6: Measurements Integration** - Measurement cards showing visit dates and items, add measurement button, edit measurement modal, integration with measurement items display.

**Step 7: Quotation Integration** - Quotation items table, totals display, discount info, edit quotation (if no job), add/remove items, approve/reject quotation actions.

**Step 8: Customer Section** - Customer name, phone (call/WhatsApp links), address, customer notes, "View Customer Profile" link to CRM module.

**Step 9: Activity & Documents** - Activity feed from ActivityLog table (automatic timeline events), Documents section placeholder for future file uploads.

**Step 10: Polish & UX** - Responsive design audit, loading states polish, error handling improvements, toast notifications, keyboard navigation, accessibility audit, print stylesheet.

---

## Cross-Cutting Concerns

### Automatic Timeline Recording

**Principle**: Timeline events are created automatically by backend when significant actions occur. No manual timeline entry.

**Event Sources**:
1. **Database Triggers** (Preferred): PostgreSQL triggers on status changes
2. **Service Layer** (Current): Service methods emit events after operations
3. **ActivityLog Table**: Store all events with timestamp, user, action, metadata

**Example Implementation**:
```python
# Backend: app/services/job.py
async def complete_stage(db: Session, job_id: int, stage: str, user_id: int):
    job = await job_repo.get_by_id(db, job_id)
    
    # Update job status
    job.status = get_next_status(stage)
    job.updated_at = datetime.utcnow()
    
    # Record in ActivityLog
    activity = ActivityLog(
        job_id=job_id,
        user_id=user_id,
        action=f"stage_completed_{stage}",
        description=f"Completed {stage} stage",
        metadata={"stage": stage, "duration": calculate_duration(job, stage)},
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    db.commit()
    return job
```

**Frontend Integration**:
```typescript
// Fetch timeline events
const { data: timeline } = useQuery({
  queryKey: ['timeline', jobId],
  queryFn: () => activityLogsApi.getByJobId(jobId)
});

// Timeline auto-updates when mutations occur
const markPaidMutation = useMutation({
  mutationFn: (paymentId) => paymentsApi.markAsPaid(paymentId),
  onSuccess: () => {
    queryClient.invalidateQueries(['timeline', jobId]); // Refetch timeline
    queryClient.invalidateQueries(['payments', jobId]);
  }
});
```

### Workflow Stage Management

**Stage Definitions**:
```typescript
const workflowStages = [
  {
    id: 'quotation',
    name: 'Quotation',
    jobStatus: null, // No job yet
    entryCondition: () => true, // Always can enter
    exitCondition: (quotation) => quotation.status === 'approved',
    requiredActions: ['Send quotation', 'Follow up with customer'],
    allowedActions: ['Edit quotation', 'Add items', 'Approve', 'Reject'],
    nextStage: 'measurement'
  },
  {
    id: 'measurement',
    name: 'Measurement',
    jobStatus: 'measuring',
    entryCondition: (job) => job.quotation.status === 'approved',
    exitCondition: (job) => job.measurement_date !== null,
    requiredActions: ['Schedule visit', 'Conduct measurement'],
    allowedActions: ['Add measurement', 'Edit measurement', 'Reschedule'],
    nextStage: 'deposit',
    expectedDuration: 7 // days
  },
  {
    id: 'deposit',
    name: 'Deposit',
    jobStatus: 'pending',
    entryCondition: (job) => job.measurement_date !== null,
    exitCondition: (job, payments) =>
      payments.some(p => p.payment_type === 'deposit' && p.status === 'paid'),
    requiredActions: ['Invoice customer', 'Collect deposit'],
    allowedActions: ['Add payment', 'Mark paid', 'Send reminder'],
    nextStage: 'production',
    expectedDuration: 3
  },
  {
    id: 'production',
    name: 'Manufacturing',
    jobStatus: 'in_production',
    entryCondition: (job, payments) =>
      payments.some(p => p.payment_type === 'deposit' && p.status === 'paid'),
    exitCondition: (job) => job.production_end !== null,
    requiredActions: ['Start production', 'Track progress', 'Complete manufacturing'],
    allowedActions: ['Update dates', 'Add notes', 'Quality check'],
    nextStage: 'installation',
    expectedDuration: 14
  },
  {
    id: 'installation',
    name: 'Installation',
    jobStatus: 'ready_for_installation',
    entryCondition: (job) => job.production_end !== null,
    exitCondition: (job) => job.installation_date !== null && job.status === 'installed',
    requiredActions: ['Schedule installation', 'Install product', 'Customer sign-off'],
    allowedActions: ['Update date', 'Add installer notes', 'Upload photos'],
    nextStage: 'completed',
    expectedDuration: 1
  },
  {
    id: 'completed',
    name: 'Completed',
    jobStatus: 'completed',
    entryCondition: (job) => job.status === 'installed',
    exitCondition: () => false, // Terminal state
    requiredActions: ['Collect final payment', 'Close project'],
    allowedActions: ['View only', 'Add notes'],
    nextStage: null
  }
];
```

**Stage Transition Logic**:
```typescript
const completeStage = async (jobId: number, stageId: string) => {
  const stage = workflowStages.find(s => s.id === stageId);
  if (!stage) throw new Error('Invalid stage');
  
  const job = await getJob(jobId);
  const payments = await getPayments(jobId);
  
  // Validate exit condition
  if (!stage.exitCondition(job, payments)) {
    throw new Error(`Cannot complete ${stage.name}: conditions not met`);
  }
  
  // Update job to next stage
  const nextStage = workflowStages.find(s => s.id === stage.nextStage);
  if (nextStage) {
    await updateJobStatus(jobId, nextStage.jobStatus);
  }
  
  // Record completion in timeline
  await recordTimelineEvent({
    jobId,
    event: `${stage.id}_completed`,
    timestamp: new Date(),
    userId: currentUser.id
  });
};
```

### Payment Integration Architecture

**Principle**: Project page shows payments for THIS project only. Global Payments page shows ALL payments for accounting.

**Data Flow**:
```
ProjectDetailsPage
  ├─ GET /api/v1/payments?job_id=123  (only this project's payments)
  ├─ Display payment summary cards
  ├─ Display payment history list
  └─ Link to: /payments?job_id=123 (global page filtered)

PaymentsPage (Global)
  ├─ GET /api/v1/payments (all payments, all projects)
  ├─ Display consolidated accounting view
  ├─ Reports, reconciliation, bulk operations
  └─ Optional filter by job_id, customer_id, date range
```

**Component Architecture**:
```tsx
// In ProjectDetailsPage
<CollapsibleSection title="Payments" defaultOpen>
  <PaymentsSummary
    quotationTotal={quotation.final_price}
    payments={payments}
  />
  <PaymentsList
    payments={payments}
    onAddPayment={handleAddPayment}
    onMarkPaid={handleMarkPaid}
  />
  <Link to={`/payments?job_id=${job.id}`} target="_blank">
    View in Global Payments Module →
  </Link>
</CollapsibleSection>
```

### Dashboard KPI Integration

**Principle**: Dashboard KPIs filter Projects page. Dashboard does not duplicate project functionality.

**KPI Click Handlers**:
```typescript
// Dashboard KPI Component
const KPICard = ({ metric, value, onClick }: KPICardProps) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    const filters = getFiltersForMetric(metric);
    navigate('/jobs', { state: { filters, source: 'dashboard', metric } });
  };
  
  return (
    <div onClick={handleClick} className="cursor-pointer hover:shadow-lg">
      <h3>{metric}</h3>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
};

// Filter mapping
const getFiltersForMetric = (metric: string): ProjectFilters => {
  switch (metric) {
    case 'delayed-jobs':
      return { showOverdueOnly: true, stages: ['measuring', 'in_production', 'ready_for_installation'] };
    
    case 'waiting-quotations':
      return { stages: ['pending'] }; // Quotation stage
    
    case 'today-measurements':
      return {
        dateRange: { from: today, to: today },
        stages: ['measuring']
      };
    
    case 'overdue-payments':
      return { paymentStatuses: ['overdue'] };
    
    default:
      return {};
  }
};
```

### Future Scalability Architecture

**Collapsible Section Pattern**:
```tsx
// All major sections use CollapsibleSection component
<CollapsibleSection title="Workflow" icon={<GitBranch />} defaultOpen>
  <WorkflowPipeline ... />
</CollapsibleSection>

<CollapsibleSection title="Timeline" icon={<Clock />}>
  <ProjectTimeline ... />
</CollapsibleSection>

<CollapsibleSection title="Payments" icon={<DollarSign />}>
  <PaymentsSection ... />
</CollapsibleSection>

// Future features add new collapsible sections
<CollapsibleSection title="Materials" icon={<Package />}>
  <MaterialsTracking ... />  {/* Future */}
</CollapsibleSection>

<CollapsibleSection title="Team" icon={<Users />}>
  <TeamAssignments ... />  {/* Future */}
</CollapsibleSection>
```

**Plugin Architecture** (Future):
```typescript
// Registry pattern for extensibility
interface ProjectSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  component: React.ComponentType<ProjectSectionProps>;
  requiredPermissions?: string[];
  enabled: boolean;
}

const projectSections: ProjectSection[] = [
  { id: 'workflow', title: 'Workflow', icon: <GitBranch />, component: WorkflowSection, enabled: true },
  { id: 'timeline', title: 'Timeline', icon: <Clock />, component: TimelineSection, enabled: true },
  { id: 'materials', title: 'Materials', icon: <Package />, component: MaterialsSection, enabled: false }, // Future
  // ... more sections
];

// Render dynamically
{projectSections
  .filter(section => section.enabled)
  .map(section => (
    <CollapsibleSection key={section.id} title={section.title} icon={section.icon}>
      <section.component job={job} quotation={quotation} />
    </CollapsibleSection>
  ))
}
```

---

## Testing Strategy

### Unit Testing

**Components**:
- Test `ProjectCard` renders correctly with various project states
- Test `FinancialSummary` calculations (total, paid, remaining, progress)
- Test `WorkflowStage` conditional rendering based on stage status
- Test filter logic in `useProjectsFilters` hook
- Test search debounce in `useProjectsSearch` hook

**Example**:
```typescript
describe('FinancialSummary', () => {
  it('calculates total paid correctly', () => {
    const payments = [
      { id: 1, amount: '10000', status: 'paid' },
      { id: 2, amount: '5000', status: 'pending' },
      { id: 3, amount: '15000', status: 'paid' }
    ];
    
    const { getByText } = render(
      <FinancialSummary quotationTotal={50000} payments={payments} />
    );
    
    expect(getByText('EGP 25,000')).toBeInTheDocument(); // Total paid
    expect(getByText('EGP 25,000')).toBeInTheDocument(); // Remaining
  });
});
```

### Integration Testing

**Scenarios**:
1. Complete project workflow end-to-end
2. Add payment and verify financial summary updates
3. Complete stage and verify timeline records event
4. Filter projects list and verify correct projects shown
5. Navigate from Dashboard KPI to filtered Projects page

### Manual Testing Checklist

**Per Step**:
- [ ] All features work as designed
- [ ] Responsive on mobile (320px), tablet (768px), desktop (1024px+)
- [ ] RTL layout correct (Arabic)
- [ ] Loading states show skeletons
- [ ] Error states show helpful messages
- [ ] Success feedback via toast notifications
- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] Print stylesheet works (for Step 10)
- [ ] No console errors/warnings
- [ ] No TypeScript errors
- [ ] Performance acceptable (<2s initial load)

---

## Deployment Strategy

### Step-by-Step Deployment

**Process**:
1. Complete Step N implementation
2. Run unit tests
3. Manual testing checklist
4. Code review
5. Deploy to staging
6. Stakeholder review
7. Deploy to production
8. Monitor for issues
9. **Only then proceed to Step N+1**

**Rollback Plan**:
- Each step is independently deployable
- If Step N has issues, roll back to Step N-1
- No database migrations = easy rollback

### Feature Flags (Optional)

```typescript
// Enable gradual rollout
const useFeatureFlag = (flag: string) => {
  return localStorage.getItem(`feature_${flag}`) === 'true';
};

// Usage
{useFeatureFlag('new_project_list') ? (
  <NewProjectsList />
) : (
  <OldProjectsList />
)}
```

---

## Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Initial page load (Projects list) | < 2 seconds | Lighthouse, RUM |
| Project details page load | < 1.5 seconds | Lighthouse |
| Header data load | < 500ms | Network tab |
| Filter application | < 100ms (instant) | Performance.now() |
| Search results | < 300ms (debounced) | Performance.now() |
| Timeline rendering | < 200ms | React Profiler |
| Workflow stage completion | < 500ms | Network + UI update |

### Optimization Techniques

1. **Code Splitting**: Lazy load heavy components (date pickers, rich text editors)
2. **React Query Caching**: 5-minute cache, background refetch
3. **Virtual Scrolling**: If >200 projects in list
4. **Image Optimization**: Use WebP, lazy load
5. **Bundle Analysis**: Keep JS bundle <500KB gzipped
6. **Debouncing**: Search input 300ms
7. **Memoization**: Expensive calculations (filters, sorts)
8. **React.memo**: Prevent unnecessary re-renders

---

## Accessibility Requirements

### WCAG 2.1 AA Compliance

**Keyboard Navigation**:
- Tab through all interactive elements
- Enter/Space activate buttons
- Escape closes modals
- Arrow keys navigate lists

**Screen Reader**:
- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- ARIA labels for icons ("Add payment", "Mark as paid")
- ARIA live regions for dynamic updates
- Focus management (trap focus in modals)

**Visual**:
- Color contrast ≥4.5:1 for text
- Focus indicators visible
- No color-only information (use icons + text)
- Resizable text up to 200%

**Touch**:
- Touch targets ≥44x44px
- No hover-only functionality
- Swipe gestures optional (provide buttons)

**Example**:
```tsx
<button
  onClick={handleAddPayment}
  aria-label="Add new payment to this project"
  className="min-h-[44px] min-w-[44px]"
>
  <Plus className="w-5 h-5" aria-hidden="true" />
  <span className="sr-only">Add Payment</span>
</button>
```

---

## Security Considerations

**Authentication**:
- All API requests require valid JWT token
- Token refresh on expiration

**Authorization**:
- Role-based access control (future)
- Currently: authenticated users can access all projects

**Input Validation**:
- Client-side: Form validation with error messages
- Server-side: DTOs with Pydantic validation
- Sanitize user input (XSS prevention)

**Data Protection**:
- HTTPS only
- Sensitive data (payments) show confirmation dialogs
- No PII in URLs or logs

**Example**:
```typescript
// Payment amount confirmation
const handleMarkPaid = (payment: Payment) => {
  confirmDialog({
    title: 'Mark Payment as Paid',
    message: `Confirm payment of ${formatCurrency(payment.amount)}?`,
    onConfirm: async () => {
      await markPaidMutation.mutateAsync(payment.id);
    }
  });
};
```

---

## Monitoring & Observability

**Frontend Metrics**:
- Page load times (Lighthouse CI)
- API response times (React Query devtools)
- Error rates (Sentry / error boundary)
- User interactions (analytics)

**Backend Metrics**:
- API endpoint latency
- Database query performance
- Error rates and types

**Alerting**:
- Page load >3 seconds
- API errors >5% of requests
- Database queries >1 second

---

## Documentation Deliverables

1. ✅ **design.md** (This document) - Complete technical design
2. **architecture.md** - System architecture diagrams
3. **api-design.md** - Every endpoint specification
4. **component-tree.md** - Frontend component hierarchy
5. **implementation-order.md** - Exact implementation sequence
6. **risk-analysis.md** - Technical risks and mitigation
7. **future-roadmap.md** - Scalability plan for 11 future features

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Next Phase**: Create specialized design documents  
**Status**: Ready for stakeholder review

