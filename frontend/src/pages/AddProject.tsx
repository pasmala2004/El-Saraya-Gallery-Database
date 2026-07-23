import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { ArrowLeft, Plus, Trash2, Save } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import { quotationsApi } from '../services/quotations';
import { jobsApi } from '../services/jobs';
import { customersApi } from '../services/customers';
import { productsApi } from '../services/products';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import LoadingSpinner from '../components/LoadingSpinner';

interface QuotationItem {
  product_id: string;
  product_name?: string;
  quantity: number;
  unit_price: string;
  total_price: string;
  description?: string;
}

export default function AddProject() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [customer_id, setCustomerId] = useState('');
  const [items, setItems] = useState<QuotationItem[]>([]);
  const [discount, setDiscount] = useState('0');
  const [quotationDate, setQuotationDate] = useState(new Date().toISOString().split('T')[0]);
  
  const [jobData, setJobData] = useState({
    measurement_date: '',
    production_start: '',
    production_end: '',
    installation_date: '',
    delivery_date: '',
    notes: '',
  });

  // Fetch customers
  const { data: customersData, isLoading: loadingCustomers, error: customersError } = useQuery({
    queryKey: ['customers'],
    queryFn: async () => {
      console.log('Fetching customers...');
      try {
        const result = await customersApi.getAll({ limit: 100 });
        console.log('Customers fetched successfully:', result);
        return result;
      } catch (err) {
        console.error('Customer fetch error:', err);
        throw err;
      }
    },
  });

  // Fetch products
  const { data: productsData, isLoading: loadingProducts, error: productsError } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      console.log('Fetching products...');
      try {
        const result = await productsApi.getAll({ limit: 100, active: true });
        console.log('Products fetched successfully:', result);
        return result;
      } catch (err) {
        console.error('Product fetch error:', err);
        throw err;
      }
    },
  });

  const customers = customersData?.items || [];
  const products = productsData?.items || [];

  console.log('Render state:', { 
    customers: customers.length, 
    products: products.length,
    loadingCustomers,
    loadingProducts,
    customersError: customersError ? (customersError as Error).message : null,
    productsError: productsError ? (productsError as Error).message : null,
    customersData,
    productsData
  });

  // Calculate totals
  const subtotal = items.reduce((sum, item) => sum + parseFloat(item.total_price || '0'), 0);
  const discountAmount = (subtotal * parseFloat(discount)) / 100;
  const total = subtotal - discountAmount;
  const deposit = total * 0.7;
  const remaining = total - deposit;

  // Create project mutation
  const createProjectMutation = useMutation({
    mutationFn: async () => {
      // Step 1: Create quotation in draft
      const quotation = await quotationsApi.create({
        customer_id,
        quotation_date: quotationDate,
        status: 'draft',
        total_price: subtotal.toString(),
        discount: discountAmount.toString(),
        final_price: total.toString(),
        notes: jobData.notes,
      });

      // Step 2: Add items to quotation
      for (const item of items) {
        await quotationsApi.addItem(quotation.id, {
          product_id: item.product_id,
          quantity: item.quantity,
          unit_price: item.unit_price,
          total_price: item.total_price,
          description: item.description,
        });
      }

      // Step 3: Progress quotation through required workflow stages
      // draft → waiting_for_measurement → measured → sent → approved
      await quotationsApi.updateStatus(quotation.id, 'waiting_for_measurement');
      await quotationsApi.updateStatus(quotation.id, 'measured');
      await quotationsApi.updateStatus(quotation.id, 'sent');
      
      // Step 4: Approve quotation (creates job automatically)
      const result = await quotationsApi.updateStatus(quotation.id, 'approved');
      
      // Step 5: Update job with dates
      if (result.job) {
        await jobsApi.update(result.job.id, {
          measurement_date: jobData.measurement_date || undefined,
          production_start: jobData.production_start || undefined,
          production_end: jobData.production_end || undefined,
          installation_date: jobData.installation_date || undefined,
          delivery_date: jobData.delivery_date || undefined,
          notes: jobData.notes || undefined,
        });
        return result.job.id;
      }
      
      throw new Error('Job creation failed');
    },
    onSuccess: (jobId) => {
      navigate(`/jobs/${jobId}`);
    },
  });

  const addItem = () => {
    setItems([...items, {
      product_id: '',
      quantity: 1,
      unit_price: '0',
      total_price: '0',
    }]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof QuotationItem, value: string | number) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // Calculate total_price
    if (field === 'quantity' || field === 'unit_price') {
      const qty = field === 'quantity' ? Number(value) : newItems[index].quantity;
      const price = field === 'unit_price' ? value : newItems[index].unit_price;
      newItems[index].total_price = (qty * parseFloat(price.toString())).toString();
    }
    
    // Update product name
    if (field === 'product_id') {
      const product = products.find(p => p.id === value);
      newItems[index].product_name = product?.name;
    }
    
    setItems(newItems);
  };

  const handleSubmit = () => {
    if (!customer_id) {
      alert('الرجاء اختيار عميل');
      return;
    }
    if (items.length === 0) {
      alert('الرجاء إضافة منتج واحد على الأقل');
      return;
    }
    createProjectMutation.mutate();
  };

  const canProceedToStep2 = customer_id && items.length > 0 && items.every(i => i.product_id && i.quantity > 0);
  const canSubmit = canProceedToStep2;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('projects.addProject')}</h1>
          <p className="text-sm text-gray-600 mt-1">إنشاء مشروع جديد مع عرض السعر</p>
        </div>
      </div>

      {/* Steps Indicator */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-center gap-4">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>1</div>
            <span className="font-medium">العميل والمنتجات</span>
          </div>
          <div className="w-16 h-1 bg-gray-200"></div>
          <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>2</div>
            <span className="font-medium">تفاصيل المشروع</span>
          </div>
        </div>
      </div>

      {/* Step 1: Customer & Products */}
      {step === 1 && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          {/* Error Display for Debugging */}
          {(customersError || productsError) && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg space-y-2">
              {customersError && (
                <div className="text-red-700 text-sm">
                  <strong>خطأ في تحميل العملاء:</strong> {(customersError as Error).message}
                </div>
              )}
              {productsError && (
                <div className="text-red-700 text-sm">
                  <strong>خطأ في تحميل المنتجات:</strong> {(productsError as Error).message}
                </div>
              )}
            </div>
          )}

          {/* Customer Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              العميل <span className="text-red-500">*</span>
            </label>
            {loadingCustomers ? (
              <LoadingSpinner size="sm" />
            ) : (
              <>
                <Select value={customer_id} onChange={(value) => setCustomerId(value)} required>
                  <option value="">اختر العميل</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.full_name} - {c.phone_number}
                    </option>
                  ))}
                </Select>
                {customers.length === 0 && !loadingCustomers && (
                  <p className="text-sm text-amber-600 mt-1">لم يتم العثور على عملاء</p>
                )}
              </>
            )}
          </div>

          {/* Quotation Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              تاريخ عرض السعر
            </label>
            <Input
              type="date"
              value={quotationDate}
              onChange={(e) => setQuotationDate(e.target.value)}
            />
          </div>

          {/* Products */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                المنتجات <span className="text-red-500">*</span>
              </label>
              <Button variant="outline" size="sm" onClick={addItem} className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                إضافة منتج
              </Button>
            </div>

            {items.length === 0 ? (
              <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg border-2 border-dashed">
                لم يتم إضافة منتجات بعد
              </div>
            ) : (
              <div className="space-y-3">
                {items.map((item, index) => (
                  <div key={index} className="flex gap-3 items-start p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1 grid grid-cols-4 gap-3">
                      <div className="col-span-2">
                        {loadingProducts ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Select
                            value={item.product_id}
                            onChange={(value) => updateItem(index, 'product_id', value)}
                            required
                          >
                            <option value="">اختر المنتج</option>
                            {products.map((p) => (
                              <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                          </Select>
                        )}
                        {products.length === 0 && !loadingProducts && (
                          <p className="text-xs text-amber-600 mt-1">لم يتم العثور على منتجات</p>
                        )}
                      </div>
                      <div>
                        <Input
                          type="number"
                          min="1"
                          placeholder="الكمية"
                          value={item.quantity}
                          onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                        />
                      </div>
                      <div>
                        <Input
                          type="number"
                          min="0"
                          step="0.01"
                          placeholder="السعر"
                          value={item.unit_price}
                          onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
                        />
                      </div>
                    </div>
                    <div className="text-sm font-semibold text-gray-900 pt-2 w-24 text-left">
                      {parseFloat(item.total_price).toLocaleString()} ج.م
                    </div>
                    <button
                      onClick={() => removeItem(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quotation Summary */}
          {items.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
              <h3 className="font-semibold text-blue-900 mb-3">ملخص عرض السعر</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">المجموع الفرعي:</span>
                  <span className="font-semibold text-blue-900">{subtotal.toLocaleString()} ج.م</span>
                </div>
                <div className="flex justify-between items-center gap-2">
                  <span className="text-blue-700">الخصم:</span>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={discount}
                      onChange={(e) => setDiscount(e.target.value)}
                      className="w-20 text-center"
                    />
                    <span>%</span>
                    <span className="font-semibold text-blue-900">({discountAmount.toLocaleString()} ج.م)</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700 font-semibold">الإجمالي:</span>
                  <span className="font-bold text-blue-900 text-lg">{total.toLocaleString()} ج.م</span>
                </div>
                <div></div>
                <div className="flex justify-between">
                  <span className="text-blue-700">العربون (70%):</span>
                  <span className="font-semibold text-green-600">{deposit.toLocaleString()} ج.م</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">المتبقي:</span>
                  <span className="font-semibold text-red-600">{remaining.toLocaleString()} ج.م</span>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={() => navigate(-1)}>
              إلغاء
            </Button>
            <Button onClick={() => setStep(2)} disabled={!canProceedToStep2}>
              التالي: تفاصيل المشروع
            </Button>
          </div>
        </div>
      )}

      {/* Step 2: Project Details */}
      {step === 2 && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تاريخ القياس
              </label>
              <Input
                type="date"
                value={jobData.measurement_date}
                onChange={(e) => setJobData({...jobData, measurement_date: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                بداية التصنيع
              </label>
              <Input
                type="date"
                value={jobData.production_start}
                onChange={(e) => setJobData({...jobData, production_start: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نهاية التصنيع
              </label>
              <Input
                type="date"
                value={jobData.production_end}
                onChange={(e) => setJobData({...jobData, production_end: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تاريخ التركيب
              </label>
              <Input
                type="date"
                value={jobData.installation_date}
                onChange={(e) => setJobData({...jobData, installation_date: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تاريخ التسليم
              </label>
              <Input
                type="date"
                value={jobData.delivery_date}
                onChange={(e) => setJobData({...jobData, delivery_date: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ملاحظات
            </label>
            <textarea
              value={jobData.notes}
              onChange={(e) => setJobData({...jobData, notes: e.target.value})}
              placeholder="أضف ملاحظات عن المشروع..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-between pt-4 border-t">
            <Button variant="outline" onClick={() => setStep(1)}>
              رجوع
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={createProjectMutation.isPending || !canSubmit}
              className="flex items-center gap-2"
            >
              {createProjectMutation.isPending ? (
                <>
                  <LoadingSpinner size="sm" />
                  جاري الإنشاء...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  إنشاء المشروع
                </>
              )}
            </Button>
          </div>

          {createProjectMutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
              خطأ: {(createProjectMutation.error as Error).message}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
