# Project Details Page Redesign

## Goal
Transform Project Details into a single-page interface with collapsible sections, inline editing, and minimal modals.

## Design Principles
1. **Everything on one screen** - no navigation away for edits
2. **Collapsible sections** - reduce scroll, focus on relevant data
3. **Inline editing** - click to edit, save/cancel inline
4. **Minimal modals** - only for complex forms (add measurement, add payment)
5. **Smart defaults** - commonly used sections open by default

## Section Structure

### 1. Header (Always Visible)
- Back button
- Project title & quotation number
- Status badge (inline editable dropdown)
- Quick actions (Approve for quotations only)

### 2. Customer Section (Collapsible - Default: Open)
- Customer name (read-only, links to customer page)
- Phone number (read-only)
- City (read-only)
- Address (read-only if exists)

### 3. Quotation Section (Collapsible - Default: Open)
- Items table with inline edit
- Add item inline (no modal)
- Totals with inline discount edit
- Quote date (inline edit)
- Notes (inline edit textarea)

### 4. Measurements Section (Collapsible - Default: Open if job exists)
- List of measurements
- Click measurement expands inline to show items
- Add measurement button (keeps modal for complexity)
- Edit measurement inline where possible

### 5. Payments Section (Collapsible - Default: Open if job exists)
- Payment summary cards
- Payment list with inline status change
- Add payment inline form
- Mark as paid inline action

### 6. Timeline Section (Collapsible - Default: Closed)
- Measurement date (inline date picker)
- Production start/end (inline date picker)
- Installation date (inline date picker)
- Completion date (inline date picker)

### 7. Activity Section (Collapsible - Default: Closed)
- Read-only activity log
- Auto-generated from backend
- Shows recent 10 activities

## Inline Editing Behavior
- **Click to edit**: Shows input/select/textarea
- **Auto-save on blur**: Saves when clicking outside
- **Enter to save**: For text inputs
- **Escape to cancel**: Reverts changes
- **Visual feedback**: Loading spinner on save, success checkmark
- **Error handling**: Shows error message inline, reverts value

## Components Needed
1. `CollapsibleSection` - Section wrapper with expand/collapse
2. `InlineEdit` - Text/number/date inline editing
3. `InlineSelect` - Dropdown inline editing
4. `InlineTextarea` - Multiline inline editing
5. `ExpandableList` - For measurements/payments lists

## State Management
- Optimistic updates for inline edits
- React Query for data fetching
- Automatic cache invalidation
- No form state unless in modal

## Accessibility
- Keyboard navigation
- ARIA labels for collapsible sections
- Focus management on edit mode
- Screen reader friendly

## Mobile Considerations
- Sections stack vertically
- Collapsible helps reduce scroll
- Touch-friendly tap targets
- Inline editing works on mobile
