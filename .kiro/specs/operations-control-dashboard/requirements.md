# Requirements Document

## Introduction

This document specifies the requirements for redesigning the existing dashboard into a comprehensive Operations Control Center for the ERP system. The Operations Control Center will provide real-time business intelligence, key performance indicators (KPIs), operational metrics, and quick access to critical business operations across all modules including Customers, Quotations, Jobs, Payments, and Products.

The current dashboard displays static placeholder values (all zeros) and basic quick action links. The redesigned Operations Control Center will fetch live data from the FastAPI backend, display actionable metrics with trend indicators, provide visual analytics through charts and graphs, show critical alerts and pending actions, and enable quick navigation to detailed views.

## Glossary

- **Dashboard**: The main landing page that provides an overview of business operations
- **Operations_Control_Center**: The redesigned dashboard component that displays real-time operational metrics and KPIs
- **KPI**: Key Performance Indicator - a measurable value that demonstrates effectiveness of business objectives
- **Metric_Card**: A visual component displaying a single KPI value with context (trend, comparison, status)
- **Backend_API**: The FastAPI service that provides data endpoints for dashboard metrics
- **Frontend_Component**: The React TypeScript component that renders the Operations Control Center
- **Real_Time_Data**: Current data fetched from the database reflecting the actual system state
- **Trend_Indicator**: A visual element showing whether a metric is increasing, decreasing, or stable
- **Quick_Action**: A clickable link that navigates the user to a specific module or action
- **Status_Badge**: A visual indicator showing the status category (e.g., draft, pending, overdue)
- **Time_Filter**: A control allowing users to view metrics for different time periods (today, week, month, year)
- **Chart_Widget**: A visualization component displaying data as charts or graphs
- **Revenue_Metric**: Financial metrics related to quotations, jobs, and payments
- **Pipeline_Metric**: Metrics tracking quotations and jobs through their lifecycle stages
- **Performance_Metric**: Metrics measuring operational efficiency and timing
- **Alert_Item**: A notification about critical issues requiring attention (overdue payments, pending actions)

## Requirements

### Requirement 1: Display Real-Time Business Metrics

**User Story:** As an operations manager, I want to see real-time business metrics on the dashboard, so that I can quickly assess the current state of operations without navigating to individual modules.

#### Acceptance Criteria

1. WHEN the Operations_Control_Center component mounts in the user's browser, THE Frontend_Component SHALL initiate an HTTP GET request to the Backend_API at /api/v1/dashboard/metrics within 100 milliseconds
2. IF the Backend_API responds with HTTP status 200 within 10 seconds, THEN THE Frontend_Component SHALL display the returned metrics
3. THE Frontend_Component SHALL display total customer count as an integer value
4. THE Frontend_Component SHALL display a Trend_Indicator beside the total customer count showing the percentage change compared to the customer count from 24 hours before the current time
5. IF the customer count 24 hours ago is zero, THEN THE Frontend_Component SHALL display the Trend_Indicator as "N/A"
6. THE Frontend_Component SHALL display total quotation count as an integer value with a breakdown showing the count for each QuotationStatus enum value (draft, sent, approved, rejected)
7. THE Frontend_Component SHALL display active job count as an integer value with a breakdown showing the count for each JobStatus enum value (pending, in_production, ready_for_installation)
8. THE Frontend_Component SHALL display total quotation value as a decimal number with 2 decimal places representing the sum of all quotation final_total field values
9. THE Frontend_Component SHALL display paid amount as a decimal number with 2 decimal places representing the sum of all payment amount field values where the PaymentStatus is paid
10. THE Frontend_Component SHALL display pending payment amount as a decimal number with 2 decimal places representing the sum of all payment amount field values where the PaymentStatus is pending or overdue
11. IF the Backend_API returns an HTTP error status (4xx or 5xx) or the request timeout exceeds 10 seconds, THEN THE Frontend_Component SHALL display an error message stating "Unable to load metrics" and provide a "Retry" button
12. WHEN a user clicks the "Retry" button, THE Frontend_Component SHALL immediately re-initiate the metrics fetch request
13. THE Frontend_Component SHALL automatically re-fetch metrics from the Backend_API every 60 seconds after the previous fetch completes
14. THE Frontend_Component SHALL provide a manual refresh control (button or icon)
15. WHEN a user clicks the manual refresh control, THE Frontend_Component SHALL immediately initiate a new metrics fetch request regardless of the automatic refresh timer
16. WHILE a metrics fetch request is in progress, THE Frontend_Component SHALL display a loading indicator

### Requirement 2: Provide Revenue and Financial Overview

**User Story:** As a business owner, I want to see financial metrics and revenue information, so that I can monitor cash flow and financial health at a glance.

#### Acceptance Criteria

1. THE Frontend_Component SHALL display total quotation value calculated as the sum of the final_total field for all quotations where status equals approved, formatted as a decimal number with 2 decimal places
2. THE Frontend_Component SHALL display total paid amount calculated as the sum of the amount field for all payments where status equals paid, formatted as a decimal number with 2 decimal places
3. THE Frontend_Component SHALL display total pending payment amount calculated as the sum of the amount field for all payments where status equals pending or status equals overdue, formatted as a decimal number with 2 decimal places
4. THE Frontend_Component SHALL display collection percentage calculated as (total paid amount divided by total quotation value) multiplied by 100, formatted as a decimal number with 1 decimal place followed by the percent symbol
5. IF total quotation value equals zero, THEN THE Frontend_Component SHALL display collection percentage as 0.0%
6. THE Frontend_Component SHALL display overdue payment count calculated as the count of payments where status equals overdue
7. IF overdue payment count is greater than zero, THEN THE Frontend_Component SHALL display the overdue payment count with a warning indicator (exclamation icon or red text)
8. WHEN a user clicks on the total quotation value metric, THE Frontend_Component SHALL navigate to the quotations list page at /quotations with a filter applied showing only quotations where status equals approved
9. WHEN a user clicks on the total paid amount metric, THE Frontend_Component SHALL navigate to the payments list page at /payments with a filter applied showing only payments where status equals paid
10. WHEN a user clicks on the total pending payment amount metric, THE Frontend_Component SHALL navigate to the payments list page at /payments with a filter applied showing payments where status equals pending or status equals overdue
11. THE Frontend_Component SHALL display revenue breakdown by payment_type showing three separate values: deposit amount, production amount, and final amount
12. THE Frontend_Component SHALL calculate deposit amount as the sum of the amount field for all payments where payment_type equals deposit, formatted as a decimal number with 2 decimal places
13. THE Frontend_Component SHALL calculate production amount as the sum of the amount field for all payments where payment_type equals production, formatted as a decimal number with 2 decimal places
14. THE Frontend_Component SHALL calculate final amount as the sum of the amount field for all payments where payment_type equals final, formatted as a decimal number with 2 decimal places
15. IF deposit amount, production amount, or final amount equals zero, THEN THE Frontend_Component SHALL display the respective amount as 0.00

### Requirement 3: Visualize Sales and Job Pipeline

**User Story:** As a sales manager, I want to visualize the quotation and job pipeline, so that I can identify bottlenecks and monitor conversion rates.

#### Acceptance Criteria

1. THE Frontend_Component SHALL display a visual pipeline component showing the count of quotations for each QuotationStatus enum value (draft, sent, approved, rejected) as separate labeled stages
2. THE Frontend_Component SHALL calculate the conversion rate from draft quotations to sent quotations as (count of quotations with status sent) divided by (count of quotations with status draft) multiplied by 100
3. IF the count of quotations with status draft equals zero, THEN THE Frontend_Component SHALL display the draft-to-sent conversion rate as "N/A"
4. THE Frontend_Component SHALL display the draft-to-sent conversion rate as a percentage with 1 decimal place
5. THE Frontend_Component SHALL calculate the conversion rate from sent quotations to approved quotations as (count of quotations with status approved) divided by (count of quotations with status sent) multiplied by 100
6. IF the count of quotations with status sent equals zero, THEN THE Frontend_Component SHALL display the sent-to-approved conversion rate as "N/A"
7. THE Frontend_Component SHALL display the sent-to-approved conversion rate as a percentage with 1 decimal place
8. THE Frontend_Component SHALL display a visual pipeline component showing the count of jobs for each JobStatus enum value as separate labeled stages
9. THE Frontend_Component SHALL calculate the average time spent in each job status as the mean number of days between the timestamp when the status was entered and the timestamp when the status was exited, for all jobs that have completed that status within the selected time period
10. THE Frontend_Component SHALL display the average time spent in each job status as a decimal number with 1 decimal place followed by "days"
11. IF fewer than 1 job has completed a given status within the selected time period, THEN THE Frontend_Component SHALL display the average time for that status as "Insufficient data"
12. THE Frontend_Component SHALL highlight a pipeline stage with a warning indicator (yellow border or icon) when the count of items in that stage exceeds 150 percent of the average count across all stages
13. THE Frontend_Component SHALL highlight a pipeline stage with a warning indicator (yellow border or icon) when the average time spent in that stage exceeds 14 days
14. WHEN a user clicks on a quotation pipeline stage, THE Frontend_Component SHALL navigate to the quotations list page at /quotations with a filter applied showing only quotations where status matches the clicked stage's status value
15. WHEN a user clicks on a job pipeline stage, THE Frontend_Component SHALL navigate to the jobs list page at /jobs with a filter applied showing only jobs where status matches the clicked stage's status value

### Requirement 4: Show Critical Alerts and Pending Actions

**User Story:** As an operations manager, I want to see critical alerts and pending actions, so that I can prioritize urgent tasks and prevent issues from escalating.

#### Acceptance Criteria

1. THE Frontend_Component SHALL display count of overdue payments calculated as the number of payments where the due_date field is before the current date
2. THE Frontend_Component SHALL display count of quotations awaiting measurement calculated as the number of quotations where measurement_scheduled field is NULL and status equals approved
3. THE Frontend_Component SHALL display count of jobs pending measurement date scheduling calculated as the number of jobs where measurement_date field is NULL
4. THE Frontend_Component SHALL display count of jobs ready for installation calculated as the number of jobs where status equals ready_for_installation
5. IF the quotation model includes an expiration_date field, THEN THE Frontend_Component SHALL display count of quotations approaching expiration calculated as the number of quotations where expiration_date is within 7 days from the current date and status equals sent
6. THE Frontend_Component SHALL display all Alert_Items in a dedicated alert section with a contrasting background color
7. WHEN a user clicks on the overdue payments alert, THE Frontend_Component SHALL navigate to /payments with a filter applied showing payments where due_date is before the current date
8. WHEN a user clicks on the quotations awaiting measurement alert, THE Frontend_Component SHALL navigate to /quotations with a filter applied showing quotations where measurement_scheduled is NULL and status equals approved
9. WHEN a user clicks on the jobs pending measurement alert, THE Frontend_Component SHALL navigate to /jobs with a filter applied showing jobs where measurement_date is NULL
10. WHEN a user clicks on the jobs ready for installation alert, THE Frontend_Component SHALL navigate to /jobs with a filter applied showing jobs where status equals ready_for_installation
11. IF the quotation model includes an expiration_date field, WHEN a user clicks on the quotations approaching expiration alert, THEN THE Frontend_Component SHALL navigate to /quotations with a filter applied showing quotations where expiration_date is within 7 days from the current date and status equals sent
12. THE Frontend_Component SHALL sort Alert_Items in the following order: overdue payments first, quotations approaching expiration second, jobs ready for installation third, quotations awaiting measurement fourth, jobs pending measurement fifth
13. THE Frontend_Component SHALL display overdue payments alert with red text or red icon when the count is greater than zero
14. IF the quotation model includes an expiration_date field, THEN THE Frontend_Component SHALL display quotations approaching expiration alert with yellow text or yellow icon when the count is greater than zero
15. THE Frontend_Component SHALL display jobs ready for installation alert with yellow text or yellow icon when the count is greater than zero
16. IF all alert counts equal zero, THEN THE Frontend_Component SHALL display a message stating "No pending alerts"

### Requirement 5: Enable Time-Based Filtering

**User Story:** As an analyst, I want to filter dashboard metrics by time period, so that I can analyze trends and compare performance across different timeframes.

#### Acceptance Criteria

1. THE Frontend_Component SHALL provide a Time_Filter control with options: Today, This Week, This Month, This Year, All Time

2. THE Frontend_Component SHALL define time period boundaries as follows: Today (current calendar day 00:00:00 to 23:59:59 in user browser timezone), This Week (current Monday 00:00:00 to Sunday 23:59:59 in user browser timezone), This Month (first day 00:00:00 to last day 23:59:59 of current calendar month in user browser timezone), This Year (January 1 00:00:00 to December 31 23:59:59 of current calendar year in user browser timezone), All Time (all records regardless of date)

3. WHEN a user selects a time period, THE Frontend_Component SHALL fetch filtered metrics from the Backend_API

4. THE Backend_API SHALL calculate metrics based on records where the created_at timestamp falls within the requested time period boundaries converted to UTC

5. THE Frontend_Component SHALL display the selected time period label within the Time_Filter control

6. THE Frontend_Component SHALL persist the selected time period value in browser session storage

7. WHEN the Operations_Control_Center loads, THE Frontend_Component SHALL restore the previously selected time period from session storage if available

8. IF no previously selected time period exists in session storage, THEN THE Frontend_Component SHALL default to This Month filter

9. THE Frontend_Component SHALL display comparison metrics showing both absolute change and percentage change from the previous equivalent period

10. THE Frontend_Component SHALL define previous equivalent period as follows: For Today (previous calendar day), For This Week (previous Monday to Sunday), For This Month (previous calendar month), For This Year (previous calendar year), For All Time (no comparison displayed)

11. THE Frontend_Component SHALL display comparison metrics with format: absolute difference followed by percentage in parentheses and up or down indicator icon

12. IF the time period filter request fails, THEN THE Frontend_Component SHALL display an error message indicating filter unavailable and retain the currently displayed metrics

### Requirement 6: Display Performance Metrics

**User Story:** As an operations manager, I want to see performance metrics about process efficiency, so that I can identify areas for operational improvement.

#### Acceptance Criteria

1. THE Frontend_Component SHALL display average time from quotation creation to approval calculated as the mean number of days (with 1 decimal place) between the created_at timestamp and the updated_at timestamp for all quotations where status equals approved within the selected time period
2. IF fewer than 1 quotation with status approved exists within the selected time period, THEN THE Frontend_Component SHALL display the average time from quotation creation to approval as "Insufficient data"
3. THE Frontend_Component SHALL display average time from job creation to completion calculated as the mean number of days (with 1 decimal place) between the created_at timestamp and the completion_date timestamp for all jobs where status equals completed within the selected time period
4. IF fewer than 1 job with status completed exists within the selected time period, THEN THE Frontend_Component SHALL display the average time from job creation to completion as "Insufficient data"
5. THE Frontend_Component SHALL display average time from measurement date to production start calculated as the mean number of days (with 1 decimal place) between the measurement_scheduled timestamp and the production_start_date timestamp for all jobs where measurement_scheduled is not NULL and production_start_date is not NULL within the selected time period
6. IF fewer than 1 job with both measurement_scheduled and production_start_date exists within the selected time period, THEN THE Frontend_Component SHALL display the average time from measurement to production as "Insufficient data"
7. THE Frontend_Component SHALL display average time from production start to installation calculated as the mean number of days (with 1 decimal place) between the production_start_date timestamp and the installation_date timestamp for all jobs where production_start_date is not NULL and installation_date is not NULL within the selected time period
8. IF fewer than 1 job with both production_start_date and installation_date exists within the selected time period, THEN THE Frontend_Component SHALL display the average time from production to installation as "Insufficient data"
9. IF a customer_satisfaction_score field exists in the database, THEN THE Frontend_Component SHALL display the mean customer satisfaction score (with 1 decimal place) for the selected time period
10. IF no customer_satisfaction_score field exists, THEN THE Frontend_Component SHALL display a placeholder message stating "Customer satisfaction tracking coming soon"
11. THE Frontend_Component SHALL calculate the previous period as the time period of equal length immediately preceding the current selected time period
12. THE Frontend_Component SHALL compare each current period performance metric to the corresponding previous period metric by calculating the percentage change as ((current value minus previous value) divided by previous value) multiplied by 100
13. THE Frontend_Component SHALL display the percentage change beside each performance metric with a positive or negative sign and 1 decimal place
14. IF the percentage change for a performance metric is less than -20 percent (decrease of more than 20 percent), THEN THE Frontend_Component SHALL highlight that metric with green text or a green downward arrow icon
15. IF the percentage change for a performance metric is greater than +20 percent (increase of more than 20 percent), THEN THE Frontend_Component SHALL highlight that metric with red text or a red upward arrow icon

### Requirement 7: Provide Quick Access to Module Actions

**User Story:** As a user, I want quick access links to common actions, so that I can efficiently perform frequent tasks without multiple navigation steps.

#### Acceptance Criteria

1. THE Frontend_Component SHALL display a Quick_Action link labeled "Create Customer" that is visually distinct (button or prominent link styling)
2. THE Frontend_Component SHALL display a Quick_Action link labeled "Create Quotation" that is visually distinct
3. THE Frontend_Component SHALL display a Quick_Action link labeled "View Active Jobs" that is visually distinct
4. THE Frontend_Component SHALL display a Quick_Action link labeled "Record Payment" that is visually distinct
5. THE Frontend_Component SHALL display a Quick_Action link labeled "View Overdue Payments" that is visually distinct
6. THE Frontend_Component SHALL display a Quick_Action link labeled "View Pending Measurements" that is visually distinct
7. WHEN a user clicks the "Create Customer" Quick_Action link, THE Frontend_Component SHALL navigate to the /customers/new route
8. WHEN a user clicks the "Create Quotation" Quick_Action link, THE Frontend_Component SHALL navigate to the /quotations/new route
9. WHEN a user clicks the "View Active Jobs" Quick_Action link, THE Frontend_Component SHALL navigate to the /jobs route with a filter applied showing jobs where status equals in_production
10. WHEN a user clicks the "Record Payment" Quick_Action link, THE Frontend_Component SHALL navigate to the /payments/new route
11. WHEN a user clicks the "View Overdue Payments" Quick_Action link, THE Frontend_Component SHALL navigate to the /payments route with a filter applied showing payments where status equals overdue
12. WHEN a user clicks the "View Pending Measurements" Quick_Action link, THE Frontend_Component SHALL navigate to the /quotations route with a filter applied showing quotations where measurement_scheduled is NULL and status equals approved
13. THE Frontend_Component SHALL display a numeric badge on the "View Active Jobs" Quick_Action link showing the count of jobs where status equals in_production
14. THE Frontend_Component SHALL display a numeric badge on the "View Overdue Payments" Quick_Action link showing the count of payments where status equals overdue
15. THE Frontend_Component SHALL display a numeric badge on the "View Pending Measurements" Quick_Action link showing the count of quotations where measurement_scheduled is NULL and status equals approved
16. THE Frontend_Component SHALL update all Quick_Action count badges whenever dashboard metrics are refreshed

### Requirement 8: Create Backend API Endpoints for Dashboard Metrics

**User Story:** As a frontend developer, I want dedicated API endpoints for dashboard metrics, so that I can efficiently fetch aggregated data without multiple requests.

#### Acceptance Criteria

1. THE Backend_API SHALL provide a GET endpoint at /api/v1/dashboard/metrics returning a JSON response with HTTP status 200 containing fields for customer_metrics, quotation_metrics, job_metrics, payment_metrics, alert_metrics, and pipeline_metrics
2. THE Backend_API SHALL accept an optional query parameter time_period with allowed values: today, week, month, year, all, defaulting to month if not provided
3. IF the time_period query parameter contains a value other than today, week, month, year, or all, THEN THE Backend_API SHALL return HTTP status 400 with an error message indicating invalid time_period value
4. THE Backend_API SHALL filter all metrics using the server's local timezone to determine date boundaries for today, week, month, and year time periods
5. THE Backend_API SHALL return customer_metrics containing total_count (all customers) and new_count (customers where created_at falls within the selected time period)
6. THE Backend_API SHALL return quotation_metrics containing a count for each quotation status value and total_value as the sum of all quotations' final_total field within the selected time period
7. THE Backend_API SHALL return job_metrics containing a count for each job status value and average_duration_days calculated as the mean number of calendar days between start_date and completion_date for all completed jobs within the selected time period
8. THE Backend_API SHALL return payment_metrics containing paid_amount (sum of payments where status is paid), pending_amount (sum of payments where status is pending), and overdue_count (count of payments where status is pending and due_date is more than 30 days before the current date)
9. THE Backend_API SHALL return alert_metrics containing overdue_payments_count (payments with status pending and due_date more than 30 days past), pending_measurements_count (measurements with status pending), and stalled_jobs_count (jobs with status in_progress and updated_at more than 14 days before current date)
10. THE Backend_API SHALL return pipeline_metrics containing quote_to_job_conversion_rate (percentage of quotations with status accepted that have an associated job), average_quote_to_acceptance_days (mean days between quotation created_at and updated_at for quotations with status accepted), and average_job_completion_days (mean days between job start_date and completion_date for jobs with status completed)
11. WHEN a database query fails during metrics aggregation, THEN THE Backend_API SHALL return HTTP status 500 with an error message indicating database error
12. THE Backend_API SHALL complete the metrics request and return the response within 2 seconds when handling up to 10 concurrent requests

### Requirement 9: Visualize Data with Charts

**User Story:** As a manager, I want to see visual charts and graphs, so that I can quickly understand trends and patterns without analyzing raw numbers.

#### Acceptance Criteria

1. THE Frontend_Component SHALL display a bar chart showing quotation counts by status with one bar per QuotationStatus enum value
2. THE Frontend_Component SHALL display a line chart showing revenue trend over the selected time period with data points aggregated by day when the time period is Today or This Week, by week when the time period is This Month, and by month when the time period is This Year or All Time
3. THE Frontend_Component SHALL display a pie chart showing job distribution by status with one segment per JobStatus enum value
4. THE Frontend_Component SHALL display a bar chart showing payment collection by payment_type with one bar for deposit, one bar for production, and one bar for final
5. THE Frontend_Component SHALL use a consistent color scheme across all Chart_Widget components where the same status or category always uses the same color
6. WHEN a user hovers over a chart data point, bar, or segment, THEN THE Frontend_Component SHALL display a tooltip showing the label and the numeric value with 2 decimal places for currency values and 0 decimal places for count values
7. IF chart data for a Chart_Widget is unavailable because the Backend_API returned an error or because the selected time period contains zero records, THEN THE Frontend_Component SHALL display a message stating "No data available" in place of the chart
8. THE Frontend_Component SHALL render charts with a width that scales proportionally to the container width and a height that scales proportionally to the container height, maintaining a minimum width of 200 pixels and a minimum height of 150 pixels
9. WHILE chart data is being fetched from the Backend_API, THE Frontend_Component SHALL display a loading spinner or skeleton placeholder in the chart area

### Requirement 10: Ensure Responsive Design and Performance

**User Story:** As a user on different devices, I want the Operations Control Center to work well on desktop, tablet, and mobile screens, so that I can access critical information from any device.

#### Acceptance Criteria

1. THE Frontend_Component SHALL render on desktop screens (1920x1080 and above) with no horizontal overflow, no overlapping elements, and all interactive elements having a minimum touch target size of 44x44 pixels
2. THE Frontend_Component SHALL render on laptop screens (1366x768 and above) with no horizontal overflow, no overlapping elements, and all interactive elements having a minimum touch target size of 44x44 pixels
3. THE Frontend_Component SHALL render on tablet screens (768x1024 portrait and landscape) with no horizontal overflow, no overlapping elements, and all interactive elements having a minimum touch target size of 44x44 pixels
4. THE Frontend_Component SHALL render on mobile screens (375x667 and above) with no horizontal overflow, no overlapping elements, and all interactive elements having a minimum touch target size of 44x44 pixels
5. THE Frontend_Component SHALL use responsive grid layouts with CSS breakpoints at 375px, 768px, 1366px, and 1920px that reflow based on screen width
6. THE Frontend_Component SHALL complete initial page load and render within 1 second on desktop with network conditions of at least 10 Mbps bandwidth and 50ms latency
7. THE Frontend_Component SHALL implement loading states for all async data operations by displaying a loading indicator or skeleton screen while data is being fetched
8. THE Frontend_Component SHALL implement skeleton screens showing placeholder content with the same layout structure as the final content while fetching data from the Backend_API
9. IF a network request exceeds 2 seconds, THEN THE Frontend_Component SHALL show a progress indicator with a message stating "Loading metrics..."
10. THE Frontend_Component SHALL cache dashboard metrics in browser memory for 30 seconds after a successful fetch to prevent redundant API calls when the component re-renders
11. THE Frontend_Component SHALL provide a mobile-friendly navigation menu on screens smaller than 768px that collapses Quick_Action links into a hamburger menu or bottom navigation bar
12. IF a network request fails or times out after 10 seconds, THEN THE Frontend_Component SHALL display an error message stating "Unable to load metrics" with a "Retry" button

