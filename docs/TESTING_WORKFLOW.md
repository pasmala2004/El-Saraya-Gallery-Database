# Testing Workflow Checklist

## Prerequisites

### 1. Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```
**Expected**: Server running on http://localhost:8000

### 2. Start Frontend
```bash
cd frontend
npm run dev
```
**Expected**: Dev server running on http://localhost:3000

### 3. Verify API
Open: http://localhost:8000/docs
**Expected**: Swagger UI loads

---

## Complete Workflow Test

### Step 1: Create Customer ✓

1. Navigate to http://localhost:3000/customers
2. Click "إضافة عميل" (Add Customer)
3. Fill form:
   - Name: محمد أحمد السيد
   - Phone: 01012345678
   - City: القاهرة
   - Address: 123 شارع النيل
   - Notes: عميل VIP
4. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Customer appears in table
- ✅ Phone formatted as: 0101 234 5678

**Issues to Note**:
- ❌ No delete button (by design)

---

### Step 2: Edit Customer ✓

1. Click edit icon (pencil) on customer
2. Change city to: الإسكندرية
3. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ City updated in table

---

### Step 3: Search Customer ✓

1. Type "محمد" in search box

**Expected**:
- ✅ Real-time filtering
- ✅ Only matching customers shown

---

### Step 4: Create Product Category ✓

1. Navigate to http://localhost:3000/products
2. Click "إضافة فئة" (Add Category)
3. Fill form:
   - Name: نوافذ ألومنيوم
   - Description: نوافذ بجودة عالية
4. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Category appears in dropdown

**Issues to Note**:
- ⚠️ Cannot edit categories (backend limitation)

---

### Step 5: Create Product ✓

1. Still on products page
2. Click "إضافة منتج" (Add Product)
3. Fill form:
   - Name: نافذة مفصلية 100×150
   - Category: نوافذ ألومنيوم
   - Description: نافذة مفصلية بمقاس 100×150 سم
   - Active: ✓ (checked)
4. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Product appears in table
- ✅ Shows green "نشط" badge

**Issues to Note**:
- ❌ No delete button (by design)

---

### Step 6: Edit Product ✓

1. Click edit icon on product
2. Uncheck "نشط" (Active)
3. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Badge changes to red "غير نشط"

---

### Step 7: Filter Products ✓

1. Select category from dropdown
2. Select status: "نشط" (Active)

**Expected**:
- ✅ Only active products in that category shown

---

### Step 8: Create Quotation ✓

1. Navigate to http://localhost:3000/quotations
2. Click "إضافة عرض سعر" (Add Quotation)
3. Fill form:
   - Customer: محمد أحمد السيد
   - Date: (today's date - default)
   - Discount: 100
   - Notes: عرض تجريبي
4. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Quotation appears in table
- ✅ Status badge shows "مسودة" (Draft)
- ✅ Final price shows: 0.00 ج.م (no items yet)

---

### Step 9: View Quotation Details ✓

1. Click eye icon on quotation

**Expected**:
- ✅ Modal opens
- ✅ Shows quotation info
- ✅ Shows empty items table
- ✅ Shows totals:
  - Total: 0.00 ج.م
  - Discount: 100.00 ج.م
  - Final: -100.00 ج.م (negative because no items)

---

### Step 10: Add Quotation Item ✓

1. In details modal, click "إضافة عنصر" (Add Item)
2. Fill form:
   - Product: نافذة مفصلية 100×150
   - Quantity: 3
   - Unit Price: 1500
   - Description: تركيب في الصالة
4. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Item appears in table
- ✅ Item total shows: 4,500.00 ج.م
- ✅ Quotation totals update:
  - Total: 4,500.00 ج.م
  - Discount: 100.00 ج.م
  - Final: 4,400.00 ج.م

---

### Step 11: Add Another Item ✓

1. Click "إضافة عنصر" again
2. Fill form:
   - Product: (same or different)
   - Quantity: 2
   - Unit Price: 2000
   - Description: تركيب في غرفة النوم
3. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Item appears in table
- ✅ Quotation totals update:
  - Total: 8,500.00 ج.م (4500 + 4000)
  - Discount: 100.00 ج.م
  - Final: 8,400.00 ج.م

---

### Step 12: Edit Quotation Item ✓

1. Click edit icon on first item
2. Change quantity to: 5
3. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Item total updates: 7,500.00 ج.م (5 × 1500)
- ✅ Quotation totals update:
  - Total: 11,500.00 ج.م (7500 + 4000)
  - Discount: 100.00 ج.م
  - Final: 11,400.00 ج.م

**Issues to Note**:
- ❌ Cannot delete items (by design)

---

### Step 13: Change Quotation Status ✓

1. Close details modal
2. Click dollar sign icon on quotation
3. Select status: "في انتظار القياس" (Waiting for Measurement)
4. Click "حفظ" (Save)

**Expected**:
- ✅ Success toast appears
- ✅ Status badge updates in table

**Test Invalid Transition**:
1. Click status icon again
2. Try to select: "موافق عليه" (Approved)
3. Click "حفظ" (Save)

**Expected**:
- ❌ Error toast appears
- ❌ Status doesn't change
- **Reason**: Invalid transition (need to go through workflow)

---

### Step 14: Complete Status Workflow ✓

Follow the workflow:
1. Draft → Waiting for Measurement ✓ (already done)
2. Waiting for Measurement → Measured
3. Measured → Sent
4. Sent → Approved

**Expected**:
- ✅ Each transition succeeds
- ✅ Status badge updates each time
- ✅ Cannot go back after "Approved" (terminal state)

---

### Step 15: Search Quotations ✓

1. Type customer name in search
2. Select different statuses from filter

**Expected**:
- ✅ Filters work correctly
- ✅ Shows matching quotations only

---

### Step 16: Verify Final Data ✓

1. Reopen quotation details
2. Verify all data is correct:
   - Customer name
   - Quotation number
   - Date
   - Status
   - All items with correct quantities/prices
   - Correct totals

**Expected**:
- ✅ All data intact
- ✅ Calculations correct
- ✅ No data loss

---

## Issues to Report

### Critical Bugs ⚠️
List any errors that prevent workflow completion:

1. ________________
2. ________________
3. ________________

### Backend Limitations Found 📋
List any missing features you tried to use:

1. Cannot edit categories (no PUT endpoint)
2. ________________
3. ________________

### UI/UX Issues 💡
List any confusing or difficult interactions:

1. ________________
2. ________________
3. ________________

### Performance Issues ⏱️
List any slow operations:

1. ________________
2. ________________
3. ________________

---

## Success Criteria

### Must Pass ✓
- [ ] All CRUD operations work without errors
- [ ] All data displays correctly in Arabic
- [ ] Totals calculate correctly
- [ ] Status workflow respects business rules
- [ ] Search and filters work
- [ ] No console errors
- [ ] No network failures

### Should Pass ✓
- [ ] Forms validate properly
- [ ] Error messages are clear
- [ ] Loading states show appropriately
- [ ] Mobile layout acceptable
- [ ] Page refreshes don't lose data

### Nice to Have ✓
- [ ] Animations smooth
- [ ] No visual glitches
- [ ] Fast response times
- [ ] Intuitive navigation

---

## Test Results

**Date Tested**: ______________  
**Tester**: ______________  
**Overall Status**: ☐ PASS  ☐ FAIL  ☐ PARTIAL  

**Notes**:
_________________________________________
_________________________________________
_________________________________________

**Readiness for Jobs Module**: ☐ YES  ☐ NO  

**Reason if NO**:
_________________________________________
_________________________________________

---

## Next Steps After Testing

### If All Tests Pass:
1. ✅ Mark as production-ready
2. ✅ Begin Jobs module implementation
3. ✅ Document any workarounds for users

### If Tests Fail:
1. ❌ Document all failures
2. ❌ Prioritize fixes (critical first)
3. ❌ Fix and re-test
4. ❌ Repeat until passing

---

*Use this checklist for systematic testing*  
*Report ALL issues found*  
*Do not skip steps*
