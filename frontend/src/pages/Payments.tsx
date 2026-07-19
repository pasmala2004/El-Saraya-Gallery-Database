export default function Payments() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
        <p className="mt-1 text-sm text-gray-600">Track customer payments and transactions</p>
      </div>

      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Payments Module</h3>
          <p className="text-gray-600 mb-6">
            The Payments module will track all customer payments, payment methods, and
            outstanding balances. Link payments to quotations and jobs.
          </p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-left">
            <p className="font-medium text-green-900 mb-2">Coming Soon:</p>
            <ul className="space-y-1 text-green-700">
              <li>• Record payments</li>
              <li>• Multiple payment methods</li>
              <li>• Link to quotations/jobs</li>
              <li>• Payment history</li>
              <li>• Outstanding balances</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
