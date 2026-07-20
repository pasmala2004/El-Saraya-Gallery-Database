# Arabic RTL Implementation Guide

This document describes the complete Arabic localization and RTL (Right-to-Left) implementation for the Gallery ERP frontend.

## Overview

The frontend has been fully configured to provide an Arabic user experience with RTL layout, specifically tailored for Egyptian gallery assistants.

## Key Features

### 1. **Arabic Language**
- Default language is Arabic (ar)
- All visible UI text translated to Arabic
- Database values, API fields, and enum values remain in English
- Frontend-only translation of enum values

### 2. **RTL Layout**
- HTML configured with `dir="rtl"` and `lang="ar"`
- Sidebar positioned on the right
- Navigation and icons properly mirrored
- Tables, forms, modals support RTL
- Toast notifications positioned on top-left

### 3. **Cairo Font**
- Google Fonts integration
- Cairo font applied throughout the application
- Font weights: 300, 400, 500, 600, 700

### 4. **Egyptian Locale (ar-EG)**
- Date formatting: Arabic numerals with Egyptian format
- Number formatting: Arabic numerals with proper separators
- Currency formatting: Egyptian Pounds (EGP / ج.م)
- Time formatting: 24-hour format in Arabic

## File Structure

```
frontend/src/
├── i18n/
│   ├── translations.ts       # All Arabic translations
│   ├── useTranslation.ts     # Translation hook & enum helpers
│   └── index.ts              # Barrel export
├── utils/
│   ├── formatters.ts         # Date, number, currency formatters
│   └── index.ts              # Barrel export
├── components/
│   └── Layout.tsx            # RTL-aware navigation
├── pages/
│   ├── Dashboard.tsx         # Translated dashboard
│   ├── Customers.tsx         # Translated customers page
│   ├── Products.tsx          # Translated products page
│   ├── Quotations.tsx        # Translated quotations page
│   ├── Jobs.tsx              # Translated jobs page
│   └── Payments.tsx          # Translated payments page
├── index.css                 # RTL base styles
└── App.tsx                   # RTL toast configuration
```

## Usage Examples

### Translation Hook

```tsx
import { useTranslation } from '../i18n/useTranslation';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.subtitle')}</p>
    </div>
  );
}
```

### Enum Translation

```tsx
import { translateQuotationStatus, translateJobStatus, translatePaymentMethod } from '../i18n';

// Translate quotation status
const statusText = translateQuotationStatus('draft'); // "مسودة"

// Translate job status
const jobStatusText = translateJobStatus('in_progress'); // "قيد التنفيذ"

// Translate payment method
const methodText = translatePaymentMethod('cash'); // "نقدي"
```

### Formatters

```tsx
import { formatCurrency, formatDate, formatNumber, formatPhoneNumber } from '../utils';

// Currency formatting
formatCurrency(1500.50);  // "١٬٥٠٠٫٥٠ ج.م"

// Date formatting
formatDate('2026-01-15');  // "١٥‏/٠١‏/٢٠٢٦"
formatDate('2026-01-15', 'long');  // "١٥ يناير ٢٠٢٦"

// Number formatting
formatNumber(1234567.89);  // "١٬٢٣٤٬٥٦٧٫٨٩"

// Phone formatting
formatPhoneNumber('01012345678');  // "0101 234 5678"
```

## Translation Structure

### Available Translation Keys

#### Common
- `common.search`, `common.filter`, `common.add`, `common.edit`, `common.delete`
- `common.save`, `common.cancel`, `common.close`, `common.confirm`
- `common.loading`, `common.error`, `common.success`

#### Navigation
- `nav.dashboard`, `nav.customers`, `nav.products`, `nav.quotations`, `nav.jobs`, `nav.payments`

#### Dashboard
- `dashboard.title`, `dashboard.subtitle`
- `dashboard.totalCustomers`, `dashboard.totalQuotations`
- `dashboard.quickActions`, `dashboard.addCustomer`

#### Customers
- `customers.title`, `customers.subtitle`
- `customers.fullName`, `customers.phoneNumber`, `customers.city`, `customers.address`

#### Products
- `products.title`, `products.subtitle`
- `products.productName`, `products.category`, `products.description`

#### Quotations
- `quotations.title`, `quotations.subtitle`
- `quotations.quotationNumber`, `quotations.customer`, `quotations.status`
- `quotations.totalPrice`, `quotations.discount`, `quotations.finalPrice`

#### Jobs
- `jobs.title`, `jobs.subtitle`
- `jobs.jobNumber`, `jobs.startDate`, `jobs.endDate`, `jobs.status`

#### Payments
- `payments.title`, `payments.subtitle`
- `payments.amount`, `payments.paymentDate`, `payments.paymentMethod`

### Enum Translations

#### Quotation Status
- `draft` → مسودة
- `waiting_for_measurement` → في انتظار القياس
- `measured` → تم القياس
- `under_negotiation` → قيد التفاوض
- `sent` → مُرسل
- `approved` → موافق عليه
- `rejected` → مرفوض
- `cancelled` → ملغى
- `expired` → منتهي الصلاحية

#### Job Status
- `pending` → معلق
- `in_progress` → قيد التنفيذ
- `completed` → مكتمل
- `cancelled` → ملغى

#### Payment Method
- `cash` → نقدي
- `bank_transfer` → تحويل بنكي
- `check` → شيك
- `credit_card` → بطاقة ائتمان

## RTL Layout Specifics

### Sidebar
- Positioned on the **right** side (changed from left)
- Icons have margin-left instead of margin-right (`ml-3` instead of `mr-3`)
- Mobile slide-in from right (`translate-x-full` / `translate-x-0`)
- Border on left side (`border-l` instead of `border-r`)

### Main Content
- Padding on right side to accommodate sidebar (`lg:pr-64` instead of `lg:pl-64`)
- Header elements arranged right-to-left
- Menu button positioned on the right

### Component Adjustments
- Flex items naturally reverse in RTL
- Text alignment defaults to right
- Icon spacing adjusted (ml instead of mr)
- Lists bullets on the right side

## CSS Configuration

### Base Styles (index.css)
```css
body {
  font-family: 'Cairo', sans-serif;
  direction: rtl;
}

* {
  direction: rtl;
}

.ltr {
  direction: ltr;  /* For specific LTR elements if needed */
}
```

### Tailwind Configuration
```js
theme: {
  extend: {
    fontFamily: {
      sans: ['Cairo', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    },
  },
}
```

## API Integration Notes

### Important: No Backend Changes
- API requests and responses remain unchanged
- Database stores English values
- Field names remain in English
- Only the frontend displays Arabic translations

### Example API Response
```json
{
  "quotation_number": "Q-2026-001",
  "status": "draft",           // English in API
  "total_price": "1500.00"
}
```

### Frontend Display
```tsx
// Display with Arabic translation
<div>
  <span>{t('quotations.quotationNumber')}: {data.quotation_number}</span>
  <span>{t('quotations.status')}: {translateQuotationStatus(data.status)}</span>
  <span>{t('quotations.totalPrice')}: {formatCurrency(data.total_price)}</span>
</div>

// Output:
// رقم عرض السعر: Q-2026-001
// الحالة: مسودة
// السعر الإجمالي: ١٬٥٠٠٫٠٠ ج.م
```

## Browser Support

The implementation uses standard web APIs supported by all modern browsers:
- `Intl.NumberFormat` for number and currency formatting
- `Intl.DateTimeFormat` for date/time formatting
- CSS `dir="rtl"` for layout direction
- Google Fonts for Cairo font

## Testing Checklist

- [x] HTML has `dir="rtl"` and `lang="ar"`
- [x] Cairo font loads from Google Fonts
- [x] Sidebar appears on right side
- [x] Navigation items have correct spacing
- [x] All UI text displays in Arabic
- [x] Currency shows as Egyptian Pounds
- [x] Dates format with Arabic numerals
- [x] Numbers format with Arabic numerals
- [x] Toast notifications appear on top-left
- [x] Enum values translate correctly
- [x] API communication remains in English

## Future Enhancements

When adding new features:
1. Add translation keys to `translations.ts`
2. Use `useTranslation()` hook in components
3. Apply RTL-aware spacing (ml instead of mr)
4. Translate enum values using helper functions
5. Format dates/numbers using formatter utilities
6. Test RTL layout for tables, forms, and modals

## Support

For Egyptian locale specifics:
- **Currency**: EGP (ج.م - Egyptian Pound)
- **Date Format**: DD/MM/YYYY
- **Number Format**: Arabic-Indic numerals (٠-٩)
- **Phone Format**: Egyptian mobile format (0101 234 5678)
