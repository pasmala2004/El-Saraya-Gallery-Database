import { memo } from 'react';
import { User, Phone, MapPin } from 'lucide-react';
import type { Customer } from '../../types';
import { formatPhoneNumber } from '../../utils/formatters';

interface CustomerSummaryProps {
  customer: Customer;
}

function CustomerSummary({ customer }: CustomerSummaryProps) {
  const handleCallClick = () => {
    window.location.href = `tel:${customer.phone_number}`;
  };

  const handleWhatsAppClick = () => {
    const cleanPhone = customer.phone_number.replace(/\D/g, '');
    const phone = cleanPhone.startsWith('0') ? `2${cleanPhone}` : cleanPhone;
    window.open(`https://wa.me/${phone}`, '_blank');
  };

  return (
    <div className="flex items-start gap-3">
      <div className="p-2.5 rounded-lg bg-blue-50">
        <User className="w-5 h-5 text-blue-600" />
      </div>
      
      <div className="flex-1 min-w-0">
        <h3 className="text-lg font-bold text-gray-900 mb-1 truncate">
          {customer.full_name}
        </h3>
        
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Phone className="w-3.5 h-3.5 flex-shrink-0" />
            <button
              onClick={handleCallClick}
              className="hover:text-blue-600 transition-colors font-medium"
              dir="ltr"
            >
              {formatPhoneNumber(customer.phone_number)}
            </button>
            <button
              onClick={handleWhatsAppClick}
              className="text-xs text-green-600 hover:text-green-700 font-medium px-2 py-0.5 bg-green-50 rounded-full transition-colors"
            >
              واتساب
            </button>
          </div>
          
          {customer.address && (
            <div className="flex items-start gap-2 text-sm text-gray-600">
              <MapPin className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
              <span className="line-clamp-2">{customer.address}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default memo(CustomerSummary);
