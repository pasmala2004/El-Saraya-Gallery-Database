# Dashboard KPIs - Frontend Implementation Guide

**Date:** July 22, 2026  
**For:** Frontend Development Team  
**Backend API:** Ready and tested ✅  

---

## Overview

The dashboard KPIs have been redesigned to provide **actionable operational metrics** for daily ERP usage. Each KPI is clickable and filters the Projects page to show relevant items.

---

## API Response Structure

### Endpoint
```
GET /api/v1/dashboard
```

### Response (KPIs section)

```json
{
  "kpis": {
    "active_jobs": 23,
    "pending_quotations": 8,
    "measurements_scheduled_today": 3,
    "installations_scheduled_today": 2,
    "manufacturing_queue": 12,
    "completed_last_7_days": 4,
    "maintenance_jobs": 0,
    "late_manufacturing": 2,
    "overdue_payments": 5,
    "delayed_projects": 3
  },
  "pipeline": { /* ... */ },
  "alerts": [ /* ... */ ],
  "recentActivity": [ /* ... */ ],
  "metadata": {
    "generated_at": "2026-07-22T16:30:00Z",
    "execution_time_ms": 245
  }
}
```

---

## KPI Cards Implementation

### 1. Active Jobs

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.activeJobs')}
  value={kpis.active_jobs}
  icon={<BriefcaseIcon />}
  color={getColor('active_jobs', kpis.active_jobs)}
  tooltip={t('dashboard.kpis.activeJobsTooltip')}
  onClick={() => navigate('/projects?filter=active')}
/>
```

**Color Logic:**
```typescript
if (value < 50) return 'green';   // Healthy
if (value < 100) return 'orange'; // Warning
return 'red';                     // Critical
```

**Filter:** Shows jobs with status not in [completed, cancelled]

---

### 2. Pending Quotations

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.pendingQuotations')}
  value={kpis.pending_quotations}
  icon={<DocumentIcon />}
  color={getColor('pending_quotations', kpis.pending_quotations)}
  tooltip={t('dashboard.kpis.pendingQuotationsTooltip')}
  onClick={() => navigate('/quotations?status=sent,under_negotiation')}
/>
```

**Color Logic:**
```typescript
if (value < 10) return 'green';
if (value < 20) return 'orange';
return 'red';
```

**Filter:** Quotations with status = sent OR under_negotiation

---

### 3. Measurements Scheduled Today

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.measurementsToday')}
  value={kpis.measurements_scheduled_today}
  icon={<RulerIcon />}
  color={getColor('measurements_today', kpis.measurements_scheduled_today)}
  tooltip={t('dashboard.kpis.measurementsTodayTooltip')}
  onClick={() => navigate('/projects?measurement_date=today')}
  badge={value > 0 ? 'Today' : null}
/>
```

**Color Logic:**
```typescript
if (value === 0) return 'gray';
if (value < 5) return 'green';
if (value < 10) return 'orange';
return 'red';
```

**Filter:** Jobs with measurement_date = today

---

### 4. Installations Scheduled Today

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.installationsToday')}
  value={kpis.installations_scheduled_today}
  icon={<WrenchIcon />}
  color={getColor('installations_today', kpis.installations_scheduled_today)}
  tooltip={t('dashboard.kpis.installationsTodayTooltip')}
  onClick={() => navigate('/projects?installation_date=today')}
  badge={value > 0 ? 'Today' : null}
/>
```

**Color Logic:**
```typescript
if (value === 0) return 'gray';
if (value < 3) return 'green';
if (value < 5) return 'orange';
return 'red';
```

**Filter:** Jobs with installation_date = today

---

### 5. Manufacturing Queue

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.manufacturingQueue')}
  value={kpis.manufacturing_queue}
  icon={<FactoryIcon />}
  color={getColor('manufacturing_queue', kpis.manufacturing_queue)}
  tooltip={t('dashboard.kpis.manufacturingQueueTooltip')}
  onClick={() => navigate('/projects?status=in_production')}
/>
```

**Color Logic:**
```typescript
if (value < 10) return 'green';
if (value < 20) return 'orange';
return 'red';
```

**Filter:** Jobs with status = in_production

---

### 6. Completed Projects (Last 7 Days)

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.completedLast7Days')}
  value={kpis.completed_last_7_days}
  icon={<CheckCircleIcon />}
  color={getColor('completed_last_7', kpis.completed_last_7_days)}
  tooltip={t('dashboard.kpis.completedLast7DaysTooltip')}
  onClick={() => navigate('/projects?status=completed&period=last_7_days')}
  trend="up"
/>
```

**Color Logic:**
```typescript
if (value >= 5) return 'green';  // Good progress
if (value >= 2) return 'orange';
return 'red';                    // Low completion rate
```

**Filter:** Jobs completed in last 7 days

---

### 7. Maintenance Jobs

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.maintenanceJobs')}
  value={kpis.maintenance_jobs}
  icon={<ToolIcon />}
  color="gray"
  tooltip={t('dashboard.kpis.maintenanceJobsTooltip')}
  onClick={() => navigate('/projects?filter=maintenance')}
  badge="Coming Soon"
  disabled={kpis.maintenance_jobs === 0}
/>
```

**Color Logic:**
```typescript
// Currently always 0 (placeholder)
if (value === 0) return 'gray';
if (value < 5) return 'green';
if (value < 10) return 'orange';
return 'red';
```

**Filter:** Jobs in maintenance phase (future feature)

---

### 8. Late Manufacturing (CRITICAL) 🚨

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.lateManufacturing')}
  subtitle="Deposit Paid • Not Started"
  value={kpis.late_manufacturing}
  icon={<AlertTriangleIcon />}
  color={kpis.late_manufacturing > 0 ? 'red' : 'green'}
  tooltip={t('dashboard.kpis.lateManufacturingTooltip')}
  onClick={() => navigate('/projects?filter=late_manufacturing')}
  severity="critical"
  pulse={kpis.late_manufacturing > 0}
/>
```

**Color Logic:**
```typescript
// Always critical if any exist
if (value > 0) return 'red';
return 'green';
```

**Explanation:**
This KPI identifies critical projects where:
1. Customer paid deposit
2. Manufacturing has NOT started
3. Expected start date passed

This is **business-critical** because we have the customer's money but haven't started work.

**Filter:** Complex filter:
- Payment type = deposit AND status = paid
- Job status = pending OR measuring
- Expected start date < today

---

### 9. Overdue Payments

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.overduePayments')}
  value={kpis.overdue_payments}
  icon={<CurrencyIcon />}
  color={kpis.overdue_payments > 0 ? 'red' : 'green'}
  tooltip={t('dashboard.kpis.overduePaymentsTooltip')}
  onClick={() => navigate('/projects?filter=overdue_payments')}
  severity="high"
/>
```

**Color Logic:**
```typescript
if (value === 0) return 'green';
return 'red';  // Any overdue is critical
```

**Filter:** Jobs with payments where status = overdue

---

### 10. Delayed Projects

**Display:**
```typescript
<KPICard
  title={t('dashboard.kpis.delayedProjects')}
  value={kpis.delayed_projects}
  icon={<ClockIcon />}
  color={kpis.delayed_projects > 0 ? 'orange' : 'green'}
  tooltip={t('dashboard.kpis.delayedProjectsTooltip')}
  onClick={() => navigate('/projects?filter=delayed')}
/>
```

**Color Logic:**
```typescript
if (value === 0) return 'green';
if (value < 5) return 'orange';
return 'red';
```

**Filter:** Jobs where:
- installation_date < today
- status != completed AND status != cancelled

---

## Complete React Component Example

```typescript
// src/components/Dashboard/KPIGrid.tsx

import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useDashboard } from '@/hooks/useDashboard';
import { KPICard } from './KPICard';
import {
  BriefcaseIcon,
  DocumentIcon,
  RulerIcon,
  WrenchIcon,
  FactoryIcon,
  CheckCircleIcon,
  ToolIcon,
  AlertTriangleIcon,
  CurrencyIcon,
  ClockIcon,
} from '@/icons';

export const KPIGrid: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { data: dashboard, isLoading } = useDashboard();

  if (isLoading) return <KPIGridSkeleton />;
  if (!dashboard) return null;

  const { kpis } = dashboard;

  const getKPIColor = (kpi: string, value: number): string => {
    switch (kpi) {
      case 'active_jobs':
        if (value < 50) return 'green';
        if (value < 100) return 'orange';
        return 'red';
      
      case 'pending_quotations':
        if (value < 10) return 'green';
        if (value < 20) return 'orange';
        return 'red';
      
      case 'measurements_today':
      case 'installations_today':
        if (value === 0) return 'gray';
        if (value < 5) return 'green';
        if (value < 10) return 'orange';
        return 'red';
      
      case 'manufacturing_queue':
        if (value < 10) return 'green';
        if (value < 20) return 'orange';
        return 'red';
      
      case 'completed_last_7':
        if (value >= 5) return 'green';
        if (value >= 2) return 'orange';
        return 'red';
      
      case 'late_manufacturing':
      case 'overdue_payments':
        return value > 0 ? 'red' : 'green';
      
      case 'delayed_projects':
        if (value === 0) return 'green';
        if (value < 5) return 'orange';
        return 'red';
      
      default:
        return 'gray';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Row 1: Active Projects */}
      <KPICard
        title={t('dashboard.kpis.activeJobs')}
        value={kpis.active_jobs}
        icon={<BriefcaseIcon />}
        color={getKPIColor('active_jobs', kpis.active_jobs)}
        tooltip={t('dashboard.tooltips.activeJobs')}
        onClick={() => navigate('/projects?filter=active')}
      />

      <KPICard
        title={t('dashboard.kpis.pendingQuotations')}
        value={kpis.pending_quotations}
        icon={<DocumentIcon />}
        color={getKPIColor('pending_quotations', kpis.pending_quotations)}
        tooltip={t('dashboard.tooltips.pendingQuotations')}
        onClick={() => navigate('/quotations?status=sent,under_negotiation')}
      />

      <KPICard
        title={t('dashboard.kpis.measurementsToday')}
        value={kpis.measurements_scheduled_today}
        icon={<RulerIcon />}
        color={getKPIColor('measurements_today', kpis.measurements_scheduled_today)}
        tooltip={t('dashboard.tooltips.measurementsToday')}
        onClick={() => navigate('/projects?measurement_date=today')}
        badge={kpis.measurements_scheduled_today > 0 ? 'Today' : null}
      />

      <KPICard
        title={t('dashboard.kpis.installationsToday')}
        value={kpis.installations_scheduled_today}
        icon={<WrenchIcon />}
        color={getKPIColor('installations_today', kpis.installations_scheduled_today)}
        tooltip={t('dashboard.tooltips.installationsToday')}
        onClick={() => navigate('/projects?installation_date=today')}
        badge={kpis.installations_scheduled_today > 0 ? 'Today' : null}
      />

      <KPICard
        title={t('dashboard.kpis.manufacturingQueue')}
        value={kpis.manufacturing_queue}
        icon={<FactoryIcon />}
        color={getKPIColor('manufacturing_queue', kpis.manufacturing_queue)}
        tooltip={t('dashboard.tooltips.manufacturingQueue')}
        onClick={() => navigate('/projects?status=in_production')}
      />

      {/* Row 2: Progress & Issues */}
      <KPICard
        title={t('dashboard.kpis.completedLast7Days')}
        value={kpis.completed_last_7_days}
        icon={<CheckCircleIcon />}
        color={getKPIColor('completed_last_7', kpis.completed_last_7_days)}
        tooltip={t('dashboard.tooltips.completedLast7Days')}
        onClick={() => navigate('/projects?status=completed&period=last_7_days')}
        trend="up"
      />

      <KPICard
        title={t('dashboard.kpis.maintenanceJobs')}
        value={kpis.maintenance_jobs}
        icon={<ToolIcon />}
        color="gray"
        tooltip={t('dashboard.tooltips.maintenanceJobs')}
        onClick={() => navigate('/projects?filter=maintenance')}
        badge="Coming Soon"
        disabled={kpis.maintenance_jobs === 0}
      />

      <KPICard
        title={t('dashboard.kpis.lateManufacturing')}
        subtitle="Deposit Paid • Not Started"
        value={kpis.late_manufacturing}
        icon={<AlertTriangleIcon />}
        color={kpis.late_manufacturing > 0 ? 'red' : 'green'}
        tooltip={t('dashboard.tooltips.lateManufacturing')}
        onClick={() => navigate('/projects?filter=late_manufacturing')}
        severity="critical"
        pulse={kpis.late_manufacturing > 0}
      />

      <KPICard
        title={t('dashboard.kpis.overduePayments')}
        value={kpis.overdue_payments}
        icon={<CurrencyIcon />}
        color={kpis.overdue_payments > 0 ? 'red' : 'green'}
        tooltip={t('dashboard.tooltips.overduePayments')}
        onClick={() => navigate('/projects?filter=overdue_payments')}
        severity="high"
      />

      <KPICard
        title={t('dashboard.kpis.delayedProjects')}
        value={kpis.delayed_projects}
        icon={<ClockIcon />}
        color={kpis.delayed_projects > 0 ? 'orange' : 'green'}
        tooltip={t('dashboard.tooltips.delayedProjects')}
        onClick={() => navigate('/projects?filter=delayed')}
      />
    </div>
  );
};
```

---

## Translation Keys

### English (en.json)

```json
{
  "dashboard": {
    "kpis": {
      "activeJobs": "Active Jobs",
      "pendingQuotations": "Pending Quotations",
      "measurementsToday": "Measurements Today",
      "installationsToday": "Installations Today",
      "manufacturingQueue": "Manufacturing Queue",
      "completedLast7Days": "Completed (7 Days)",
      "maintenanceJobs": "Maintenance Jobs",
      "lateManufacturing": "Late Manufacturing",
      "overduePayments": "Overdue Payments",
      "delayedProjects": "Delayed Projects"
    },
    "tooltips": {
      "activeJobs": "Jobs currently in progress (not completed or cancelled)",
      "pendingQuotations": "Quotations sent to customers awaiting approval",
      "measurementsToday": "Measurements scheduled for today",
      "installationsToday": "Installations scheduled for today",
      "manufacturingQueue": "Jobs currently being manufactured",
      "completedLast7Days": "Projects completed in the last week",
      "maintenanceJobs": "Projects in maintenance phase",
      "lateManufacturing": "CRITICAL: Deposit paid but manufacturing not started (overdue)",
      "overduePayments": "Projects with unpaid overdue payments",
      "delayedProjects": "Projects past planned completion date"
    }
  }
}
```

### Arabic (ar.json)

```json
{
  "dashboard": {
    "kpis": {
      "activeJobs": "المشاريع النشطة",
      "pendingQuotations": "عروض الأسعار المعلقة",
      "measurementsToday": "قياسات اليوم",
      "installationsToday": "تركيبات اليوم",
      "manufacturingQueue": "طابور التصنيع",
      "completedLast7Days": "مكتمل (7 أيام)",
      "maintenanceJobs": "مشاريع الصيانة",
      "lateManufacturing": "تصنيع متأخر",
      "overduePayments": "مدفوعات متأخرة",
      "delayedProjects": "مشاريع متأخرة"
    },
    "tooltips": {
      "activeJobs": "المشاريع قيد التنفيذ حاليًا (غير مكتملة أو ملغاة)",
      "pendingQuotations": "عروض الأسعار المرسلة للعملاء في انتظار الموافقة",
      "measurementsToday": "القياسات المجدولة لهذا اليوم",
      "installationsToday": "التركيبات المجدولة لهذا اليوم",
      "manufacturingQueue": "المشاريع قيد التصنيع حاليًا",
      "completedLast7Days": "المشاريع المكتملة خلال الأسبوع الماضي",
      "maintenanceJobs": "المشاريع في مرحلة الصيانة",
      "lateManufacturing": "حرج: تم دفع العربون ولكن لم يبدأ التصنيع (متأخر)",
      "overduePayments": "مشاريع ذات مدفوعات متأخرة غير مدفوعة",
      "delayedProjects": "مشاريع تجاوزت تاريخ الإكمال المخطط"
    }
  }
}
```

---

## Projects Page Filter Implementation

The Projects page needs to support filtering based on KPI clicks:

```typescript
// src/pages/Projects.tsx

import { useSearchParams } from 'react-router-dom';

const Projects: React.FC = () => {
  const [searchParams] = useSearchParams();
  const filter = searchParams.get('filter');
  const status = searchParams.get('status');
  const measurementDate = searchParams.get('measurement_date');
  const installationDate = searchParams.get('installation_date');

  // Apply filters to job query
  const filters: JobFilters = {};

  if (filter === 'active') {
    filters.status = ['pending', 'measuring', 'in_production', 'ready_for_installation', 'installed'];
  } else if (filter === 'late_manufacturing') {
    filters.hasDepositPaid = true;
    filters.status = ['pending', 'measuring'];
    filters.expectedStartPassed = true;
  } else if (filter === 'overdue_payments') {
    filters.hasOverduePayments = true;
  } else if (filter === 'delayed') {
    filters.installationDatePassed = true;
    filters.statusNot = ['completed', 'cancelled'];
  } else if (status) {
    filters.status = status.split(',');
  }

  if (measurementDate === 'today') {
    filters.measurementDate = new Date().toISOString().split('T')[0];
  }

  if (installationDate === 'today') {
    filters.installationDate = new Date().toISOString().split('T')[0];
  }

  const { data: jobs } = useJobs(filters);

  return (
    <div>
      {filter && <ActiveFilterBadge filter={filter} />}
      <JobsTable jobs={jobs} />
    </div>
  );
};
```

---

## Summary

### For Frontend Team:

1. ✅ Update Dashboard component to use new KPI structure
2. ✅ Implement 10 clickable KPI cards
3. ✅ Add color coding based on provided logic
4. ✅ Add tooltips for each KPI
5. ✅ Implement navigation with filters
6. ✅ Update Projects page to support filters
7. ✅ Add translation keys

### Backend is Ready:
- API endpoint working
- All 10 KPIs calculated efficiently
- Tests passing
- Documentation complete

**Questions?** Check DEMO-READY-SUMMARY.md or backend code comments.

---

**Prepared by:** Kiro AI  
**Date:** July 22, 2026  
**Status:** Ready for Frontend Implementation
