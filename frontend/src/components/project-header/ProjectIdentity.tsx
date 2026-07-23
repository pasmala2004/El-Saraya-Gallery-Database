import { memo } from 'react';
import { FileText, Briefcase } from 'lucide-react';

interface ProjectIdentityProps {
  quotationNumber: string;
  jobId?: string;
}

function ProjectIdentity({ quotationNumber, jobId }: ProjectIdentityProps) {
  return (
    <div className="flex items-center gap-4 flex-wrap">
      {/* Quotation Number */}
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-blue-600" />
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">عرض السعر</span>
          <span className="font-semibold text-gray-900">{quotationNumber}</span>
        </div>
      </div>

      {/* Job/Project ID (if exists) */}
      {jobId && (
        <>
          <div className="h-6 w-px bg-gray-300" />
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-green-600" />
            <div className="flex flex-col">
              <span className="text-xs text-gray-500">رقم المشروع</span>
              <span className="font-semibold text-gray-900">#{jobId.substring(0, 8)}</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default memo(ProjectIdentity);
