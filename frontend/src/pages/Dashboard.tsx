import { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import { dashboardApi } from '../services/dashboard';
import type { DashboardData } from '../types/dashboard';
import LoadingSpinner from '../components/LoadingSpinner';
import KPIGrid from '../components/dashboard/KPIGrid';
import PipelineBoard from '../components/dashboard/PipelineBoard';
import AlertsPanel from '../components/dashboard/AlertsPanel';
import RecentActivity from '../components/dashboard/RecentActivity';
import QuotationsWaitingPanel from '../components/dashboard/QuotationsWaitingPanel';

export default function Dashboard() {
  const { t } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboard = async (isManualRefresh = false) => {
    try {
      if (isManualRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError(null);

      const dashboardData = await dashboardApi.getDashboard();
      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('dashboard.errorLoadingData'));
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboard();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchDashboard(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => fetchDashboard()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {t('dashboard.retry')}
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
          <p className="mt-1 text-sm text-gray-600">{t('dashboard.subtitle')}</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? t('dashboard.refreshing') : t('common.refresh')}
        </button>
      </div>

      {/* KPI Cards */}
      <KPIGrid kpis={data.kpis} />

      {/* Quotations Waiting for Job Creation */}
      <QuotationsWaitingPanel />

      {/* Pipeline Board */}
      <PipelineBoard pipeline={data.pipeline} />

      {/* Alerts and Activity in Two Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertsPanel alerts={data.alerts} />
        <RecentActivity activities={data.recentActivity} />
      </div>

      {/* Metadata Footer */}
      <div className="text-xs text-gray-500 text-center py-2">
        {t('dashboard.lastUpdated')}: {new Date(data.metadata.generated_at).toLocaleString()} 
        {' '}({data.metadata.execution_time_ms}ms)
      </div>
    </div>
  );
}
