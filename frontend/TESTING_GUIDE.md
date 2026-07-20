# Testing Guide: Arabic RTL Implementation

This guide will help you verify that the Arabic RTL implementation is working correctly.

## Prerequisites

1. Development server is running:
   ```bash
   cd frontend
   npm run dev
   ```

2. Open browser to: http://localhost:3000/

## Visual Testing Checklist

### 1. HTML & Font Loading
- [ ] **Browser tab title** shows: "نظام إدارة المعرض"
- [ ] **Cairo font** is loaded (check DevTools → Network → Fonts)
- [ ] **Text appears in Arabic** with proper rendering
- [ ] **No font fallback** issues visible

### 2. Layout Direction (RTL)

#### Desktop View (> 1024px)
- [ ] **Sidebar is on the RIGHT** side of screen
- [ ] **Main content** occupies left portion
- [ ] **Logo** "نظام إدارة المعرض" is visible in sidebar header
- [ ] **Navigation icons** have space on the RIGHT (not left)
- [ ] **Text flows** from right to left naturally

#### Mobile View (< 1024px)
- [ ] **Menu button** appears on the RIGHT
- [ ] **Page title** appears on the LEFT
- [ ] **Sidebar slides FROM RIGHT** when opened
- [ ] **Backdrop overlay** appears when sidebar is open
- [ ] **Sidebar closes** when clicking backdrop

### 3. Navigation Menu

Check all navigation items display in Arabic:
- [ ] **لوحة التحكم** (Dashboard)
- [ ] **العملاء** (Customers)
- [ ] **المنتجات** (Products)
- [ ] **عروض الأسعار** (Quotations)
- [ ] **الأعمال** (Jobs)
- [ ] **المدفوعات** (Payments)

Verify behavior:
- [ ] Active page is **highlighted** (blue background)
- [ ] Hover effect works on menu items
- [ ] Icons appear BEFORE text (on the right)
- [ ] Clicking navigates to correct page

### 4. Dashboard Page

#### Page Header
- [ ] Title shows: **"لوحة التحكم"**
- [ ] Subtitle shows: **"مرحباً بك في نظام إدارة المعرض - عملك في لمحة"**

#### Statistics Cards
Check all 4 cards display:
- [ ] **إجمالي العملاء** (Total Customers)
- [ ] **إجمالي عروض الأسعار** (Total Quotations)
- [ ] **عروض الأسعار المسودة** (Draft Quotations)
- [ ] **عروض الأسعار المرسلة** (Sent Quotations)

Verify card layout:
- [ ] Icon is on the **LEFT** side
- [ ] Text is on the **RIGHT** side
- [ ] Numbers display correctly (currently 0)

#### Quick Actions Section
- [ ] Section title: **"إجراءات سريعة"**
- [ ] Four action cards visible
- [ ] Icons appear on the **RIGHT** of text
- [ ] Cards have proper hover effects

Check action cards:
- [ ] **إضافة عميل** / إنشاء عميل جديد
- [ ] **عرض سعر جديد** / إنشاء عرض سعر
- [ ] **عرض الأعمال** / إدارة الأعمال النشطة
- [ ] **تسجيل دفعة** / إضافة دفعة جديدة

### 5. Other Pages

#### Customers Page
- [ ] Title: **"العملاء"**
- [ ] Subtitle: **"إدارة قاعدة بيانات العملاء"**
- [ ] Coming soon message: **"إدارة العملاء قريباً..."**

#### Products Page
- [ ] Title: **"المنتجات"**
- [ ] Subtitle: **"إدارة كتالوج المنتجات"**
- [ ] Coming soon message: **"إدارة المنتجات قريباً..."**

#### Quotations Page
- [ ] Title: **"عروض الأسعار"**
- [ ] Subtitle: **"إدارة عروض الأسعار للعملاء"**
- [ ] Coming soon message: **"إدارة عروض الأسعار قريباً..."**

#### Jobs Page
- [ ] Title: **"الأعمال"**
- [ ] Subtitle: **"إدارة الأعمال النشطة والمكتملة"**
- [ ] Module title: **"وحدة الأعمال"**
- [ ] Description paragraph in Arabic
- [ ] "Coming Soon" title: **"قريباً:"**
- [ ] Five bullet points in Arabic
- [ ] List bullets on the **RIGHT** side

#### Payments Page
- [ ] Title: **"المدفوعات"**
- [ ] Subtitle: **"تتبع مدفوعات العملاء والمعاملات"**
- [ ] Module title: **"وحدة المدفوعات"**
- [ ] Description paragraph in Arabic
- [ ] "Coming Soon" title: **"قريباً:"**
- [ ] Five bullet points in Arabic
- [ ] List bullets on the **RIGHT** side

### 6. Footer
- [ ] Copyright text: **"© 2026 نظام إدارة المعرض"**
- [ ] Centered in sidebar footer

### 7. Responsive Behavior

#### Tablet (768px - 1023px)
- [ ] Sidebar becomes collapsible
- [ ] Layout adjusts properly
- [ ] Touch targets are adequate

#### Mobile (< 768px)
- [ ] Hamburger menu on right
- [ ] Full-width content area
- [ ] Cards stack vertically
- [ ] Text remains readable

## Browser Compatibility Testing

Test in multiple browsers:

### Chrome/Edge
- [ ] RTL layout correct
- [ ] Cairo font loads
- [ ] Arabic text renders properly
- [ ] No console errors

### Firefox
- [ ] RTL layout correct
- [ ] Cairo font loads
- [ ] Arabic text renders properly
- [ ] No console errors

### Safari (if available)
- [ ] RTL layout correct
- [ ] Cairo font loads
- [ ] Arabic text renders properly
- [ ] No console errors

## Developer Tools Verification

### 1. HTML Inspection
Open DevTools → Elements:
```html
<html lang="ar" dir="rtl">
```

### 2. Font Loading
Open DevTools → Network → Filter "font":
- [ ] Cairo font files downloaded (woff2 format)
- [ ] Status: 200 OK
- [ ] Multiple font weights loaded

### 3. Console Errors
Open DevTools → Console:
- [ ] No errors about missing translations
- [ ] No font loading errors
- [ ] No RTL-related warnings

### 4. Computed Styles
Inspect body element:
- [ ] `direction: rtl`
- [ ] `font-family: Cairo, ...`
- [ ] `text-align: right` (default)

## Formatting Verification (Browser Console)

Open browser console and test formatters:

```javascript
// Import example (if using dev tools)
// These should work if you inspect the window object

// Test date formatting - should show Arabic numerals
const date = new Date('2026-01-15');
new Intl.DateTimeFormat('ar-EG').format(date);
// Expected: "١٥‏/٠١‏/٢٠٢٦"

// Test currency formatting - should show EGP
new Intl.NumberFormat('ar-EG', {
  style: 'currency',
  currency: 'EGP'
}).format(1500.50);
// Expected: "١٬٥٠٠٫٥٠ ج.م"

// Test number formatting - should show Arabic numerals
new Intl.NumberFormat('ar-EG').format(1234567.89);
// Expected: "١٬٢٣٤٬٥٦٧٫٨٩"
```

## Accessibility Testing

### 1. Screen Reader Testing (if available)
- [ ] Page title announced correctly
- [ ] Navigation items announced
- [ ] Headings in proper hierarchy
- [ ] Links have descriptive text

### 2. Keyboard Navigation
- [ ] Tab order flows right-to-left
- [ ] Focus indicators visible
- [ ] All interactive elements reachable
- [ ] Enter/Space activate buttons

### 3. Contrast & Readability
- [ ] Text contrast meets WCAG AA standards
- [ ] Cairo font is legible at all sizes
- [ ] Icons are clear and recognizable

## Known Issues to Check

### Things That Should NOT Happen:
- [ ] ~~Sidebar on the left~~ (should be right)
- [ ] ~~English text anywhere in UI~~ (should be Arabic)
- [ ] ~~Icons with mr-3~~ (should be ml-3 in RTL)
- [ ] ~~Western numerals~~ (should be Arabic-Indic)
- [ ] ~~Toast on top-right~~ (should be top-left)
- [ ] ~~Text aligned left~~ (should be right by default)
- [ ] ~~Border-right on sidebar~~ (should be border-left)

## Performance Testing

### 1. Initial Load
- [ ] Page loads in < 2 seconds
- [ ] Font loading doesn't block rendering (FOIT/FOUT)
- [ ] No layout shift when fonts load

### 2. Navigation
- [ ] Page transitions are smooth
- [ ] No jank when opening sidebar
- [ ] Hover effects perform well

### 3. Bundle Size
Check in DevTools → Network:
- [ ] Main JS bundle < 500KB (gzipped)
- [ ] CSS bundle < 50KB (gzipped)
- [ ] Total page weight reasonable

## Example Component Testing

If you want to view the example component:

1. Temporarily add route in `App.tsx`:
```tsx
<Route path="/example" element={<ArabicRTLExample />} />
```

2. Navigate to http://localhost:3000/example

3. Verify:
- [ ] All sections display correctly
- [ ] Formatting examples show Arabic numerals
- [ ] Enum translations work
- [ ] Table layout is RTL
- [ ] Form layout is RTL

## Testing with Real Data

When you have actual API data, verify:

### Quotation Status Translation
```tsx
// API returns: status: "draft"
// Display should show: "مسودة"
```

### Job Status Translation
```tsx
// API returns: status: "in_progress"
// Display should show: "قيد التنفيذ"
```

### Payment Method Translation
```tsx
// API returns: payment_method: "cash"
// Display should show: "نقدي"
```

### Currency Formatting
```tsx
// API returns: total_price: "1500.50"
// Display should show: "١٬٥٠٠٫٥٠ ج.م"
```

### Date Formatting
```tsx
// API returns: created_at: "2026-01-15T10:30:00Z"
// Display should show: "١٥‏/٠١‏/٢٠٢٦"
```

### Phone Formatting
```tsx
// API returns: phone_number: "01012345678"
// Display should show: "0101 234 5678"
```

## Regression Testing

After making future changes, verify:

- [ ] RTL layout still correct
- [ ] Arabic translations still working
- [ ] Formatters still functioning
- [ ] No new English text introduced
- [ ] Sidebar still on right
- [ ] Icons still have correct spacing

## Sign-Off Checklist

Before considering the implementation complete:

- [ ] All visual tests passed
- [ ] All pages reviewed
- [ ] Tested in at least 2 browsers
- [ ] Mobile responsive verified
- [ ] No console errors
- [ ] Documentation reviewed
- [ ] Example component works
- [ ] Ready for user acceptance testing

## User Acceptance Testing

When Egyptian gallery assistants test:

Ask them to verify:
- [ ] Text is natural and professional in Arabic
- [ ] Numbers are readable in Arabic format
- [ ] Currency display is clear (ج.م)
- [ ] Layout feels natural for RTL users
- [ ] Phone numbers are formatted as expected
- [ ] Navigation is intuitive
- [ ] No confusing translations

## Troubleshooting

### Issue: Font not loading
- Check Google Fonts link in index.html
- Verify network connection
- Check browser console for errors

### Issue: Layout still LTR
- Verify `dir="rtl"` in HTML
- Check CSS `direction: rtl`
- Clear browser cache

### Issue: Numbers show Western style
- Verify `ar-EG` locale in formatters
- Check Intl API support in browser

### Issue: Translations not showing
- Check translation key spelling
- Verify import statements
- Look for console warnings

### Issue: Sidebar on wrong side
- Check `right-0` vs `left-0` in Layout
- Verify `pr-64` vs `pl-64` for main content
- Clear cache and hard reload

## Success Criteria

✅ **The implementation is successful when:**

1. All UI text displays in Arabic
2. Layout flows right-to-left naturally
3. Cairo font renders throughout
4. Numbers show Arabic-Indic numerals
5. Currency displays as Egyptian Pounds
6. Dates format with ar-EG locale
7. No English text visible to users
8. All pages are accessible and functional
9. Mobile responsive behavior works
10. Egyptian users find it natural and intuitive

## Report Issues

If you find any issues during testing:

1. Note the page/component affected
2. Describe the expected behavior
3. Describe the actual behavior
4. Include browser/device information
5. Provide screenshots if helpful
6. Check console for errors

Document in the project issue tracker or communicate with the development team.
