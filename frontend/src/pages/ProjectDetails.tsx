import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { 
  ArrowLeft, Edit, Plus, Calendar, Package, Wrench, Truck, CheckCircle, 
  Check, User, Phone, MapPin, FileText, DollarSign, Printer, MoreHorizontal,
  X, AlertCircle, Clock
} from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import { jobsApi } from '../services/jobs';
import { quotationsApi } from '../services/quotations';
import { customersApi } from '../services/customers';
import { productsApi } from '../services/products';
import { measurementsApi } from '../services/measurements';
import { paymentsApi } from '../services/payments';
import { formatDate, formatCurrency } from '../utils/formatters';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input from '../components/Input';
import Select from '../components/Select';
import LoadingSpinner from '../components/LoadingSpinner';
import JobStatusBadge from '../components/JobStatusBadge';
import Badge from '../components/Badge';
import PaymentStatusBadge from '../components/PaymentStatusBadge';
import ConfirmationDialog from '../components/ConfirmationDialog';
import CollapsibleSection from '../components/CollapsibleSection';
import InlineEdit from '../components/InlineEdit';
import type { 
  Job, JobStatus, Quotation, QuotationStatus, QuotationItem,
  Measurement, Payment, PaymentType, PaymentMethod 
} from '../types';

export default function ProjectDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const isJobRoute = window.location.pathname.startsWith('/jobs/');

  // Modal states
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [isAddMeasurementModalOpen, setIsAddMeasurementModalOpen] = useState(false);
  const [isAddPaymentModalOpen, setIsAddPaymentModalOpen] = useState(false);
  const [isEditPaymentModalOpen, setIsEditPaymentModalOpen] = useState(false);
  const [isConfirmMarkPaidModalOpen, setIsConfirmMarkPaidModalOpen] = useState(false);
  const [isAddItemModalOpen, setIsAddItemModalOpen] = useState(false);
  const [isEditItemModalOpen, setIsEditItemModalOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [selectedItem, setSelectedItem] = useState<QuotationItem | null>(null);

  // Collapsible section states
  const [sectionsOpen, setSectionsOpen] = useState({
    workflow: true,
    quotation: true,
    measurements: true,
    payments: true,
    timeline: false,
    activity: false,
    notes: false,
    documents: false,
  });

  // Form states
  const [newStatus, setNewStatus] = useState<JobStatus | QuotationStatus>('pending');
  const [measurementData, setMeasurementData] = useState({
    visit_date: '',
    measured_by: '',
    notes: '',
  });
  const [paymentData, setPaymentData] = useState({
    payment_type: 'deposit' as PaymentType,
    payment_method: 'cash' as PaymentMethod,
    percentage: '',
    amount: '',
    due_date: '',
    paid_date: '',
    notes: '',
  });
  const [itemFormData, setItemFormData] = useState({
    product_id: '',
    quantity: 1,
    unit_price: '',
    description: '',
    notes: '',
  });

  // Data fetching
  const { data: quotation, isLoading: isLoadingQuotation } = useQuery({
    queryKey: ['quotations', !isJobRoute ? id : null],
    queryFn: () => quotationsApi.getById(id!),
    enabled: !!id && !isJobRoute,
  });

  const { data: job, isLoading: isLoadingJob } = useQuery({
    queryKey: ['jobs', isJobRoute ? id : null],
    queryFn: () => jobsApi.getById(id!),
    enabled: !!id && isJobRoute,
  });

  const { data: jobQuotation } = useQuery({
    queryKey: ['quotations', job?.quotation_id],
    queryFn: () => quotationsApi.getById(job!.quotation_id),
    enabled: !!job?.quotation_id,
  });

  const activeQuotation = !isJobRoute ? quotation : jobQuotation;

  const { data: customer } = useQuery({
    queryKey: ['customers', activeQuotation?.customer_id],
    queryFn: () => customersApi.getById(activeQuotation!.customer_id),
    enabled: !!activeQuotation?.customer_id,
  });

  const { data: itemsData, refetch: refetchItems } = useQuery({
    queryKey: ['quotation-items', activeQuotation?.id],
    queryFn: () => activeQuotation ? quotationsApi.getItems(activeQuotation.id) : Promise.resolve({ items: [], total: 0 }),
    enabled: !!activeQuotation,
  });

  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.getAll({ limit: 100, active: true }),
  });

  const { data: measurementsData } = useQuery({
    queryKey: ['measurements', job?.id],
    queryFn: () => measurementsApi.getJobMeasurements(job!.id, { sort_order: 'desc' }),
    enabled: !!job,
  });

  const { data: paymentsData } = useQuery({
    queryKey: ['payments', job?.id],
    queryFn: () => paymentsApi.getJobPayments(job!.id, { sort_order: 'asc' }),
    enabled: !!job,
  });

  const items = itemsData?.items || [];
  const products = productsData?.items || [];
  const measurements = measurementsData?.items || [];
  const payments = paymentsData?.items || [];

  const totalPaid = payments.filter(p => p.status === 'paid').reduce((sum, p) => sum + parseFloat(p.amount), 0);
  const totalScheduled = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
  const remainingBalance = totalScheduled - totalPaid;
  const paidPercentage = totalScheduled > 0 ? (totalPaid / totalScheduled) * 100 : 0;

  // Mutations
  const updateJobStatusMutation = useMutation({
    mutationFn: (status: JobStatus) => jobsApi.updateStatus(job!.id, status),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['jobs', job?.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setIsStatusModalOpen(false);
    },
    onError: () => toast.error(t('errors.generic')),
  });

  const updateQuotationStatusMutation = useMutation({
    mutationFn: (status: QuotationStatus) => quotationsApi.updateStatus(activeQuotation!.id, status),
    onSuccess: (response) => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setIsStatusModalOpen(false);
      if (response.job) {
        navigate(`/jobs/${response.job.id}`);
      }
    },
    onError: () => toast.error(t('errors.generic')),
  });

  const addItemMutation = useMutation({
    mutationFn: (item: Partial<QuotationItem>) => quotationsApi.addItem(activeQuotation!.id, item),
    onSuccess: () => {
      toast.success(t('success.created'));
      refetchItems();
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsAddItemModalOpen(false);
      setItemFormData({ product_id: '', quantity: 1, unit_price: '', description: '', notes: '' });
    },
    onError: () => toast.error(t('errors.generic')),
  });

  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, item }: { itemId: string; item: Partial<QuotationItem> }) =>
      quotationsApi.updateItem(itemId, item),
    onSuccess: () => {
      toast.success(t('success.updated'));
      refetchItems();
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsEditItemModalOpen(false);
    },
    onError: () => toast.error(t('errors.generic')),
  });

  const createMeasurementMutation = useMutation({
    mutationFn: (data: typeof measurementData) => measurementsApi.create(job!.id, data),
    onSuccess: (newMeasurement) => {
      toast.success(t('success.created'));
      queryClient.invalidateQueries({ queryKey: ['measurements', job?.id] });
      setIsAddMeasurementModalOpen(false);
      setMeasurementData({ visit_date: '', measured_by: '', notes: '' });
      navigate(`/jobs/${job?.id}/measurements/${newMeasurement.id}`);
    },
    onError: () => toast.error(t('errors.generic')),
  });

  const createPaymentMutation = useMutation({
    mutationFn: (data: typeof paymentData) => paymentsApi.create(job!.id, data),
    onSuccess: () => {
      toast.success(t('success.created'));
      queryClient.invalidateQueries({ queryKey: ['payments', job?.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
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
    onError: () => toast.error(t('errors.generic')),
  });

  const updatePaymentMutation = useMutation({
    mutationFn: ({ id: paymentId, data }: { id: string; data: Partial<Payment> }) =>
      paymentsApi.update(paymentId, data),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['payments', job?.id] });
      setIsEditPaymentModalOpen(false);
      setSelectedPayment(null);
    },
    onError: () => toast.error(t('errors.generic')),
  });

  const markPaidMutation = useMutation({
    mutationFn: (paymentId: string) => paymentsApi.updateStatus(paymentId, 'paid'),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['payments', job?.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setIsConfirmMarkPaidModalOpen(false);
      setSelectedPayment(null);
    },
    onError: () => toast.error(t('errors.generic')),
  });

  // Handlers
  const handleApproveQuotation = () => {
    updateQuotationStatusMutation.mutate('approved');
  };

  const handleStatusChange = () => {
    if (job) {
      setNewStatus(job.status);
    } else if (activeQuotation) {
      setNewStatus(activeQuotation.status);
    }
    setIsStatusModalOpen(true);
  };

  const handleEditItem = (item: QuotationItem) => {
    setSelectedItem(item);
    setItemFormData({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: item.unit_price,
      description: item.description || '',
      notes: item.notes || '',
    });
    setIsEditItemModalOpen(true);
  };

  const handleEditPayment = (payment: Payment) => {
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

  const getProductName = (productId: string) => {
    const product = products.find(p => p.id === productId);
    return product?.name || '-';
  };

  const getQuotationStatusBadgeVariant = (status: QuotationStatus): 'info' | 'success' | 'warning' | 'danger' => {
    const variants: Record<QuotationStatus, 'info' | 'success' | 'warning' | 'danger'> = {
      draft: 'info',
      waiting_for_measurement: 'warning',
      measured: 'info',
      under_negotiation: 'warning',
      sent: 'info',
      approved: 'success',
      rejected: 'danger',
      cancelled: 'danger',
      expired: 'danger',
    };
    return variants[status] || 'info';
  };

  const jobStatuses: JobStatus[] = ['pending', 'measuring', 'in_production', 'ready_for_installation', 'installed', 'completed', 'cancelled'];
  const quotationStatuses: QuotationStatus[] = ['draft', 'waiting_for_measurement', 'measured', 'under_negotiation', 'sent', 'approved', 'rejected', 'cancelled', 'expired'];

  const isLoading = isLoadingQuotation || isLoadingJob;
  const hasJob = !!job;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!activeQuotation) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">{t('errors.notFound')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* ========== 1. ENHANCED HEADER - COMMAND CENTER ========== */}
      <div className="sticky top-0 z-20 bg-white border-b shadow-md">
        <div className="px-6 py-4">
          {/* Row 1: Back Button + Project Info */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/projects')}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                {t('common.back')}
              </Button>
              <div className="flex items-center gap-3">
                <div className="text-xs text-gray-500">{t('projects.quotationNumber')}:</div>
                <div className="font-semibold text-gray-900">{activeQuotation.quotation_number}</div>
              </div>
              {hasJob && job && (
                <div className="flex items-center gap-3">
                  <div className="text-xs text-gray-500">{t('projects.projectNumber')}:</div>
                  <div className="font-semibold text-gray-900">#{job.id.substring(0, 8)}</div>
                </div>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="flex items-center gap-2">
                <Printer className="w-4 h-4" />
                {t('projects.print')}
              </Button>
              <Button variant="ghost" size="sm" className="flex items-center gap-2">
                <MoreHorizontal className="w-4 h-4" />
                {t('projects.moreActions')}
              </Button>
            </div>
          </div>

          {/* Row 2: Customer + Status + Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            {/* Customer */}
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <div className="text-xs text-gray-500 mb-1">{t('projects.customer')}</div>
                <div className="font-medium text-gray-900">{customer?.full_name || '-'}</div>
                <div className="text-xs text-gray-600 flex items-center gap-1">
                  <Phone className="w-3 h-3" />
                  {customer?.phone_number || '-'}
                </div>
              </div>
            </div>

            {/* Status */}
            <div>
              <div className="text-xs text-gray-500 mb-1">{t('projects.status')}</div>
              {hasJob ? (
                <JobStatusBadge status={job.status} />
              ) : (
                <Badge variant={getQuotationStatusBadgeVariant(activeQuotation.status)}>
                  {t(`quotationStatus.${activeQuotation.status}`)}
                </Badge>
              )}
              <div className="text-xs text-gray-600 mt-1">
                {t('projects.createdDate')}: {formatDate(activeQuotation.created_at)}
              </div>
            </div>

            {/* Outstanding Balance */}
            {hasJob && (
              <div>
                <div className="text-xs text-gray-500 mb-1">{t('projects.outstandingBalance')}</div>
                <div className="text-lg font-bold text-red-600">
                  {formatCurrency(remainingBalance)}
                </div>
                <div className="text-xs text-gray-600">
                  {t('projects.paymentProgress')}: {paidPercentage.toFixed(0)}%
                </div>
              </div>
            )}

            {/* Contract Value / Final Price */}
            <div>
              <div className="text-xs text-gray-500 mb-1">
                {hasJob ? t('projects.totalContractValue') : t('quotations.finalPrice')}
              </div>
              <div className="text-lg font-bold text-green-600">
                {formatCurrency(activeQuotation.final_price)}
              </div>
              {!hasJob && (
                <div className="text-xs text-gray-600">
                  {t('quotations.discount')}: {formatCurrency(activeQuotation.discount)}
                </div>
              )}
            </div>
          </div>

          {/* Row 3: Quick Actions */}
          <div className="flex items-center gap-2 pb-2 border-t pt-3">
            {!hasJob && activeQuotation.status !== 'approved' && activeQuotation.status !== 'rejected' && (
              <>
                <Button onClick={handleApproveQuotation} size="sm" className="flex items-center gap-2">
                  <Check className="w-4 h-4" />
                  {t('projects.approve')}
                </Button>
                <Button variant="outline" size="sm" onClick={() => updateQuotationStatusMutation.mutate('rejected')} className="flex items-center gap-2">
                  <X className="w-4 h-4" />
                  {t('projects.reject')}
                </Button>
              </>
            )}
            {hasJob && (
              <>
                <Button onClick={() => setIsAddMeasurementModalOpen(true)} size="sm" className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  {t('projects.addMeasurement')}
                </Button>
                <Button onClick={() => setIsAddPaymentModalOpen(true)} size="sm" className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  {t('payments.addPayment')}
                </Button>
              </>
            )}
            <Button variant="outline" size="sm" onClick={handleStatusChange}>
              {t('projects.changeStatus')}
            </Button>
          </div>
        </div>
      </div>

      {/* ========== 2. WORKFLOW PROGRESS (Only if job exists) ========== */}
      {hasJob && job && (
        <CollapsibleSection
          title={t('projects.workflowProgress')}
          defaultOpen={sectionsOpen.workflow}
        >
          <div className="flex items-center justify-between">
            {[
              { status: 'pending', label: t('jobStatus.pending'), icon: FileText },
              { status: 'measuring', label: t('jobStatus.measuring'), icon: Calendar },
              { status: 'in_production', label: t('jobStatus.in_production'), icon: Package },
              { status: 'ready_for_installation', label: t('jobStatus.ready_for_installation'), icon: Wrench },
              { status: 'installed', label: t('jobStatus.installed'), icon: Truck },
              { status: 'completed', label: t('jobStatus.completed'), icon: CheckCircle },
            ].map((step, index) => {
              const Icon = step.icon;
              const statusIndex = jobStatuses.indexOf(job.status as JobStatus);
              const stepIndex = jobStatuses.indexOf(step.status as JobStatus);
              const isActive = stepIndex === statusIndex;
              const isCompleted = stepIndex < statusIndex;

              return (
                <div key={step.status} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div className={`
                      w-10 h-10 rounded-full flex items-center justify-center
                      ${isActive ? 'bg-blue-600 text-white' : isCompleted ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'}
                    `}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-xs mt-2 text-center max-w-[80px]">{step.label}</span>
                  </div>
                  {index < 5 && (
                    <div className={`h-0.5 w-12 mx-2 ${isCompleted ? 'bg-green-500' : 'bg-gray-200'}`} />
                  )}
                </div>
              );
            })}
          </div>
        </CollapsibleSection>
      )}

      {/* ========== 3. QUOTATION ========== */}
      <CollapsibleSection
        title={t('quotations.quotation')}
        defaultOpen={sectionsOpen.quotation}
        badge={<DollarSign className="w-5 h-5 text-gray-400" />}
        headerActions={
          !hasJob ? (
            <Button size="sm" onClick={() => setIsAddItemModalOpen(true)} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              {t('quotations.addItem')}
            </Button>
          ) : undefined
        }
      >
        {items.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {t('common.noResults')}
          </div>
        ) : (
          <>
            <div className="border rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.product')}</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.quantity')}</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.unitPrice')}</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.total')}</th>
                    {!hasJob && (
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('common.actions')}</th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-4 py-3 text-sm text-gray-900">{getProductName(item.product_id)}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{item.quantity}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{formatCurrency(item.unit_price)}</td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(item.total_price)}</td>
                      {!hasJob && (
                        <td className="px-4 py-3 text-sm">
                          <Button variant="ghost" size="sm" onClick={() => handleEditItem(item)} className="text-blue-600">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Totals */}
            <div className="border-t mt-4 pt-4">
              <div className="space-y-2 max-w-md mr-auto">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">{t('quotations.totalPrice')}:</span>
                  <span className="font-medium">{formatCurrency(activeQuotation.total_price)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">{t('quotations.discount')}:</span>
                  <span className="font-medium">{formatCurrency(activeQuotation.discount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>{t('quotations.finalPrice')}:</span>
                  <span className="text-blue-600">{formatCurrency(activeQuotation.final_price)}</span>
                </div>
              </div>
            </div>
          </>
        )}
      </CollapsibleSection>

      {/* ========== 4. MEASUREMENTS (Only if job exists) ========== */}
      {hasJob && job && (
        <CollapsibleSection
          title={t('projects.measurements')}
          defaultOpen={sectionsOpen.measurements}
          badge={<Badge variant="info">{measurements.length}</Badge>}
          headerActions={
            <Button size="sm" onClick={() => setIsAddMeasurementModalOpen(true)} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              {t('projects.addMeasurement')}
            </Button>
          }
        >
          {measurements.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">{t('projects.noMeasurements')}</p>
              <Button size="sm" onClick={() => setIsAddMeasurementModalOpen(true)}>
                {t('projects.addFirstMeasurement')}
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {measurements.map((measurement) => (
                <div
                  key={measurement.id}
                  onClick={() => navigate(`/jobs/${job.id}/measurements/${measurement.id}`)}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
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
        </CollapsibleSection>
      )}

      {/* ========== 5. PAYMENTS (Only if job exists) ========== */}
      {hasJob && job && (
        <CollapsibleSection
          title={t('payments.jobPayments')}
          defaultOpen={sectionsOpen.payments}
          badge={
            <div className="flex items-center gap-2">
              <Badge variant="success">{payments.filter(p => p.status === 'paid').length}</Badge>
              <span className="text-xs text-gray-500">/</span>
              <Badge variant="info">{payments.length}</Badge>
            </div>
          }
          headerActions={
            <Button size="sm" onClick={() => setIsAddPaymentModalOpen(true)} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              {t('payments.addPayment')}
            </Button>
          }
        >
          {/* Payment Summary */}
          {payments.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="text-xs text-green-600 mb-1">{t('payments.totalPaid')}</div>
                <div className="text-2xl font-bold text-green-700">{formatCurrency(totalPaid)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <div className="text-xs text-gray-600 mb-1">{t('payments.remainingBalance')}</div>
                <div className="text-2xl font-bold text-gray-700">{formatCurrency(remainingBalance)}</div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-blue-600">{t('payments.paidPercentage')}</span>
                  <span className="text-lg font-bold text-blue-700">{paidPercentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-blue-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min(paidPercentage, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {payments.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">{t('payments.noPayments')}</p>
              <Button size="sm" onClick={() => setIsAddPaymentModalOpen(true)}>
                {t('payments.addFirstPayment')}
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {payments.map((payment) => {
                const isOverdue = payment.status === 'pending' && payment.due_date && new Date(payment.due_date) < new Date();
                
                return (
                  <div key={payment.id} className={`border rounded-lg p-4 ${isOverdue ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <span className="font-semibold text-gray-900">
                          {t('payments.installment')} #{payment.payment_order}
                        </span>
                        <span className="text-sm text-gray-600 mr-2">
                          {' '}({t(`paymentType.${payment.payment_type}`)})
                        </span>
                      </div>
                      <PaymentStatusBadge status={payment.status} />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                      <div>
                        <span className="text-gray-600">{t('payments.amount')}:</span>
                        <span className="font-semibold mr-2">{formatCurrency(parseFloat(payment.amount))}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">{t('payments.percentage')}:</span>
                        <span className="font-semibold">{payment.percentage}%</span>
                      </div>
                      {payment.due_date && (
                        <div>
                          <span className="text-gray-600">{t('payments.dueDate')}:</span>
                          <span className={isOverdue ? 'text-red-600 font-semibold mr-2' : 'mr-2'}>
                            {formatDate(payment.due_date)}
                          </span>
                        </div>
                      )}
                      {payment.paid_date && (
                        <div>
                          <span className="text-gray-600">{t('payments.paidDate')}:</span>
                          <span className="text-green-600 mr-2">{formatDate(payment.paid_date)}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      {payment.status === 'pending' && (
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => { setSelectedPayment(payment); setIsConfirmMarkPaidModalOpen(true); }}
                          className="flex items-center gap-1 flex-1"
                        >
                          <Check className="w-3 h-3" />
                          {t('payments.markAsPaid')}
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEditPayment(payment)}
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
        </CollapsibleSection>
      )}

      {/* ========== 6. TIMELINE (Only if job exists) ========== */}
      {hasJob && job && (
        <CollapsibleSection
          title={t('projects.timeline')}
          defaultOpen={sectionsOpen.timeline}
          badge={<Clock className="w-5 h-5 text-gray-400" />}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900">{t('projects.measurementDate')}</div>
                <div className="text-sm text-gray-600">{job.measurement_date ? formatDate(job.measurement_date) : '-'}</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-yellow-50 text-yellow-600">
                <Package className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900">{t('projects.productionStart')}</div>
                <div className="text-sm text-gray-600">{job.production_start ? formatDate(job.production_start) : '-'}</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-yellow-50 text-yellow-600">
                <Wrench className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900">{t('projects.productionEnd')}</div>
                <div className="text-sm text-gray-600">{job.production_end ? formatDate(job.production_end) : '-'}</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                <Truck className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900">{t('projects.installationDate')}</div>
                <div className="text-sm text-gray-600">{job.installation_date ? formatDate(job.installation_date) : '-'}</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-green-50 text-green-600">
                <CheckCircle className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900">{t('projects.completionDate')}</div>
                <div className="text-sm text-gray-600">{job.completion_date ? formatDate(job.completion_date) : '-'}</div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}

      {/* ========== 7. RECENT ACTIVITY ========== */}
      <CollapsibleSection
        title={t('projects.recentActivity')}
        defaultOpen={sectionsOpen.activity}
        badge={<AlertCircle className="w-5 h-5 text-gray-400" />}
      >
        <div className="text-center py-8 text-gray-500">
          <p>{t('projects.activityPlaceholder')}</p>
        </div>
      </CollapsibleSection>

      {/* ========== 8. NOTES ========== */}
      <CollapsibleSection
        title={t('projects.notes')}
        defaultOpen={sectionsOpen.notes}
      >
        {(hasJob ? job?.notes : activeQuotation.notes) ? (
          <p className="text-gray-700 whitespace-pre-wrap">{hasJob ? job.notes : activeQuotation.notes}</p>
        ) : (
          <p className="text-gray-500 italic">{t('projects.noNotes')}</p>
        )}
      </CollapsibleSection>

      {/* ========== 9. DOCUMENTS (Placeholder) ========== */}
      <CollapsibleSection
        title={t('projects.documents')}
        defaultOpen={sectionsOpen.documents}
        badge={<FileText className="w-5 h-5 text-gray-400" />}
      >
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>{t('projects.documentsPlaceholder')}</p>
        </div>
      </CollapsibleSection>

      {/* ========== MODALS ========== */}
      
      {/* Status Change Modal */}
      <Modal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        title={hasJob ? t('projects.changeStatus') : t('quotations.changeStatus')}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          if (hasJob) {
            updateJobStatusMutation.mutate(newStatus as JobStatus);
          } else {
            updateQuotationStatusMutation.mutate(newStatus as QuotationStatus);
          }
        }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('projects.status')}
            </label>
            <Select value={newStatus} onChange={(e) => setNewStatus(e.target.value as JobStatus | QuotationStatus)}>
              {(hasJob ? jobStatuses : quotationStatuses).map(status => (
                <option key={status} value={status}>
                  {t(`${hasJob ? 'jobStatus' : 'quotationStatus'}.${status}`)}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsStatusModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit">{t('common.save')}</Button>
          </div>
        </form>
      </Modal>

      {/* Add Item Modal */}
      <Modal
        isOpen={isAddItemModalOpen}
        onClose={() => setIsAddItemModalOpen(false)}
        title={t('quotations.addItem')}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          addItemMutation.mutate(itemFormData);
        }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.product')} *
            </label>
            <Select
              value={itemFormData.product_id}
              onChange={(e) => setItemFormData({ ...itemFormData, product_id: e.target.value })}
              required
            >
              <option value="">{t('quotations.selectProduct')}</option>
              {products.map(product => (
                <option key={product.id} value={product.id}>{product.name}</option>
              ))}
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.quantity')} *
            </label>
            <Input
              type="number"
              min="1"
              value={itemFormData.quantity}
              onChange={(e) => setItemFormData({ ...itemFormData, quantity: parseInt(e.target.value) || 1 })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.unitPrice')} *
            </label>
            <Input
              type="number"
              step="0.01"
              min="0"
              value={itemFormData.unit_price}
              onChange={(e) => setItemFormData({ ...itemFormData, unit_price: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.notes')}
            </label>
            <textarea
              value={itemFormData.notes}
              onChange={(e) => setItemFormData({ ...itemFormData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsAddItemModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit">{t('common.add')}</Button>
          </div>
        </form>
      </Modal>

      {/* Edit Item Modal */}
      <Modal
        isOpen={isEditItemModalOpen}
        onClose={() => setIsEditItemModalOpen(false)}
        title={t('quotations.editItem')}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          if (selectedItem) {
            updateItemMutation.mutate({ itemId: selectedItem.id, item: itemFormData });
          }
        }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.product')} *
            </label>
            <Select
              value={itemFormData.product_id}
              onChange={(e) => setItemFormData({ ...itemFormData, product_id: e.target.value })}
              required
            >
              <option value="">{t('quotations.selectProduct')}</option>
              {products.map(product => (
                <option key={product.id} value={product.id}>{product.name}</option>
              ))}
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.quantity')} *
            </label>
            <Input
              type="number"
              min="1"
              value={itemFormData.quantity}
              onChange={(e) => setItemFormData({ ...itemFormData, quantity: parseInt(e.target.value) || 1 })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.unitPrice')} *
            </label>
            <Input
              type="number"
              step="0.01"
              min="0"
              value={itemFormData.unit_price}
              onChange={(e) => setItemFormData({ ...itemFormData, unit_price: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.notes')}
            </label>
            <textarea
              value={itemFormData.notes}
              onChange={(e) => setItemFormData({ ...itemFormData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsEditItemModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit">{t('common.save')}</Button>
          </div>
        </form>
      </Modal>

      {/* Add Measurement Modal */}
      <Modal
        isOpen={isAddMeasurementModalOpen}
        onClose={() => setIsAddMeasurementModalOpen(false)}
        title={t('projects.addMeasurement')}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          createMeasurementMutation.mutate(measurementData);
        }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('measurements.visitDate')}
            </label>
            <Input
              type="date"
              value={measurementData.visit_date}
              onChange={(e) => setMeasurementData({ ...measurementData, visit_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('measurements.measuredBy')}
            </label>
            <Input
              type="text"
              value={measurementData.measured_by}
              onChange={(e) => setMeasurementData({ ...measurementData, measured_by: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('measurements.notes')}
            </label>
            <textarea
              value={measurementData.notes}
              onChange={(e) => setMeasurementData({ ...measurementData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsAddMeasurementModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit">{t('common.create')}</Button>
          </div>
        </form>
      </Modal>

      {/* Add Payment Modal */}
      <Modal
        isOpen={isAddPaymentModalOpen}
        onClose={() => setIsAddPaymentModalOpen(false)}
        title={t('payments.addPayment')}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          createPaymentMutation.mutate(paymentData);
        }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.paymentType')} *
            </label>
            <Select
              value={paymentData.payment_type}
              onChange={(e) => setPaymentData({ ...paymentData, payment_type: e.target.value as PaymentType })}
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
              onChange={(e) => setPaymentData({ ...paymentData, payment_method: e.target.value as PaymentMethod })}
              required
            >
              <option value="cash">{t('paymentMethod.cash')}</option>
              <option value="bank_transfer">{t('paymentMethod.bank_transfer')}</option>
              <option value="instapay">{t('paymentMethod.instapay')}</option>
              <option value="cheque">{t('paymentMethod.cheque')}</option>
              <option value="other">{t('paymentMethod.other')}</option>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.percentage')} *
              </label>
              <Input
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={paymentData.percentage}
                onChange={(e) => setPaymentData({ ...paymentData, percentage: e.target.value })}
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
                onChange={(e) => setPaymentData({ ...paymentData, amount: e.target.value })}
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.dueDate')}
            </label>
            <Input
              type="date"
              value={paymentData.due_date}
              onChange={(e) => setPaymentData({ ...paymentData, due_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.notes')}
            </label>
            <textarea
              value={paymentData.notes}
              onChange={(e) => setPaymentData({ ...paymentData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsAddPaymentModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit">{t('common.create')}</Button>
          </div>
        </form>
      </Modal>

      {/* Edit Payment Modal */}
      <Modal
        isOpen={isEditPaymentModalOpen}
        onClose={() => setIsEditPaymentModalOpen(false)}
        title={t('payments.editPayment')}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          if (selectedPayment) {
            updatePaymentMutation.mutate({ id: selectedPayment.id, data: paymentData });
          }
        }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.paymentType')} *
            </label>
            <Select
              value={paymentData.payment_type}
              onChange={(e) => setPaymentData({ ...paymentData, payment_type: e.target.value as PaymentType })}
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
              onChange={(e) => setPaymentData({ ...paymentData, payment_method: e.target.value as PaymentMethod })}
              required
            >
              <option value="cash">{t('paymentMethod.cash')}</option>
              <option value="bank_transfer">{t('paymentMethod.bank_transfer')}</option>
              <option value="instapay">{t('paymentMethod.instapay')}</option>
              <option value="cheque">{t('paymentMethod.cheque')}</option>
              <option value="other">{t('paymentMethod.other')}</option>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('payments.percentage')} *
              </label>
              <Input
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={paymentData.percentage}
                onChange={(e) => setPaymentData({ ...paymentData, percentage: e.target.value })}
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
                onChange={(e) => setPaymentData({ ...paymentData, amount: e.target.value })}
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.dueDate')}
            </label>
            <Input
              type="date"
              value={paymentData.due_date}
              onChange={(e) => setPaymentData({ ...paymentData, due_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.paidDate')}
            </label>
            <Input
              type="date"
              value={paymentData.paid_date}
              onChange={(e) => setPaymentData({ ...paymentData, paid_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('payments.notes')}
            </label>
            <textarea
              value={paymentData.notes}
              onChange={(e) => setPaymentData({ ...paymentData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsEditPaymentModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit">{t('common.save')}</Button>
          </div>
        </form>
      </Modal>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={isConfirmMarkPaidModalOpen}
        onClose={() => setIsConfirmMarkPaidModalOpen(false)}
        onConfirm={() => selectedPayment && markPaidMutation.mutate(selectedPayment.id)}
        title={t('payments.confirmMarkPaid')}
        message={t('payments.confirmMarkPaidMessage')}
      />
    </div>
  );
}
