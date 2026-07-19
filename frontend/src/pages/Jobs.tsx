export default function Jobs() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
        <p className="mt-1 text-sm text-gray-600">Manage active and completed jobs</p>
      </div>

      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Jobs Module</h3>
          <p className="text-gray-600 mb-6">
            The Jobs module will display all active jobs, their status, and allow you to manage
            job progress. Jobs are created from approved quotations.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-left">
            <p className="font-medium text-blue-900 mb-2">Coming Soon:</p>
            <ul className="space-y-1 text-blue-700">
              <li>• View all jobs</li>
              <li>• Update job status</li>
              <li>• Track job progress</li>
              <li>• Link to quotations</li>
              <li>• Job completion workflow</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
