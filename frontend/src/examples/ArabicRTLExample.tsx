/**
 * Example component demonstrating Arabic RTL features
 * This file shows how to use translation, formatting, and RTL layout
 */

import { useTranslation, translateQuotationStatus, translatePaymentMethod } from '../i18n';
import { formatCurrency, formatDate, formatNumber, formatPhoneNumber } from '../utils';

// Example data (as it comes from the API)
const exampleCustomer = {
  id: '123',
  full_name: 'Ahmed Mohamed',
  phone_number: '01012345678',
  city: 'Cairo',
  created_at: '2026-01-15T10:30:00Z',
};

const exampleQuotation = {
  id: '456',
  quotation_number: 'Q-2026-001',
  customer_id: '123',
  status: 'draft', // English value from API
  total_price: '15750.50',
  discount: '750.50',
  final_price: '15000.00',
  quotation_date: '2026-01-15',
};

const examplePayment = {
  id: '789',
  amount: '5000.00',
  payment_date: '2026-01-16T14:20:00Z',
  payment_method: 'cash', // English value from API
};

export default function ArabicRTLExample() {
  const { t } = useTranslation();

  return (
    <div className="space-y-8 p-6">
      {/* Page Header with Translation */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <p className="mt-2 text-gray-600">{t('dashboard.subtitle')}</p>
      </div>

      {/* Customer Information Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">{t('customers.customerDetails')}</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">{t('customers.fullName')}:</span>
            <span className="font-medium">{exampleCustomer.full_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('customers.phoneNumber')}:</span>
            <span className="font-medium">{formatPhoneNumber(exampleCustomer.phone_number)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('customers.city')}:</span>
            <span className="font-medium">{exampleCustomer.city}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('customers.createdAt')}:</span>
            <span className="font-medium">{formatDate(exampleCustomer.created_at, 'long')}</span>
          </div>
        </div>
      </div>

      {/* Quotation Card with Enum Translation */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">{t('quotations.quotationDetails')}</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">{t('quotations.quotationNumber')}:</span>
            <span className="font-medium">{exampleQuotation.quotation_number}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('quotations.quotationDate')}:</span>
            <span className="font-medium">{formatDate(exampleQuotation.quotation_date)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('quotations.status')}:</span>
            {/* Translate enum value from English to Arabic */}
            <span className="font-medium bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
              {translateQuotationStatus(exampleQuotation.status)}
            </span>
          </div>
          <div className="border-t pt-3 mt-3">
            <div className="flex justify-between mb-2">
              <span className="text-gray-600">{t('quotations.totalPrice')}:</span>
              <span className="font-medium">{formatCurrency(exampleQuotation.total_price)}</span>
            </div>
            <div className="flex justify-between mb-2">
              <span className="text-gray-600">{t('quotations.discount')}:</span>
              <span className="font-medium text-red-600">- {formatCurrency(exampleQuotation.discount)}</span>
            </div>
            <div className="flex justify-between text-lg font-bold">
              <span className="text-gray-900">{t('quotations.finalPrice')}:</span>
              <span className="text-green-600">{formatCurrency(exampleQuotation.final_price)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">{t('payments.title')}</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">{t('payments.amount')}:</span>
            <span className="font-medium text-green-600">{formatCurrency(examplePayment.amount)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('payments.paymentDate')}:</span>
            <span className="font-medium">{formatDate(examplePayment.payment_date, 'long')}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">{t('payments.paymentMethod')}:</span>
            {/* Translate payment method from English to Arabic */}
            <span className="font-medium">{translatePaymentMethod(examplePayment.payment_method)}</span>
          </div>
        </div>
      </div>

      {/* Number Formatting Examples */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">أمثلة التنسيق (Formatting Examples)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded p-4">
            <p className="text-sm text-gray-600 mb-2">عدد كبير:</p>
            <p className="text-lg font-medium">{formatNumber(1234567.89)}</p>
          </div>
          <div className="border rounded p-4">
            <p className="text-sm text-gray-600 mb-2">مبلغ مالي:</p>
            <p className="text-lg font-medium">{formatCurrency(99999.99)}</p>
          </div>
          <div className="border rounded p-4">
            <p className="text-sm text-gray-600 mb-2">تاريخ قصير:</p>
            <p className="text-lg font-medium">{formatDate('2026-07-20')}</p>
          </div>
          <div className="border rounded p-4">
            <p className="text-sm text-gray-600 mb-2">تاريخ طويل:</p>
            <p className="text-lg font-medium">{formatDate('2026-07-20', 'long')}</p>
          </div>
        </div>
      </div>

      {/* RTL Table Example */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">جدول العملاء (Customer Table)</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('customers.fullName')}
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('customers.phoneNumber')}
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('customers.city')}
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('common.actions')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                Ahmed Mohamed
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatPhoneNumber('01012345678')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">القاهرة</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <button className="text-blue-600 hover:text-blue-800 ml-3">
                  {t('common.edit')}
                </button>
                <button className="text-red-600 hover:text-red-800">
                  {t('common.delete')}
                </button>
              </td>
            </tr>
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                Fatima Ali
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatPhoneNumber('01198765432')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">الإسكندرية</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <button className="text-blue-600 hover:text-blue-800 ml-3">
                  {t('common.edit')}
                </button>
                <button className="text-red-600 hover:text-red-800">
                  {t('common.delete')}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* RTL Form Example */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">نموذج إضافة عميل (Add Customer Form)</h2>
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('customers.fullName')}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="أدخل الاسم الكامل"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('customers.phoneNumber')}
            </label>
            <input
              type="tel"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="01012345678"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('customers.city')}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="أدخل المدينة"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('customers.address')}
            </label>
            <textarea
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="أدخل العنوان"
            />
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              {t('common.save')}
            </button>
            <button
              type="button"
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
            >
              {t('common.cancel')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
