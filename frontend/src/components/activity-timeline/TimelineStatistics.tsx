import { memo, useMemo } from 'react';
import { Activity, Clock, Calendar, Zap } from 'lucide-react';
import type { ActivityLog } from '../../types';
import { formatDate } from '../../utils/formatters';

interface TimelineStatisticsProps {
  events: ActivityLog[];
  projectCreatedAt: string;
}

function TimelineStatistics({ events, projectCreatedAt }: TimelineStatisticsProps) {
  const stats = useMemo(() => {
    const totalEvents = events.length;
    
    // Last activity
    const lastActivity = events.length > 0 
      ? events.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0]
      : null;
    
    // Project age in days
    const projectAge = Math.floor(
      (new Date().getTime() - new Date(projectCreatedAt).getTime()) / (1000 * 60 * 60 * 24)
    );
    
    // Days since last activity
    const daysSinceLastActivity = lastActivity
      ? Math.floor((new Date().getTime() - new Date(lastActivity.created_at).getTime()) / (1000 * 60 * 60 * 24))
      : 0;

    return {
      totalEvents,
      lastActivity,
      projectAge,
      daysSinceLastActivity,
    };
  }, [events, projectCreatedAt]);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {/* Total Events */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="w-4 h-4 text-blue-600" />
          <span className="text-xs font-medium text-blue-700">إجمالي الأحداث</span>
        </div>
        <div className="text-2xl font-bold text-blue-900">
          {stats.totalEvents}
        </div>
      </div>

      {/* Last Activity */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 border border-green-200">
        <div className="flex items-center gap-2 mb-1">
          <Zap className="w-4 h-4 text-green-600" />
          <span className="text-xs font-medium text-green-700">آخر نشاط</span>
        </div>
        <div className="text-sm font-bold text-green-900">
          {stats.daysSinceLastActivity === 0 ? 'اليوم' : 
           stats.daysSinceLastActivity === 1 ? 'أمس' : 
           `منذ ${stats.daysSinceLastActivity} أيام`}
        </div>
      </div>

      {/* Project Age */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
        <div className="flex items-center gap-2 mb-1">
          <Calendar className="w-4 h-4 text-purple-600" />
          <span className="text-xs font-medium text-purple-700">عمر المشروع</span>
        </div>
        <div className="text-lg font-bold text-purple-900">
          {stats.projectAge} يوم
        </div>
      </div>

      {/* Last Updated */}
      <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-3 border border-orange-200">
        <div className="flex items-center gap-2 mb-1">
          <Clock className="w-4 h-4 text-orange-600" />
          <span className="text-xs font-medium text-orange-700">آخر تحديث</span>
        </div>
        <div className="text-xs font-bold text-orange-900">
          {stats.lastActivity ? formatDate(stats.lastActivity.created_at) : '-'}
        </div>
      </div>
    </div>
  );
}

export default memo(TimelineStatistics);
