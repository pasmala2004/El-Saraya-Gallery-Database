# Frontend Testing Checklist

## Prerequisites
- Backend server running on http://localhost:8000
- Frontend dev server running on http://localhost:5173
- Database seeded with reference data (product categories, products)
- At least one customer in the database

---

## Customers Module Testing

### List View
- [ ] Navigate to /customers
- [ ] Verify table displays customer data
- [ ] Verify Arabic text displays correctly (RTL)
- [ ] Verify dates are in Arabic format

### Search & Filter
- [ ] Type in search box - verify real-time filtering works
- [ ] Enter city name - verify city filter works
- [ ] Clear filters - verify all customers appear

### Create Customer
- [ ] Click "إضافة عميل" button
- [ ] Verify modal opens
- [ ] Try submitting empty form - verify validation errors
- [ ] Fill in required fields:
  - Full name (Arabic): محمد أحمد
  - Phone number: 01012345678
- [ ] Fill optional fields:
  - City: القاهرة
  - Address: شارع النيل
  - Notes: عميل مميز
- [ ] Click save
- [ ] Verify success toast appears
- [ ] Verify customer appears in table
- [ ] Verify phone number formatted correctly

### Edit Customer
- [ ] Click edit icon (pencil) on a customer
- [ ] Verify modal opens with pre-filled data
- [ ] Modify name or city
- [ ] Click save
- [ ] Verify success toast appears
- [ ] Verify changes appear in table

### Delete Customer
- [ ] Click delete icon (trash) on a customer
- [ ] Verify confirmation dialog appears
- [ ] Verify customer details shown in dialog
- [ ] Click cancel - verify nothing happens
- [ ] Click delete icon again
- [ ] Click confirm delete
- [ ] Verify success toast appears
- [ ] Verify customer removed from table

### Error Handling
- [ ] Stop backend server
- [ ] Refresh page
- [ ] Verify error message displays
- [ ] Start backend server
- [ ] Refresh page - verify data loads

---

## Products Module Testing

### List View
- [ ] Navigate to /products
- [ ] Verify table displays products
- [ ] Verify category badges display
- [ ] Verify active/inactive status badges display correctly
- [ ] Verify descriptions truncate with "..."

### Search & Filter
- [ ] Type product name in search - verify filtering
- [ ] Select category from dropdown - verify filtering
- [ ] Select status (Active/Inactive/All) - verify filtering
- [ ] Clear all filters - verify all products appear

### Create Category
- [ ] Click "إضافة فئة" button
- [ ] Fill category name: نوافذ
- [ ] Fill description (optional)
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify category appears in category dropdown

### Create Product
- [ ] Click "إضافة منتج" button
- [ ] Try submitting without required fields - verify validation
- [ ] Fill product name: نافذة ألومنيوم
- [ ] Select category from dropdown
- [ ] Fill description: نافذة ألومنيوم بجودة عالية
- [ ] Check "نشط" checkbox
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify product appears in table
- [ ] Verify product shows with active badge

### Edit Product
- [ ] Click edit icon on a product
- [ ] Modify name or description
- [ ] Uncheck "نشط" to make inactive
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify product shows inactive badge

### Delete Product
- [ ] Click delete icon on a product
- [ ] Verify confirmation shows product details
- [ ] Click confirm
- [ ] Verify success toast
- [ ] Verify product removed from table

---

## Quotations Module Testing

### List View
- [ ] Navigate to /quotations
- [ ] Verify table displays quotations
- [ ] Verify customer names display
- [ ] Verify quotation numbers display
- [ ] Verify dates in Arabic format
- [ ] Verify status badges with correct colors
- [ ] Verify final prices in Egyptian Pounds

### Search & Filter
- [ ] Type customer name in search
- [ ] Select status from dropdown
- [ ] Verify filtering works for each status

### Create Quotation
- [ ] Click "إضافة عرض سعر" button
- [ ] Try submitting without customer - verify validation
- [ ] Select customer from dropdown
- [ ] Set quotation date (default is today)
- [ ] Enter discount: 100
- [ ] Enter notes (optional)
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify quotation appears in table

### View Quotation Details
- [ ] Click eye icon on a quotation
- [ ] Verify modal opens with quotation info
- [ ] Verify customer name displays
- [ ] Verify quotation number displays
- [ ] Verify status badge displays
- [ ] Verify items section exists (empty if no items)
- [ ] Verify totals section shows:
  - Total price: 0.00 ج.م
  - Discount: 100.00 ج.م
  - Final price: calculated correctly

### Add Quotation Item
- [ ] While in details modal, click "إضافة عنصر"
- [ ] Try submitting empty - verify validation
- [ ] Select product from dropdown
- [ ] Enter quantity: 5
- [ ] Enter unit price: 1000
- [ ] Enter description (optional): مقاس 150x200
- [ ] Enter notes (optional)
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify item appears in items table
- [ ] Verify item total = quantity × unit price
- [ ] Verify quotation totals update automatically
- [ ] Add another item - verify totals update again

### Edit Quotation Item
- [ ] In details modal, click edit icon on an item
- [ ] Modify quantity or unit price
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify item total updates
- [ ] Verify quotation totals update

### Change Quotation Status
- [ ] Close details modal
- [ ] Click status change icon (dollar sign) on a quotation
- [ ] Select new status from dropdown
- [ ] Click save
- [ ] Verify success toast
- [ ] Verify status badge updates in table
- [ ] Open details again - verify status changed

### Status Workflow Testing
Test the backend business logic by trying these status transitions:

- [ ] Create quotation (status: draft)
- [ ] Change to "waiting_for_measurement"
- [ ] Change to "measured"
- [ ] Change to "sent"
- [ ] Change to "approved"
- [ ] Try changing back to "draft" - backend should reject
- [ ] Create another quotation
- [ ] Change to "sent"
- [ ] Change to "rejected"

### Quotation Totals Verification
- [ ] Create quotation with 100 discount
- [ ] Add item: quantity=2, unit_price=500 (total=1000)
- [ ] Verify: total_price=1000, discount=100, final_price=900
- [ ] Add item: quantity=1, unit_price=300 (total=300)
- [ ] Verify: total_price=1300, discount=100, final_price=1200
- [ ] Edit first item: quantity=3
- [ ] Verify: total_price=1800, discount=100, final_price=1700

---

## RTL & Arabic Testing

### Text Direction
- [ ] Verify all text aligns to the right
- [ ] Verify form inputs have correct text direction
- [ ] Verify phone numbers are LTR
- [ ] Verify numbers and prices are formatted correctly

### Icons
- [ ] Verify search icon on right side of input
- [ ] Verify chevrons/arrows point in correct direction
- [ ] Verify edit/delete icons align properly

### Layout
- [ ] Verify sidebar on right side
- [ ] Verify action buttons on right
- [ ] Verify table columns flow right-to-left

---

## Responsive Testing

### Desktop (1920x1080)
- [ ] Verify all pages display correctly
- [ ] Verify tables have proper spacing
- [ ] Verify modals center properly

### Tablet (768x1024)
- [ ] Verify grid layouts adapt
- [ ] Verify tables scroll horizontally
- [ ] Verify modals resize

### Mobile (375x667)
- [ ] Verify header stacks vertically
- [ ] Verify filter inputs stack vertically
- [ ] Verify tables scroll horizontally
- [ ] Verify action buttons touch-friendly

---

## Loading & Error States

### Loading States
- [ ] Slow down network in DevTools
- [ ] Verify loading spinner appears
- [ ] Verify buttons show loading state during mutations

### Error States
- [ ] Stop backend
- [ ] Try creating customer - verify error toast
- [ ] Refresh page - verify error message displays
- [ ] Start backend - verify recovery

### Empty States
- [ ] Clear all filters with no results
- [ ] Verify empty state message
- [ ] Verify call-to-action button works

---

## Performance Testing

### Initial Load
- [ ] Open DevTools Network tab
- [ ] Hard refresh page
- [ ] Verify page loads in < 2 seconds
- [ ] Verify no unnecessary API calls

### Interaction Performance
- [ ] Type in search box - verify no lag
- [ ] Open/close modals - verify smooth transitions
- [ ] Switch between pages - verify instant navigation

---

## Browser Testing

Test in each browser:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

Verify in each:
- [ ] Page renders correctly
- [ ] Interactions work
- [ ] API calls succeed
- [ ] No console errors

---

## Common Issues to Check

### Form Validation
- [ ] Required fields prevent submission
- [ ] Error messages display clearly
- [ ] Success messages appear after actions

### Data Refresh
- [ ] After creating item, list updates
- [ ] After editing item, changes appear
- [ ] After deleting item, item disappears
- [ ] No stale data displayed

### Modal Behavior
- [ ] Click outside modal - verify it closes (or doesn't, depending on UX choice)
- [ ] Press Escape key - verify modal closes
- [ ] Open second modal - verify first closes
- [ ] Close modal - verify form resets

---

## Final Checklist

- [ ] All CRUD operations work for all three modules
- [ ] All Arabic translations display correctly
- [ ] RTL layout works perfectly
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] All API calls use correct endpoints
- [ ] Success/error toasts appear for all actions
- [ ] Loading states work correctly
- [ ] Responsive design works on all screen sizes
- [ ] Forms validate properly
- [ ] Modals open/close correctly

---

## Known Issues (From Implementation)

1. **Pagination Navigation**: Previous/Next buttons exist but don't change the offset parameter yet
2. **Delete Quotation Item**: API endpoint might not exist in backend (`DELETE /quotation-items/:id`)
3. **Delete Quotation**: No delete quotation button in UI (design decision - use status change instead)

---

## Reporting Issues

When reporting issues, include:
1. Browser and version
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Console errors (if any)
6. Network response (if API related)
