import { memo } from 'react';
import { Search, X } from 'lucide-react';

interface TimelineSearchProps {
  value: string;
  onChange: (value: string) => void;
}

function TimelineSearch({ value, onChange }: TimelineSearchProps) {
  return (
    <div className="relative">
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <Search className="w-4 h-4 text-gray-400" />
      </div>
      
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="ابحث في السجل... (الوصف، الحدث، التاريخ)"
        className="w-full pr-10 pl-10 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        dir="rtl"
      />
      
      {value && (
        <button
          onClick={() => onChange('')}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

export default memo(TimelineSearch);
