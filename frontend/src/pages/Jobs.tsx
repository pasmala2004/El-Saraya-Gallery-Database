import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, RefreshCw } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import { jobsApi } from '../services/jobs';
import { quotationsApi } from '../services/quotations';
import { customersApi } from '../services/customers';
import { formatDate } from '../utils/formatters';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import Modal from '../components/Modal';
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell, EmptyState } from '../components/Table';
import LoadingSpinner from '../components/LoadingSpinner';
import JobStatusBadge from '../components/JobStatusBadge';
import type { Job, JobStatus } from '../types';

export default function Jobs() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedQuotationId, setSelectedQuotationId] = useState('');
  const [notes, setNotes] = useState('');

  // Fetch jobs with filters
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['jobs', statusFilter],
    queryFn: () => jobsApi.getAll({
      status: statusFilter || undefined,
      limit: 100,
      sort_by: 'created_at',
      sort_order: 'desc',
    }),
  });

  // Fetch approved quotations for job creation
  const { data: quotationsData } = useQuery({
    queryKey: ['quotations', 'approved'],
    queryFn: () => quotationsApi.getAll({
      status: 'approved',
      limit: 100,
    }),
    enabled: isCreateModalOpen,
  });

  // Fetch customers for display
  const { data: customersData } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.getAll({ limit: 1000 }),
  });

  // Fetch quotations for display
  const { data: allQuotationsData } = useQuery({
    queryKey: ['quotations', 'all'],
    queryFn: () => quotationsApi.getAll({ limit: 1000 }),
  });

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedQuotationId) return;

    try {
      await jobsApi.create({
        quotation_id: selectedQuotationId,
        notes: notes || undefined,
      });
      
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsCreateModalOpen(false);
      setSelectedQuotationId('');
      setNotes('');
    } catch (error) {
      console.error('Failed to create job:', error);
    }
  };

  const handleRowClick = (job: Job) => {
    navigate(`/jobs/${job.id}`);
  };

  const jobs = data?.items || [];
  const customers = customersData?.items || [];
  const quotations = allQuotationsData?.items || [];
  const approvedQuotations = quotationsData?.items || [];

  // Helper to get customer name
  const getCustomerName = (quotationId: string) => {
    const quotation = quotations.find(q => q.id === quotationId);
    if (!quotation) return '-';
    const customer = customers.find(c => c.id === quotation.customer_id);
    return customer?.full_name || '-';
  };

  // Helper to get quotation number
  const getQuotationNumber = (quotationId: string) => {
    const quotation = quotations.find(q => q.id === quotationId);
    return quotation?.quotation_number || '-';
  };

  // Filter jobs by search term
  const filteredJobs = jobs.filter(job => {
    if (!searchTerm) return true;
    const quotationNumber = getQuotationNumber(job.quotation_id);
    const customerName = getCustomerName(job.quotation_id);
    return (
      quotationNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customerName.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const jobStatuses: JobStatus[] = [
    'pending',
    'measuring',
    'in_production',
    'ready_for_installation',
    'installed',
    'completed',
    'cancelled',
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('jobs.title')}</h1>
          <p className="mt-1 text-sm text-gray-600">{t('jobs.subtitle')}</p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          {t('jobs.addJob')}
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('common.search')}
            </label>
            <div className="relative">
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder={t('jobs.searchJobs')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pr-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.status')}
            </label>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">{t('jobs.allStatuses')}</option>
              {jobStatuses.map(status => (
                <option key={status} value={status}>
                  {t(`jobStatus.${status}`)}
                </option>
              ))}
            </Select>
          </div>

          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={() => refetch()}
              className="flex items-center gap-2 w-full"
            >
              <RefreshCw className="w-4 h-4" />
              {t('common.refresh')}
            </Button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        ) : isError ? (
          <div className="p-8 text-center text-red-600">
            {t('errors.generic')}
          </div>
        ) : filteredJobs.length === 0 ? (
          <EmptyState
            title={t('jobs.noJobsFound')}
            description={t('jobs.addJob')}
          />
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeaderCell>{t('jobs.quotationNumber')}</TableHeaderCell>
                  <TableHeaderCell>{t('jobs.customer')}</TableHeaderCell>
                  <TableHeaderCell>{t('jobs.status')}</TableHeaderCell>
                  <TableHeaderCell>{t('jobs.measurementDate')}</TableHeaderCell>
                  <TableHeaderCell>{t('jobs.productionStart')}</TableHeaderCell>
                  <TableHeaderCell>{t('jobs.installationDate')}</TableHeaderCell>
                  <TableHeaderCell>{t('jobs.completionDate')}</TableHeaderCell>
                  <TableHeaderCell>{t('common.createdAt')}</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredJobs.map((job) => (
                  <TableRow
                    key={job.id}
                    onClick={() => handleRowClick(job)}
                    className="cursor-pointer hover:bg-gray-50"
                  >
                    <TableCell className="font-medium">
                      {getQuotationNumber(job.quotation_id)}
                    </TableCell>
                    <TableCell>{getCustomerName(job.quotation_id)}</TableCell>
                    <TableCell>
                      <JobStatusBadge status={job.status} />
                    </TableCell>
                    <TableCell>
                      {job.measurement_date ? formatDate(job.measurement_date) : '-'}
                    </TableCell>
                    <TableCell>
                      {job.production_start ? formatDate(job.production_start) : '-'}
                    </TableCell>
                    <TableCell>
                      {job.installation_date ? formatDate(job.installation_date) : '-'}
                    </TableCell>
                    <TableCell>
                      {job.completion_date ? formatDate(job.completion_date) : '-'}
                    </TableCell>
                    <TableCell>{formatDate(job.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Create Job Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title={t('jobs.addJob')}
      >
        <form onSubmit={handleCreateJob} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.selectQuotation')} *
            </label>
            <Select
              value={selectedQuotationId}
              onChange={(e) => setSelectedQuotationId(e.target.value)}
              required
            >
              <option value="">{t('jobs.selectQuotation')}</option>
              {approvedQuotations.map(quotation => {
                const customer = customers.find(c => c.id === quotation.customer_id);
                return (
                  <option key={quotation.id} value={quotation.id}>
                    {quotation.quotation_number} - {customer?.full_name || 'Unknown'}
                  </option>
                );
              })}
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.notes')}
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsCreateModalOpen(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button type="submit">
              {t('common.create')}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
