# Before & After: Arabic RTL Transformation

## Visual Changes Overview

### HTML Document
```html
<!-- BEFORE -->
<html lang="en">
  <head>
    <title>frontend</title>
  </head>
</html>

<!-- AFTER -->
<html lang="ar" dir="rtl">
  <head>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <title>نظام إدارة المعرض</title>
  </head>
</html>
```

### Layout Component

#### Sidebar Position
```tsx
// BEFORE: Left side
<aside className="fixed inset-y-0 left-0 border-r">

// AFTER: Right side
<aside className="fixed inset-y-0 right-0 border-l">
```

#### Navigation Items
```tsx
// BEFORE: English with left margin icons
<Link>
  <item.icon className="w-5 h-5 mr-3" />
  Dashboard
</Link>

// AFTER: Arabic with right margin icons
<Link>
  <item.icon className="w-5 h-5 ml-3" />
  {t('nav.dashboard')}  // "لوحة التحكم"
</Link>
```

#### Main Content Padding
```tsx
// BEFORE: Padding left
<div className="lg:pl-64">

// AFTER: Padding right
<div className="lg:pr-64">
```

### Dashboard Page

#### Page Header
```tsx
// BEFORE
<h1>Dashboard</h1>
<p>Welcome to Gallery ERP - Your business at a glance</p>

// AFTER
<h1>{t('dashboard.title')}</h1>  // "لوحة التحكم"
<p>{t('dashboard.subtitle')}</p>  // "مرحباً بك في نظام إدارة المعرض - عملك في لمحة"
```

#### Statistics Cards
```tsx
// BEFORE
stats = [
  { name: 'Total Customers', value: 0 },
  { name: 'Total Quotations', value: 0 },
  { name: 'Draft Quotations', value: 0 },
  { name: 'Sent Quotations', value: 0 },
]

// AFTER
stats = [
  { name: t('dashboard.totalCustomers'), value: 0 },      // "إجمالي العملاء"
  { name: t('dashboard.totalQuotations'), value: 0 },     // "إجمالي عروض الأسعار"
  { name: t('dashboard.draftQuotations'), value: 0 },     // "عروض الأسعار المسودة"
  { name: t('dashboard.sentQuotations'), value: 0 },      // "عروض الأسعار المرسلة"
]
```

#### Quick Actions
```tsx
// BEFORE
<Users className="w-6 h-6 text-blue-600 mr-3" />
<div>
  <p>Add Customer</p>
  <p>Create new customer</p>
</div>

// AFTER
<Users className="w-6 h-6 text-blue-600 ml-3" />
<div>
  <p>{t('dashboard.addCustomer')}</p>        // "إضافة عميل"
  <p>{t('dashboard.createNewCustomer')}</p>  // "إنشاء عميل جديد"
</div>
```

### Data Display Examples

#### Currency Display
```tsx
// BEFORE
<span>${totalPrice}</span>
// Output: $1500.50

// AFTER
<span>{formatCurrency(totalPrice)}</span>
// Output: ١٬٥٠٠٫٥٠ ج.م
```

#### Date Display
```tsx
// BEFORE
<span>{quotation_date}</span>
// Output: 2026-01-15

// AFTER
<span>{formatDate(quotation_date)}</span>
// Output: ١٥‏/٠١‏/٢٠٢٦

<span>{formatDate(quotation_date, 'long')}</span>
// Output: ١٥ يناير ٢٠٢٦
```

#### Status Display
```tsx
// BEFORE
<span>{status}</span>
// Output: draft

// AFTER
<span>{translateQuotationStatus(status)}</span>
// Output: مسودة
```

#### Phone Number Display
```tsx
// BEFORE
<span>{phone_number}</span>
// Output: 01012345678

// AFTER
<span>{formatPhoneNumber(phone_number)}</span>
// Output: 0101 234 5678
```

### Table Layout

```tsx
// BEFORE: Left-aligned
<th className="px-6 py-3 text-left">Full Name</th>
<td className="px-6 py-4">Ahmed Mohamed</td>

// AFTER: Right-aligned with Arabic
<th className="px-6 py-3 text-right">{t('customers.fullName')}</th>
<td className="px-6 py-4">Ahmed Mohamed</td>
```

### Form Layout

```tsx
// BEFORE
<label>Full Name</label>
<input type="text" placeholder="Enter full name" />

// AFTER
<label>{t('customers.fullName')}</label>
<input type="text" placeholder="أدخل الاسم الكامل" />
```

### Toast Notifications

```tsx
// BEFORE: Top-right position
<Toaster position="top-right" richColors />

// AFTER: Top-left position for RTL
<Toaster position="top-left" richColors dir="rtl" />
```

## Typography Changes

### Font Family
```css
/* BEFORE */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', ...;
}

/* AFTER */
body {
  font-family: 'Cairo', -apple-system, BlinkMacSystemFont, ...;
  direction: rtl;
}
```

## Component Usage Pattern

### Before (English)
```tsx
export default function CustomerCard({ customer }) {
  return (
    <div className="p-4">
      <h3>Customer Details</h3>
      <div className="flex justify-between">
        <span>Name:</span>
        <span>{customer.full_name}</span>
      </div>
      <div className="flex justify-between">
        <span>Phone:</span>
        <span>{customer.phone_number}</span>
      </div>
      <div className="flex justify-between">
        <span>Created:</span>
        <span>{customer.created_at}</span>
      </div>
    </div>
  );
}
```

### After (Arabic with RTL)
```tsx
import { useTranslation } from '../i18n';
import { formatPhoneNumber, formatDate } from '../utils';

export default function CustomerCard({ customer }) {
  const { t } = useTranslation();
  
  return (
    <div className="p-4">
      <h3>{t('customers.customerDetails')}</h3>
      <div className="flex justify-between">
        <span>{t('customers.fullName')}:</span>
        <span>{customer.full_name}</span>
      </div>
      <div className="flex justify-between">
        <span>{t('customers.phoneNumber')}:</span>
        <span>{formatPhoneNumber(customer.phone_number)}</span>
      </div>
      <div className="flex justify-between">
        <span>{t('customers.createdAt')}:</span>
        <span>{formatDate(customer.created_at, 'long')}</span>
      </div>
    </div>
  );
}
```

## Number & Currency Examples

| Type | Before | After |
|------|--------|-------|
| Plain Number | 1234567.89 | ١٬٢٣٤٬٥٦٧٫٨٩ |
| Currency | $1,500.50 | ١٬٥٠٠٫٥٠ ج.م |
| Date Short | 01/15/2026 | ١٥‏/٠١‏/٢٠٢٦ |
| Date Long | January 15, 2026 | ١٥ يناير ٢٠٢٦ |
| Phone | 01012345678 | 0101 234 5678 |

## Status Translation Examples

### Quotation Status
| English | Arabic |
|---------|--------|
| draft | مسودة |
| waiting_for_measurement | في انتظار القياس |
| measured | تم القياس |
| under_negotiation | قيد التفاوض |
| sent | مُرسل |
| approved | موافق عليه |
| rejected | مرفوض |
| cancelled | ملغى |
| expired | منتهي الصلاحية |

### Job Status
| English | Arabic |
|---------|--------|
| pending | معلق |
| in_progress | قيد التنفيذ |
| completed | مكتمل |
| cancelled | ملغى |

### Payment Method
| English | Arabic |
|---------|--------|
| cash | نقدي |
| bank_transfer | تحويل بنكي |
| check | شيك |
| credit_card | بطاقة ائتمان |

## File Import Pattern

### Before
```tsx
// No imports needed
```

### After
```tsx
// Add these imports to every component
import { useTranslation } from '../i18n';
import { formatCurrency, formatDate } from '../utils';

// Use in component
const { t } = useTranslation();
```

## API Integration Pattern

### Data Flow
```
┌─────────────────┐
│   Backend API   │  (English values)
└────────┬────────┘
         │
         │ GET /quotations/123
         │ {
         │   "status": "draft",
         │   "total_price": "1500.00",
         │   "quotation_date": "2026-01-15"
         │ }
         │
         ↓
┌─────────────────┐
│  Frontend (RTL) │  (Display in Arabic)
└─────────────────┘
         │
         │ Display:
         │ الحالة: مسودة
         │ السعر الإجمالي: ١٬٥٠٠٫٠٠ ج.م
         │ تاريخ عرض السعر: ١٥‏/٠١‏/٢٠٢٦
         ↓
```

## Visual Layout Changes

### Desktop View

```
BEFORE (LTR):
┌────────────────────────────────────┐
│ [≡] Dashboard            [User] │
├──────┬─────────────────────────────┤
│      │                             │
│ Nav  │   Content Area              │
│ Bar  │                             │
│ (L)  │                             │
│      │                             │
└──────┴─────────────────────────────┘

AFTER (RTL):
┌────────────────────────────────────┐
│ [User]          لوحة التحكم [≡] │
├─────────────────────────────┬──────┤
│                             │      │
│   Content Area              │ Nav  │
│                             │ Bar  │
│                             │ (R)  │
│                             │      │
└─────────────────────────────┴──────┘
```

### Mobile View

```
BEFORE (LTR):
Sidebar slides from left ←

AFTER (RTL):
Sidebar slides from right →
```

## Summary of Changes

### Structure
- ✅ Sidebar: Left → Right
- ✅ Icons: mr-3 → ml-3
- ✅ Padding: pl-64 → pr-64
- ✅ Text alignment: Default right
- ✅ Flex direction: Auto-reversed

### Content
- ✅ All text: English → Arabic
- ✅ Numbers: Western → Arabic-Indic
- ✅ Currency: $ → ج.م (EGP)
- ✅ Dates: en-US → ar-EG format
- ✅ Phone: Raw → Egyptian format

### Typography
- ✅ Font: System → Cairo
- ✅ Direction: LTR → RTL
- ✅ Language: en → ar

### Data
- ✅ API: Unchanged (English)
- ✅ Database: Unchanged (English)
- ✅ Display: Translated (Arabic)
- ✅ Enums: Frontend translation only
