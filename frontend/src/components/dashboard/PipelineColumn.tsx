import { useTranslation } from '../../i18n/useTranslation';
import type { JobPipelineCard as JobCard } from '../../types/dashboard';
import JobPipelineCard from './JobPipelineCard';

interface PipelineColumnProps {
  title: string;
  count: number;
  color: string;
  jobs: JobCard[];
}

export default function PipelineColumn({ title, count, color, jobs }: PipelineColumnProps) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col h-full">
      {/* Column Header - Fixed Height */}
      <div className={`${color} text-white px-4 py-3 rounded-t-lg`}>
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm truncate flex-1">{title}</h3>
          <span className="bg-white bg-opacity-30 px-2 py-1 rounded-full text-xs font-medium mr-2">
            {count}
          </span>
        </div>
      </div>

      {/* Column Content - Consistent Sizing */}
      <div className="flex-1 bg-gray-50 p-3 rounded-b-lg space-y-3 overflow-y-auto min-h-[400px] max-h-[600px]">
        {jobs.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-8">
            {t('dashboard.pipeline.noJobs')}
          </div>
        ) : (
          jobs.map((job) => <JobPipelineCard key={job.job_id} data={job} />)
        )}
      </div>
    </div>
  );
}
