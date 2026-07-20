import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Products from './pages/Products';
import Quotations from './pages/Quotations';
import Jobs from './pages/Jobs';
import JobDetails from './pages/JobDetails';
import MeasurementDetails from './pages/MeasurementDetails';
import Payments from './pages/Payments';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/products" element={<Products />} />
            <Route path="/quotations" element={<Quotations />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/jobs/:id" element={<JobDetails />} />
            <Route path="/jobs/:jobId/measurements/:measurementId" element={<MeasurementDetails />} />
            <Route path="/payments" element={<Payments />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      <Toaster position="top-left" richColors dir="rtl" />
    </QueryClientProvider>
  );
}

export default App;
