import { memo } from 'react';
import { Activity, AlertCircle } from 'lucide-react';

interface TimelineEmptyStateProps {
  hasFilters: boolean;
  searchQuery: string;
  onClearFilters: () => void;
  daysSinceLastActivity?: number;
}

function TimelineEmptyState({ 
  hasFilters, 
  searchQuery, 
  onClearFilters,
  daysSinceLastActivity 
}: TimelineEmptyStateProps) {
  // Show warning if no activity for 7+ days
  if (daysSinceLastActivity !== undefined && daysSinceLastActivity >= 7) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <div className="flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 mb-4">
          <AlertCircle className="w-8 h-8 text-orange-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          ⚠️ لا يوجد نشاط منذ {daysSinceLastActivity} أيام
        </h3>
        <p className="text-sm text-gray-600 text-center max-w-md">
          لم يتم تسجيل أي نشاط على هذا المشروع منذ أكثر من أسبوع. يُنصح بمتابعة المشروع والتأكد من سير العمل.
        </p>
      </div>
    );
  }

  // Show search/filter empty state
  if (hasFilters || searchQuery) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
          <Activity className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          لا توجد نتائج
        </h3>
        <p className="text-sm text-gray-600 text-center mb-4">
          {searchQuery 
            ? `لم يتم العثور على أحداث تطابق "${searchQuery}"`
            : 'لم يتم العثور على أحداث بالفلتر المحدد'
          }
        </p>
        <button
          onClick={onClearFilters}
          className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
        >
          مسح الفلاتر
        </button>
      </div>
    );
  }

  // Show no events state (project just created)
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
        <Activity className="w-8 h-8 text-blue-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        بداية السجل
      </h3>
      <p className="text-sm text-gray-600 text-center max-w-md">
        لم يتم تسجيل أي أحداث بعد. سيتم تسجيل جميع الأنشطة والتغييرات تلقائياً هنا.
      </p>
    </div>
  );
}

export default memo(TimelineEmptyState);
