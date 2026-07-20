# Quick Reference: Arabic RTL Development

## Import Statements

```tsx
// Translation
import { useTranslation, translateQuotationStatus, translateJobStatus, translatePaymentMethod } from '../i18n';

// Formatters
import { formatCurrency, formatDate, formatDateTime, formatNumber, formatPhoneNumber } from '../utils';
```

## Translation

```tsx
const { t } = useTranslation();

// Use in JSX
<h1>{t('dashboard.title')}</h1>
<p>{t('customers.fullName')}</p>

// Enum translation
<span>{translateQuotationStatus('draft')}</span>  // "مسودة"
<span>{translateJobStatus('in_progress')}</span>  // "قيد التنفيذ"
<span>{translatePaymentMethod('cash')}</span>     // "نقدي"
```

## Formatting

```tsx
// Currency (EGP)
formatCurrency(1500)              // "١٬٥٠٠٫٠٠ ج.م"
formatCurrency("1500.50")         // "١٬٥٠٠٫٥٠ ج.م"

// Numbers
formatNumber(1234567.89)          // "١٬٢٣٤٬٥٦٧٫٨٩"

// Dates
formatDate("2026-01-15")          // "١٥‏/٠١‏/٢٠٢٦"
formatDate("2026-01-15", "long")  // "١٥ يناير ٢٠٢٦"
formatDate("2026-01-15", "full")  // "الاثنين، ١٥ يناير ٢٠٢٦"

// Date & Time
formatDateTime("2026-01-15T14:30:00Z")  // "١٥‏/٠١‏/٢٠٢٦ ١٤:٣٠"

// Phone
formatPhoneNumber("01012345678")  // "0101 234 5678"
```

## RTL Layout Tips

### Icon Spacing
```tsx
// ❌ Wrong (LTR)
<Icon className="mr-3" />

// ✅ Correct (RTL)
<Icon className="ml-3" />
```

### Flex Layout
```tsx
// Flex automatically reverses in RTL
<div className="flex items-center justify-between">
  <span>Label</span>
  <span>Value</span>
</div>
```

### Text Alignment
```tsx
// Text naturally aligns right in RTL
<p className="text-gray-600">النص العربي</p>

// Force left alignment if needed
<p className="text-left">English text</p>
```

### Tables
```tsx
<th className="px-6 py-3 text-right">  {/* text-right for RTL */}
  {t('customers.fullName')}
</th>
```

### Positioning
```tsx
// Sidebar on right
<aside className="fixed right-0">

// Content padding on right
<main className="lg:pr-64">
```

## Common Translation Keys

### Navigation
- `nav.dashboard` → لوحة التحكم
- `nav.customers` → العملاء
- `nav.products` → المنتجات
- `nav.quotations` → عروض الأسعار
- `nav.jobs` → الأعمال
- `nav.payments` → المدفوعات

### Common Actions
- `common.add` → إضافة
- `common.edit` → تعديل
- `common.delete` → حذف
- `common.save` → حفظ
- `common.cancel` → إلغاء
- `common.search` → بحث
- `common.filter` → تصفية

### Status Messages
- `common.loading` → جاري التحميل...
- `common.error` → خطأ
- `common.success` → نجح

### Customer Fields
- `customers.fullName` → الاسم الكامل
- `customers.phoneNumber` → رقم الهاتف
- `customers.city` → المدينة
- `customers.address` → العنوان

### Quotation Fields
- `quotations.quotationNumber` → رقم عرض السعر
- `quotations.customer` → العميل
- `quotations.status` → الحالة
- `quotations.totalPrice` → السعر الإجمالي
- `quotations.discount` → الخصم
- `quotations.finalPrice` → السعر النهائي

## Status Badge Example

```tsx
// Quotation status with color
const getStatusColor = (status: string) => {
  const colors = {
    draft: 'bg-yellow-100 text-yellow-800',
    sent: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

<span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(status)}`}>
  {translateQuotationStatus(status)}
</span>
```

## Form Example

```tsx
<form className="space-y-4">
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">
      {t('customers.fullName')}
    </label>
    <input
      type="text"
      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
      placeholder="أدخل الاسم الكامل"
    />
  </div>
  
  <div className="flex gap-3">
    <button type="submit" className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg">
      {t('common.save')}
    </button>
    <button type="button" className="flex-1 bg-gray-200 px-4 py-2 rounded-lg">
      {t('common.cancel')}
    </button>
  </div>
</form>
```

## Table Example

```tsx
<table className="min-w-full">
  <thead className="bg-gray-50">
    <tr>
      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
        {t('customers.fullName')}
      </th>
      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
        {t('customers.phoneNumber')}
      </th>
    </tr>
  </thead>
  <tbody className="bg-white divide-y divide-gray-200">
    {customers.map(customer => (
      <tr key={customer.id} className="hover:bg-gray-50">
        <td className="px-6 py-4 text-sm">{customer.full_name}</td>
        <td className="px-6 py-4 text-sm">{formatPhoneNumber(customer.phone_number)}</td>
      </tr>
    ))}
  </tbody>
</table>
```

## API Integration Pattern

```tsx
// API returns English values
const fetchQuotation = async (id: string) => {
  const response = await api.get(`/quotations/${id}`);
  return response.data;  // { status: "draft", ... }
};

// Display with Arabic translation
function QuotationCard({ data }) {
  return (
    <div>
      <p>{t('quotations.status')}: {translateQuotationStatus(data.status)}</p>
      <p>{t('quotations.totalPrice')}: {formatCurrency(data.total_price)}</p>
      <p>{t('quotations.quotationDate')}: {formatDate(data.quotation_date)}</p>
    </div>
  );
}
```

## Remember

1. **API stays English** - only translate in the UI
2. **Use `ml-` instead of `mr-`** for icon/element spacing
3. **Use formatters** for all numbers, dates, and currency
4. **Translate enums** using helper functions
5. **Test RTL** for all new components
6. **Cairo font** is automatically applied
7. **Tables** need `text-right` in headers/cells
8. **Forms** work naturally in RTL

## Development Server

```bash
cd frontend
npm run dev
# Opens at http://localhost:3000/
```

## File Locations

- Translations: `src/i18n/translations.ts`
- Formatters: `src/utils/formatters.ts`
- Example: `src/examples/ArabicRTLExample.tsx`
- Full Guide: `ARABIC_RTL_IMPLEMENTATION.md`
