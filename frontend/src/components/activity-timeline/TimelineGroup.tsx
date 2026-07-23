import { memo } from 'react';
import type { ReactNode } from 'react';

interface TimelineGroupProps {
  title: string;
  children: ReactNode;
}

function TimelineGroup({ title, children }: TimelineGroupProps) {
  return (
    <div className="space-y-3">
      {/* Group Header */}
      <div className="flex items-center gap-3">
        <h3 className="text-sm font-bold text-gray-900">{title}</h3>
        <div className="flex-1 h-px bg-gray-300" />
      </div>
      
      {/* Group Content */}
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );
}

export default memo(TimelineGroup);
