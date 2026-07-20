import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Search, Plus, Edit, Trash2, Eye, DollarSign } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import { quotationsApi } from '../services/quotations';
import { customersApi } from '../services/customers';
import { productsApi } from '../services/products';
import { formatCurrency, formatDate } from '../utils';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import Modal from '../components/Modal';
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell, EmptyState } from '../components/Table';
import LoadingSpinner from '../components/LoadingSpinner';
import Badge from '../components/Badge';
import ConfirmationDialog from '../components/ConfirmationDialog';
import type { Quotation, QuotationItem, QuotationStatus } from '../types/index';

export default function Quotations() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<QuotationStatus | ''>('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  const [isEditItemModalOpen, setIsEditItemModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleteItemDialogOpen, setIsDeleteItemDialogOpen] = useState(false);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [selectedQuotation, setSelectedQuotation] = useState<Quotation | null>(null);
  const [selectedItem, setSelectedItem] = useState<QuotationItem | null>(null);
  const [formData, setFormData] = useState({
    customer_id: '',
    quotation_date: new Date().toISOString().split('T')[0],
    discount: '0',
    notes: '',
  });
  const [itemFormData, setItemFormData] = useState({
    product_id: '',
    quantity: 1,
    unit_price: '',
    description: '',
    notes: '',
  });
  const [statusFormData, setStatusFormData] = useState<QuotationStatus>('draft');

  // Fetch quotations with filters
  const { data: quotationsData, isLoading: isLoadingQuotations, isError: isQuotationsError } = useQuery({
    queryKey: ['quotations', searchTerm, statusFilter],
    queryFn: () => quotationsApi.getAll({
      customer: searchTerm || undefined,
      status: statusFilter || undefined,
      limit: 20,
    }),
  });

  // Fetch customers for dropdown
  const { data: customersData } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.getAll({ limit: 100 }),
  });

  // Fetch products for items dropdown
  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.getAll({ limit: 100, active: true }),
  });

  // Fetch quotation items when details modal is open
  const { data: itemsData, refetch: refetchItems } = useQuery({
    queryKey: ['quotation-items', selectedQuotation?.id],
    queryFn: () => selectedQuotation ? quotationsApi.getItems(selectedQuotation.id) : Promise.resolve({ items: [], total: 0 }),
    enabled: !!selectedQuotation && isDetailsModalOpen,
  });

  // Create quotation mutation
  const createMutation = useMutation({
    mutationFn: quotationsApi.create,
    onSuccess: () => {
      toast.success(t('success.created'));
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsCreateModalOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message || t('errors.generic'));
    },
  });

  // Update quotation mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Quotation> }) => 
      quotationsApi.update(id, data),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      if (selectedQuotation) {
        refetchItems();
      }
    },
    onError: (error) => {
      toast.error(error.message || t('errors.generic'));
    },
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: QuotationStatus }) => 
      quotationsApi.updateStatus(id, status),
    onSuccess: () => {
      toast.success(t('success.updated'));
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsStatusModalOpen(false);
      if (selectedQuotation) {
        setSelectedQuotation({ ...selectedQuotation, status: statusFormData });
      }
    },
    onError: (error) => {
      toast.error(error.message || t('errors.generic'));
    },
  });

  // Add item mutation
  const addItemMutation = useMutation({
    mutationFn: ({ quotationId, item }: { quotationId: string; item: Partial<QuotationItem> }) =>
      quotationsApi.addItem(quotationId, item),
    onSuccess: () => {
      toast.success(t('success.created'));
      refetchItems();
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsItemModalOpen(false);
      resetItemForm();
    },
    onError: (error) => {
      toast.error(error.message || t('errors.generic'));
    },
  });

  // Update item mutation
  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, item }: { itemId: string; item: Partial<QuotationItem> }) =>
      quotationsApi.updateItem(itemId, item),
    onSuccess: () => {
      toast.success(t('success.updated'));
      refetchItems();
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsEditItemModalOpen(false);
      resetItemForm();
    },
    onError: (error) => {
      toast.error(error.message || t('errors.generic'));
    },
  });

  const resetForm = () => {
    setFormData({
      customer_id: '',
      quotation_date: new Date().toISOString().split('T')[0],
      discount: '0',
      notes: '',
    });
    setSelectedQuotation(null);
  };

  const resetItemForm = () => {
    setItemFormData({
      product_id: '',
      quantity: 1,
      unit_price: '',
      description: '',
      notes: '',
    });
    setSelectedItem(null);
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleStatusSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedQuotation) {
      updateStatusMutation.mutate({
        id: selectedQuotation.id,
        status: statusFormData,
      });
    }
  };

  const handleAddItemSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedQuotation) {
      addItemMutation.mutate({
        quotationId: selectedQuotation.id,
        item: itemFormData,
      });
    }
  };

  const handleEditItemSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedItem) {
      updateItemMutation.mutate({
        itemId: selectedItem.id,
        item: itemFormData,
      });
    }
  };

  const handleViewDetailsClick = (quotation: Quotation) => {
    setSelectedQuotation(quotation);
    setIsDetailsModalOpen(true);
  };

  const handleStatusChangeClick = (quotation: Quotation) => {
    setSelectedQuotation(quotation);
    setStatusFormData(quotation.status);
    setIsStatusModalOpen(true);
  };

  const handleEditItemClick = (item: QuotationItem) => {
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleItemInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setItemFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleItemSelectChange = (name: string, value: string | number) => {
    setItemFormData(prev => ({ ...prev, [name]: value }));
  };

  const getCustomerName = (customerId: string) => {
    const customer = customersData?.items.find(c => c.id === customerId);
    return customer ? customer.full_name : '-';
  };

  const getProductName = (productId: string) => {
    const product = productsData?.items.find(p => p.id === productId);
    return product ? product.name : '-';
  };

  const getStatusBadgeVariant = (status: QuotationStatus) => {
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

  const quotations = quotationsData?.items || [];
  const customers = customersData?.items || [];
  const products = productsData?.items || [];
  const items = itemsData?.items || [];
  const isLoadingMutation = createMutation.isPending || updateMutation.isPending || 
    updateStatusMutation.isPending || addItemMutation.isPending || updateItemMutation.isPending;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('quotations.title')}</h1>
          <p className="mt-1 text-sm text-gray-600">{t('quotations.subtitle')}</p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          {t('quotations.addQuotation')}
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('common.search')}
            </label>
            <div className="relative">
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder={t('quotations.searchQuotations')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pr-10"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('quotations.status')}
            </label>
            <Select
              value={statusFilter}
              onChange={(value) => setStatusFilter(value as QuotationStatus)}
              options={[
                { value: '', label: t('common.all') },
                { value: 'draft', label: t('quotationStatus.draft') },
                { value: 'waiting_for_measurement', label: t('quotationStatus.waiting_for_measurement') },
                { value: 'measured', label: t('quotationStatus.measured') },
                { value: 'under_negotiation', label: t('quotationStatus.under_negotiation') },
                { value: 'sent', label: t('quotationStatus.sent') },
                { value: 'approved', label: t('quotationStatus.approved') },
                { value: 'rejected', label: t('quotationStatus.rejected') },
                { value: 'cancelled', label: t('quotationStatus.cancelled') },
                { value: 'expired', label: t('quotationStatus.expired') },
              ]}
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoadingQuotations && (
        <div className="bg-white rounded-lg shadow p-12">
          <LoadingSpinner size="lg" text={t('common.loading')} />
        </div>
      )}

      {/* Error State */}
      {isQuotationsError && !isLoadingQuotations && (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('errors.generic')}</h3>
          <p className="text-gray-600">{t('errors.networkError')}</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoadingQuotations && !isQuotationsError && quotations.length === 0 && (
        <div className="bg-white rounded-lg shadow">
          <EmptyState
            title={t('common.noResults')}
            description={searchTerm || statusFilter ? t('common.noResults') : t('quotations.comingSoon')}
            action={
              <Button onClick={() => setIsCreateModalOpen(true)}>
                {t('quotations.addQuotation')}
              </Button>
            }
          />
        </div>
      )}

      {/* Quotations Table */}
      {!isLoadingQuotations && !isQuotationsError && quotations.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <Table>
            <TableHead>
              <TableHeaderCell>{t('quotations.quotationNumber')}</TableHeaderCell>
              <TableHeaderCell>{t('quotations.customer')}</TableHeaderCell>
              <TableHeaderCell>{t('quotations.quotationDate')}</TableHeaderCell>
              <TableHeaderCell>{t('quotations.status')}</TableHeaderCell>
              <TableHeaderCell>{t('quotations.finalPrice')}</TableHeaderCell>
              <TableHeaderCell>{t('common.actions')}</TableHeaderCell>
            </TableHead>
            <TableBody>
              {quotations.map((quotation) => (
                <TableRow key={quotation.id}>
                  <TableCell>
                    <div className="font-medium text-gray-900">{quotation.quotation_number}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-gray-900">{getCustomerName(quotation.customer_id)}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-gray-500">
                      {formatDate(quotation.quotation_date)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusBadgeVariant(quotation.status)} size="sm">
                      {t(`quotationStatus.${quotation.status}`)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-gray-900">
                      {formatCurrency(quotation.final_price)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewDetailsClick(quotation)}
                        className="text-blue-600 hover:text-blue-800"
                        title={t('common.details')}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStatusChangeClick(quotation)}
                        className="text-green-600 hover:text-green-800"
                        title={t('quotations.changeStatus')}
                      >
                        <DollarSign className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Create Quotation Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title={t('quotations.addQuotation')}
        size="lg"
      >
        <form onSubmit={handleCreateSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.customer')}
                <span className="text-red-500 mr-1">*</span>
              </label>
              <Select
                value={formData.customer_id}
                onChange={(value) => handleSelectChange('customer_id', value)}
                options={customers.map(customer => ({ 
                  value: customer.id, 
                  label: customer.full_name 
                }))}
                placeholder={t('quotations.selectCustomer')}
                required
              />
            </div>
            <Input
              label={t('quotations.quotationDate')}
              name="quotation_date"
              type="date"
              value={formData.quotation_date}
              onChange={handleInputChange}
              required
            />
            <Input
              label={t('quotations.discount')}
              name="discount"
              type="number"
              value={formData.discount}
              onChange={handleInputChange}
              min="0"
              step="0.01"
              dir="ltr"
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.notes')}
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[100px] text-right"
                dir="rtl"
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end pt-6 mt-6 border-t border-gray-200">
            <Button
              variant="ghost"
              type="button"
              onClick={() => {
                setIsCreateModalOpen(false);
                resetForm();
              }}
              disabled={isLoadingMutation}
            >
              {t('common.cancel')}
            </Button>
            <Button
              type="submit"
              loading={createMutation.isPending}
              disabled={isLoadingMutation}
            >
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Quotation Details Modal */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedQuotation(null);
        }}
        title={t('quotations.quotationDetails')}
        size="xl"
      >
        {selectedQuotation && (
          <div className="space-y-6">
            {/* Quotation Info */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="text-sm text-gray-600">{t('quotations.quotationNumber')}</div>
                <div className="font-medium">{selectedQuotation.quotation_number}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">{t('quotations.customer')}</div>
                <div className="font-medium">{getCustomerName(selectedQuotation.customer_id)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">{t('quotations.quotationDate')}</div>
                <div className="font-medium">{formatDate(selectedQuotation.quotation_date)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">{t('quotations.status')}</div>
                <Badge variant={getStatusBadgeVariant(selectedQuotation.status)}>
                  {t(`quotationStatus.${selectedQuotation.status}`)}
                </Badge>
              </div>
            </div>

            {/* Items Section */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium">{t('quotations.items')}</h3>
                <Button
                  size="sm"
                  onClick={() => setIsItemModalOpen(true)}
                  className="flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  {t('quotations.addItem')}
                </Button>
              </div>

              {items.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  {t('common.noResults')}
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.product')}</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.quantity')}</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.unitPrice')}</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('quotations.total')}</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('common.actions')}</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {items.map((item) => (
                        <tr key={item.id}>
                          <td className="px-4 py-3 text-sm text-gray-900">{getProductName(item.product_id)}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{item.quantity}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{formatCurrency(item.unit_price)}</td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(item.total_price)}</td>
                          <td className="px-4 py-3 text-sm">
                            <div className="flex items-center gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEditItemClick(item)}
                                className="text-blue-600 hover:text-blue-800"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Totals Section */}
            <div className="border-t pt-4">
              <div className="space-y-2 max-w-md mr-auto">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">{t('quotations.totalPrice')}:</span>
                  <span className="font-medium">{formatCurrency(selectedQuotation.total_price)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">{t('quotations.discount')}:</span>
                  <span className="font-medium">{formatCurrency(selectedQuotation.discount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>{t('quotations.finalPrice')}:</span>
                  <span>{formatCurrency(selectedQuotation.final_price)}</span>
                </div>
              </div>
            </div>

            {selectedQuotation.notes && (
              <div>
                <div className="text-sm text-gray-600 mb-1">{t('quotations.notes')}:</div>
                <div className="p-3 bg-gray-50 rounded text-sm">{selectedQuotation.notes}</div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Add Item Modal */}
      <Modal
        isOpen={isItemModalOpen}
        onClose={() => {
          setIsItemModalOpen(false);
          resetItemForm();
        }}
        title={t('quotations.addItem')}
        size="lg"
      >
        <form onSubmit={handleAddItemSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.product')}
                <span className="text-red-500 mr-1">*</span>
              </label>
              <Select
                value={itemFormData.product_id}
                onChange={(value) => handleItemSelectChange('product_id', value)}
                options={products.map(product => ({ 
                  value: product.id, 
                  label: product.name 
                }))}
                placeholder={t('common.search')}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label={t('quotations.quantity')}
                name="quantity"
                type="number"
                value={itemFormData.quantity}
                onChange={handleItemInputChange}
                min="1"
                required
                dir="ltr"
              />
              <Input
                label={t('quotations.unitPrice')}
                name="unit_price"
                type="number"
                value={itemFormData.unit_price}
                onChange={handleItemInputChange}
                min="0"
                step="0.01"
                required
                dir="ltr"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('products.description')}
              </label>
              <textarea
                name="description"
                value={itemFormData.description}
                onChange={handleItemInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[80px] text-right"
                dir="rtl"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.notes')}
              </label>
              <textarea
                name="notes"
                value={itemFormData.notes}
                onChange={handleItemInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[60px] text-right"
                dir="rtl"
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end pt-6 mt-6 border-t border-gray-200">
            <Button
              variant="ghost"
              type="button"
              onClick={() => {
                setIsItemModalOpen(false);
                resetItemForm();
              }}
              disabled={isLoadingMutation}
            >
              {t('common.cancel')}
            </Button>
            <Button
              type="submit"
              loading={addItemMutation.isPending}
              disabled={isLoadingMutation}
            >
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Item Modal */}
      <Modal
        isOpen={isEditItemModalOpen}
        onClose={() => {
          setIsEditItemModalOpen(false);
          resetItemForm();
        }}
        title={t('quotations.editItem')}
        size="lg"
      >
        <form onSubmit={handleEditItemSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.product')}
                <span className="text-red-500 mr-1">*</span>
              </label>
              <Select
                value={itemFormData.product_id}
                onChange={(value) => handleItemSelectChange('product_id', value)}
                options={products.map(product => ({ 
                  value: product.id, 
                  label: product.name 
                }))}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label={t('quotations.quantity')}
                name="quantity"
                type="number"
                value={itemFormData.quantity}
                onChange={handleItemInputChange}
                min="1"
                required
                dir="ltr"
              />
              <Input
                label={t('quotations.unitPrice')}
                name="unit_price"
                type="number"
                value={itemFormData.unit_price}
                onChange={handleItemInputChange}
                min="0"
                step="0.01"
                required
                dir="ltr"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('products.description')}
              </label>
              <textarea
                name="description"
                value={itemFormData.description}
                onChange={handleItemInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[80px] text-right"
                dir="rtl"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.notes')}
              </label>
              <textarea
                name="notes"
                value={itemFormData.notes}
                onChange={handleItemInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[60px] text-right"
                dir="rtl"
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end pt-6 mt-6 border-t border-gray-200">
            <Button
              variant="ghost"
              type="button"
              onClick={() => {
                setIsEditItemModalOpen(false);
                resetItemForm();
              }}
              disabled={isLoadingMutation}
            >
              {t('common.cancel')}
            </Button>
            <Button
              type="submit"
              loading={updateItemMutation.isPending}
              disabled={isLoadingMutation}
            >
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Change Status Modal */}
      <Modal
        isOpen={isStatusModalOpen}
        onClose={() => {
          setIsStatusModalOpen(false);
          setSelectedQuotation(null);
        }}
        title={t('quotations.changeStatus')}
        size="md"
      >
        <form onSubmit={handleStatusSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('quotations.status')}
                <span className="text-red-500 mr-1">*</span>
              </label>
              <Select
                value={statusFormData}
                onChange={(value) => setStatusFormData(value as QuotationStatus)}
                options={[
                  { value: 'draft', label: t('quotationStatus.draft') },
                  { value: 'waiting_for_measurement', label: t('quotationStatus.waiting_for_measurement') },
                  { value: 'measured', label: t('quotationStatus.measured') },
                  { value: 'under_negotiation', label: t('quotationStatus.under_negotiation') },
                  { value: 'sent', label: t('quotationStatus.sent') },
                  { value: 'approved', label: t('quotationStatus.approved') },
                  { value: 'rejected', label: t('quotationStatus.rejected') },
                  { value: 'cancelled', label: t('quotationStatus.cancelled') },
                  { value: 'expired', label: t('quotationStatus.expired') },
                ]}
                required
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end pt-6 mt-6 border-t border-gray-200">
            <Button
              variant="ghost"
              type="button"
              onClick={() => {
                setIsStatusModalOpen(false);
                setSelectedQuotation(null);
              }}
              disabled={isLoadingMutation}
            >
              {t('common.cancel')}
            </Button>
            <Button
              type="submit"
              loading={updateStatusMutation.isPending}
              disabled={isLoadingMutation}
            >
              {t('common.save')}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
