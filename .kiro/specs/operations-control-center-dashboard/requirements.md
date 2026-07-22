# Requirements Document

## Introduction

The Operations Control Center Dashboard transforms the current basic dashboard into an **operational ERP dashboard** focused on helping gallery assistants manage daily tasks. Unlike executive analytics dashboards, this interface prioritizes surfacing what needs attention today through a visual pipeline board showing all active jobs in their current stage. The dashboard provides actionable KPIs, smart alerts, recent activity tracking, and comprehensive job cards that update automatically as backend status changes.

## Glossary

- **Dashboard**: The main control center interface displaying business metrics and analytics
- **KPI**: Key Performance Indicator - a measurable value demonstrating business effectiveness
- **Metric_Card**: A visual component displaying a single business metric with its current value
- **Chart_Component**: A visual data representation (line chart, bar chart, pie chart)
- **Activity_Feed**: A chronological list of recent business operations and events
- **Alert_System**: A notification mechanism for critical business events requiring attention
- **Conversion_Rate**: The percentage of quotations that convert to jobs
- **Revenue_Metrics**: Financial performance indicators including total revenue and pending payments
- **Time_Series_Data**: Data points indexed by time for trend analysis
- **Drill_Down_View**: A detailed view accessed by clicking on a summary metric
- **API_Endpoint**: A backend HTTP endpoint that provides data for dashboard components
- **Real_Time_Data**: Data fetched dynamically from the backend reflecting current system state

## Requirements

### Requirement 1: Real-Time Business Metrics Display

**User Story:** As a business manager, I want to see real-time business metrics on the dashboard, so that I can monitor overall operational performance at a glance.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Dashboard SHALL make an HTTP GET request to `/api/v1/dashboard/metrics` within 5 seconds of page load
2. THE Dashboard SHALL display loading skeleton placeholders for all Metric_Cards WHILE the API request is in progress
3. WHEN the API response is received, THE Dashboard SHALL display total customer count with a Users icon
4. THE Dashboard SHALL display total quotation count grouped by status values (draft, sent, accepted, rejected)
5. THE Dashboard SHALL display active job count (jobs WHERE status NOT EQUAL TO "cancelled") grouped by status values
6. THE Dashboard SHALL display total revenue as sum of payment amounts WHERE status equals "paid"
7. THE Dashboard SHALL display pending payment amount as sum of payment amounts WHERE status equals "pending"
8. WHEN the API request fails, THE Dashboard SHALL display an error message stating "Failed to load metrics" AND SHALL show a retry button
9. WHEN the retry button is clicked, THE Dashboard SHALL repeat the API request up to 3 times with 2 second intervals between attempts
10. THE Dashboard SHALL cache the API response for 30 seconds AND SHALL reuse cached data for subsequent renders within that period
11. THE Metric_Card SHALL format all numeric values with comma thousands separators AND 2 decimal places for currency values
12. WHEN cached data becomes older than 30 seconds, THE Dashboard SHALL display a "refresh" indicator icon on each Metric_Card

### Requirement 2: Quotation Conversion Analytics

**User Story:** As a business manager, I want to track quotation conversion rates, so that I can understand sales effectiveness.

#### Acceptance Criteria

1. THE Dashboard SHALL calculate Conversion_Rate as (count of quotations WHERE status equals "accepted") divided by (count of quotations WHERE status is NOT "draft") multiplied by 100
2. THE Dashboard SHALL display the Conversion_Rate as a percentage with 1 decimal place
3. WHEN the count of non-draft quotations equals 0, THE Dashboard SHALL display Conversion_Rate as "N/A"
4. THE Dashboard SHALL calculate quotation status distribution as percentage of total quotations per status value
5. THE Chart_Component SHALL render a pie chart with 4 segments labeled "Draft", "Sent", "Accepted", "Rejected"
6. THE Dashboard SHALL calculate average quotation value as (sum of total_amount from all quotations) divided by (count of all quotations)
7. THE Dashboard SHALL calculate average accepted quotation value as (sum of total_amount from quotations WHERE status equals "accepted") divided by (count of accepted quotations)
8. THE Dashboard SHALL display monthly quotation trends showing count of created quotations grouped by month for the 6 calendar months preceding the current date
9. WHEN a user clicks on any quotation metric Metric_Card, THE Dashboard SHALL navigate to "/quotations" route
10. WHEN zero quotations exist, THE Chart_Component SHALL display message "No quotation data available"

### Requirement 3: Job Pipeline Monitoring

**User Story:** As an operations manager, I want to monitor the job pipeline, so that I can identify bottlenecks and ensure timely completion.

#### Acceptance Criteria

1. THE Dashboard SHALL display job count grouped by all status enum values: pending_measurement, measuring, pending_approval, approved, in_production, ready_for_installation, installed, completed, cancelled
2. THE Chart_Component SHALL render a horizontal bar chart with one bar per job status showing count of jobs in that status
3. THE Dashboard SHALL calculate average job duration as arithmetic mean of (completed_at date minus created_at date) in calendar days for all jobs WHERE status equals "completed"
4. THE Dashboard SHALL identify jobs as "overdue for measurement" WHEN status equals "pending_measurement" AND (current date minus created_at) exceeds 7 calendar days
5. THE Dashboard SHALL identify jobs as "overdue for production" WHEN status equals "in_production" AND (current date minus status_changed_at) exceeds 30 calendar days
6. THE Dashboard SHALL identify jobs as "overdue for installation" WHEN status equals "ready_for_installation" AND (current date minus status_changed_at) exceeds 14 calendar days
7. THE Dashboard SHALL flag a job as "at risk" WHEN status equals "pending_measurement" AND (current date minus created_at) exceeds 14 calendar days
8. THE Dashboard SHALL flag a job as "at risk" WHEN status equals "measuring" AND (current date minus status_changed_at) exceeds 7 calendar days
9. THE Dashboard SHALL flag a job as "at risk" WHEN status equals "pending_approval" AND (current date minus status_changed_at) exceeds 21 calendar days
10. THE Dashboard SHALL flag a job as "at risk" WHEN status equals "in_production" AND (current date minus status_changed_at) exceeds 45 calendar days
11. THE Dashboard SHALL calculate completion rate as (count of jobs WHERE status equals "completed") divided by (count of jobs WHERE status NOT EQUAL TO "cancelled") multiplied by 100
12. THE Dashboard SHALL display completion rate as percentage with 1 decimal place
13. WHEN a user clicks on a job status bar in the Chart_Component, THE Dashboard SHALL navigate to "/jobs?status={clicked_status_value}"
14. WHEN no jobs exist with status "completed", THE Dashboard SHALL display average job duration as "N/A"

### Requirement 4: Payment and Revenue Tracking

**User Story:** As a finance manager, I want to track payment status and revenue, so that I can manage cash flow effectively.

#### Acceptance Criteria

1. THE Dashboard SHALL display total revenue as the sum of amount values from all payments WHERE status equals "paid"
2. THE Dashboard SHALL display total pending payment amount as the sum of amount values from all payments WHERE status equals "pending"
3. THE Dashboard SHALL display overdue payment count as the count of payments WHERE status equals "overdue"
4. THE Dashboard SHALL display total overdue amount as the sum of amount values from all payments WHERE status equals "overdue"
5. THE Dashboard SHALL calculate payment collection rate as (sum of amount from payments WHERE status equals "paid") divided by (sum of amount from all payments WHERE status NOT EQUAL TO "cancelled") multiplied by 100
6. THE Dashboard SHALL display payment collection rate as percentage with 2 decimal places
7. WHEN the sum of amount from all non-cancelled payments equals 0, THE Dashboard SHALL display payment collection rate as "0.00%"
8. THE Chart_Component SHALL visualize monthly revenue trend as a line chart showing sum of amount from payments WHERE status equals "paid" grouped by month of paid_date for the 12 calendar months preceding the current date
9. THE Dashboard SHALL display payment breakdown showing sum of amount grouped by payment_method values (cash, bank_transfer, instapay, cheque, other) for all payments WHERE status equals "paid"
10. WHEN a payment has status "overdue" AND (current date minus due_date) exceeds 7 calendar days, THE Alert_System SHALL classify it as severity "critical"
11. THE Dashboard SHALL calculate average payment delay as arithmetic mean of (paid_date minus due_date) in calendar days for all payments WHERE status equals "paid" AND both paid_date and due_date are not null
12. THE Dashboard SHALL display average payment delay rounded to 1 decimal place with unit label "days"
13. WHEN a payment has due_date that is null, THE Dashboard SHALL exclude that payment from overdue payment count calculation
14. WHEN no payments exist WHERE status equals "paid", THE Dashboard SHALL display total revenue as "0.00"

### Requirement 5: Activity Feed and Recent Operations

**User Story:** As a user, I want to see recent business activities, so that I can stay informed about what's happening in the system.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Activity_Feed SHALL make an HTTP GET request to `/api/v1/dashboard/activities?limit=10`
2. THE Activity_Feed SHALL display the 10 most recent activity log entries ordered by created_at descending (newest first)
3. THE Activity_Feed SHALL display loading skeleton placeholders WHILE the API request is in progress
4. THE Activity_Feed SHALL show activity entries with entity_type values: quotation_created, quotation_sent, quotation_accepted, job_status_changed, payment_received
5. THE Activity_Feed SHALL display timestamp in relative format using these rules: less than 60 seconds "just now", 1-59 minutes "{n} minutes ago", 1-23 hours "{n} hours ago", 1-6 days "{n} days ago", 7+ days show full date "MMM DD, YYYY"
6. THE Activity_Feed SHALL display customer_name from the activity log entity_metadata field
7. THE Activity_Feed SHALL use entity_type-specific icons: FileText for quotation operations, Briefcase for job operations, CreditCard for payment operations
8. THE Activity_Feed SHALL use entity_type-specific colors: blue for quotation_created, green for quotation_sent/quotation_accepted, purple for job_status_changed, orange for payment_received
9. WHEN a user clicks on an activity entry, THE Dashboard SHALL navigate to route "/{entity_type_plural}/{entity_id}" derived from entity_type and entity_id fields
10. THE Activity_Feed SHALL auto-refresh by repeating the API request every 60 seconds
11. WHEN the API response returns an empty array, THE Activity_Feed SHALL display message "No recent activities"
12. WHEN the API request fails, THE Activity_Feed SHALL display message "Failed to load activities" AND SHALL show retry button
13. WHEN customer_name in entity_metadata is null, THE Activity_Feed SHALL display "Unknown Customer"
14. WHEN entity_metadata field is missing or malformed, THE Activity_Feed SHALL display the activity with entity_type and timestamp only, omitting customer_name

### Requirement 6: Alert System for Critical Events

**User Story:** As a manager, I want to be notified of critical business events, so that I can take immediate action when necessary.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Alert_System SHALL make an HTTP GET request to `/api/v1/dashboard/alerts`
2. THE Alert_System SHALL identify alerts from the API response with alert_type values: overdue_payment, at_risk_job, stale_quotation
3. THE Alert_System SHALL display an alert count badge in the dashboard header showing count of alerts WHERE severity equals "critical"
4. THE Alert_System SHALL prioritize alerts by severity in this order: critical (highest), warning, info (lowest)
5. WHEN an alert is displayed, THE Alert_System SHALL show alert_type translated label, description text, and entity_reference values
6. THE Alert_System SHALL provide a clickable link constructed from entity_type and entity_id in entity_reference
7. THE Dashboard SHALL display the top 5 alerts with severity "critical" in a dedicated Alert_Panel component
8. WHEN a user clicks "View All Alerts" button, THE Dashboard SHALL navigate to "/alerts" route
9. THE Alert_System SHALL auto-refresh by repeating the API request every 60 seconds
10. WHEN the API response returns zero alerts, THE Alert_Panel SHALL display message "No critical alerts"
11. WHEN the API request fails, THE Alert_Panel SHALL display message "Unable to load alerts"

### Requirement 7: Visual Data Representations

**User Story:** As a business user, I want to see visual charts and graphs, so that I can quickly understand trends and patterns.

#### Acceptance Criteria

1. THE Dashboard SHALL display 4 distinct Chart_Components: quotation status pie chart, job pipeline bar chart, revenue trend line chart, payment method bar chart
2. THE Chart_Component SHALL render quotation status distribution as a pie chart with 4 labeled segments using colors: draft (yellow), sent (blue), accepted (green), rejected (red)
3. THE Chart_Component SHALL render job pipeline as a horizontal bar chart with one bar per job status enum value
4. THE Chart_Component SHALL render monthly revenue trend as a line chart with x-axis showing month labels and y-axis showing currency amounts
5. THE Chart_Component SHALL render payment method distribution as a vertical bar chart with x-axis showing payment_method values and y-axis showing total amounts
6. THE Chart_Component SHALL use color scheme: blue (#3B82F6), green (#10B981), yellow (#F59E0B), red (#EF4444), purple (#8B5CF6), orange (#F97316)
7. WHEN a user hovers over a chart element, THE Chart_Component SHALL display a tooltip showing exact numeric value and label
8. THE Chart_Component SHALL adjust layout to fit container width while maintaining aspect ratio between 320px and 2560px screen widths
9. WHEN data array for a chart is empty or contains only zero values, THE Chart_Component SHALL display centered message "No data available"

### Requirement 8: Backend API for Dashboard Metrics

**User Story:** As the system, I want to provide efficient API endpoints for dashboard data, so that the frontend can retrieve metrics quickly.

#### Acceptance Criteria

1. THE API_Endpoint SHALL expose HTTP GET route `/api/v1/dashboard/metrics` returning JSON response with status code 200
2. THE API_Endpoint SHALL calculate all aggregate metrics using SQL queries executed server-side
3. THE API_Endpoint response SHALL include field `quotations` containing: `total` (count), `by_status` (object with draft/sent/accepted/rejected counts), `conversion_rate` (percentage), `average_value` (decimal)
4. THE API_Endpoint response SHALL include field `jobs` containing: `by_status` (object with count per status enum value), `average_duration_days` (decimal or null), `completion_rate` (percentage), `at_risk_count` (integer)
5. THE API_Endpoint response SHALL include field `payments` containing: `total_revenue` (decimal), `pending_amount` (decimal), `overdue_amount` (decimal), `overdue_count` (integer), `collection_rate` (percentage), `by_method` (object with amount per payment_method)
6. THE API_Endpoint response SHALL include field `customers` containing: `total` (integer count)
7. THE API_Endpoint SHALL respond with complete metrics within 500 milliseconds under normal load
8. WHEN any database query exceeds 5 seconds timeout, THE API_Endpoint SHALL return HTTP 500 with error message indicating timeout
9. THE API_Endpoint SHALL use database indexes on columns: quotations.status, jobs.status, jobs.created_at, jobs.completed_at, payments.status, payments.paid_date

### Requirement 9: Backend API for Activity Feed

**User Story:** As the system, I want to provide recent activity data, so that the frontend can display operational updates.

#### Acceptance Criteria

1. THE API_Endpoint SHALL expose HTTP GET route `/api/v1/dashboard/activities` returning JSON response with status code 200
2. THE API_Endpoint SHALL accept query parameter `limit` with default value 50 and maximum value 100
3. THE API_Endpoint SHALL accept query parameter `offset` with default value 0
4. THE API_Endpoint SHALL return activity log entries ordered by created_at timestamp descending
5. THE API_Endpoint response SHALL include array of activity objects each containing: `id`, `entity_type`, `entity_id`, `description`, `created_at`, `entity_metadata` (JSON object)
6. THE API_Endpoint SHALL include `customer_name` field in entity_metadata JSON object for all activities
7. THE API_Endpoint SHALL filter activities to include only entity_type values: quotation_created, quotation_sent, quotation_accepted, job_status_changed, payment_received
8. THE API_Endpoint SHALL respond within 200 milliseconds for queries requesting up to 50 activities
9. WHEN no activity log entries exist, THE API_Endpoint SHALL return empty array with HTTP 200 status code

### Requirement 10: Backend API for Alerts

**User Story:** As the system, I want to identify and provide critical alerts, so that users can be notified of issues requiring attention.

#### Acceptance Criteria

1. THE API_Endpoint SHALL expose HTTP GET route `/api/v1/dashboard/alerts` returning JSON response with status code 200
2. THE API_Endpoint SHALL identify overdue payments by querying payments WHERE status equals "overdue"
3. THE API_Endpoint SHALL identify at-risk jobs using the risk criteria defined in Requirement 3 acceptance criteria 7-10
4. THE API_Endpoint SHALL identify stale quotations by querying quotations WHERE status equals "sent" AND (current date minus sent_date) exceeds 14 calendar days
5. THE API_Endpoint response SHALL include array of alert objects each containing: `alert_type`, `severity`, `description`, `entity_reference` (object with entity_type and entity_id), `created_at`
6. THE API_Endpoint SHALL assign severity "critical" to alerts WHERE: overdue payment exceeds 7 days, at-risk job criteria met, stale quotation exceeds 21 days
7. THE API_Endpoint SHALL assign severity "warning" to alerts WHERE: overdue payment 1-7 days, stale quotation 14-21 days
8. THE API_Endpoint SHALL return maximum 100 alerts ordered by severity descending then created_at descending
9. THE API_Endpoint SHALL respond within 300 milliseconds for alert calculation queries

### Requirement 11: Backend API for Time-Series Data

**User Story:** As the system, I want to provide historical trend data, so that users can analyze business performance over time.

#### Acceptance Criteria

1. THE API_Endpoint SHALL expose HTTP GET route `/api/v1/dashboard/trends/quotations` returning monthly quotation metrics
2. THE API_Endpoint SHALL expose HTTP GET route `/api/v1/dashboard/trends/revenue` returning monthly revenue data
3. THE API_Endpoint SHALL accept query parameters `start_date` and `end_date` in ISO 8601 format (YYYY-MM-DD)
4. WHEN start_date and end_date are not provided, THE API_Endpoint SHALL default to last 12 calendar months from current date
5. THE API_Endpoint response SHALL return Time_Series_Data as JSON array of objects with fields: `period` (YYYY-MM format), `value` (numeric)
6. THE API_Endpoint `/trends/quotations` SHALL aggregate count of quotations grouped by month of created_at date
7. THE API_Endpoint `/trends/revenue` SHALL aggregate sum of payment amounts WHERE status equals "paid" grouped by month of paid_date
8. WHEN a calendar month has zero records, THE API_Endpoint SHALL include that month in the response with value 0
9. THE API_Endpoint SHALL respond within 400 milliseconds for 12-month trend queries

### Requirement 12: Responsive Design and Mobile Support

**User Story:** As a mobile user, I want the dashboard to be responsive, so that I can monitor operations from any device.

#### Acceptance Criteria

1. THE Dashboard SHALL use CSS media queries to adapt layout for viewport widths from 320px to 2560px
2. WHEN viewport width is less than 768px, THE Dashboard SHALL render Metric_Cards in a single column layout
3. WHEN viewport width is 768px to 1023px, THE Dashboard SHALL render Metric_Cards in a 2-column grid
4. WHEN viewport width is 1024px or greater, THE Dashboard SHALL render Metric_Cards in a 4-column grid
5. WHEN viewport width is less than 768px, THE Chart_Component SHALL render in single-column layout with full container width
6. THE Dashboard SHALL use touch targets with minimum 44px height and 44px width for all interactive elements on viewports less than 768px wide
7. THE Dashboard SHALL use minimum font size of 14px for body text and 16px for input elements on all viewport sizes
8. WHEN viewport width is less than 768px, THE Activity_Feed SHALL show condensed entries displaying only icon, customer name, and relative time
9. THE Dashboard SHALL complete initial render and display above-the-fold content within 3 seconds on simulated 3G network connection (750ms RTT, 1.6Mbps down)

### Requirement 13: Internationalization Support

**User Story:** As a user in different locales, I want the dashboard to display in my language, so that I can understand the metrics clearly.

#### Acceptance Criteria

1. THE Dashboard SHALL use the i18n translation hook `useTranslation()` for all user-facing text strings
2. THE Dashboard SHALL translate metric labels using keys: `dashboard.metrics.{metric_name}`, chart titles using keys: `dashboard.charts.{chart_name}`, activity descriptions using keys: `dashboard.activities.{activity_type}`
3. THE Dashboard SHALL format numbers using `Intl.NumberFormat` with locale from current i18n language setting
4. THE Dashboard SHALL format dates and times using `Intl.DateTimeFormat` with locale from current i18n language setting
5. THE Dashboard SHALL format currency values using `Intl.NumberFormat` with style "currency" and currency code from application config
6. WHEN a translation key is missing from the current locale file, THE Dashboard SHALL display the key string prefixed with "[MISSING]"
7. WHEN the i18n language is set to "ar" (Arabic), THE Dashboard SHALL apply CSS class "rtl" to root container AND SHALL reverse flex direction for horizontally arranged components

### Requirement 14: Error Handling and Loading States

**User Story:** As a user, I want clear feedback when data is loading or errors occur, so that I understand the system status.

#### Acceptance Criteria

1. WHEN the Dashboard initiates data fetch, THE Dashboard SHALL display skeleton loading placeholder components matching the layout of Metric_Card, Chart_Component, and Activity_Feed
2. WHEN an API request is in progress, THE individual component SHALL display animated loading indicator overlaying the component area
3. WHEN an API request returns HTTP status code 4xx or 5xx, THE Dashboard SHALL display error message "{Component_Name} failed to load" with a retry button
4. WHEN network connectivity is lost (API request fails with network error), THE Dashboard SHALL display banner message "You are offline. Data may not be current."
5. WHEN an individual component API request fails, THE Dashboard SHALL render that component in error state WHILE other components continue to display successfully loaded data
6. THE Dashboard SHALL implement retry mechanism with exponential backoff: 1st retry after 1 second, 2nd retry after 2 seconds, 3rd retry after 4 seconds, then stop
7. WHEN retry request succeeds, THE Dashboard SHALL remove error message AND SHALL render the component with returned data
8. THE Dashboard SHALL log all error messages to browser console using `console.error()` including: error type, API endpoint, HTTP status code, timestamp

### Requirement 15: Performance and Optimization

**User Story:** As a user, I want the dashboard to load and respond quickly, so that I can work efficiently.

#### Acceptance Criteria

1. THE Dashboard SHALL implement response caching with 30-second time-to-live (TTL) for data from `/api/v1/dashboard/metrics`
2. THE Dashboard SHALL use React Query library (or equivalent) for data fetching with built-in caching and deduplication
3. THE Dashboard SHALL lazy-load Chart_Component library using React.lazy() to defer loading until the component is rendered
4. THE Dashboard SHALL debounce auto-refresh API calls with minimum 1000 millisecond delay between consecutive requests to the same endpoint
5. WHEN the Activity_Feed displays more than 50 entries, THE Dashboard SHALL implement virtual scrolling to render only visible items plus 10-item buffer
6. THE Dashboard SHALL make parallel API requests to `/api/v1/dashboard/metrics`, `/api/v1/dashboard/activities`, and `/api/v1/dashboard/alerts` simultaneously on page load
7. THE Dashboard SHALL code-split the chart library into separate bundle chunk to reduce main bundle size
8. THE Dashboard SHALL achieve Google Lighthouse performance score of 85 or higher on desktop viewport (1920x1080) AND 70 or higher on mobile viewport (375x667) when tested with simulated 4G throttling
