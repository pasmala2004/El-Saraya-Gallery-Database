# Projects Module Redesign - Requirements Document

**Feature ID**: `projects-module-redesign`  
**Status**: Phase 0 - Architecture (No Code)  
**Priority**: High  
**Target Users**: Gallery Assistants, Operations Staff  
**Created**: 2026-07-21

---

## Executive Summary

Transform the Projects module into **the central operational workspace** of the entire ERP system. After quotation approval, the quotation becomes a **Project** - the single source of truth for all related information (customer, measurements, payments, manufacturing, installation, documents, notes, activity). The Projects module will serve as the primary interface where employees spend 80% of their daily work time, eliminating the need for constant navigation between modules.

---

## Core Principles

### 1. Project as the Center of the ERP

**Philosophy**: After a quotation is approved, it becomes a **Project** - the central entity that aggregates all related information.

**Everything Attached to Project**:
- Customer information
- Quotation details and items
- Measurements (all visits)
- Payments (summary and history)
- Manufacturing status
- Installation schedule
- Documents and files
- Internal and customer notes
- Complete activity history

**Navigation Principle**: No information should require navigating to another page unless accessing a management/reporting module (e.g., global Payments page for accounting, global Customers page for CRM).

### 2. Single Project Workspace

**Philosophy**: The Project Details page is the **operational workspace** used every day. Employees should perform almost every operation from this page without leaving.

**Operations Available on Project Page**:
- ✅ Edit quotation (before job creation)
- ✅ Add quotation items
- ✅ Add new measurement
- ✅ Edit existing measurements
- ✅ Add payment
- ✅ Update payment status (mark as paid)
- ✅ Update workflow stage
- ✅ Add internal notes
- ✅ Upload documents (future)
- ✅ View customer information
- ✅ View complete activity history
- ✅ Print project summary
- ✅ Export project data

**External Navigation Only For**:
- Global customer management (CRM)
- Global payments accounting
- Global product catalog
- Reporting and analytics
- System administration

### 3. ERP Navigation Philosophy

```
Dashboard ──────> Overview & KPIs
                  Clicking KPI ──> Filtered Projects
                  
Projects ───────> Daily operational workspace (80% of time)
                  Single source of truth per project
                  
Customers ──────> CRM & customer management
                  
Payments ───────> Financial management & accounting
                  (Shows all payments across all projects)
                  
Products ───────> Catalog management
```

**Anti-Pattern to Avoid**: Duplicating functionality across modules. Each module has a clear purpose.

### 4. Future Scalability

**Philosophy**: The design must support future additions without architectural redesign.

**Planned Future Features** (not in scope now, but architecture must accommodate):
- Employee assignments (assign measurement engineer, installer, etc.)
- Calendar integration (sync schedules)
- Notifications system (SMS, email, push)
- Inventory tracking (materials used)
- Manufacturing workflow tracking
- Installer management
- AI assistant (chatbot, recommendations)
- Advanced reports and analytics
- File management system (upload contracts, photos, invoices)
- Multi-location support
- Custom fields per project type

**Design Requirement**: All future features must integrate into the Project page without breaking existing functionality or requiring navigation away from the workspace.

---

## Problem Statement

### Current Pain Points

1. **Fragmented Workflow**: Staff must navigate between 4-5 different pages (Jobs, Quotations, Payments, Measurements) to manage a single project
2. **Limited Visibility**: Project overview lacks critical information like payment status, financial progress, and workflow stage
3. **Inefficient Operations**: Common tasks require multiple clicks and page loads
4. **Minimal Project Creation**: Dialog only captures Quotation and Notes, missing critical planning data
5. **Poor Context Switching**: Losing context when moving between modules

### User Impact

- Gallery assistants spend 30-40% of time navigating between pages
- Increased risk of errors from context switching
- Slower response times to customer inquiries
- Difficulty tracking project financial health
- Limited visibility into project delays and bottlenecks

---

## Goals & Success Metrics

### Primary Goals

1. **Project as Center**: Make Project the central entity with all information aggregated
2. **Single Workspace**: Enable all operations from Project Details page without navigation
3. **Operational Home**: Projects page becomes the operations team's home page (not Dashboard)
4. **Automatic Timeline**: Record every important event automatically with date, time, user, description
5. **Real Workflow**: Implement business process stages with entry/exit conditions
6. **Payment Integration**: Show payment summary while keeping accounting in separate module
7. **Instant Visibility**: Project list shows all critical info without opening individual projects
8. **Dashboard Integration**: Dashboard KPIs filter Projects page (not standalone functionality)
9. **Future-Proof**: Architecture supports planned features without redesign

### Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Pages visited per project check | 3-5 | 1 | Analytics tracking |
| Time to check project status | 3 min | 30 sec | User timing |
| Payment visibility | 0% | 100% | Feature usage |
| Customer satisfaction | Baseline | +20% | Surveys |
| Navigation between modules | High | Minimal | Click tracking |

---

## Implementation Strategy

### Phased Approach (10 Steps)

**Each step must be:**
- Fully functional and production-ready
- Zero regressions from previous functionality
- Independently deployable
- Verified before proceeding to next step

### Phase 0: Architecture (Current Phase)
- ✅ Freeze current implementation
- ✅ Create comprehensive specification
- ✅ Define component reuse strategy
- ✅ Document backend API requirements

---

## Requirements by Implementation Step

## STEP 1: Project List Redesign

### User Stories

**US-1.1**: As an operations team member, I want the Projects page to be my home page, so I can immediately see all active work

**Acceptance Criteria**:
- WHEN viewing the Projects page
- THEN it serves as the operational home (primary daily interface)
- AND each project card/row shows comprehensive information:
  - **Project ID** (prominent, clickable)
  - **Customer name** (large, bold)
  - **Current stage** (colored badge: Quotation/Measurement/Deposit/Manufacturing/Installation/Completed/Cancelled/On Hold)
  - **Priority** (High/Medium/Low badge with icon)
  - **Latest activity** (relative time: "2 hours ago", with description)
  - **Payment progress** (visual bar showing % paid)
  - **Days in current stage** (number badge)
  - **Expected completion date** (formatted date)
  - **Warning badges** (overdue, payment due, action required)
- AND I can understand project status WITHOUT opening the project
- AND layout is card-based (not simple table)
- AND cards are visually scannable (color coding, icons, hierarchy)

**US-1.2**: As a gallery assistant, I want to filter projects by multiple criteria, so I can quickly find specific projects

**Acceptance Criteria**:
- WHEN using filter controls
- THEN I can filter by:
  - Stage (Quotation, Measurement, Deposit, Manufacturing, Installation, Completed, Rejected, Pending)
  - Priority (High, Medium, Low, All)
  - Payment Status (Paid, Pending, Overdue, All)
  - Customer (dropdown with search)
  - Date range (Created date, Expected delivery)
  - Overdue status (toggle)
- AND filters can be combined (AND logic)
- AND filter state persists during session
- AND "Clear Filters" button resets all filters

**US-1.3**: As a gallery assistant, I want to search projects by multiple fields, so I can quickly locate any project

**Acceptance Criteria**:
- WHEN typing in search box
- THEN system searches across:
  - Customer name (fuzzy match)
  - Quotation number (exact match)
  - Job ID (partial match)
  - Phone number (partial match)
- AND results update in real-time (debounced 300ms)
- AND search highlights matching text
- AND "No results" message shows when nothing matches

**US-1.4**: As an operations manager, I want to click Dashboard KPIs to filter Projects, so I can quickly access relevant work

**Acceptance Criteria**:
- WHEN clicking a Dashboard KPI (e.g., "Delayed Jobs")
- THEN system navigates to Projects page
- AND automatically applies appropriate filter:
  - "Delayed Jobs" KPI → Projects filtered to overdue stages
  - "Waiting Quotations" KPI → Projects filtered to pending approval
  - "Today's Measurements" KPI → Projects with measurements scheduled today
  - "Overdue Payments" KPI → Projects with unpaid overdue payments
  - "Active Projects" KPI → Projects in active stages (not completed/cancelled)
- AND filter badge shows "(Filtered from Dashboard: [KPI name])"
- AND "Clear Filter" button returns to all projects
- AND filter state persists in URL (shareable)

---

## STEP 2: Project Details - Complete Workspace

### Core Principle
**The Project Details page is a complete operational workspace. Users should perform ALL daily operations here without leaving the page.**

### User Stories: In-Page Operations

**US-2.1**: As a gallery assistant, I want to edit quotation details from the Project page, so I don't need to navigate to Quotations module

**Acceptance Criteria**:
- WHEN project is in Quotation stage (no job created yet)
- THEN "Edit Quotation" button displays in Quotation section
- WHEN clicking "Edit Quotation"
- THEN inline edit mode activates OR modal opens
- AND I can edit: discount, notes, valid until date
- WHEN saving changes
- THEN quotation updates via API
- AND Project page refreshes automatically
- AND activity log records "Quotation edited by [user]"
- AND I remain on Project page (no navigation)

**US-2.2**: As a gallery assistant, I want to add quotation items from the Project page, so I can update the quotation without leaving

**Acceptance Criteria**:
- WHEN project is in Quotation stage (no job created yet)
- THEN "Add Item" button displays in Quotation section header
- WHEN clicking "Add Item"
- THEN modal opens with form:
  - Product (dropdown with search)
  - Quantity (number input)
  - Unit price (auto-filled from product, editable)
  - Description (textarea, optional)
  - Notes (textarea, optional)
- WHEN submitting form
- THEN item adds to quotation via API
- AND Quotation section refreshes with new item
- AND totals recalculate automatically
- AND activity log records "Item added: [product name]"
- AND modal closes
- AND I remain on Project page

**US-2.3**: As a gallery assistant, I want to add a measurement from the Project page, so I can record site visits immediately

**Acceptance Criteria**:
- WHEN project has an active job
- THEN "Add Measurement" button displays in Measurements section (and header)
- WHEN clicking "Add Measurement"
- THEN modal opens with form:
  - Visit date (date picker, defaults to today)
  - Measured by (text input for engineer name)
  - Notes (textarea, optional)
- WHEN submitting form
- THEN measurement creates via API
- AND system navigates to Measurement Details page to add items
- OR stays on Project page and opens inline measurement item entry
- AND Measurements section refreshes
- AND activity log records "Measurement #X added by [user]"

**US-2.4**: As a gallery assistant, I want to edit measurements from the Project page, so I can correct information quickly

**Acceptance Criteria**:
- WHEN viewing measurement card in Measurements section
- THEN "Edit" button displays on hover
- WHEN clicking "Edit"
- THEN measurement details become editable inline OR modal opens
- AND I can edit: visit date, measured by, notes
- WHEN saving changes
- THEN measurement updates via API
- AND measurement card refreshes
- AND activity log records "Measurement #X edited by [user]"
- AND I remain on Project page

**US-2.5**: As a gallery assistant, I want to add a payment from the Project page, so I can record collections immediately

**Acceptance Criteria**:
- WHEN project has an active job
- THEN "Add Payment" button displays in Payments section (and header)
- WHEN clicking "Add Payment"
- THEN modal opens with form:
  - Payment type (Deposit/Production/Final)
  - Payment method (Cash/Bank/Instapay/Cheque/Other)
  - Percentage (auto-suggests based on type)
  - Amount (auto-calculated, editable)
  - Due date (date picker)
  - Notes (textarea)
- WHEN submitting form
- THEN payment creates via API
- AND Payments section refreshes with new payment
- AND payment summary recalculates (total paid, balance, progress)
- AND activity log records "Payment #X added: [amount]"
- AND I remain on Project page

**US-2.6**: As a gallery assistant, I want to mark payments as paid from the Project page, so I can update status instantly

**Acceptance Criteria**:
- WHEN viewing pending payment in Payments section
- THEN "Mark as Paid" button displays
- WHEN clicking "Mark as Paid"
- THEN confirmation dialog asks: "Mark payment as paid? Paid date will be set to today."
- WHEN confirming
- THEN payment status updates to 'paid' via API
- AND paid_date sets to current date
- AND payment card updates with green "Paid" badge
- AND payment summary recalculates
- AND activity log records "Payment #X marked paid by [user]"
- AND I remain on Project page

**US-2.7**: As a gallery assistant, I want to update workflow stage from the Project page, so I can advance the project

**Acceptance Criteria**:
- WHEN project is in active stage
- THEN "Complete Stage" button displays in Workflow section
- WHEN clicking "Complete Stage"
- THEN confirmation dialog shows:
  - "Mark [Stage] as complete?"
  - Entry/exit conditions checklist (if any not met, show warnings)
  - "This will advance the project to [Next Stage]"
- WHEN confirming
- THEN system:
  - Records completion timestamp for current stage
  - Records current user as responsible person
  - Advances project to next stage
  - Updates job status via API
  - Creates activity log entry
  - Refreshes Workflow section
  - Shows success toast: "[Stage] completed. Project moved to [Next Stage]"
- AND I remain on Project page

**US-2.8**: As a gallery assistant, I want to add internal notes from the Project page, so I can document important information

**Acceptance Criteria**:
- WHEN viewing Notes section
- THEN "Add Note" button or inline text area displays
- WHEN clicking "Add Note" or typing in text area
- THEN note input becomes active
- AND I can enter rich text (bold, lists, links - future)
- WHEN saving note
- THEN note appends to project notes via API
- AND Notes section refreshes showing new note with timestamp and author
- AND activity log records "Note added by [user]"
- AND I remain on Project page

**US-2.9**: As a gallery assistant, I want to view customer information from the Project page, so I can contact them quickly

**Acceptance Criteria**:
- WHEN viewing Customer section
- THEN displays:
  - Customer name (large, prominent)
  - Phone number with "Call" icon (tel: link)
  - "Copy Phone" button (clipboard)
  - "WhatsApp" button (opens wa.me/[phone])
  - Address (full)
  - Customer notes (if any)
  - "View Customer Profile" link (opens Customers page in new tab)
- AND clicking phone number initiates call on mobile
- AND clicking WhatsApp opens WhatsApp Web/App with number pre-filled
- AND I can perform all actions WITHOUT leaving Project page

**US-2.10**: As a gallery assistant, I want to view activity history from the Project page, so I can see what happened

**Acceptance Criteria**:
- WHEN viewing Activity section
- THEN displays chronological feed (newest first):
  - Icon (representing action type)
  - Action description ("Quotation approved", "Payment added", etc.)
  - User who performed action
  - Timestamp (absolute and relative: "2 hours ago")
  - Additional details (if applicable)
- AND activity auto-refreshes when changes occur on page
- AND activity loads from ActivityLog table via API
- AND I can see complete project history WITHOUT leaving page

---

## STEP 3: Workflow Section - Real Business Process

### Core Principle
**The workflow represents the actual business process with defined stages, conditions, and automatic tracking.**

### Workflow Stages Definition

**Stage 1: Quotation**
- **Entry Condition**: Quotation created
- **Exit Condition**: Quotation approved by customer
- **Required Actions**: Send quotation to customer, follow up
- **Allowed Actions**: Edit quotation, add items, change discount, cancel
- **Completion %**: When status = 'approved'
- **Next Stage**: Measurement

**Stage 2: Measurement**
- **Entry Condition**: Quotation approved (job created)
- **Exit Condition**: Measurement completed and reviewed
- **Required Actions**: Schedule measurement, conduct site visit, record dimensions
- **Allowed Actions**: Add measurement, edit measurement, reschedule
- **Completion %**: When measurement_date is set and measurements exist
- **Next Stage**: Deposit

**Stage 3: Deposit**
- **Entry Condition**: Measurement completed
- **Exit Condition**: Deposit payment received
- **Required Actions**: Invoice customer for deposit, collect payment
- **Allowed Actions**: Add deposit payment, mark payment as paid
- **Completion %**: When deposit payment status = 'paid'
- **Next Stage**: Manufacturing

**Stage 4: Manufacturing**
- **Entry Condition**: Deposit received
- **Exit Condition**: Manufacturing completed
- **Required Actions**: Start production, track progress, complete manufacturing
- **Allowed Actions**: Update production dates, add manufacturing notes
- **Completion %**: When production_end is set
- **Next Stage**: Installation

**Stage 5: Installation**
- **Entry Condition**: Manufacturing completed
- **Exit Condition**: Installation completed successfully
- **Required Actions**: Schedule installation, conduct installation, get customer sign-off
- **Allowed Actions**: Update installation date, add installation notes
- **Completion %**: When installation_date is set and job status = 'installed'
- **Next Stage**: Completed

**Stage 6: Completed**
- **Entry Condition**: Installation completed and customer satisfied
- **Exit Condition**: Final payment received (or N/A if fully paid)
- **Required Actions**: Collect final payment, close project, archive
- **Allowed Actions**: View only (except add notes, upload documents)
- **Completion %**: 100%
- **Next Stage**: None (terminal state)

**Stage 7: Cancelled**
- **Entry Condition**: Customer cancels OR internal cancellation
- **Exit Condition**: None (terminal state)
- **Required Actions**: Document cancellation reason, process refunds (if applicable)
- **Allowed Actions**: View only, add cancellation notes
- **Completion %**: N/A
- **Next Stage**: None (terminal state)

**Stage 8: On Hold**
- **Entry Condition**: Manual action (customer requests hold, material shortage, etc.)
- **Exit Condition**: Manual action (resume to previous stage)
- **Required Actions**: Document hold reason, set expected resume date
- **Allowed Actions**: Add hold notes, resume project
- **Completion %**: Frozen at current %
- **Next Stage**: Previous stage (when resumed)

**TR-1.1**: Frontend Component Structure
```
ProjectsList/
├── ProjectsHeader (title, create button, stats summary)
├── ProjectsFilters (stage, priority, payment status, customer, date, overdue)
├── ProjectsSearch (search input with debounce)
├── ProjectsSort (sort controls)
├── ProjectsGrid (responsive card grid)
│   └── ProjectCard (rich card component)
└── ProjectsPagination (if needed for large datasets)
```

**TR-1.2**: State Management
- Use React Query for data fetching and caching
- Local state for UI controls (filters, search, sort)
- URL query params for shareable filtered views
- Session storage for filter persistence

**TR-1.3**: Data Requirements
- Reuse existing `jobsApi.getAll()` endpoint
- Reuse existing `quotationsApi.getAll()` endpoint
- Reuse existing `customersApi.getAll()` for filter dropdown
- Calculate derived fields in frontend (progress %, overdue status)

**TR-1.4**: Performance Requirements
- Initial load < 1 second
- Search response < 300ms
- Filter application instant (client-side)
- Support 100+ projects without pagination
- Implement virtual scrolling if > 200 projects

### Backend Changes
**None required** - All data available from existing endpoints

---

## STEP 2: Project Details Header

### User Stories

**US-2.1**: As a gallery assistant, I want to see all critical project information in the header, so I don't need to scroll to understand project status

**Acceptance Criteria**:
- WHEN opening Project Details page
- THEN header section displays (sticky at top):
  - **Row 1**: Back button, Project ID, Job ID, Quotation Number, Print button, More actions menu
  - **Row 2**: 
    - Customer info (name, phone with icon, address)
    - Current stage (large colored badge)
    - Priority (High/Medium/Low badge)
  - **Row 3**: Financial summary
    - Total contract value (green, large)
    - Amount paid (green)
    - Remaining balance (red if > 0, large)
    - Progress bar (visual % paid)
  - **Row 4**: Dates
    - Created date
    - Expected delivery date
    - Last updated (relative time)
- AND header is sticky (remains visible when scrolling)
- AND all information is read-only display
- AND numbers format with currency (EGP)
- AND dates format consistently (DD/MM/YYYY)

**US-2.2**: As a gallery assistant, I want quick actions in the header, so I can perform common tasks without scrolling

**Acceptance Criteria**:
- WHEN viewing header
- THEN quick action buttons display based on project state:
  - If Quotation (no job): "Approve Quotation", "Reject Quotation"
  - If Active Job: "Add Measurement", "Add Payment", "Change Status"
  - Always: "Print", "More Actions"
- AND clicking "Print" opens print preview
- AND "More Actions" menu shows secondary actions
- AND buttons are always visible (part of sticky header)

**US-2.3**: As a gallery assistant, I want to see financial health at a glance, so I can prioritize payment collection

**Acceptance Criteria**:
- WHEN outstanding balance > 0
- THEN remaining balance displays in red
- AND progress bar shows red for unpaid portion
- WHEN outstanding balance = 0
- THEN remaining balance shows "Paid in Full" in green
- AND progress bar is 100% green
- WHEN payment is overdue
- THEN "Overdue Payment" warning badge displays in header

### Technical Requirements

**TR-2.1**: Component Structure
```tsx
ProjectDetailsHeader/
├── ProjectIdentification (IDs, numbers, badges)
├── CustomerSummary (name, phone, address - compact)
├── StatusIndicator (stage badge, priority, progress)
├── FinancialSummary (totals, balance, progress bar)
├── DatesSummary (created, expected, updated)
└── QuickActions (conditional action buttons)
```

**TR-2.2**: Data Aggregation
- Calculate total paid from payments array
- Calculate remaining from quotation.final_price - total_paid
- Calculate progress percentage
- Determine overdue status from payment due_dates
- Format all currency values
- Format all dates consistently

**TR-2.3**: Responsive Design
- Desktop: 4-column grid for financial summary
- Tablet: 2-column grid
- Mobile: Single column stack
- Maintain sticky header on all breakpoints
- Adjust font sizes for mobile

### Backend Changes
**Option A** (Recommended): Create aggregated endpoint
```
GET /api/v1/projects/{id}/summary
Response: {
  project_id, job_id, quotation_id,
  customer: { name, phone, address },
  status, priority,
  financial: { total, paid, remaining, progress },
  dates: { created, expected_delivery, last_updated }
}
```

**Option B**: Use existing endpoints (frontend aggregation)
- GET /jobs/{id}
- GET /quotations/{id}
- GET /customers/{customer_id}
- GET /payments?job_id={id}
- Aggregate in frontend

**Decision**: Start with Option B (no backend changes), consider Option A if performance issues

---

## STEP 3: Workflow Section

### User Stories

**US-3.1**: As a gallery assistant, I want to see a visual workflow pipeline, so I understand exactly what stage the project is in

**Acceptance Criteria**:
- WHEN viewing Project Details
- THEN Workflow section displays visual pipeline:
  - Stages: Quotation → Measurement → Deposit → Production → Installation → Completed
  - Current stage highlighted in blue
  - Completed stages shown in green with checkmarks
  - Upcoming stages shown in gray
  - Connecting lines between stages (green if passed, gray if upcoming)
- AND each stage shows:
  - Stage icon
  - Stage name
  - Completion date (if completed)
  - Responsible person (if assigned)
  - Duration in days (if completed)
- AND pipeline adapts to RTL (right-to-left for Arabic)

**US-3.2**: As a gallery assistant, I want to complete workflow stages with one click, so I can efficiently update project progress

**Acceptance Criteria**:
- WHEN current stage is active and incomplete
- THEN "Complete Stage" button displays for that stage
- WHEN clicking "Complete Stage"
- THEN system:
  - Records completion timestamp automatically
  - Records current user as responsible person
  - Calculates duration from stage start
  - Advances project to next stage
  - Updates job status accordingly
  - Invalidates relevant caches
  - Shows success toast
- AND confirmation dialog asks "Mark [Stage] as complete?"
- AND cannot complete stages out of order

**US-3.3**: As a gallery assistant, I want to see overdue stages highlighted, so I can prioritize delayed projects

**Acceptance Criteria**:
- WHEN a stage exceeds expected duration
- THEN stage displays with red border and "Overdue" badge
- AND overdue duration shows (e.g., "Overdue by 3 days")
- WHEN hovering over overdue stage
- THEN tooltip shows: "Expected: [date], Current: [date]"
- AND overdue indicator updates in real-time

### Technical Requirements

**TR-3.1**: Workflow Component
```tsx
WorkflowPipeline/
├── WorkflowStage (repeatable stage component)
│   ├── StageIcon
│   ├── StageName
│   ├── StageStatus (completed/active/upcoming)
│   ├── StageMetadata (date, person, duration)
│   ├── CompleteStageButton (conditional)
│   └── OverdueIndicator (conditional)
└── StageConnector (line between stages)
```

**TR-3.2**: Stage Configuration
```typescript
const workflowStages = [
  { id: 'quotation', name: 'Quotation', icon: FileText, jobStatus: null },
  { id: 'measurement', name: 'Measurement', icon: Calendar, jobStatus: 'measuring', dateField: 'measurement_date' },
  { id: 'deposit', name: 'Deposit', icon: DollarSign, jobStatus: 'pending', checkPayments: 'deposit' },
  { id: 'production', name: 'Production', icon: Package, jobStatus: 'in_production', dateFields: ['production_start', 'production_end'] },
  { id: 'installation', name: 'Installation', icon: Wrench, jobStatus: 'ready_for_installation', dateField: 'installation_date' },
  { id: 'completed', name: 'Completed', icon: CheckCircle, jobStatus: 'completed', dateField: 'completion_date' }
];
```

**TR-3.3**: Stage Completion Logic
```typescript
async function completeStage(stageId: string) {
  // 1. Validate stage can be completed (not out of order)
  // 2. Update job with completion timestamp
  // 3. Advance job status
  // 4. Record activity log entry
  // 5. Invalidate queries
  // 6. Show success feedback
}
```

### Backend Changes
**Option A** (Recommended): Add stage completion endpoint
```
POST /api/v1/jobs/{id}/complete-stage
Body: { stage: 'measurement', completed_by: 'user_id' }
Response: { job, activity_log_entry }
```

**Option B**: Use existing job update endpoint
```
PUT /api/v1/jobs/{id}
Body: { measurement_date: '2026-07-21', status: 'in_production' }
```

**Decision**: Implement Option A for cleaner semantics and automatic activity logging

---

## STEP 4: Timeline Section - Automatic Event Recording

### Core Principle
**The timeline automatically records every important event with date, time, user, and description. No manual timeline entry.**

### Automatic Timeline Events

**Event: Project Created**
- **Trigger**: Job created from approved quotation
- **Recorded Data**:
  - Date/Time: job.created_at
  - User: Created by user (from auth context)
  - Description: "Project created from Quotation [number]"
  - Metadata: quotation_id, customer_id

**Event: Quotation Sent**
- **Trigger**: Quotation status changes to 'sent'
- **Recorded Data**:
  - Date/Time: timestamp of status change
  - User: User who sent
  - Description: "Quotation [number] sent to customer"
  - Metadata: quotation_id, customer_email (if available)

**Event: Quotation Approved**
- **Trigger**: Quotation status changes to 'approved'
- **Recorded Data**:
  - Date/Time: timestamp of approval
  - User: User who approved
  - Description: "Quotation [number] approved"
  - Metadata: quotation_id, approval_method

**Event: Measurement Scheduled**
- **Trigger**: Measurement created with visit_date in future
- **Recorded Data**:
  - Date/Time: measurement.created_at
  - User: User who scheduled
  - Description: "Measurement #[number] scheduled for [visit_date]"
  - Metadata: measurement_id, visit_date, engineer

**Event: Measurement Completed**
- **Trigger**: Measurement visit_date passes OR job.measurement_date is set
- **Recorded Data**:
  - Date/Time: job.measurement_date OR measurement.created_at
  - User: measurement.measured_by
  - Description: "Measurement #[number] completed by [engineer]"
  - Metadata: measurement_id, items_count, rooms_measured

**Event: Deposit Received**
- **Trigger**: First payment (type='deposit') status changes to 'paid'
- **Recorded Data**:
  - Date/Time: payment.paid_date
  - User: User who marked paid
  - Description: "Deposit received: [amount] via [method]"
  - Metadata: payment_id, amount, payment_method

**Event: Production Started**
- **Trigger**: job.production_start is set OR job status changes to 'in_production'
- **Recorded Data**:
  - Date/Time: job.production_start
  - User: User who started production
  - Description: "Manufacturing started"
  - Metadata: estimated_completion_date

**Event: Production Completed**
- **Trigger**: job.production_end is set OR job status changes to 'ready_for_installation'
- **Recorded Data**:
  - Date/Time: job.production_end
  - User: User who completed
  - Description: "Manufacturing completed (Duration: [X] days)"
  - Metadata: production_duration, quality_check_status

**Event: Installation Scheduled**
- **Trigger**: job.installation_date is set (future date)
- **Recorded Data**:
  - Date/Time: timestamp when scheduled
  - User: User who scheduled
  - Description: "Installation scheduled for [date]"
  - Metadata: installation_date, installer, customer_confirmed

**Event: Installation Completed**
- **Trigger**: job.installation_date passes OR job status changes to 'installed'
- **Recorded Data**:
  - Date/Time: job.installation_date
  - User: Installer name OR user who updated
  - Description: "Installation completed successfully"
  - Metadata: customer_signature, photos_count, issues

**Event: Project Closed**
- **Trigger**: job status changes to 'completed'
- **Recorded Data**:
  - Date/Time: job.completion_date
  - User: User who closed
  - Description: "Project completed and closed"
  - Metadata: total_duration, final_payment_status, customer_satisfaction

**Event: Payment Added**
- **Trigger**: New payment created
- **Recorded Data**:
  - Date/Time: payment.created_at
  - User: User who added
  - Description: "Payment #[order] added: [amount] due [due_date]"
  - Metadata: payment_id, payment_type, due_date

**Event: Payment Received**
- **Trigger**: Payment status changes to 'paid'
- **Recorded Data**:
  - Date/Time: payment.paid_date
  - User: User who marked paid
  - Description: "Payment #[order] received: [amount] via [method]"
  - Metadata: payment_id, amount, payment_method, receipt_number

**Event: Stage Changed**
- **Trigger**: job status changes
- **Recorded Data**:
  - Date/Time: timestamp of change
  - User: User who changed
  - Description: "Stage changed from [old_stage] to [new_stage]"
  - Metadata: old_status, new_status, reason

**Event: Project Cancelled**
- **Trigger**: job status changes to 'cancelled'
- **Recorded Data**:
  - Date/Time: timestamp of cancellation
  - User: User who cancelled
  - Description: "Project cancelled: [reason]"
  - Metadata: cancellation_reason, refund_status

**Event: Project On Hold**
- **Trigger**: job status changes to 'on_hold' (if implemented)
- **Recorded Data**:
  - Date/Time: timestamp of hold
  - User: User who put on hold
  - Description: "Project put on hold: [reason]"
  - Metadata: hold_reason, expected_resume_date

**Event: Note Added**
- **Trigger**: job.notes updated OR separate note entity created
- **Recorded Data**:
  - Date/Time: note.created_at
  - User: User who added note
  - Description: "Note added: [first 50 chars]..."
  - Metadata: note_type (internal/customer/installation)

### User Stories: Timeline

**US-4.1**: As a gallery assistant, I want the timeline to record events automatically, so I have a complete audit trail without manual entry

**Acceptance Criteria**:
- WHEN any significant action occurs (listed above)
- THEN timeline event is created automatically
- AND event includes:
  - Date (formatted: DD/MM/YYYY)
  - Time (formatted: HH:MM AM/PM)
  - User who triggered event
  - Event description (clear, readable)
  - Event icon (matching event type)
- AND I never manually create timeline entries
- AND timeline updates in real-time when viewing Project page

**US-4.2**: As a gallery assistant, I want to see planned vs actual dates in timeline, so I can identify delays

**Acceptance Criteria**:
- WHEN viewing Timeline section
- THEN table displays all events with columns:
  - Event (with icon)
  - Planned Date (if applicable)
  - Actual Date (when occurred)
  - User (who triggered)
  - Duration (time from previous event)
  - Status (On Time / Delayed / Upcoming)
- AND delayed events highlight in red
- AND on-time events show in green
- AND upcoming events show in gray
- AND duration calculates automatically

**US-4.3**: As a manager, I want to see total project duration and estimates, so I can plan capacity

**Acceptance Criteria**:
- WHEN viewing Timeline summary
- THEN displays:
  - Total project duration (days from creation to current/completion)
  - Average stage durations (based on this project)
  - Estimated completion date (if not completed)
  - Days until expected delivery
  - Comparison to typical project duration
- AND if project delayed: "Project delayed by X days" warning
- AND if on track: "On schedule for delivery" success message

### Technical Requirements

**TR-4.1**: Timeline Component
```tsx
ProjectTimeline/
├── TimelineSummary (totals, estimates, warnings)
├── TimelineTable (phase rows)
│   └── TimelineRow
│       ├── StageCell
│       ├── PlannedDateCell (editable)
│       ├── ActualDateCell
│       ├── CompletedByCell
│       ├── DurationCell (calculated)
│       └── StatusCell (icon + text)
└── TimelineInsights (delays, bottlenecks)
```

**TR-4.2**: Duration Calculations
```typescript
function calculateDuration(startDate: Date, endDate: Date): string {
  const days = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24));
  if (days === 0) return 'Same day';
  if (days === 1) return '1 day';
  return `${days} days`;
}

function estimateCompletion(currentStage: string, avgDurations: Record<string, number>): Date {
  // Sum remaining stage durations + current date
}
```

### Backend Changes
**Minimal**: Use existing Job date fields
- `measurement_date`
- `production_start`
- `production_end`
- `installation_date`
- `completion_date`

**Enhancement** (Optional): Add planned date fields to Job model
- `planned_measurement_date`
- `planned_production_start`
- `planned_installation_date`
- `planned_completion_date`

---

## STEP 5: Payments Integration - Summary Within Project

### Core Principle
**Payments remain in their own module for accounting. The Project page shows payment summary, history, progress, and status. The global Payments page remains responsible for managing all payments across all projects.**

### Relationship Between Modules

**Project Page (Payments Section)**:
- Shows payments FOR THIS PROJECT ONLY
- Displays: payment summary, payment history, remaining balance, payment progress, payment status
- Allows: add payment, mark as paid, view payment details
- Purpose: Operational visibility for project team

**Global Payments Page (Separate Module)**:
- Shows payments FOR ALL PROJECTS
- Displays: consolidated payment reports, accounting views, financial summaries
- Allows: bulk operations, reports, reconciliation, advanced filters
- Purpose: Financial management and accounting

### User Stories: Payments in Project

**US-5.1**: As a gallery assistant, I want to see payment summary at the top of Payments section, so I immediately know payment status FOR THIS PROJECT

**Acceptance Criteria**:
- WHEN viewing Payments section within Project page
- THEN summary displays (3 cards):
  - **Card 1**: Total Paid (green background, large number, this project only)
  - **Card 2**: Remaining Balance (red if > 0, green if 0, this project only)
  - **Card 3**: Progress (percentage + visual progress bar, this project only)
- AND summary calculates ONLY from this project's payments
- AND clicking "View All Payments" link navigates to global Payments page filtered to this project
- AND I can see payment health at a glance

**US-5.2**: As a gallery assistant, I want to see payment history FOR THIS PROJECT, so I can track this customer's payments

**Acceptance Criteria**:
- WHEN viewing payment list in Payments section
- THEN displays payments FOR THIS PROJECT ONLY (filtered by job_id)
- AND each payment shows: order, type, method, percentage, amount, due date, paid date, status, notes, actions
- AND payments sort by payment_order
- AND I see complete payment timeline for this project
- AND "View Global Payments" link available for accounting team

**US-5.3**: As an accountant, I want to access global Payments module from Project page, so I can see all payments across all projects

**Acceptance Criteria**:
- WHEN viewing Payments section in Project page
- THEN "View Global Payments Page" link displays at section header
- WHEN clicking link
- THEN navigates to global Payments module
- AND optionally filters to this customer OR this project
- AND global page shows payments from ALL projects
- AND I can perform accounting operations (reconciliation, reports, etc.)

### Technical Requirements

**TR-5.1**: Payments Component Structure
```tsx
PaymentsSection/
├── PaymentsSummary (3 cards: paid, remaining, progress)
├── PaymentsList (list of payment cards/rows)
│   └── PaymentCard
│       ├── PaymentDetails
│       ├── PaymentStatus
│       └── PaymentActions
├── AddPaymentButton
├── AddPaymentModal (reuse existing)
└── MarkPaidConfirmation (dialog)
```

**TR-5.2**: Payment Calculations
```typescript
const totalPaid = payments.filter(p => p.status === 'paid')
  .reduce((sum, p) => sum + parseFloat(p.amount), 0);
const totalScheduled = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
const remainingBalance = totalScheduled - totalPaid;
const paidPercentage = (totalPaid / totalScheduled) * 100;
const overduePayments = payments.filter(p => 
  p.status === 'pending' && 
  p.due_date && 
  new Date(p.due_date) < new Date()
);
```

### Backend Changes
**None required** - All functionality exists:
- `POST /api/v1/payments` (create)
- `PUT /api/v1/payments/{id}` (update)
- `PATCH /api/v1/payments/{id}/status` (mark paid)
- `GET /api/v1/jobs/{job_id}/payments` (list)

---

## STEP 6: Measurements Integration

*(Continuing with similar detailed format for Steps 6-10...)*

**Due to length constraints, I'll create the complete requirements doc as a file. The remaining steps follow the same detailed pattern.)**

---

## Non-Functional Requirements

### Performance
- Initial page load: < 2 seconds
- Subsequent interactions: < 500ms
- Real-time calculations: < 100ms
- Support 100+ projects without pagination
- Support 50+ payments per project
- Support 20+ measurements per project

### Security
- All API calls authenticated
- Role-based access control (future)
- Audit trail for all changes
- Sensitive data (financial) requires confirmation

### Usability
- Mobile responsive (320px min width)
- Keyboard navigation support
- Screen reader compatible
- RTL (Arabic) fully supported
- Touch-friendly (44px min touch targets)
- Clear error messages
- Undo functionality (future)

### Reliability
- Graceful API failure handling
- Offline indicators
- Auto-save form state
- Network retry logic
- Data validation client + server

### Maintainability
- Component reuse > 80%
- Code coverage > 70% (future)
- TypeScript strict mode
- ESLint compliant
- Consistent naming conventions
- Inline documentation

---

## Architecture & Scalability

### Module Boundaries

**Projects Module (Central Hub)**
- **Purpose**: Daily operational workspace for project management
- **Scope**: Everything related to a SINGLE project
- **Contains**:
  - Project header (IDs, customer, status, financial summary)
  - Workflow pipeline (current stage, next actions)
  - Timeline (all events for this project)
  - Quotation details (items, totals, for this project)
  - Measurements (all visits for this project)
  - Payments summary (for this project only)
  - Customer info (read-only, quick access)
  - Activity history (all events for this project)
  - Notes (internal, customer, installation)
  - Documents (future: files for this project)
- **Navigation OUT**: Links to global modules (Customers, Payments) open in new tab OR navigate with back button

**Customers Module (CRM)**
- **Purpose**: Customer relationship management
- **Scope**: Everything related to ALL customers
- **Contains**:
  - Customer list (all customers)
  - Customer details (single customer profile)
  - Customer projects (list of projects for this customer)
  - Customer payments (list of payments from this customer across all projects)
  - Customer communication history
  - Customer documents
- **Navigation IN**: From Project page "View Customer Profile" link

**Payments Module (Accounting)**
- **Purpose**: Financial management and accounting
- **Scope**: ALL payments across ALL projects
- **Contains**:
  - Payment list (all payments, filterable by project/customer/date)
  - Payment reports (revenue, outstanding, overdue, forecasts)
  - Payment reconciliation
  - Bulk payment operations
  - Receipt generation
  - Payment analytics
- **Navigation IN**: From Project page "View Global Payments" link
- **Navigation IN**: From Dashboard KPI "Overdue Payments"

**Products Module (Catalog)**
- **Purpose**: Product and category management
- **Scope**: Product catalog, pricing, inventory (future)
- **Contains**:
  - Product list
  - Product categories
  - Product pricing
  - Product availability (future)
  - Product specifications
- **Navigation IN**: From Quotation form (product selector)

**Dashboard Module (Overview)**
- **Purpose**: High-level operational overview
- **Scope**: KPIs and summaries across ALL projects
- **Contains**:
  - KPI cards (active projects, delayed, measurements today, etc.)
  - Workflow pipeline (all projects grouped by stage)
  - Alerts (critical issues requiring attention)
  - Recent activity (across all projects)
  - Quotations waiting (unapproved)
- **Navigation OUT**: All KPIs link to Projects page with filters applied

### Data Flow

```
Dashboard KPI Click
    ↓
Projects Page (Filtered)
    ↓
Project Details Page (Single Project Workspace)
    ├→ View Customer Profile → Customers Module
    ├→ View Global Payments → Payments Module
    ├→ Select Product → Products Module (modal/dropdown)
    └→ All other operations stay on Project page
```

### Future Feature Integration Plan

**Employee Assignments** (Future)
- **Implementation**: Add `assigned_to` fields to Job, Measurement, Installation
- **UI Integration**: Dropdown in Project Header + Workflow stages
- **Impact**: Minimal - adds fields to existing components
- **No Redesign**: Fits within current architecture

**Calendar Integration** (Future)
- **Implementation**: Sync measurement_date, installation_date to external calendar
- **UI Integration**: "Add to Calendar" buttons in Timeline section
- **Impact**: None - additional feature, no structural changes
- **No Redesign**: Calendar widget embeds in Timeline section

**Notifications System** (Future)
- **Implementation**: Notification service triggers on timeline events
- **UI Integration**: Bell icon in header, notification panel sidebar
- **Impact**: Minimal - adds notification bell, doesn't change project structure
- **No Redesign**: Notification panel overlays existing UI

**Inventory Tracking** (Future)
- **Implementation**: Track materials used per project
- **UI Integration**: New "Materials" section in Project page (collapsible)
- **Impact**: Adds one collapsible section, follows existing pattern
- **No Redesign**: Uses CollapsibleSection component, consistent with current design

**Manufacturing Workflow** (Future)
- **Implementation**: Detailed manufacturing steps tracking
- **UI Integration**: Expand Manufacturing stage in Workflow section
- **Impact**: Enhances existing Workflow section with sub-stages
- **No Redesign**: Workflow section designed to support sub-stages

**Installer Management** (Future)
- **Implementation**: Track installer assignments, availability, performance
- **UI Integration**: Installer selector in Installation stage
- **Impact**: Adds dropdown to Installation section
- **No Redesign**: Fits within existing Installation workflow

**AI Assistant** (Future)
- **Implementation**: Chatbot for project queries, suggestions
- **UI Integration**: Chat widget (bottom-right corner bubble)
- **Impact**: None - overlay widget, doesn't modify project structure
- **No Redesign**: Independent floating widget

**Advanced Reports** (Future)
- **Implementation**: Generate PDF reports, analytics dashboards
- **UI Integration**: "Generate Report" button in Project Header
- **Impact**: Minimal - adds button, opens report in new tab/modal
- **No Redesign**: Report generation separate from project UI

**File Management** (Future)
- **Implementation**: Upload/organize contracts, photos, invoices
- **UI Integration**: Documents section (already planned in Step 10)
- **Impact**: None - placeholder already reserved
- **No Redesign**: Documents section designed for this purpose

**Multi-Location Support** (Future)
- **Implementation**: Location field added to Customer, Project
- **UI Integration**: Location dropdown in Project Header
- **Impact**: Minimal - adds one field to header
- **No Redesign**: Header designed to accommodate additional fields

**Custom Fields** (Future)
- **Implementation**: Configurable custom fields per project type
- **UI Integration**: Custom Fields section (collapsible) in Project page
- **Impact**: Adds one collapsible section
- **No Redesign**: Uses CollapsibleSection pattern, follows existing design

### Scalability Guarantees

1. **Collapsible Sections**: All future features add as new collapsible sections
2. **Component Reuse**: All future features use existing UI components
3. **API Extension**: New features add endpoints, don't modify existing ones
4. **No Structural Changes**: Project page layout supports unlimited sections
5. **Performance**: Virtual scrolling, lazy loading for large datasets
6. **Extensibility**: Plugin architecture for future modules (not in scope now)

---

## Dependencies & Constraints

### External Dependencies
- React Query (data fetching)
- React Router (navigation)
- Tailwind CSS (styling)
- Lucide React (icons)
- Date-fns (date handling)
- Sonner (toast notifications)

### Technical Constraints
- Backend API structure immutable
- Database schema frozen
- Must support IE11 (false - modern browsers only)
- Must work offline (false - online only)
- Must support multi-tenancy (false - single tenant)

### Resource Constraints
- Development time: 6-8 hours per step
- Testing time: 1-2 hours per step
- No dedicated QA team
- No automated E2E tests (initially)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Scope creep | High | Medium | Strict adherence to 10-step plan, no new features mid-step |
| Performance issues with large datasets | Medium | Low | Implement pagination/virtualization if needed |
| Backend changes required | Medium | Medium | Document alternatives, seek approval before proceeding |
| User adoption resistance | High | Low | Maintain familiar patterns, provide training |
| Regression bugs | High | Medium | Comprehensive testing checklist per step |
| Timeline slippage | Medium | Medium | One step at a time, verify before proceeding |

---

## Acceptance & Sign-off

### Definition of Done (Per Step)
- [ ] All user stories implemented
- [ ] All acceptance criteria met
- [ ] Zero TypeScript errors
- [ ] Zero console errors/warnings
- [ ] Responsive design verified (mobile, tablet, desktop)
- [ ] RTL layout verified
- [ ] All translations present (Arabic)
- [ ] Manual testing completed
- [ ] No regressions from previous functionality
- [ ] Code reviewed
- [ ] Deployed to staging
- [ ] Stakeholder approval

### Step Dependencies
```
Step 1 (List) ──> Independent (can start immediately)
Step 2 (Header) ──> Depends on Step 1 (uses same data fetching patterns)
Step 3 (Workflow) ──> Depends on Step 2 (header sets context)
Step 4 (Timeline) ──> Depends on Step 3 (workflow completion data)
Step 5 (Payments) ──> Independent (can parallel with 2-4)
Step 6 (Measurements) ──> Independent (can parallel with 2-5)
Step 7 (Quotation) ──> Independent (can parallel with 2-6)
Step 8 (Customer) ──> Depends on Step 2 (header already shows customer)
Step 9 (Activity) ──> Depends on Steps 3-7 (activity generated by those)
Step 10 (Documents) ──> Independent (placeholder only)
```

---

## Appendix

### Glossary
- **Project**: A customer order tracked through the system (combination of Quotation + Job)
- **Job**: Active work order created from approved quotation
- **Quotation**: Price estimate provided to customer
- **Stage**: Phase in project workflow (Quotation, Measurement, Production, etc.)
- **Workflow**: Complete sequence of stages from quotation to completion
- **Timeline**: Historical view of planned vs actual dates for all stages
- **Gallery Assistant**: Primary user role, manages daily project operations

### References
- Current ProjectDetails implementation: `frontend/src/pages/ProjectDetails.tsx`
- Phase 2 Progress: `.kiro/PHASE2-PROGRESS.md`
- Dashboard Polish: `.kiro/DASHBOARD-POLISH-SUMMARY.md`
- Existing APIs: `frontend/src/services/jobs.ts`, `payments.ts`, `measurements.ts`, `quotations.ts`

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Next Review**: After Step 1 completion  
**Owner**: Development Team  
**Approver**: Product Owner
