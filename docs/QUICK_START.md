# Gallery ERP - Quick Start Guide

## 🚀 Start the Application (2 Commands)

### 1. Start Backend (Terminal 1)
```bash
cd d:\erp-backend\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend (Terminal 2)
```bash
cd d:\erp-backend\backend\frontend
npm run dev
```

### 3. Open Browser
```
http://localhost:3000
```

That's it! 🎉

## 📍 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## 🎯 First Steps

### 1. Explore the Dashboard
- View statistics
- Try quick action cards
- Navigate using sidebar

### 2. Create a Customer
1. Click "Customers" in sidebar
2. Click "Add Customer" button
3. Fill in details:
   - Full Name: "Ahmed Mohamed"
   - Phone: "01012345678"
   - City: "Cairo"
   - Address: "123 Main St"
4. Click "Create"
5. ✅ Success toast appears!

### 3. Create a Product Category
1. Open API docs: http://localhost:8000/docs
2. Find `POST /api/v1/product-categories`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "name": "Windows",
     "description": "Window products"
   }
   ```
5. Click "Execute"

### 4. Create a Product
1. Click "Products" in sidebar
2. Click "Add Product"
3. Fill in details:
   - Product Name: "Sliding Window"
   - Category: Select "Windows"
   - Description: "Aluminum sliding window"
   - Active: Checked
4. Click "Create"
5. ✅ Product appears in table!

### 5. Create a Quotation
1. Click "Quotations" in sidebar
2. Click "New Quotation"
3. Select customer
4. Enter discount: "0"
5. Add notes: "Initial quotation"
6. Click "Create"
7. ✅ New quotation created (status: draft)

## 🔍 Features to Try

### Search
- Go to Customers page
- Type in search box
- Results filter instantly

### Edit
- Click edit icon (pencil) on any customer
- Modify details
- Click "Update"
- ✅ Changes saved

### Delete
- Click delete icon (trash) on any customer
- Confirm deletion
- ✅ Customer removed

### Filter
- Go to Quotations page
- Use status dropdown
- Select "Draft"
- Table filters to show only drafts

## 🎨 What You'll See

### Dashboard
- 4 colorful stat cards
- Quick action buttons
- Clean, modern design

### Tables
- Searchable
- Hover effects
- Action buttons
- Responsive

### Forms
- Modal popups
- Clean inputs
- Required field indicators
- Loading states

### Notifications
- Toast messages (top-right)
- Success (green)
- Error (red)
- Auto-dismiss

## 📱 Try Mobile View

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select "iPhone 12 Pro" or any mobile device
4. Click hamburger menu (☰) to open sidebar
5. Navigate through pages
6. Tables scroll horizontally
7. Forms stack vertically

## ⚙️ Database Setup (If Starting Fresh)

### Option 1: Use Seeders (Recommended)
```bash
cd d:\erp-backend\backend

# Seed reference data (categories, products)
python -m app.database.seeders.reference.run_reference

# Seed demo data (customers, quotations)
python -m app.database.seeders.development.run_demo

# Or seed everything at once
python -m app.database.seeders.run_all
```

### Option 2: Use API to Create Data
Use the API docs at http://localhost:8000/docs to create:
1. Customers
2. Product categories
3. Products
4. Quotations

## 🛠️ Troubleshooting

### Backend Won't Start
**Error**: `No module named 'app'`
**Solution**: 
```bash
cd d:\erp-backend\backend
python -m uvicorn app.main:app --reload
```

**Error**: `Port 8000 already in use`
**Solution**: 
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Change port
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend Won't Start
**Error**: `Cannot find module`
**Solution**:
```bash
cd d:\erp-backend\backend\frontend
rm -rf node_modules
npm install
npm run dev
```

**Error**: `Port 3000 already in use`
**Solution**: Edit `vite.config.ts` and change port to 3001

### API Calls Failing
**Issue**: CORS errors or 404s
**Check**:
1. Backend is running on port 8000
2. Frontend proxy is configured correctly
3. Check browser console for errors
4. Verify API endpoint in `src/lib/api.ts`

### Empty Tables
**Issue**: No data appears
**Solution**: 
1. Check browser console for API errors
2. Verify backend is running
3. Create some data using API docs
4. Check network tab in DevTools

### Styling Issues
**Issue**: No styles applied
**Solution**:
```bash
cd frontend
npm install -D tailwindcss postcss autoprefixer
npm run dev
```

## 🧪 Test the API Directly

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Create Customer
```bash
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test Customer","phone_number":"01012345678"}'
```

### List Customers
```bash
curl http://localhost:8000/api/v1/customers
```

## 📚 Next Steps

1. **Explore All Pages** - Navigate through all 6 sections
2. **Create Test Data** - Add customers, products, quotations
3. **Test Workflows** - Create quotation for customer
4. **Try Mobile View** - Test responsive design
5. **Check API Docs** - Explore available endpoints
6. **Read Documentation** - Review FRONTEND_MVP_SUMMARY.md

## 💡 Tips

- **Hot Reload**: Both frontend and backend auto-reload on changes
- **Browser DevTools**: Essential for debugging (F12)
- **API Docs**: Interactive testing at /docs
- **Toast Notifications**: Watch for success/error messages
- **Console Logs**: Check for errors or warnings

## ⌨️ Keyboard Shortcuts

- **F12** - Open DevTools
- **Ctrl+Shift+M** - Toggle device toolbar (mobile view)
- **Ctrl+R** - Refresh page
- **ESC** - Close modal
- **Tab** - Navigate form fields

## 🎯 Success Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts on port 3000
- [ ] Dashboard loads with stats
- [ ] Can create a customer
- [ ] Can create a product
- [ ] Can create a quotation
- [ ] Search works
- [ ] Edit works
- [ ] Delete works
- [ ] Mobile view works
- [ ] Toast notifications appear

## 🆘 Need Help?

1. Check browser console for errors
2. Check backend terminal for errors
3. Check API docs: http://localhost:8000/docs
4. Read FRONTEND_MVP_SUMMARY.md
5. Review code in `src/` directory

## 🎉 You're All Set!

The Gallery ERP MVP is now running. Start by creating some customers and products, then create a quotation. Enjoy! 🚀
