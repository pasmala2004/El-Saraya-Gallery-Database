import { useQueries } from '@tanstack/react-query';
import { paymentsApi } from '../services/payments';
import type { Payment } from '../types';

export function useAllJobPayments(jobIds: string[]) {
  const queries = useQueries({
    queries: jobIds.map((jobId) => ({
      queryKey: ['payments', 'job', jobId],
      queryFn: () => paymentsApi.getJobPayments(jobId, { limit: 100 }),
      staleTime: 5 * 60 * 1000, // 5 minutes
    })),
  });

  const isLoading = queries.some(q => q.isLoading);
  
  // Create a map of jobId -> payments
  const paymentsMap = new Map<string, Payment[]>();
  
  jobIds.forEach((jobId, index) => {
    const data = queries[index]?.data;
    if (data?.items) {
      paymentsMap.set(jobId, data.items);
    } else {
      paymentsMap.set(jobId, []);
    }
  });

  return {
    paymentsMap,
    isLoading,
  };
}
