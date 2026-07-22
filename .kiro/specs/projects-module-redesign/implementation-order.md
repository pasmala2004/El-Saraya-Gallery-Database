# Projects Module - Implementation Order

**Feature ID**: `projects-module-redesign`  
**Version**: 1.0  
**Created**: 2026-07-21

---

## Implementation Sequence

### Principle

**One step at a time. Each step must be production-ready before proceeding to the next.**

---

## Step 1: Project List Redesign (6-8 hours)

### Order of Implementation

1. **Create Reusable Components** (2 hours)
   - `StatusBadge.tsx` - Colored status indicator
   - `PriorityBadge.tsx` - Priority indicator with icon
   - `ProgressBar.tsx` - Payment progress visualization
   
2. **Create ProjectCard Component** (2 hours)
   - Use new badges and progress bar
   - Display customer, status, payments, dates
   - Calculate derived data (progress %, overdue, days in stage)
   - Handle click to navigate

3. **Create Filter Components** (2 hours)
   - `ProjectsFilters.tsx` - Filter panel with all criteria
   - `ProjectsSearch.tsx` - Debounced search input
   - `useProjectsFilters.ts` - Filter state hook

4. **Redesign Jobs Page** (2 hours)
   - Replace table with card grid
   - Integrate filters and search
   - Handle Dashboard KPI navigation (apply filters from state)
   - Loading skeletons
   - Empty states

5. **Add Translations** (30 min)
   - Filter labels
   - Card field labels
   - Warning badge texts

6. **Testing** (1 hour)
   - All filters work
   - Search works
   - Dashboard KPI filtering works
   - Responsive (mobile, tablet, desktop)
   - RTL layout

**Dependencies**: None (can start immediately)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Card-based layout displays correctly
- [ ] All filters work independently and combined
- [ ] Search queries customer, quotation #, job ID, phone
- [ ] Dashboard KPIs link to filtered Projects page
- [ ] Payment progress calculates correctly
- [ ] Overdue indicators show when appropriate
- [ ] Days in stage calculate correctly
- [ ] Responsive on all breakpoints
- [ ] RTL layout correct
- [ ] No console errors
- [ ] Performance <2s initial load

---

## Step 2: Project Header Redesign (4-6 hours)

### Order of Implementation

1. **Create Header Components** (3 hours)
   - `ProjectDetailsHeader.tsx` - Main sticky header
   - `ProjectIdentification.tsx` - IDs and badges
   - `CustomerSummary.tsx` - Customer info compact
   - `FinancialSummary.tsx` - Totals, balance, progress
   - `DatesSummary.tsx` - Key dates
   - `QuickActions.tsx` - Conditional buttons

2. **Create useProjectDetails Hook** (1 hour)
   - Aggregate all data fetching
   - Parallel queries with React Query
   - Loading state management

3. **Integrate Header into ProjectDetails Page** (1 hour)
   - Replace existing header
   - Make sticky (CSS)
   - Connect to data hooks
   - Handle print action

4. **Add Translations** (30 min)
   - Header labels
   - Financial labels
   - Date labels

5. **Testing** (1 hour)
   - Header displays all info correctly
   - Sticky positioning works
   - Financial calculations correct
   - Phone/WhatsApp links work
   - Print button works
   - Responsive

**Dependencies**: Step 1 (reuses StatusBadge, PriorityBadge, ProgressBar)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Header is sticky (stays visible on scroll)
- [ ] All IDs display correctly
- [ ] Customer info correct
- [ ] Financial summary accurate (total, paid, remaining, progress)
- [ ] Dates format correctly
- [ ] Phone link initiates call
- [ ] WhatsApp opens with number
- [ ] Print button works
- [ ] Responsive (stacks on mobile)
- [ ] RTL layout correct
- [ ] No layout shifts during load

---

## Step 3: Workflow Redesign (6-8 hours)

### Order of Implementation

1. **Define Workflow Stage Configuration** (1 hour)
   - Create `workflowStages` array
   - Define entry/exit conditions
   - Define allowed actions per stage
   - Expected durations

2. **Create Workflow Components** (3 hours)
   - `WorkflowPipeline.tsx` - Visual pipeline container
   - `WorkflowStage.tsx` - Individual stage component
   - `StageConnector.tsx` - Line between stages
   - `CompleteStageModal.tsx` - Confirmation dialog

3. **Implement Stage Completion Logic** (2 hours)
   - Frontend validation
   - API mutation (use existing PUT /jobs/{id} OR new POST /jobs/{id}/complete-stage)
   - Optimistic updates
   - Query invalidation

4. **Backend Enhancement** (1 hour) - OPTIONAL
   - Create POST /jobs/{id}/complete-stage endpoint
   - Automatic activity log creation
   - Status transition validation

5. **Add Translations** (30 min)
   - Stage names
   - Completion confirmation texts

6. **Testing** (1 hour)
   - Visual pipeline renders correctly
   - Current stage highlighted
   - Completed stages show green
   - Overdue stages show red
   - Complete button works
   - Cannot complete out of order

**Dependencies**: Step 2 (header provides context)

**Backend Changes**: Optional (create complete-stage endpoint for cleaner semantics)

**Verification Checklist**:
- [ ] Pipeline displays all 8 stages
- [ ] Current stage highlighted in blue
- [ ] Completed stages green with checkmarks
- [ ] Overdue stages red with indicator
- [ ] Complete Stage button only on active stage
- [ ] Confirmation dialog shows before completion
- [ ] Stage completion updates job status
- [ ] Timeline records event
- [ ] Workflow refreshes after completion
- [ ] RTL layout (stages flow right-to-left)

---

## Step 4: Timeline Redesign (5-7 hours)

### Order of Implementation

1. **Backend: ActivityLog Integration** (2 hours)
   - Create GET /activity-logs?job_id={id} endpoint (if not exists)
   - Ensure all significant actions create ActivityLog entries:
     - Job created
     - Quotation approved
     - Payment added
     - Payment marked paid
     - Measurement added
     - Stage completed

2. **Create Timeline Components** (2 hours)
   - `ProjectTimeline.tsx` - Timeline container
   - `TimelineTable.tsx` - Table layout
   - `TimelineRow.tsx` - Individual event row
   - `TimelineSummary.tsx` - Duration summary

3. **Create activityLogsApi Service** (1 hour)
   - GET /activity-logs?job_id={id}
   - Type definitions

4. **Implement Duration Calculations** (1 hour)
   - Calculate stage durations
   - Estimate completion
   - Identify delays

5. **Add Translations** (30 min)
   - Timeline labels
   - Event descriptions

6. **Testing** (1 hour)
   - Timeline displays all events
   - Events sort by date (newest first)
   - Duration calculations correct
   - Delay indicators show
   - Planned vs actual dates display

**Dependencies**: Step 3 (workflow completion generates events)

**Backend Changes**: Ensure ActivityLog entries created for all actions

**Verification Checklist**:
- [ ] Timeline loads all events
- [ ] Events display with icon, date, time, user, description
- [ ] Planned vs actual dates table renders
- [ ] Delayed events highlight in red
- [ ] On-time events show in green
- [ ] Duration calculates correctly
- [ ] Total project duration displays
- [ ] Estimated completion calculates
- [ ] New events appear in real-time (after mutation)

---

## Step 5: Payments Integration (4-6 hours)

### Order of Implementation

1. **Create Payment Components** (2 hours)
   - `PaymentsSection.tsx` - Main container
   - `PaymentsSummary.tsx` - 3-card summary
   - `PaymentsList.tsx` - Payment list
   - `PaymentCard.tsx` - Individual payment display

2. **Reuse Existing Add Payment Modal** (1 hour)
   - Ensure modal works in ProjectDetails context
   - Pre-fill job_id
   - Handle success callback

3. **Implement Mark as Paid** (1 hour)
   - Confirmation dialog
   - API mutation (PATCH /payments/{id}/status)
   - Optimistic update
   - Query invalidation (payments, timeline, header)

4. **Add Link to Global Payments Module** (30 min)
   - Link to `/payments?job_id={id}` 
   - Opens in new tab

5. **Add Translations** (30 min)
   - Payment section labels

6. **Testing** (1 hour)
   - Summary cards calculate correctly
   - Payment list displays all payments for THIS project only
   - Add payment works
   - Mark as paid works
   - Global Payments link works
   - Header financial summary updates

**Dependencies**: Step 2 (header financial summary)

**Backend Changes**: None (all APIs exist)

**Verification Checklist**:
- [ ] Payment summary accurate (total, paid, remaining, progress)
- [ ] Payment list shows only THIS project's payments
- [ ] Add payment modal opens and works
- [ ] Payment created successfully
- [ ] Mark as paid updates status
- [ ] Paid date sets to today
- [ ] Payment card shows green "Paid" badge
- [ ] Header financial summary recalculates
- [ ] Timeline shows "Payment added" event
- [ ] "View Global Payments" link works

---

## Step 6: Measurements Integration (4-6 hours)

### Order of Implementation

1. **Create Measurement Components** (2 hours)
   - `MeasurementsSection.tsx` - Main container
   - `MeasurementCard.tsx` - Measurement display with items
   - `AddMeasurementModal.tsx` - Add measurement form

2. **Implement Add Measurement** (2 hours)
   - Modal form (visit date, engineer, notes)
   - API mutation (POST /measurements)
   - After creation, navigate to measurement items OR stay on page
   - Query invalidation

3. **Implement Edit Measurement** (1 hour)
   - Inline edit OR modal
   - API mutation (PUT /measurements/{id})
   - Query invalidation

4. **Add Translations** (30 min)

5. **Testing** (1 hour)
   - Measurement cards display correctly
   - Add measurement works
   - Edit measurement works
   - Measurement items display

**Dependencies**: None (independent section)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Measurement cards show visit date, engineer, items
- [ ] Add measurement modal opens
- [ ] Measurement creates successfully
- [ ] Timeline records "Measurement added" event
- [ ] Edit measurement updates data
- [ ] Measurement items table displays dimensions

---

## Step 7: Quotation Integration (4-6 hours)

### Order of Implementation

1. **Create Quotation Components** (2 hours)
   - `QuotationSection.tsx` - Main container
   - `QuotationItemsTable.tsx` - Items table
   - `QuotationTotals.tsx` - Subtotal, discount, total display

2. **Implement Edit Quotation** (2 hours)
   - Only if no job exists (quotation stage)
   - Inline edit OR modal for discount, notes
   - API mutation (PUT /quotations/{id})

3. **Implement Add/Remove Items** (1 hour)
   - "Add Item" button opens modal
   - Product selector
   - API mutations
   - Query invalidation

4. **Add Translations** (30 min)

5. **Testing** (1 hour)
   - Quotation items table displays
   - Totals calculate correctly
   - Edit quotation works (if no job)
   - Add item works
   - Approve quotation creates job (existing functionality)

**Dependencies**: None (independent section)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Quotation items display with product, quantity, price, total
- [ ] Subtotal, discount, final total calculate correctly
- [ ] Edit quotation works (if no job created yet)
- [ ] Edit disabled if job exists
- [ ] Add item opens modal and creates item
- [ ] Totals recalculate after changes
- [ ] Approve quotation creates job and navigates (existing functionality)

---

## Step 8: Customer Section (2-3 hours)

### Order of Implementation

1. **Create Customer Components** (1 hour)
   - `CustomerSection.tsx` - Customer info display
   - `CustomerActions.tsx` - Quick action buttons

2. **Implement Customer Actions** (1 hour)
   - Call link (tel:)
   - WhatsApp link (wa.me)
   - Copy phone to clipboard
   - "View Customer Profile" link (opens CRM in new tab)

3. **Add Translations** (30 min)

4. **Testing** (30 min)
   - Customer info displays
   - Phone link works
   - WhatsApp opens
   - Copy phone works
   - View profile link works

**Dependencies**: Step 2 (header already shows customer summary)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Customer name, phone, address display
- [ ] Phone link initiates call on mobile
- [ ] WhatsApp opens with number pre-filled
- [ ] Copy phone copies to clipboard
- [ ] "View Customer Profile" opens Customers module

---

## Step 9: Activity & Documents (3-4 hours)

### Order of Implementation

1. **Create Activity Components** (2 hours)
   - `ActivityFeed.tsx` - Activity list
   - `ActivityItem.tsx` - Individual activity item
   - Display icon, description, user, relative time

2. **Create Documents Section** (1 hour)
   - `DocumentsSection.tsx` - Placeholder component
   - Display message: "Document upload coming soon"
   - Reserve space in architecture

3. **Add Translations** (30 min)

4. **Testing** (30 min)
   - Activity feed displays events
   - Events sort by date
   - Activity auto-updates when changes occur
   - Documents placeholder displays

**Dependencies**: Step 4 (timeline provides events)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Activity feed displays all events chronologically
- [ ] Each item shows icon, description, user, time
- [ ] Relative time calculates correctly ("2 hours ago")
- [ ] Feed updates when new events occur
- [ ] Documents section displays placeholder

---

## Step 10: Polish & UX Improvements (6-8 hours)

### Order of Implementation

1. **Responsive Design Audit** (2 hours)
   - Test all pages on mobile (320px), tablet (768px), desktop (1024px+)
   - Fix layout issues
   - Adjust font sizes
   - Touch-friendly buttons (44x44px min)

2. **Loading States Polish** (1 hour)
   - Skeleton loaders for all sections
   - Progressive loading (show data as it loads)
   - Loading spinners for mutations

3. **Error Handling Improvements** (1 hour)
   - Clear error messages
   - Retry buttons
   - Network failure indicators
   - Validation error displays

4. **Toast Notifications** (1 hour)
   - Success toasts for all mutations
   - Error toasts for failures
   - Consistent messaging

5. **Keyboard Navigation** (1 hour)
   - Tab through all interactive elements
   - Enter/Space activate buttons
   - Escape closes modals
   - Focus management

6. **Accessibility Audit** (1 hour)
   - ARIA labels for icon buttons
   - Semantic HTML
   - Color contrast check
   - Screen reader testing

7. **Print Stylesheet** (1 hour)
   - Create @media print styles
   - Hide navigation, actions
   - Show all collapsed sections
   - Page breaks

8. **Final Testing** (1 hour)
   - End-to-end workflow testing
   - Performance audit
   - No console errors/warnings
   - Stakeholder demo

**Dependencies**: All previous steps (polish everything)

**Backend Changes**: None

**Verification Checklist**:
- [ ] Responsive on all breakpoints
- [ ] Loading states smooth
- [ ] Error messages helpful
- [ ] Success feedback clear
- [ ] Keyboard navigation works
- [ ] WCAG 2.1 AA compliant
- [ ] Print stylesheet renders correctly
- [ ] Performance <2s initial load
- [ ] Zero console errors
- [ ] RTL layout perfect
- [ ] All translations present

---

## Dependencies Graph

```
Step 1 (List)
    ↓ (reuses badges)
Step 2 (Header)
    ↓ (provides context)
Step 3 (Workflow)
    ↓ (generates events)
Step 4 (Timeline)

Step 5 (Payments) ──┐
Step 6 (Measurements)├─> Independent, can parallel
Step 7 (Quotation) ──┘

Step 8 (Customer) ← depends on Step 2 (header)

Step 9 (Activity) ← depends on Step 4 (timeline)

Step 10 (Polish) ← depends on ALL previous steps
```

---

## Time Estimates

| Step | Estimated Time | Cumulative |
|------|----------------|------------|
| Step 1: Project List | 6-8 hours | 6-8 hours |
| Step 2: Header | 4-6 hours | 10-14 hours |
| Step 3: Workflow | 6-8 hours | 16-22 hours |
| Step 4: Timeline | 5-7 hours | 21-29 hours |
| Step 5: Payments | 4-6 hours | 25-35 hours |
| Step 6: Measurements | 4-6 hours | 29-41 hours |
| Step 7: Quotation | 4-6 hours | 33-47 hours |
| Step 8: Customer | 2-3 hours | 35-50 hours |
| Step 9: Activity | 3-4 hours | 38-54 hours |
| Step 10: Polish | 6-8 hours | **44-62 hours** |

**Total Estimated Time**: 44-62 hours (1-1.5 weeks full-time)

---

## Deployment Checklist (Per Step)

Before deploying any step:

1. **Development**:
   - [ ] Code complete
   - [ ] TypeScript errors: 0
   - [ ] ESLint warnings: 0
   - [ ] Console errors: 0

2. **Testing**:
   - [ ] Manual testing complete
   - [ ] All acceptance criteria met
   - [ ] Responsive tested (mobile, tablet, desktop)
   - [ ] RTL layout tested
   - [ ] No regressions

3. **Review**:
   - [ ] Code reviewed
   - [ ] Translations reviewed
   - [ ] Performance acceptable

4. **Deployment**:
   - [ ] Deploy to staging
   - [ ] Stakeholder approval
   - [ ] Deploy to production
   - [ ] Monitor for issues

5. **Verification**:
   - [ ] Production smoke test
   - [ ] No errors in logs
   - [ ] User feedback positive

**Only after all checklist items pass, proceed to next step.**

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Related**: design.md, architecture.md

