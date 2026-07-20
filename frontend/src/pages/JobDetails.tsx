import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { ArrowLeft, Edit, Plus, Calendar, Package, Wrench, Truck, CheckCircle, DollarSign, Check } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import { jobsApi } from '../services/jobs';
import { quotationsApi } from '../services/quotations';
import { customersApi } from '../services/customers';
import { measurementsApi } from '../services/measurements';
import { paymentsApi } from '../services/payments';
import { formatDate, formatDateTime, formatCurrency } from '../utils/formatters';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input from '../components/Input';
import Select from '../components/Select';
import LoadingSpinner from '../components/LoadingSpinner';
import JobStatusBadge from '../components/JobStatusBadge';
import PaymentStatusBadge from '../components/PaymentStatusBadge';
import ConfirmationDialog from '../components/ConfirmationDialog';
import type { Job, JobStatus, Measurement, Payment, PaymentType, PaymentMethod } from '../types';

export default function JobDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [isAddMeasurementModalOpen, setIsAddMeasurementModalOpen] = useState(false);
  const [isConfirmStatusChangeModalOpen, setIsConfirmStatusChangeModalOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    measurement_date: '',
    production_start: '',
    production_end: '',
    installation_date: '',
    delivery_date: '',
    notes: '',
  });

  const [newStatus, setNewStatus] = useState<JobStatus>('pending');
  
  const [measurementData, setMeasurementData] = useState({
    visit_date: '',
    measured_by: '',
    notes: '',
  });

  const [isAddPaymentModalOpen, setIsAddPaymentModalOpen] = useState(false);
  const [isEditPaymentModalOpen, setIsEditPaymentModalOpen] = useState(false);
  const [isConfirmStatusModalOpen, setIsConfirmStatusModalOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  
  const [paymentData, setPaymentData] = useState({
    payment_type: 'deposit' as PaymentType,
    payment_method: 'cash' as PaymentMethod,
    percentage: '',
    amount: '',
    due_date: '',
    paid_date: '',
    notes: '',
  });

  // Fetch job
  const { data: job, isLoading: isLoadingJob } = useQuery({
    queryKey: ['jobs', id],
    queryFn: () => jobsApi.getById(id!),
    enabled: !!id,
  });

  // Fetch quotation
  const { data: quotation } = useQuery({
    queryKey: ['quotations', job?.quotation_id],
    queryFn: () => quotationsApi.getById(job!.quotation_id),
    enabled: !!job?.quotation_id,
  });

  // Fetch customer
  const { data: customer } = useQuery({
    queryKey: ['customers', quotation?.customer_id],
    queryFn: () => customersApi.getById(quotation!.customer_id),
    enabled: !!quotation?.customer_id,
  });

  // Fetch measurements
  const { data: measurementsData } = useQuery({
    queryKey: ['measurements', id],
    queryFn: () => measurementsApi.getJobMeasurements(id!, { sort_order: 'desc' }),
    enabled: !!id,
  });

  // Fetch payments
  const { data: paymentsData } = useQuery({
    queryKey: ['payments', id],
    queryFn: () => paymentsApi.getJobPayments(id!, { sort_order: 'asc' }),
    enabled: !!id,
  });

  // Update job mutation
  const updateMutation = useMutation({
    mutationFn: (data: Partial<Job>) => jobsApi.update(id!, data),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['jobs', id] });
      setIsEditModalOpen(false);
    },
    onError: () => {
      toast.error(t('errors.generic'));
    },
  });

  // Update status mutation
  const statusMutation = useMutation({
    mutationFn: (status: JobStatus) => jobsApi.updateStatus(id!, status),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['jobs', id] });
      setIsStatusModalOpen(false);
    },
    onError: () => {
      toast.error(t('errors.generic'));
    },
  });

  // Create measurement mutation
  const createMeasurementMutation = useMutation({
    mutationFn: (data: typeof measurementData) => measurementsApi.create(id!, data),
    onSuccess: (newMeasurement) => {
      toast.success(t('success.created'));
      queryClient.invalidateQueries({ queryKey: ['measurements', id] });
      setIsAddMeasurementModalOpen(false);
      setMeasurementData({ visit_date: '', measured_by: '', notes: '' });
      navigate(`/jobs/${id}/measurements/${newMeasurement.id}`);
    },
    onError: () => {
      toast.error(t('errors.generic'));
    },
  });

  // Create payment mutation
  const createPaymentMutation = useMutation({
    mutationFn: (data: typeof paymentData) => paymentsApi.create(id!, data),
    onSuccess: () => {
      toast.success(t('success.created'));
      queryClient.invalidateQueries({ queryKey: ['payments', id] });
      setIsAddPaymentModalOpen(false);
      setPaymentData({
        payment_type: 'deposit',
        payment_method: 'cash',
        percentage: '',
        amount: '',
        due_date: '',
        paid_date: '',
        notes: '',
      });
    },
    onError: () => {
      toast.error(t('errors.generic'));
    },
  });

  // Update payment mutation
  const updatePaymentMutation = useMutation({
    mutationFn: ({ id: paymentId, data }: { id: string; data: Partial<Payment> }) =>
      paymentsApi.update(paymentId, data),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['payments', id] });
      setIsEditPaymentModalOpen(false);
      setSelectedPayment(null);
    },
    onError: () => {
      toast.error(t('errors.generic'));
    },
  });

  // Mark payment as paid mutation
  const markPaidMutation = useMutation({
    mutationFn: (paymentId: string) => paymentsApi.updateStatus(paymentId, 'paid'),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['payments', id] });
      setIsConfirmStatusModalOpen(false);
      setSelectedPayment(null);
    },
    onError: () => {
      toast.error(t('errors.generic'));
    },
  });

  const handleEditClick = () => {
    if (job) {
      setFormData({
        measurement_date: job.measurement_date || '',
        production_start: job.production_start || '',
        production_end: job.production_end || '',
        installation_date: job.installation_date || '',
        delivery_date: job.delivery_date || '',
        notes: job.notes || '',
      });
      setIsEditModalOpen(true);
    }
  };

  const handleStatusClick = () => {
    if (job) {
      setNewStatus(job.status);
      setIsStatusModalOpen(true);
    }
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  const handleStatusSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    statusMutation.mutate(newStatus);
  };

  const handleAddMeasurementSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMeasurementMutation.mutate(measurementData);
  };

  const handleMeasurementClick = (measurement: Measurement) => {
    navigate(`/jobs/${id}/measurements/${measurement.id}`);
  };

  const handleAddPaymentClick = () => {
    setPaymentData({
      payment_type: 'deposit',
      payment_method: 'cash',
      percentage: '',
      amount: '',
      due_date: '',
      paid_date: '',
      notes: '',
    });
    setIsAddPaymentModalOpen(true);
  };

  const handleEditPaymentClick = (payment: Payment) => {
    setSelectedPayment(payment);
    setPaymentData({
      payment_type: payment.payment_type,
      payment_method: payment.payment_method,
      percentage: payment.percentage,
      amount: payment.amount,
      due_date: payment.due_date || '',
      paid_date: payment.paid_date || '',
      notes: payment.notes || '',
    });
    setIsEditPaymentModalOpen(true);
  };

  const handleMarkPaidClick = (payment: Payment) => {
    setSelectedPayment(payment);
    setIsConfirmStatusModalOpen(true);
  };

  const handleAddPaymentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createPaymentMutation.mutate(paymentData);
  };

  const handleEditPaymentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedPayment) {
      updatePaymentMutation.mutate({
        id: selectedPayment.id,
        data: paymentData,
      });
    }
  };

  const handleConfirmMarkPaid = () => {
    if (selectedPayment) {
      markPaidMutation.mutate(selectedPayment.id);
    }
  };

  if (isLoadingJob) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">{t('errors.notFound')}</p>
      </div>
    );
  }

  const measurements = measurementsData?.items || [];
  const payments = paymentsData?.items || [];

  // Calculate payment summary
  const totalPaid = payments
    .filter(p => p.status === 'paid')
    .reduce((sum, p) => sum + parseFloat(p.amount), 0);
  
  const totalScheduled = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
  
  const remainingBalance = totalScheduled - totalPaid;
  
  const paidPercentage = totalScheduled > 0 ? (totalPaid / totalScheduled) * 100 : 0;

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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => navigate('/jobs')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('common.back')}
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t('jobs.jobDetails')}</h1>
            <p className="text-sm text-gray-600">
              {quotation?.quotation_number || '-'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleEditClick}
            className="flex items-center gap-2"
          >
            <Edit className="w-4 h-4" />
            {t('jobs.editJob')}
          </Button>
          <Button
            onClick={handleStatusClick}
            className="flex items-center gap-2"
          >
            {t('jobs.changeStatus')}
          </Button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Info Cards */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">{t('jobs.status')}</h2>
            <div className="flex items-center gap-4">
              <JobStatusBadge status={job.status} />
              <Button
                variant="outline"
                size="sm"
                onClick={handleStatusClick}
              >
                {t('jobs.changeStatus')}
              </Button>
            </div>
          </div>

          {/* Customer & Quotation Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">{t('jobs.customerInfo')}</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">{t('jobs.customer')}</span>
                <span className="font-medium">{customer?.full_name || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t('customers.phoneNumber')}</span>
                <span className="font-medium">{customer?.phone_number || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{t('customers.city')}</span>
                <span className="font-medium">{customer?.city || '-'}</span>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">{t('jobs.timeline')}</h2>
            <div className="space-y-4">
              <TimelineItem
                icon={Calendar}
                label={t('jobs.measurementDate')}
                value={job.measurement_date}
                variant="info"
              />
              <TimelineItem
                icon={Package}
                label={t('jobs.productionStart')}
                value={job.production_start}
                variant="warning"
              />
              <TimelineItem
                icon={Wrench}
                label={t('jobs.productionEnd')}
                value={job.production_end}
                variant="warning"
              />
              <TimelineItem
                icon={Truck}
                label={t('jobs.installationDate')}
                value={job.installation_date}
                variant="info"
              />
              <TimelineItem
                icon={CheckCircle}
                label={t('jobs.completionDate')}
                value={job.completion_date}
                variant="success"
              />
            </div>
          </div>

          {/* Notes */}
          {job.notes && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">{t('jobs.notes')}</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{job.notes}</p>
            </div>
          )}
        </div>

        {/* Right Column - Measurements and Payments */}
        <div className="space-y-6">
          {/* Measurements Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">{t('jobs.measurements')}</h2>
              <Button
                size="sm"
                onClick={() => setIsAddMeasurementModalOpen(true)}
                className="flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                {t('jobs.addMeasurement')}
              </Button>
            </div>

            {measurements.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">{t('jobs.noMeasurements')}</p>
                <Button
                  size="sm"
                  onClick={() => setIsAddMeasurementModalOpen(true)}
                >
                  {t('jobs.addFirstMeasurement')}
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {measurements.map((measurement) => (
                  <div
                    key={measurement.id}
                    onClick={() => handleMeasurementClick(measurement)}
                    className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-semibold text-blue-600">
                        {t('measurements.measurement')} #{measurement.measurement_number}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(measurement.created_at)}
                      </span>
                    </div>
                    {measurement.visit_date && (
                      <div className="text-sm text-gray-600">
                        {t('measurements.visitDate')}: {formatDate(measurement.visit_date)}
                      </div>
                    )}
                    {measurement.measured_by && (
                      <div className="text-sm text-gray-600">
                        {t('measurements.measuredBy')}: {measurement.measured_by}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Payments Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">{t('payments.jobPayments')}</h2>
              <Button
                size="sm"
                onClick={handleAddPaymentClick}
                className="flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                {t('payments.addPayment')}
              </Button>
            </div>

            {/* Payment Summary */}
            {payments.length > 0 && (
              <div className="grid grid-cols-2 gap-3 mb-4 pb-4 border-b border-gray-200">
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-xs text-green-600 mb-1">{t('payments.totalPaid')}</div>
                  <div className="text-lg font-bold text-green-700">{formatCurrency(totalPaid)}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">{t('payments.remainingBalance')}</div>
                  <div className="text-lg font-bold text-gray-700">{formatCurrency(remainingBalance)}</div>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg col-span-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-blue-600">{t('payments.paidPercentage')}</span>
                    <span className="text-sm font-bold text-blue-700">{paidPercentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(paidPercentage, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Payment List */}
            {payments.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">{t('payments.noPayments')}</p>
                <Button
                  size="sm"
                  onClick={handleAddPaymentClick}
                >
                  {t('payments.addFirstPayment')}
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {payments.map((payment) => {
                  const isOverdue = payment.status === 'pending' && payment.due_date && 
                    new Date(payment.due_date) < new Date();
                  
                  return (
                    <div
                      key={payment.id}
                      className={`border rounded-lg p-4 ${isOverdue ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="font-semibold text-gray-900">
                            {t('payments.installment')} #{payment.payment_order}
                          </span>
                          <span className="text-sm text-gray-600 mr-2">
                            ({t(`paymentType.${payment.payment_type}`)})
                          </span>
                        </div>
                        <PaymentStatusBadge status={payment.status} />
                      </div>
                      
                      <div className="space-y-1 text-sm mb-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600">{t('payments.amount')}:</span>
                          <span className="font-semibold">{formatCurrency(parseFloat(payment.amount))}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">{t('payments.percentage')}:</span>
                          <span>{payment.percentage}%</span>
                        </div>
                        {payment.due_date && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">{t('payments.dueDate')}:</span>
                            <span className={isOverdue ? 'text-red-600 font-semibold' : ''}>
                              {formatDate(payment.due_date)}
                            </span>
                          </div>
                        )}
                        {payment.paid_date && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">{t('payments.paidDate')}:</span>
                            <span className="text-green-600">{formatDate(payment.paid_date)}</span>
                          </div>
                        )}
                      </div>

                      <div className="flex gap-2">
                        {payment.status === 'pending' && (
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handleMarkPaidClick(payment)}
                            className="flex items-center gap-1 flex-1"
                          >
                            <Check className="w-3 h-3" />
                            {t('payments.markAsPaid')}
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditPaymentClick(payment)}
                          className="flex items-center gap-1 flex-1"
                        >
                          <Edit className="w-3 h-3" />
                          {t('common.edit')}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Edit Job Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title={t('jobs.editJob')}
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.measurementDate')}
            </label>
            <Input
              type="date"
              value={formData.measurement_date}
              onChange={(e) => setFormData(prev => ({ ...prev, measurement_date: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.productionStart')}
            </label>
            <Input
              type="date"
              value={formData.production_start}
              onChange={(e) => setFormData(prev => ({ ...prev, production_start: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.productionEnd')}
            </label>
            <Input
              type="date"
              value={formData.production_end}
              onChange={(e) => setFormData(prev => ({ ...prev, production_end: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.installationDate')}
            </label>
            <Input
              type="date"
              value={formData.installation_date}
              onChange={(e) => setFormData(prev => ({ ...prev, installation_date: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.deliveryDate')}
            </label>
            <Input
              type="date"
              value={formData.delivery_date}
              onChange={(e) => setFormData(prev => ({ ...prev, delivery_date: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.notes')}
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsEditModalOpen(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button type="submit">
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Change Status Modal */}
      <Modal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        title={t('jobs.changeStatus')}
      >
        <form onSubmit={handleStatusSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('jobs.status')}
            </label>
            <Select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value as JobStatus)}
            >
              {jobStatuses.map(status => (
                <option key={status} value={status}>
                  {t(`jobStatus.${status}`)}
                </option>
              ))}
            </Select>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsStatusModalOpen(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button type="submit">
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Measurement Modal */}
      <Modal
        isOpen={isAddMeasurementModalOpen}
        onClose={() => setIsAddMeasurementModalOpen(false)}
        title={t('jobs.addMeasurement')}
      >
        <form onSubmit={handleAddMeasurementSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('measurements.visitDate')}
            </label>
            <Input
              type="date"
              value={measurementData.visit_date}
              onChange={(e) => setMeasurementData(prev => ({ ...prev, visit_date: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('measurements.measuredBy')}
            </label>
            <Input
              type="text"
              value={measurementData.measured_by}
              onChange={(e) => setMeasurementData(prev => ({ ...prev, measured_by: e.target.value }))}
              placeholder={t('measurements.measuredBy')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('measurements.notes')}
            </label>
            <textarea
              value={measurementData.notes}
              onChange={(e) => setMeasurementData(prev => ({ ...prev, notes: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder={t('measurements.notes')}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsAddMeasurementModalOpen(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button type="submit" loading={createMeasurementMutation.isPending}>
              {t('common.create')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Payment Modal */}
      <Modal
        isOpen={isAddPaymentModalOpen}
        onClose={() => setIsAddPaymentModalOpen(false)}
        title={t('payments.addPayment')}
      >
        <form onSubmit={handleAddPaymentSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentType')} *
              </label>
              <Select
                value={paymentData.payment_type}
                onChange={(e) => setPaymentData(prev => ({ ...prev, payment_type: e.target.value as PaymentType }))}
                required
              >
                <option value="deposit">{t('paymentType.deposit')}</option>
                <option value="production">{t('paymentType.production')}</option>
                <option value="final">{t('paymentType.final')}</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentMethod')} *
              </label>
              <Select
                value={paymentData.payment_method}
                onChange={(e) => setPaymentData(prev => ({ ...prev, payment_method: e.target.value as PaymentMethod }))}
                required
              >
                <option value="cash">{t('paymentMethod.cash')}</option>
                <option value="bank_transfer">{t('paymentMethod.bank_transfer')}</option>
                <option value="instapay">{t('paymentMethod.instapay')}</option>
                <option value="cheque">{t('paymentMethod.cheque')}</option>
                <option value="other">{t('paymentMethod.other')}</option>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.percentage')} * (%)
              </label>
              <Input
                type="number"
                step="0.01"
                min="0.01"
                max="100"
                value={paymentData.percentage}
                onChange={(e) => setPaymentData(prev => ({ ...prev, percentage: e.target.value }))}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.amount')} *
              </label>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={paymentData.amount}
                onChange={(e) => setPaymentData(prev => ({ ...prev, amount: e.target.value }))}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.dueDate')}
              </label>
              <Input
                type="date"
                value={paymentData.due_date}
                onChange={(e) => setPaymentData(prev => ({ ...prev, due_date: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paidDate')}
              </label>
              <Input
                type="date"
                value={paymentData.paid_date}
                onChange={(e) => setPaymentData(prev => ({ ...prev, paid_date: e.target.value }))}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.notes')}
            </label>
            <textarea
              value={paymentData.notes}
              onChange={(e) => setPaymentData(prev => ({ ...prev, notes: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsAddPaymentModalOpen(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button type="submit" loading={createPaymentMutation.isPending}>
              {t('common.create')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Payment Modal */}
      <Modal
        isOpen={isEditPaymentModalOpen}
        onClose={() => setIsEditPaymentModalOpen(false)}
        title={t('payments.editPayment')}
      >
        <form onSubmit={handleEditPaymentSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentType')} *
              </label>
              <Select
                value={paymentData.payment_type}
                onChange={(e) => setPaymentData(prev => ({ ...prev, payment_type: e.target.value as PaymentType }))}
                required
              >
                <option value="deposit">{t('paymentType.deposit')}</option>
                <option value="production">{t('paymentType.production')}</option>
                <option value="final">{t('paymentType.final')}</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paymentMethod')} *
              </label>
              <Select
                value={paymentData.payment_method}
                onChange={(e) => setPaymentData(prev => ({ ...prev, payment_method: e.target.value as PaymentMethod }))}
                required
              >
                <option value="cash">{t('paymentMethod.cash')}</option>
                <option value="bank_transfer">{t('paymentMethod.bank_transfer')}</option>
                <option value="instapay">{t('paymentMethod.instapay')}</option>
                <option value="cheque">{t('paymentMethod.cheque')}</option>
                <option value="other">{t('paymentMethod.other')}</option>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.percentage')} * (%)
              </label>
              <Input
                type="number"
                step="0.01"
                min="0.01"
                max="100"
                value={paymentData.percentage}
                onChange={(e) => setPaymentData(prev => ({ ...prev, percentage: e.target.value }))}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.amount')} *
              </label>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={paymentData.amount}
                onChange={(e) => setPaymentData(prev => ({ ...prev, amount: e.target.value }))}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.dueDate')}
              </label>
              <Input
                type="date"
                value={paymentData.due_date}
                onChange={(e) => setPaymentData(prev => ({ ...prev, due_date: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.paidDate')}
              </label>
              <Input
                type="date"
                value={paymentData.paid_date}
                onChange={(e) => setPaymentData(prev => ({ ...prev, paid_date: e.target.value }))}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.notes')}
            </label>
            <textarea
              value={paymentData.notes}
              onChange={(e) => setPaymentData(prev => ({ ...prev, notes: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsEditPaymentModalOpen(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button type="submit" loading={updatePaymentMutation.isPending}>
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Confirm Mark as Paid Dialog */}
      <ConfirmationDialog
        isOpen={isConfirmStatusModalOpen}
        onClose={() => {
          setIsConfirmStatusModalOpen(false);
          setSelectedPayment(null);
        }}
        onConfirm={handleConfirmMarkPaid}
        title={t('payments.markAsPaid')}
        message={`هل أنت متأكد من تعيين الدفعة #${selectedPayment?.payment_order} كمدفوعة؟`}
        confirmText={t('common.confirm')}
        cancelText={t('common.cancel')}
        variant="info"
        isLoading={markPaidMutation.isPending}
      />
    </div>
  );
}

// Timeline Item Component
interface TimelineItemProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value?: string;
  variant?: 'default' | 'info' | 'warning' | 'success';
}

function TimelineItem({ icon: Icon, label, value, variant = 'default' }: TimelineItemProps) {
  const { t } = useTranslation();
  
  const colorMap = {
    default: 'text-gray-400',
    info: 'text-blue-500',
    warning: 'text-orange-500',
    success: 'text-green-500',
  };

  return (
    <div className="flex items-start gap-3">
      <Icon className={`w-5 h-5 mt-0.5 ${colorMap[variant]}`} />
      <div className="flex-1">
        <div className="text-sm text-gray-600">{label}</div>
        <div className="font-medium">
          {value ? formatDate(value) : t('jobs.notSet')}
        </div>
      </div>
    </div>
  );
}
