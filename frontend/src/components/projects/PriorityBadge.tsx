import { memo } from 'react';
import { AlertCircle, Circle } from 'lucide-react';

interface PriorityBadgeProps {
  priority: 'high' | 'medium' | 'low';
  label: string;
  size?: 'sm' | 'md';
}

const priorityConfig = {
  high: {
    color: 'bg-red-100 text-red-800 border-red-300',
    icon: AlertCircle,
  },
  medium: {
    color: 'bg-orange-100 text-orange-800 border-orange-300',
    icon: Circle,
  },
  low: {
    color: 'bg-green-100 text-green-800 border-green-300',
    icon: Circle,
  },
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
};

const iconSizes = {
  sm: 'w-3 h-3',
  md: 'w-3.5 h-3.5',
};

function PriorityBadge({ priority, label, size = 'md' }: PriorityBadgeProps) {
  const { color, icon: Icon } = priorityConfig[priority];
  const sizeClass = sizeClasses[size];
  const iconSize = iconSizes[size];

  return (
    <span
      className={`inline-flex items-center gap-1 justify-center rounded-full font-medium border ${color} ${sizeClass}`}
    >
      <Icon className={iconSize} />
      {label}
    </span>
  );
}

export default memo(PriorityBadge);
