import { User, FileText, Check, Calendar, CreditCard, Briefcase, Package } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../../i18n/useTranslation';
import type { Activity } from '../../types/dashboard';

interface RecentActivityProps {
  activities: Activity[];
}

const activityIcons = {
  customer_created: User,
  quotation_created: FileText,
  quotation_approved: Check,
  measurement_completed: Calendar,
  payment_received: CreditCard,
  job_started: Briefcase,
  installation_completed: Package,
};

const activityColors = {
  customer_created: 'bg-gray-100 text-gray-600',
  quotation_created: 'bg-blue-100 text-blue-600',
  quotation_approved: 'bg-green-100 text-green-600',
  measurement_completed: 'bg-purple-100 text-purple-600',
  payment_received: 'bg-orange-100 text-orange-600',
  job_started: 'bg-indigo-100 text-indigo-600',
  installation_completed: 'bg-green-100 text-green-600',
};

export default function RecentActivity({ activities }: RecentActivityProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleActivityClick = (activity: Activity) => {
    // Navigate based on entity type
    if (activity.entity_type === 'job') {
      navigate(`/jobs/${activity.entity_id}`);
    } else if (activity.entity_type === 'quotation') {
      navigate(`/projects/${activity.entity_id}`);
    } else if (activity.entity_type === 'customer') {
      navigate(`/customers/${activity.entity_id}`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('dashboard.activity.title')}</h2>

      {activities.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <Briefcase className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>{t('dashboard.activity.noActivity')}</p>
        </div>
      ) : (
        <div className="flow-root">
          <ul className="-mb-8">
            {activities.map((activity, idx) => {
              const Icon = activityIcons[activity.type as keyof typeof activityIcons] || Briefcase;
              const colorClass = activityColors[activity.type as keyof typeof activityColors] || 'bg-gray-100 text-gray-600';
              const isLast = idx === activities.length - 1;

              return (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {!isLast && (
                      <span
                        className="absolute top-4 right-4 -mr-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    )}
                    <div
                      className="relative flex space-x-3 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors"
                      onClick={() => handleActivityClick(activity)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          handleActivityClick(activity);
                        }
                      }}
                    >
                      <div>
                        <span className={`${colorClass} h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white`}>
                          <Icon className="h-4 w-4" aria-hidden="true" />
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                        <div>
                          <p className="text-sm text-gray-900 font-medium">
                            {activity.description}
                          </p>
                          <p className="text-sm text-gray-500">{activity.customer_name}</p>
                        </div>
                        <div className="whitespace-nowrap text-left text-sm text-gray-500">
                          {activity.relative_time}
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
