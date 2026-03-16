# FacilitioPDF – Setup Guide

## Project Structure
```
facilitiopdf/
├── backend/   ← Django REST API + PDF generation
└── frontend/  ← Vue 3 + Vite editor & preview
```

---

## Backend Setup

### 1. Create virtual environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. WeasyPrint on Windows (required for PDF export)
WeasyPrint needs GTK3 libraries on Windows:

1. Download the GTK3 runtime installer from:
   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Run the installer (choose "Set up PATH variable")
3. Restart your terminal
4. Test: `python -c "import weasyprint; print('OK')"`

> If you skip WeasyPrint, the app will fall back to client-side PDF (html2pdf.js) automatically.

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Start the backend
```bash
python manage.py runserver
```
API available at: http://localhost:8000/api/

---

## Frontend Setup

### 1. Install Node dependencies
```bash
cd frontend
npm install
```

### 2. Start the dev server
```bash
npm run dev
```
App available at: http://localhost:5173

---

## Usage

1. Open http://localhost:5173
2. Click **⚙ Sender Profile** to set your name, address, logo, and default currency
3. Click **+ New Invoice** to create an invoice
4. Fill in client info, add line items (description + hours/rate → auto-calculates amount)
5. Watch the **Live Preview** update in real time on the right
6. Click **Save** to store in the database
7. Click **Export PDF** to download the PDF

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/profile/ | Get sender profile |
| PATCH | /api/profile/ | Update sender profile |
| GET | /api/invoices/ | List all invoices |
| POST | /api/invoices/ | Create invoice |
| GET | /api/invoices/{id}/ | Get invoice |
| PUT | /api/invoices/{id}/ | Update invoice |
| DELETE | /api/invoices/{id}/ | Delete invoice |
| POST | /api/invoices/{id}/upload_logo/ | Upload logo |
| GET | /api/invoices/{id}/pdf/ | Download PDF |
| GET | /api/invoices/next_number/ | Get next invoice number |
