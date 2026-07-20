import { translations } from './translations';

// Simple translation hook for Arabic
export function useTranslation() {
  const t = (key: string, params?: Record<string, string>): string => {
    const keys = key.split('.');
    let value: any = translations;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        console.warn(`Translation key not found: ${key}`);
        return key;
      }
    }
    
    let result = typeof value === 'string' ? value : key;
    
    // Simple template substitution
    if (params) {
      Object.entries(params).forEach(([paramKey, paramValue]) => {
        result = result.replace(`{${paramKey}}`, paramValue);
      });
    }
    
    return result;
  };

  return { t };
}

// Helper functions for translating enums
export function translateQuotationStatus(status: string): string {
  const statusMap: Record<string, string> = {
    draft: 'مسودة',
    waiting_for_measurement: 'في انتظار القياس',
    measured: 'تم القياس',
    under_negotiation: 'قيد التفاوض',
    sent: 'مُرسل',
    approved: 'موافق عليه',
    rejected: 'مرفوض',
    cancelled: 'ملغى',
    expired: 'منتهي الصلاحية',
  };
  return statusMap[status] || status;
}

export function translateJobStatus(status: string): string {
  const statusMap: Record<string, string> = {
    pending: 'معلق',
    in_progress: 'قيد التنفيذ',
    completed: 'مكتمل',
    cancelled: 'ملغى',
  };
  return statusMap[status] || status;
}

export function translatePaymentMethod(method: string): string {
  const methodMap: Record<string, string> = {
    cash: 'نقدي',
    bank_transfer: 'تحويل بنكي',
    check: 'شيك',
    credit_card: 'بطاقة ائتمان',
  };
  return methodMap[method] || method;
}
