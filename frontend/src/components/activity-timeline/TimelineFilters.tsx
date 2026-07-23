import { memo } from 'react';
import { Filter } from 'lucide-react';

interface TimelineFiltersProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
  eventCounts: Record<string, number>;
}

const FILTERS = [
  { id: 'all', label: 'الكل', color: 'text-gray-700' },
  { id: 'workflow', label: 'سير العمل', color: 'text-blue-700' },
  { id: 'payments', label: 'المدفوعات', color: 'text-green-700' },
  { id: 'measurements', label: 'القياسات', color: 'text-purple-700' },
  { id: 'quotation', label: 'عرض السعر', color: 'text-indigo-700' },
  { id: 'notes', label: 'الملاحظات', color: 'text-gray-700' },
  { id: 'documents', label: 'المستندات', color: 'text-orange-700' },
];

function TimelineFilters({ activeFilter, onFilterChange, eventCounts }: TimelineFiltersProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <Filter className="w-4 h-4" />
        <span className="font-medium">التصفية:</span>
      </div>
      
      {FILTERS.map(filter => {
        const count = eventCounts[filter.id] || 0;
        const isActive = activeFilter === filter.id;
        
        return (
          <button
            key={filter.id}
            onClick={() => onFilterChange(filter.id)}
            className={`
              inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-full
              transition-all border
              ${isActive 
                ? 'bg-blue-600 text-white border-blue-600 shadow-sm' 
                : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:bg-blue-50'
              }
            `}
          >
            <span className={isActive ? 'text-white' : filter.color}>
              {filter.label}
            </span>
            {count > 0 && (
              <span className={`
                inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs rounded-full
                ${isActive ? 'bg-white text-blue-600' : 'bg-gray-100 text-gray-600'}
              `}>
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default memo(TimelineFilters);
