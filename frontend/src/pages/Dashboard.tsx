import { Users, FileText, Briefcase, CreditCard } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';

export default function Dashboard() {
  const { t } = useTranslation();

  const stats = [
    {
      name: t('dashboard.totalCustomers'),
      value: 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      name: t('dashboard.totalQuotations'),
      value: 0,
      icon: FileText,
      color: 'bg-green-500',
    },
    {
      name: t('dashboard.draftQuotations'),
      value: 0,
      icon: FileText,
      color: 'bg-yellow-500',
    },
    {
      name: t('dashboard.sentQuotations'),
      value: 0,
      icon: Briefcase,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <p className="mt-1 text-sm text-gray-600">
          {t('dashboard.subtitle')}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('dashboard.quickActions')}</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <a
            href="/customers"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <Users className="w-6 h-6 text-blue-600 ml-3" />
            <div>
              <p className="font-medium text-gray-900">{t('dashboard.addCustomer')}</p>
              <p className="text-sm text-gray-500">{t('dashboard.createNewCustomer')}</p>
            </div>
          </a>

          <a
            href="/quotations"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all"
          >
            <FileText className="w-6 h-6 text-green-600 ml-3" />
            <div>
              <p className="font-medium text-gray-900">{t('dashboard.newQuotation')}</p>
              <p className="text-sm text-gray-500">{t('dashboard.createQuotation')}</p>
            </div>
          </a>

          <a
            href="/jobs"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all"
          >
            <Briefcase className="w-6 h-6 text-purple-600 ml-3" />
            <div>
              <p className="font-medium text-gray-900">{t('dashboard.viewJobs')}</p>
              <p className="text-sm text-gray-500">{t('dashboard.manageActiveJobs')}</p>
            </div>
          </a>

          <a
            href="/payments"
            className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-orange-500 hover:bg-orange-50 transition-all"
          >
            <CreditCard className="w-6 h-6 text-orange-600 ml-3" />
            <div>
              <p className="font-medium text-gray-900">{t('dashboard.recordPayment')}</p>
              <p className="text-sm text-gray-500">{t('dashboard.addNewPayment')}</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
