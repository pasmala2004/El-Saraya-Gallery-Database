# Projects Module - Future Scalability Roadmap

**Feature ID**: `projects-module-redesign`  
**Version**: 1.0  
**Created**: 2026-07-21

---

## Vision

The Projects module architecture is designed to accommodate **11+ future features** without requiring redesign. Each future feature integrates seamlessly into the existing structure using the **Collapsible Section pattern**.

---

## Architecture Guarantee

**Promise**: Any future feature can be added by:
1. Creating new section component
2. Wrapping in `<CollapsibleSection>`
3. Adding to ProjectDetails page
4. **No structural changes to existing code**

**Proof**: All sections use consistent patterns:
- CollapsibleSection wrapper
- React Query for data
- Optimistic updates
- Query invalidation
- Responsive design
- RTL support

---

## Planned Future Features

### 1. Employee Assignments

**Purpose**: Assign measurement engineers, production staff, installers to projects

**Business Value**: Track who's responsible, prevent overallocation, improve accountability

**Implementation**:
```tsx
<CollapsibleSection title="Team" icon={<Users />}>
  <TeamAssignments
    job={job}
    onAssignEngineer={handleAssignEngineer}
    onAssignInstaller={handleAssignInstaller}
  />
</CollapsibleSection>
```

**Database Changes**:
```sql
ALTER TABLE jobs ADD COLUMN assigned_engineer_id INTEGER REFERENCES users(id);
ALTER TABLE jobs ADD COLUMN assigned_installer_id INTEGER REFERENCES users(id);
```

**API Endpoints**:
```http
PATCH /api/v1/jobs/{id}/assign-engineer
Body: { user_id: 123 }

PATCH /api/v1/jobs/{id}/assign-installer
Body: { user_id: 456 }
```

**UI Components**:
- `TeamAssignments.tsx` - Team section
- `EmployeeSelector.tsx` - Dropdown to select employee
- `EmployeeAvailability.tsx` - Show workload

**Timeline**: 1-2 weeks after Step 10

**Impact**: Minimal - adds one collapsible section

---

### 2. Calendar Integration

**Purpose**: Sync measurement dates, installation dates to external calendar (Google Calendar, Outlook)

**Business Value**: Visual schedule, prevent double-booking, reminders

**Implementation**:
```tsx
<CollapsibleSection title="Schedule" icon={<Calendar />}>
  <ProjectSchedule
    job={job}
    measurements={measurements}
    onExportToCalendar={handleExport}
  />
</CollapsibleSection>
```

**OR embed calendar in Timeline section**:
```tsx
<CollapsibleSection title="Timeline" icon={<Clock />}>
  <ProjectTimeline events={timeline} />
  
  <div className="mt-4">
    <h4>Calendar View</h4>
    <CalendarWidget events={calendarEvents} />
  </div>
</CollapsibleSection>
```

**Backend Integration**:
- Google Calendar API integration
- iCal export (.ics files)
- Webhook for calendar updates

**API Endpoints**:
```http
GET /api/v1/jobs/{id}/calendar-events
Response: [ { title, start, end, type } ]

POST /api/v1/jobs/{id}/export-calendar
Body: { provider: 'google' | 'outlook' }
```

**Timeline**: 2-3 weeks after Step 10

**Impact**: None on existing UI, adds calendar widget

---

### 3. Notifications System

**Purpose**: Notify team when actions required (measurement due, payment overdue, installation tomorrow)

**Business Value**: Proactive alerts, reduce delays, improve response time

**Implementation**:
```tsx
// Notification panel (sidebar overlay)
<Layout>
  <NotificationPanel
    notifications={notifications}
    onMarkRead={handleMarkRead}
    onDismiss={handleDismiss}
  />
  
  <ProjectDetailsPage>
    {/* ... existing content */}
  </ProjectDetailsPage>
</Layout>
```

**Notification Icon in Header**:
```tsx
<div className="header-actions">
  <NotificationBell count={unreadCount} onClick={togglePanel} />
  <UserMenu />
</div>
```

**Backend**:
- Notification service (emails, SMS, push)
- WebSocket for real-time notifications
- Notification preferences per user

**API Endpoints**:
```http
GET /api/v1/notifications
POST /api/v1/notifications/mark-read
POST /api/v1/notifications/preferences
```

**Notification Types**:
- Measurement scheduled tomorrow
- Payment overdue
- Production delayed
- Installation today
- Quotation awaiting approval
- Stage completed (for manager)

**Timeline**: 3-4 weeks after Step 10

**Impact**: Adds notification bell to header, sidebar panel (overlay, doesn't change layout)

---

### 4. Inventory Tracking

**Purpose**: Track materials used per project (wood, hardware, glass, etc.)

**Business Value**: Cost tracking, inventory management, prevent shortages

**Implementation**:
```tsx
<CollapsibleSection title="Materials" icon={<Package />}>
  <MaterialsTracking
    job={job}
    materials={materials}
    onAddMaterial={handleAddMaterial}
    onUpdateQuantity={handleUpdateQuantity}
  />
</CollapsibleSection>
```

**Database Changes**:
```sql
CREATE TABLE materials (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  unit VARCHAR(50),
  unit_cost NUMERIC(12, 2)
);

CREATE TABLE job_materials (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  material_id INTEGER REFERENCES materials(id),
  quantity_planned NUMERIC(10, 2),
  quantity_used NUMERIC(10, 2),
  cost NUMERIC(12, 2)
);
```

**API Endpoints**:
```http
GET /api/v1/jobs/{id}/materials
POST /api/v1/jobs/{id}/materials
PATCH /api/v1/job-materials/{id}
```

**UI Components**:
- `MaterialsTracking.tsx` - Main section
- `MaterialsList.tsx` - Table of materials
- `AddMaterialModal.tsx` - Add material form

**Timeline**: 4-6 weeks after Step 10

**Impact**: Adds one collapsible section

---

### 5. Manufacturing Workflow Tracking

**Purpose**: Detailed manufacturing steps (cutting, assembly, finishing, QC)

**Business Value**: Production visibility, identify bottlenecks, quality control

**Implementation**:
```tsx
<CollapsibleSection title="Manufacturing" icon={<Settings />} defaultOpen>
  <ManufacturingWorkflow
    job={job}
    stages={manufacturingStages}
    onCompleteStage={handleCompleteManufacturingStage}
  />
</CollapsibleSection>
```

**OR enhance existing Workflow section**:
```tsx
<WorkflowStage id="production">
  {/* Existing production stage */}
  
  {/* Expand to show sub-stages */}
  {isExpanded && (
    <ManufacturingSubStages>
      <SubStage name="Cutting" status="completed" />
      <SubStage name="Assembly" status="in_progress" />
      <SubStage name="Finishing" status="pending" />
      <SubStage name="QC" status="pending" />
    </ManufacturingSubStages>
  )}
</WorkflowStage>
```

**Database Changes**:
```sql
CREATE TABLE manufacturing_stages (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  stage VARCHAR(100),
  status VARCHAR(50),
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

**Timeline**: 3-4 weeks after Step 10

**Impact**: Either new section OR enhances existing Workflow section with sub-stages

---

### 6. Installer Management

**Purpose**: Track installers, availability, performance, assignments

**Business Value**: Optimize scheduling, prevent conflicts, track installer performance

**Implementation**:
```tsx
<CollapsibleSection title="Installation Team" icon={<Users />}>
  <InstallerManagement
    job={job}
    assignedInstaller={installer}
    onAssign={handleAssignInstaller}
    onChangeDate={handleChangeInstallationDate}
  />
</CollapsibleSection>
```

**Database Changes**:
```sql
CREATE TABLE installers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  phone VARCHAR(50),
  availability JSONB
);

ALTER TABLE jobs ADD COLUMN installer_id INTEGER REFERENCES installers(id);
```

**API Endpoints**:
```http
GET /api/v1/installers
GET /api/v1/installers/{id}/availability
PATCH /api/v1/jobs/{id}/assign-installer
```

**Timeline**: 2-3 weeks after Step 10

**Impact**: Adds one collapsible section

---

### 7. AI Assistant

**Purpose**: Chatbot for project queries, recommendations, automation

**Business Value**: Faster information retrieval, intelligent suggestions, reduced training time

**Implementation**:
```tsx
// Floating chat widget (bottom-right corner)
<AIAssistantWidget>
  <ChatInterface
    messages={messages}
    onSendMessage={handleSendMessage}
    context={{ jobId: job.id }}
  />
</AIAssistantWidget>
```

**Floating Button**:
```tsx
<button className="fixed bottom-4 right-4 z-50">
  <MessageCircle className="w-6 h-6" />
</button>
```

**AI Capabilities**:
- "What's the status of Project #123?"
- "When is the next measurement scheduled?"
- "How much has the customer paid?"
- "Show me all delayed projects"
- "Suggest next action for this project"

**Backend**:
- LLM integration (GPT-4, Claude)
- RAG (Retrieval Augmented Generation) on project data
- Natural language → SQL queries

**Timeline**: 8-12 weeks (complex feature)

**Impact**: None on existing UI, adds floating widget (overlay)

---

### 8. Advanced Reports & Analytics

**Purpose**: Generate PDF reports, analytics dashboards, KPI tracking

**Business Value**: Data-driven decisions, client reports, performance insights

**Implementation**:
```tsx
// Report generation button in header
<QuickActions>
  <Button onClick={handleGenerateReport}>
    <FileText /> Generate Report
  </Button>
</QuickActions>

// OR new section
<CollapsibleSection title="Reports" icon={<BarChart />}>
  <ProjectReports
    job={job}
    onGeneratePDF={handleGeneratePDF}
    onGenerateExcel={handleGenerateExcel}
  />
</CollapsibleSection>
```

**Report Types**:
- Project summary (PDF)
- Financial statement (PDF)
- Timeline report (PDF)
- Custom reports (user-defined)

**Analytics Dashboard** (separate page):
- Project completion rates
- Average project duration
- Revenue trends
- Payment collection rates
- Bottleneck analysis

**API Endpoints**:
```http
POST /api/v1/jobs/{id}/generate-report
Body: { type: 'summary' | 'financial' | 'timeline' }
Response: { pdf_url }
```

**Timeline**: 4-6 weeks after Step 10

**Impact**: Adds button to header, OR new collapsible section

---

### 9. File Management & Document Upload

**Purpose**: Upload contracts, invoices, photos, technical drawings per project

**Business Value**: Centralized document storage, easy access, audit trail

**Implementation**:
```tsx
<CollapsibleSection title="Documents" icon={<Folder />}>
  <DocumentsSection
    job={job}
    documents={documents}
    onUpload={handleUpload}
    onDelete={handleDelete}
    onDownload={handleDownload}
  />
</CollapsibleSection>
```

**Document Types**:
- Contracts (PDFs)
- Invoices (PDFs)
- Installation photos (images)
- Technical drawings (images, PDFs)
- Customer signatures (images)

**Database Changes**:
```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  type VARCHAR(100),
  filename VARCHAR(255),
  file_path VARCHAR(500),
  uploaded_by INTEGER,
  uploaded_at TIMESTAMP
);
```

**Backend**:
- File upload (S3, Azure Blob, local storage)
- File size limits (10MB per file)
- Virus scanning
- Thumbnail generation for images

**API Endpoints**:
```http
GET /api/v1/jobs/{id}/documents
POST /api/v1/jobs/{id}/documents (multipart/form-data)
DELETE /api/v1/documents/{id}
```

**Timeline**: 3-4 weeks after Step 10

**Impact**: Replaces placeholder Documents section (already reserved in Step 9)

---

### 10. Multi-Location Support

**Purpose**: Support multiple gallery locations, regional managers

**Business Value**: Franchise expansion, regional reporting, location-based filtering

**Implementation**:
```tsx
// Location filter in Projects list
<ProjectsFilters>
  {/* Existing filters */}
  <LocationFilter
    locations={locations}
    selectedLocations={selectedLocations}
    onChange={setSelectedLocations}
  />
</ProjectsFilters>

// Location badge in Project header
<ProjectIdentification>
  {/* Existing badges */}
  <LocationBadge location={job.location} />
</ProjectIdentification>
```

**Database Changes**:
```sql
CREATE TABLE locations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  address TEXT,
  manager_id INTEGER
);

ALTER TABLE jobs ADD COLUMN location_id INTEGER REFERENCES locations(id);
ALTER TABLE customers ADD COLUMN preferred_location_id INTEGER REFERENCES locations(id);
```

**Timeline**: 2-3 weeks after Step 10

**Impact**: Adds location filter, location badge (minimal UI changes)

---

### 11. Custom Fields per Project Type

**Purpose**: Different project types need different fields (kitchen vs bedroom vs office)

**Business Value**: Flexibility, industry-specific customization, scalability

**Implementation**:
```tsx
<CollapsibleSection title="Custom Fields" icon={<Settings />}>
  <CustomFieldsSection
    job={job}
    projectType={job.project_type}
    customFields={customFields}
    onUpdate={handleUpdateCustomField}
  />
</CollapsibleSection>
```

**Database Changes**:
```sql
CREATE TABLE project_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  custom_fields JSONB
);

ALTER TABLE jobs ADD COLUMN project_type_id INTEGER REFERENCES project_types(id);
ALTER TABLE jobs ADD COLUMN custom_data JSONB;
```

**Custom Field Examples**:
- Kitchen: Appliances (bool), Island (bool), Backsplash type (text)
- Bedroom: Wardrobe type (enum), Mirror (bool), Sliding doors (bool)
- Office: Desk configuration (text), Cable management (bool)

**API Endpoints**:
```http
GET /api/v1/project-types
GET /api/v1/project-types/{id}/fields
PATCH /api/v1/jobs/{id}/custom-data
```

**Timeline**: 4-5 weeks after Step 10

**Impact**: Adds one collapsible section

---

## Feature Priority Matrix

| Feature | Business Value | Complexity | Priority | Timeline |
|---------|----------------|------------|----------|----------|
| Employee Assignments | High | Low | P0 | 1-2 weeks |
| Notifications | High | Medium | P0 | 3-4 weeks |
| Calendar Integration | Medium | Medium | P1 | 2-3 weeks |
| File Management | High | Medium | P1 | 3-4 weeks |
| Inventory Tracking | Medium | High | P2 | 4-6 weeks |
| Manufacturing Workflow | Medium | Medium | P2 | 3-4 weeks |
| Installer Management | Medium | Low | P1 | 2-3 weeks |
| Multi-Location | Low | Low | P3 | 2-3 weeks |
| AI Assistant | Low | Very High | P3 | 8-12 weeks |
| Advanced Reports | Medium | Medium | P2 | 4-6 weeks |
| Custom Fields | Low | High | P3 | 4-5 weeks |

**Priority Levels**:
- **P0**: Critical, implement within 3 months
- **P1**: Important, implement within 6 months
- **P2**: Nice to have, implement within 1 year
- **P3**: Low priority, implement when resources available

---

## Architectural Patterns for Future Features

### Pattern 1: Collapsible Section

**Use When**: Feature is a major functional area (materials, team, documents)

**Implementation**:
```tsx
<CollapsibleSection title="New Feature" icon={<Icon />} defaultOpen={false}>
  <NewFeatureComponent {...props} />
</CollapsibleSection>
```

**Benefits**:
- Consistent UX
- Doesn't clutter UI
- Easy to add/remove
- User controls visibility

---

### Pattern 2: Enhance Existing Section

**Use When**: Feature extends existing functionality (manufacturing sub-stages)

**Implementation**:
```tsx
<WorkflowStage id="production">
  {/* Existing content */}
  
  {enhancedMode && (
    <SubStages>
      {/* New sub-stages */}
    </SubStages>
  )}
</WorkflowStage>
```

**Benefits**:
- No new section
- Contextual enhancement
- Keeps related features together

---

### Pattern 3: Floating Widget

**Use When**: Feature is global, not project-specific (AI assistant, notifications)

**Implementation**:
```tsx
<Layout>
  <FloatingWidget>
    <FeatureComponent />
  </FloatingWidget>
  
  <ProjectDetailsPage>
    {/* Existing content */}
  </ProjectDetailsPage>
</Layout>
```

**Benefits**:
- Always accessible
- Doesn't modify page layout
- Can be dismissed

---

### Pattern 4: Header Enhancement

**Use When**: Feature needs quick access (generate report, assign team)

**Implementation**:
```tsx
<QuickActions>
  {/* Existing buttons */}
  <Button onClick={handleNewAction}>
    <Icon /> New Action
  </Button>
</QuickActions>
```

**Benefits**:
- Prominent placement
- One-click access
- Doesn't require scrolling

---

## Database Extensibility

### Current Schema (No Changes Needed Now)

Tables: jobs, quotations, customers, payments, measurements, activity_logs

### Future Schema Extensions

**Principle**: Additive changes only, never break existing schema

**Pattern 1: Add Columns**:
```sql
ALTER TABLE jobs ADD COLUMN new_field VARCHAR(255);
```

**Pattern 2: Add Tables** (preferred):
```sql
CREATE TABLE new_feature (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES jobs(id),
  -- feature-specific fields
);
```

**Pattern 3: JSONB for Flexible Data**:
```sql
ALTER TABLE jobs ADD COLUMN metadata JSONB;
-- Store flexible data without schema changes
```

---

## API Extensibility

### Current APIs (Reused)

Existing endpoints handle 90% of current requirements

### Future API Patterns

**Pattern 1: Add Endpoints**:
```http
POST /api/v1/jobs/{id}/new-action
GET /api/v1/new-resource
```

**Pattern 2: Add Query Params**:
```http
GET /api/v1/jobs?include=materials,team
```

**Pattern 3: Versioning** (if breaking changes needed):
```http
GET /api/v2/jobs
```

---

## Frontend Scalability

### Bundle Size Management

**Current**: ~500KB gzipped  
**Target**: <800KB gzipped (with all 11 features)

**Strategies**:
1. **Code Splitting**: Lazy load sections
   ```tsx
   const MaterialsSection = lazy(() => import('./MaterialsSection'));
   ```

2. **Tree Shaking**: Remove unused code

3. **Dynamic Imports**: Load features on demand

4. **Vendor Splitting**: Separate vendor bundle from app code

### Performance Monitoring

**Metrics to Track**:
- Initial load time
- Time to interactive
- Bundle size
- Memory usage
- API response times

**Tools**:
- Lighthouse CI (automated)
- Web Vitals
- React Profiler
- Chrome DevTools Performance

---

## Migration Path

### Adding a New Feature

1. **Design Phase**:
   - Create feature spec document
   - Define API endpoints
   - Design component tree
   - Estimate effort

2. **Implementation Phase**:
   - Create backend endpoints (if needed)
   - Create frontend components
   - Integrate into ProjectDetails page
   - Add translations
   - Write tests

3. **Integration Phase**:
   - Wrap in CollapsibleSection (or choose appropriate pattern)
   - Add to ProjectDetails page
   - Connect to React Query
   - Handle loading/error states

4. **Testing Phase**:
   - Unit tests
   - Integration tests
   - Manual testing
   - Performance testing

5. **Deployment Phase**:
   - Deploy to staging
   - Stakeholder review
   - Deploy to production
   - Monitor

### Example: Adding Materials Tracking

**Week 1**:
- Design materials data model
- Create database tables
- Implement backend API endpoints

**Week 2**:
- Create MaterialsSection component
- Create MaterialsList, AddMaterialModal
- Connect to API with React Query

**Week 3**:
- Add to ProjectDetails page in CollapsibleSection
- Add translations
- Test responsive design, RTL

**Week 4**:
- Manual testing
- Bug fixes
- Deploy to staging
- Stakeholder review

**Week 5**:
- Deploy to production
- Monitor for issues
- Collect user feedback

---

## Success Metrics (Post-Implementation)

| Metric | Target | Method |
|--------|--------|--------|
| Feature Adoption Rate | >60% of users use new features | Analytics tracking |
| Performance After 11 Features | <3s initial load | Lighthouse |
| Bundle Size | <800KB gzipped | Webpack analyzer |
| User Satisfaction | +30% improvement | Surveys |
| Support Tickets | <10 per feature | Support system |
| Code Maintainability | High | Code complexity metrics |

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-21  
**Related**: design.md, architecture.md

