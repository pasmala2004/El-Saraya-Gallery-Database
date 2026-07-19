# Gallery ERP - Frontend

Modern, responsive ERP interface for gallery management.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **TailwindCSS** for styling
- **React Router** for navigation
- **TanStack Query** for data fetching
- **Axios** for API calls
- **Sonner** for toast notifications
- **Lucide React** for icons

## Features

### Implemented
- ✅ Dashboard with statistics and quick actions
- ✅ Customer Management (CRUD)
- ✅ Product Management (CRUD)
- ✅ Quotation Management (Create, List, Filter by status)
- ✅ Responsive sidebar navigation
- ✅ Modern modal forms
- ✅ Toast notifications
- ✅ Search and filter functionality
- ✅ Loading states

### Placeholder Pages
- 🔜 Jobs (placeholder with coming soon message)
- 🔜 Payments (placeholder with coming soon message)

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout.tsx      # Main layout with sidebar
│   │   ├── Button.tsx      # Button component
│   │   ├── Modal.tsx       # Modal/Dialog component
│   │   ├── Input.tsx       # Input field component
│   │   └── Select.tsx      # Select dropdown component
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx   # Dashboard with stats
│   │   ├── Customers.tsx   # Customer management
│   │   ├── Products.tsx    # Product management
│   │   ├── Quotations.tsx  # Quotation management
│   │   ├── Jobs.tsx        # Jobs placeholder
│   │   └── Payments.tsx    # Payments placeholder
│   ├── services/           # API service functions
│   │   ├── customers.ts    # Customer API calls
│   │   ├── products.ts     # Product API calls
│   │   └── quotations.ts   # Quotation API calls
│   ├── lib/
│   │   └── api.ts          # Axios instance configuration
│   ├── types/
│   │   └── index.ts        # TypeScript type definitions
│   ├── App.tsx             # Main app component with routing
│   ├── main.tsx            # App entry point
│   └── index.css           # Global styles with Tailwind
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

## API Integration

The frontend connects to the backend API via proxy configuration:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- Proxy: `/api/*` → `http://localhost:8000/api/*`

## Usage Guide

### Dashboard
- View key statistics (customers, quotations, jobs, payments)
- Quick access to common actions
- Navigate to any module

### Customers
- View all customers in a searchable table
- Add new customers with phone, city, address
- Edit existing customer details
- Delete customers (with confirmation)
- Search by name

### Products
- View all products with category and status
- Add new products with category selection
- Mark products as active/inactive
- Edit product details
- Delete products
- Search by name

### Quotations
- View all quotations with status badges
- Filter by status (draft, sent, approved, etc.)
- Create new quotations for customers
- View quotation details
- Status-based color coding:
  - Draft: Gray
  - Waiting for Measurement: Blue
  - Measured: Cyan
  - Under Negotiation: Yellow
  - Sent: Purple
  - Approved: Green
  - Rejected: Red
  - Cancelled: Gray
  - Expired: Orange

## Design Principles

### Simple
- Clean, uncluttered interface
- Intuitive navigation
- Minimal clicks to complete tasks

### Fast
- Optimized data fetching with React Query
- Instant feedback with loading states
- Cached data for quick navigation

### Mobile-Friendly
- Responsive sidebar that collapses on mobile
- Touch-friendly buttons and inputs
- Scrollable tables on small screens

### Modern
- Contemporary UI design
- Smooth transitions and animations
- Professional color scheme

## Future Enhancements

### Short Term
1. Complete Jobs module with full CRUD
2. Complete Payments module with full CRUD
3. Add quotation detail view with items
4. Add quotation status update workflow
5. Add customer detail view with quotations

### Medium Term
1. Advanced filtering and sorting
2. Export data to Excel/PDF
3. Print quotations
4. Bulk operations
5. Advanced search across modules

### Long Term
1. User authentication and authorization
2. Multi-user support with permissions
3. Activity logs and audit trail
4. Reports and analytics
5. Dashboard charts and graphs
6. Mobile app version

## Development Notes

### Adding New Features
1. Create type definitions in `src/types/index.ts`
2. Create API service in `src/services/`
3. Create page component in `src/pages/`
4. Add route in `src/App.tsx`
5. Add navigation item in `src/components/Layout.tsx`

### Code Style
- Use TypeScript for type safety
- Use React hooks (no class components)
- Use TanStack Query for data fetching
- Use Tailwind classes for styling
- Keep components small and focused
- Extract reusable logic into custom hooks

## Troubleshooting

### API Connection Issues
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify proxy configuration in vite.config.ts

### Build Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`

### Type Errors
- Update types in src/types/index.ts to match backend API
- Run `npm run build` to check for type errors

## License

Proprietary - Gallery ERP © 2026
