import { useState } from 'react';
import type { ReactNode } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface CollapsibleSectionProps {
  title: string;
  defaultOpen?: boolean;
  children: ReactNode;
  headerActions?: ReactNode;
  badge?: ReactNode;
}

export default function CollapsibleSection({
  title,
  defaultOpen = true,
  children,
  headerActions,
  badge,
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-3 flex-1 text-right hover:text-blue-600 transition-colors"
        >
          <div className="flex items-center gap-2">
            {badge}
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          </div>
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {headerActions && (
          <div className="mr-4" onClick={(e) => e.stopPropagation()}>
            {headerActions}
          </div>
        )}
      </div>

      {/* Content */}
      {isOpen && <div className="p-4">{children}</div>}
    </div>
  );
}
