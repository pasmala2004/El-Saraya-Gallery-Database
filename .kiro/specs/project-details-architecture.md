# Project Details Page Architecture

## Status: ✅ FROZEN - Ready for UX Improvements

## Overview
Complete restructuring of Project Details page with finalized architecture. No duplicate information, logical section grouping, single-page layout.

## Final Page Structure

### 1. Header Section
**Location**: Top of page, always visible
**Components**:
- Back button
- Customer info card (name, phone, city)
- Project status badge & quotation number
- Quick actions (Approve/Change Status)

**Business Info**:
- Customer full name
- Customer phone
- Customer city
- Quotation number
- Current status (Job or Quotation)
- Quotation date

### 2. Workflow Progress
**Location**: Full width, second section
**Components**:
- Visual progress stepper (6 stages)
- Icons for each stage
- Active/completed indicators

**Stages**:
1. Pending
2. Measuring
3. In Production
4. Ready for Installation
5. Installed
6. Completed

**Visibility**: Only shown when job exists

### 3. Quotation Section
**Location**: Main content area
**Components**:
- Items table (product, quantity, unit price, total)
- Add item button (quotation-only)
- Edit item action (quotation-only)
- Totals summary (total, discount, final price)

**Business Info**:
- All quotation items
- Product names
- Quantities
- Unit prices
- Line totals
- Grand total
- Discount amount
- Final price

### 4. Measurements Section
**Location**: Main content area
**Components**:
- Measurement cards grid (2 columns on desktop)
- Add measurement button
- Click to view measurement details

**Business Info**:
- Measurement number
- Visit date
- Measured by
- Creation date

**Visibility**: Only shown when job exists

### 5. Payments Section
**Location**: Main content area
**Components**:
- Payment summary cards (3 KPIs)
- Payment list with status badges
- Add payment button
- Mark as paid action
- Edit payment action

**Business Info**:
- Total paid amount
- Remaining balance
- Payment percentage
- Individual payments (amount, percentage, due date, paid date, status)
- Payment type (deposit/production/final)
- Payment method
- Overdue indicators

**Visibility**: Only shown when job exists

### 6. Timeline Section
**Location**: Main content area
**Components**:
- Date cards grid (3 columns on desktop)
- Icon-coded dates
- Color-coded by category

**Business Info**:
- Measurement date
- Production start date
- Production end date
- Installation date
- Completion date

**Visibility**: Only shown when job exists

### 7. Recent Activity Section
**Location**: Main content area
**Components**:
- Placeholder for future activity log

**Business Info**:
- Future: Activity timeline from backend

**Visibility**: Always shown (placeholder)

### 8. Notes Section
**Location**: Main content area
**Components**:
- Read-only notes display
- Empty state if no notes

**Business Info**:
- Job notes (if job exists)
- Quotation notes (if no job)

**Visibility**: Always shown

### 9. Documents Section
**Location**: Main content area, bottom
**Components**:
- Placeholder for future document uploads

**Business Info**:
- Future: Document attachments

**Visibility**: Always shown (placeholder)

## Data Fetching Strategy

### Queries (React Query)
1. **Quotation**: Fetched if route is `/projects/:id` (not `/jobs/:id`)
2. **Job**: Fetched if route is `/jobs/:id`
3. **Job's Quotation**: Fetched if job exists (via `job.quotation_id`)
4. **Customer**: Fetched using `activeQuotation.customer_id`
5. **Quotation Items**: Fetched using `activeQuotation.id`
6. **Products**: Fetched for item dropdown (limit 100, active only)
7. **Measurements**: Fetched if job exists
8. **Payments**: Fetched if job exists

### Active Quotation Logic
```typescript
const activeQuotation = !isJobRoute ? quotation : jobQuotation;
```

## Mutations

### Quotation Mutations
- `updateQuotationStatusMutation`: Update quotation status (auto-creates job on approval)
- `addItemMutation`: Add item to quotation
- `updateItemMutation`: Update quotation item

### Job Mutations
- `updateJobStatusMutation`: Update job status

### Measurement Mutations
- `createMeasurementMutation`: Create measurement (navigates to measurement details)

### Payment Mutations
- `createPaymentMutation`: Create payment
- `updatePaymentMutation`: Update payment
- `markPaidMutation`: Mark payment as paid

## Modals

### Required Modals (Complex Forms)
1. **Status Change Modal**: Dropdown to change quotation/job status
2. **Add Item Modal**: Product, quantity, unit price, notes
3. **Edit Item Modal**: Same as add item
4. **Add Measurement Modal**: Visit date, measured by, notes
5. **Add Payment Modal**: Type, method, percentage, amount, due date, notes
6. **Edit Payment Modal**: Same as add payment + paid date
7. **Mark Paid Confirmation**: Confirmation dialog

## Removed Duplicates

### Before Restructure
- Status shown in header AND in dedicated card
- Customer info in header AND in sidebar
- Quotation number in header AND in status card
- Timeline scattered across multiple sections

### After Restructure
- Single header with all primary info
- No duplicate customer display
- No duplicate status display
- Unified timeline section
- Clear section separation

## Component Reuse

### Existing Components Used
- `Button`: All buttons
- `Modal`: All modals
- `Input`: Form inputs
- `Select`: Dropdowns
- `LoadingSpinner`: Loading state
- `JobStatusBadge`: Job status display
- `Badge`: Quotation status display
- `PaymentStatusBadge`: Payment status display
- `ConfirmationDialog`: Mark paid confirmation

### No New Components
All functionality uses existing components, just reorganized.

## File Changes

### New Files
- `frontend/src/pages/ProjectDetailsRestructured.tsx` (active)
- `frontend/src/components/CollapsibleSection.tsx` (created, not yet used)
- `frontend/src/components/InlineEdit.tsx` (created, not yet used)

### Backup Files
- `frontend/src/pages/ProjectDetails.backup.tsx` (original)
- `frontend/src/pages/ProjectDetails.tsx` (original, can be deleted)

### Modified Files
- `frontend/src/App.tsx`: Import changed to `ProjectDetailsRestructured`
- `frontend/src/i18n/translations.ts`: Added 5 new translation keys

### Translation Keys Added
```typescript
workflowProgress: 'سير العمل',
recentActivity: 'النشاط الأخير',
activityPlaceholder: 'سيتم عرض النشاط الأخير هنا',
documents: 'المستندات',
documentsPlaceholder: 'سيتم إضافة المستندات قريباً',
noNotes: 'لا توجد ملاحظات',
quotation: 'عرض السعر',
```

## Verification Checklist

### ✅ Architecture
- [x] No duplicate information
- [x] Logical section grouping
- [x] Clear visual hierarchy
- [x] Single-page layout
- [x] All existing features preserved

### ✅ Data Flow
- [x] All queries work correctly
- [x] All mutations work correctly
- [x] Proper cache invalidation
- [x] Navigation works correctly
- [x] Conditional rendering based on job existence

### ✅ Components
- [x] All existing components reused
- [x] No new dependencies
- [x] No API changes
- [x] No backend modifications

### ✅ User Experience
- [x] Clear information hierarchy
- [x] Consistent spacing and styling
- [x] Responsive grid layouts
- [x] Accessible color contrast
- [x] Loading and error states

## Next Steps (Phase 2: UX Improvements)

Once this architecture is verified in production:

1. **Add Collapsible Sections** (30 min)
   - Wrap sections 3-9 in `CollapsibleSection` component
   - Configure default open/closed states
   - No functionality changes

2. **Add Inline Editing** (45 min)
   - Timeline dates (measurement, production, installation)
   - Quotation notes
   - Job notes
   - Discount amount

3. **Advanced Inline Features** (1-2 hours)
   - Inline item editing
   - Inline payment status updates
   - Inline add item/payment forms

4. **Remove Unnecessary Modals** (30 min)
   - Keep measurement modal (complex)
   - Move simple forms inline

## Notes

- Backend APIs remain unchanged
- All existing functionality preserved
- No breaking changes
- No new NPM packages required
- RTL support maintained
- Arabic translations complete
- Type safety preserved
