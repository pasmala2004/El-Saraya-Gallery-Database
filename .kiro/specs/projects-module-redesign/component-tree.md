# Projects Module - Component Tree

**Feature ID**: `projects-module-redesign`  
**Version**: 1.0  
**Created**: 2026-07-21

---

## Complete Component Hierarchy

```
frontend/src/
├── pages/
│   ├── Jobs.tsx (Projects List Page)
│   └── ProjectDetails.tsx (Project Details Page)
│
├── components/
│   ├── layout/
│   │   └── Layout.tsx (existing)
│   │
│   ├── common/
│   │   ├── LoadingSpinner.tsx (existing)
│   │   ├── ErrorMessage.tsx (existing)
│   │   ├── ConfirmDialog.tsx (existing)
│   │   ├── CollapsibleSection.tsx (existing)
│   │   ├── InlineEdit.tsx (existing)
│   │   ├── StatusBadge.tsx (NEW)
│   │   ├── PriorityBadge.tsx (NEW)
│   │   └── ProgressBar.tsx (NEW)
│   │
│   ├── projects/
│   │   ├── ProjectCard.tsx (NEW)
│   │   ├── ProjectsFilters.tsx (NEW)
│   │   ├── ProjectsSearch.tsx (NEW)
│   │   └── ProjectsGrid.tsx (NEW)
│   │
│   ├── project-details/
│   │   ├── header/
│   │   │   ├── ProjectDetailsHeader.tsx (NEW)
│   │   │   ├── ProjectIdentification.tsx (NEW)
│   │   │   ├── CustomerSummary.tsx (NEW)
│   │   │   ├── FinancialSummary.tsx (NEW)
│   │   │   ├── DatesSummary.tsx (NEW)
│   │   │   └── QuickActions.tsx (NEW)
│   │   │
│   │   ├── workflow/
│   │   │   ├── WorkflowPipeline.tsx (NEW)
│   │   │   ├── WorkflowStage.tsx (NEW)
│   │   │   ├── StageConnector.tsx (NEW)
│   │   │   └── CompleteStageModal.tsx (NEW)
│   │   │
│   │   ├── timeline/
│   │   │   ├── ProjectTimeline.tsx (NEW)
│   │   │   ├── TimelineTable.tsx (NEW)
│   │   │   ├── TimelineRow.tsx (NEW)
│   │   │   └── TimelineSummary.tsx (NEW)
│   │   │
│   │   ├── payments/
│   │   │   ├── PaymentsSection.tsx (NEW)
│   │   │   ├── PaymentsSummary.tsx (NEW)
│   │   │   ├── PaymentsList.tsx (NEW)
│   │   │   ├── PaymentCard.tsx (NEW)
│   │   │   └── AddPaymentModal.tsx (existing, reuse)
│   │   │
│   │   ├── measurements/
│   │   │   ├── MeasurementsSection.tsx (NEW)
│   │   │   ├── MeasurementCard.tsx (NEW)
│   │   │   └── AddMeasurementModal.tsx (NEW)
│   │   │
│   │   ├── quotation/
│   │   │   ├── QuotationSection.tsx (NEW)
│   │   │   ├── QuotationItemsTable.tsx (NEW)
│   │   │   └── QuotationTotals.tsx (NEW)
│   │   │
│   │   ├── customer/
│   │   │   ├── CustomerSection.tsx (NEW)
│   │   │   └── CustomerActions.tsx (NEW)
│   │   │
│   │   └── activity/
│   │       ├── ActivityFeed.tsx (NEW)
│   │       ├── ActivityItem.tsx (NEW)
│   │       └── DocumentsSection.tsx (NEW, placeholder)
│   │
│   └── dashboard/
│       └── (existing dashboard components)
│
├── hooks/
│   ├── useProjects.ts (NEW)
│   ├── useProjectDetails.ts (NEW)
│   ├── useProjectsFilters.ts (NEW)
│   ├── useProjectsSearch.ts (NEW)
│   └── (existing hooks)
│
├── services/
│   ├── jobs.ts (existing, may extend)
│   ├── quotations.ts (existing)
│   ├── payments.ts (existing)
│   ├── measurements.ts (existing)
│   ├── activityLogs.ts (NEW)
│   └── (existing services)
│
└── types/
    ├── index.ts (existing, extend)
    └── dashboard.ts (existing)
```

---

## Page Components

### Jobs.tsx (Projects List Page)

**Path**: `frontend/src/pages/Jobs.tsx`

**Purpose**: Display list of all projects with filters, search, and quick access

**Component Tree**:
```tsx
<Layout>
  <div className="projects-page">
    <PageHeader
      title="Projects"
      action={<Button>New Quotation</Button>}
      stats={<span>{filteredCount} Projects</span>}
    />
    
    <ProjectsFilters
      filters={filters}
      customers={customers}
      onFiltersChange={setFilters}
      onClearFilters={clearFilters}
    />
    
    <ProjectsSearch
      value={searchQuery}
      onChange={setSearchQuery}
    />
    
    {isLoading ? (
      <ProjectsGridSkeleton />
    ) : filteredProjects.length === 0 ? (
      <EmptyState />
    ) : (
      <ProjectsGrid>
        {filteredProjects.map(project => (
          <ProjectCard
            key={project.id}
            job={project.job}
            customer={project.customer}
            quotation={project.quotation}
            payments={project.payments}
            onView={() => navigate(`/projects/${project.id}`)}
          />
        ))}
      </ProjectsGrid>
    )}
  </div>
</Layout>
```

**Props**: None (uses URL params and local state)

**State**:
- `filters: ProjectFilters` - Active filters
- `searchQuery: string` - Search input
- `filteredProjects: Project[]` - Derived state (memoized)

**Hooks**:
- `useProjects()` - Fetch all projects
- `useProjectsFilters()` - Filter state management
- `useProjectsSearch()` - Debounced search

---

### ProjectDetails.tsx (Project Details Page)

**Path**: `frontend/src/pages/ProjectDetails.tsx`

**Purpose**: Single project workspace with all operations

**Component Tree**:
```tsx
<Layout>
  <div className="project-details-page">
    {isLoading ? (
      <LoadingSkeleton />
    ) : (
      <>
        <ProjectDetailsHeader
          job={job}
          quotation={quotation}
          customer={customer}
          payments={payments}
          onPrint={handlePrint}
          onBack={() => navigate('/jobs')}
        />
        
        <CollapsibleSection title="Workflow" icon={<GitBranch />} defaultOpen>
          <WorkflowPipeline
            job={job}
            payments={payments}
            onCompleteStage={handleCompleteStage}
          />
        </CollapsibleSection>
        
        <CollapsibleSection title="Timeline" icon={<Clock />}>
          <ProjectTimeline
            job={job}
            events={timelineEvents}
          />
        </CollapsibleSection>
        
        <CollapsibleSection title="Quotation" icon={<FileText />} defaultOpen>
          <QuotationSection
            quotation={quotation}
            canEdit={!job} // Only if no job yet
            onEdit={handleEditQuotation}
          />
        </CollapsibleSection>
        
        <CollapsibleSection title="Measurements" icon={<Ruler />}>
          <MeasurementsSection
            measurements={measurements}
            onAdd={handleAddMeasurement}
            onEdit={handleEditMeasurement}
          />
        </CollapsibleSection>
        
        <CollapsibleSection title="Payments" icon={<DollarSign />} defaultOpen>
          <PaymentsSection
            quotation={quotation}
            payments={payments}
            onAddPayment={handleAddPayment}
            onMarkPaid={handleMarkPaid}
          />
        </CollapsibleSection>
        
        <CollapsibleSection title="Customer" icon={<User />}>
          <CustomerSection customer={customer} />
        </CollapsibleSection>
        
        <CollapsibleSection title="Activity" icon={<Activity />}>
          <ActivityFeed events={timelineEvents} />
        </CollapsibleSection>
        
        <CollapsibleSection title="Documents" icon={<Folder />}>
          <DocumentsSection />  {/* Placeholder */}
        </CollapsibleSection>
      </>
    )}
  </div>
</Layout>
```

**Props**:
- Receives `jobId` from URL params

**State**:
- Various modal open states (addPayment, addMeasurement, etc.)

**Hooks**:
- `useProjectDetails(jobId)` - Aggregates all data fetching
- `useJob(jobId)`
- `useQuotation(quotationId)`
- `useCustomer(customerId)`
- `usePayments(jobId)`
- `useMeasurements(jobId)`
- `useActivityLogs(jobId)`

---

## Feature Components

### ProjectCard

**Path**: `frontend/src/components/projects/ProjectCard.tsx`

**Purpose**: Rich card displaying project summary

**Props**:
```typescript
interface ProjectCardProps {
  job: Job;
  customer: Customer;
  quotation: Quotation;
  payments: Payment[];
  onView: () => void;
}
```

**Component Tree**:
```tsx
<div className="project-card">
  <div className="card-header">
    <h3 className="project-id">Project #{job.id}</h3>
    <PriorityBadge priority={job.priority} />
    {isOverdue && <Badge variant="danger">Overdue</Badge>}
    {hasOverduePayments && <Badge variant="warning">Payment Due</Badge>}
  </div>
  
  <div className="card-body">
    <h2 className="customer-name" onClick={onViewCustomer}>
      {customer.name}
    </h2>
    
    <StatusBadge status={job.status} />
    
    <ProgressBar
      current={totalPaid}
      total={quotationTotal}
      label={`${progress}% Paid`}
    />
    
    <div className="dates">
      <span>Expected: {formatDate(job.expected_delivery_date)}</span>
    </div>
    
    <div className="meta">
      <Badge>{daysInStage} days in {currentStage}</Badge>
    </div>
    
    <div className="activity">
      <Clock className="icon" />
      <span>{relativeTime(latestActivity)} - {latestActivity.description}</span>
    </div>
  </div>
  
  <div className="card-footer">
    <Button onClick={onView}>View Project</Button>
  </div>
</div>
```

**Calculations**:
- `totalPaid` - Sum of paid payments
- `progress` - (totalPaid / quotationTotal) * 100
- `isOverdue` - expectedDeliveryDate < today
- `hasOverduePayments` - Any pending payment with dueDate < today
- `daysInStage` - Days since stage started
- `latestActivity` - Most recent timeline event

---

### ProjectDetailsHeader

**Path**: `frontend/src/components/project-details/header/ProjectDetailsHeader.tsx`

**Purpose**: Sticky header with critical project information

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

**Component Tree**:
```tsx
<header className="project-details-header sticky top-0 z-40">
  {/* Row 1: Navigation & Identification */}
  <div className="header-row-1">
    <Button onClick={onBack} variant="ghost">
      <ArrowLeft /> Back to Projects
    </Button>
    
    <ProjectIdentification
      projectId={job.id}
      jobId={job.id}
      quotationNumber={quotation.quotation_number}
    />
    
    <div className="actions">
      <Button onClick={onPrint} variant="outline">
        <Printer /> Print
      </Button>
      <MoreActionsMenu />
    </div>
  </div>
  
  {/* Row 2: Customer & Status */}
  <div className="header-row-2 grid grid-cols-3">
    <CustomerSummary customer={customer} />
    
    <div className="status-center">
      <StatusBadge status={job.status} size="lg" />
      <PriorityBadge priority={job.priority} />
    </div>
    
    <QuickActions job={job} quotation={quotation} />
  </div>
  
  {/* Row 3: Financial Summary */}
  <div className="header-row-3">
    <FinancialSummary
      quotation={quotation}
      payments={payments}
    />
  </div>
  
  {/* Row 4: Dates */}
  <div className="header-row-4">
    <DatesSummary job={job} />
  </div>
</header>
```

---

### WorkflowPipeline

**Path**: `frontend/src/components/project-details/workflow/WorkflowPipeline.tsx`

**Purpose**: Visual workflow stages with completion

**Props**:
```typescript
interface WorkflowPipelineProps {
  job: Job;
  payments: Payment[];
  onCompleteStage: (stageId: string) => void;
}
```

**Component Tree**:
```tsx
<div className="workflow-pipeline">
  {workflowStages.map((stage, index) => (
    <React.Fragment key={stage.id}>
      <WorkflowStage
        stage={stage}
        status={getStageStatus(stage, job, payments)}
        completionDate={getCompletionDate(stage, job)}
        isOverdue={isStageOverdue(stage, job)}
        canComplete={canCompleteStage(stage, job, payments)}
        onComplete={() => onCompleteStage(stage.id)}
      />
      
      {index < workflowStages.length - 1 && (
        <StageConnector
          completed={getStageStatus(stage, job, payments) === 'completed'}
        />
      )}
    </React.Fragment>
  ))}
</div>
```

**Stage Definitions**:
```typescript
const workflowStages = [
  { id: 'quotation', name: 'Quotation', icon: FileText },
  { id: 'measurement', name: 'Measurement', icon: Ruler },
  { id: 'deposit', name: 'Deposit', icon: DollarSign },
  { id: 'production', name: 'Production', icon: Package },
  { id: 'installation', name: 'Installation', icon: Wrench },
  { id: 'completed', name: 'Completed', icon: CheckCircle }
];
```

---

### PaymentsSection

**Path**: `frontend/src/components/project-details/payments/PaymentsSection.tsx`

**Purpose**: Payment summary, history, and actions for THIS project

**Props**:
```typescript
interface PaymentsSectionProps {
  quotation: Quotation;
  payments: Payment[];
  onAddPayment: () => void;
  onMarkPaid: (paymentId: number) => void;
}
```

**Component Tree**:
```tsx
<div className="payments-section">
  <div className="section-header">
    <h3>Payments</h3>
    <Button onClick={onAddPayment}>
      <Plus /> Add Payment
    </Button>
    <Link to={`/payments?job_id=${job.id}`} target="_blank">
      View in Global Payments Module →
    </Link>
  </div>
  
  <PaymentsSummary
    quotationTotal={parseFloat(quotation.final_price)}
    payments={payments}
  />
  
  <PaymentsList>
    {payments.map(payment => (
      <PaymentCard
        key={payment.id}
        payment={payment}
        onMarkPaid={() => onMarkPaid(payment.id)}
      />
    ))}
  </PaymentsList>
</div>
```

---

### ProjectTimeline

**Path**: `frontend/src/components/project-details/timeline/ProjectTimeline.tsx`

**Purpose**: Planned vs actual dates for all stages

**Props**:
```typescript
interface ProjectTimelineProps {
  job: Job;
  events: ActivityLog[];
}
```

**Component Tree**:
```tsx
<div className="project-timeline">
  <TimelineSummary
    totalDuration={calculateTotalDuration(job)}
    isDelayed={isDelayed(job)}
    estimatedCompletion={estimateCompletion(job)}
  />
  
  <TimelineTable>
    <thead>
      <tr>
        <th>Stage</th>
        <th>Planned Date</th>
        <th>Actual Date</th>
        <th>User</th>
        <th>Duration</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {workflowStages.map(stage => (
        <TimelineRow
          key={stage.id}
          stage={stage}
          plannedDate={getPlannedDate(stage, job)}
          actualDate={getActualDate(stage, job)}
          user={getCompletedBy(stage, events)}
          duration={getDuration(stage, job)}
          status={getTimelineStatus(stage, job)}
        />
      ))}
    </tbody>
  </TimelineTable>
</div>
```

---

## Reusable Components

### StatusBadge

**Path**: `frontend/src/components/common/StatusBadge.tsx`

**Purpose**: Colored badge for job/quotation status

**Props**:
```typescript
interface StatusBadgeProps {
  status: JobStatus | QuotationStatus;
  size?: 'sm' | 'md' | 'lg';
}
```

**Implementation**:
```tsx
const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  measuring: 'bg-purple-100 text-purple-800',
  in_production: 'bg-orange-100 text-orange-800',
  ready_for_installation: 'bg-indigo-100 text-indigo-800',
  installed: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800'
};

return (
  <span className={`badge ${statusColors[status]} ${sizeClass}`}>
    {statusLabels[status]}
  </span>
);
```

### PriorityBadge

**Path**: `frontend/src/components/common/PriorityBadge.tsx`

**Props**:
```typescript
interface PriorityBadgeProps {
  priority: 'high' | 'medium' | 'low';
}
```

**Implementation**:
```tsx
const priorityConfig = {
  high: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
  medium: { color: 'bg-yellow-100 text-yellow-800', icon: Circle },
  low: { color: 'bg-gray-100 text-gray-800', icon: Circle }
};

const { color, icon: Icon } = priorityConfig[priority];

return (
  <span className={`badge ${color}`}>
    <Icon className="w-3 h-3" />
    {t(`priority.${priority}`)}
  </span>
);
```

### ProgressBar

**Path**: `frontend/src/components/common/ProgressBar.tsx`

**Props**:
```typescript
interface ProgressBarProps {
  current: number;
  total: number;
  label?: string;
  showPercentage?: boolean;
}
```

**Implementation**:
```tsx
const percentage = total > 0 ? (current / total) * 100 : 0;
const color = percentage === 100 ? 'bg-green-500' : 'bg-blue-500';

return (
  <div className="progress-bar">
    {label && <span className="label">{label}</span>}
    
    <div className="bar-container bg-gray-200 rounded-full h-2">
      <div
        className={`bar ${color} h-2 rounded-full transition-all`}
        style={{ width: `${percentage}%` }}
      />
    </div>
    
    {showPercentage && (
      <span className="percentage text-sm">{percentage.toFixed(0)}%</span>
    )}
  </div>
);
```

---

## Hooks

### useProjects

**Path**: `frontend/src/hooks/useProjects.ts`

**Purpose**: Fetch and manage all projects data

**Implementation**:
```typescript
export const useProjects = () => {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const [jobs, customers, quotations, allPayments] = await Promise.all([
        jobsApi.getAll(),
        customersApi.getAll(),
        quotationsApi.getAll(),
        paymentsApi.getAll() // Or fetch per job if too large
      ]);
      
      // Enrich jobs with related data
      return jobs.map(job => ({
        ...job,
        customer: customers.find(c => c.id === job.customer_id),
        quotation: quotations.find(q => q.id === job.quotation_id),
        payments: allPayments.filter(p => p.job_id === job.id)
      }));
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true
  });
};
```

### useProjectDetails

**Path**: `frontend/src/hooks/useProjectDetails.ts`

**Purpose**: Aggregate all data for single project

**Implementation**:
```typescript
export const useProjectDetails = (jobId: number) => {
  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.getById(jobId)
  });
  
  const { data: quotation, isLoading: quotationLoading } = useQuery({
    queryKey: ['quotation', job?.quotation_id],
    queryFn: () => quotationsApi.getById(job!.quotation_id),
    enabled: !!job?.quotation_id
  });
  
  const { data: customer, isLoading: customerLoading } = useQuery({
    queryKey: ['customer', job?.customer_id],
    queryFn: () => customersApi.getById(job!.customer_id),
    enabled: !!job?.customer_id
  });
  
  const { data: payments = [], isLoading: paymentsLoading } = useQuery({
    queryKey: ['payments', 'job', jobId],
    queryFn: () => paymentsApi.getByJobId(jobId)
  });
  
  const { data: measurements = [], isLoading: measurementsLoading } = useQuery({
    queryKey: ['measurements', 'job', jobId],
    queryFn: () => measurementsApi.getByJobId(jobId)
  });
  
  const { data: timeline = [], isLoading: timelineLoading } = useQuery({
    queryKey: ['timeline', jobId],
    queryFn: () => activityLogsApi.getByJobId(jobId)
  });
  
  const isLoading = jobLoading || quotationLoading || customerLoading || 
                    paymentsLoading || measurementsLoading || timelineLoading;
  
  return {
    job,
    quotation,
    customer,
    payments,
    measurements,
    timeline,
    isLoading,
    error: /* aggregate errors */
  };
};
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Related**: design.md, architecture.md

