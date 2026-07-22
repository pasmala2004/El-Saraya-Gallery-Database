# Design Document: Operations Control Dashboard

## Overview

The Operations Control Dashboard is a comprehensive business intelligence interface that transforms the existing static dashboard into a real-time operational command center for the ERP system. This feature provides executives, managers, and operators with immediate visibility into critical business metrics, financial performance, operational bottlenecks, and actionable alerts.

### Core Objectives

1. **Real-Time Intelligence**: Display live business metrics refreshed automatically and on-demand
2. **Financial Visibility**: Provide immediate insight into revenue, collections, and payment status
3. **Operational Awareness**: Visualize sales pipeline, job progress, and process bottlenecks
4. **Proactive Alerting**: Surface critical issues requiring immediate attention
5. **Quick Action Access**: Enable rapid navigation to common tasks and filtered views

### Key Features

- **Metric Cards**: Display KPIs with trend indicators and contextual information
- **Pipeline Visualization**: Show quotation and job flow through status stages
- **Financial Overview**: Revenue breakdown, collection rates, and payment status
- **Alert Dashboard**: Prioritized list of overdue items and pending actions
- **Time Filtering**: View metrics across different periods (today, week, month, year, all time)
- **Performance Analytics**: Track operational efficiency and cycle times
- **Interactive Charts**: Visual representations of quotations, jobs, payments, and revenue trends
- **Responsive Design**: Seamless experience across desktop, tablet, and mobile devices

### Technology Stack

**Backend**:
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Pydantic v2 for schemas

**Frontend**:
- React 18+
- TypeScript
- Chart library (e.g., Recharts, Chart.js, or Victory)
- Tailwind CSS or Material-UI for styling
- React Query or SWR for data fetching and caching

