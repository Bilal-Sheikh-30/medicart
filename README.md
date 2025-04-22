# Medicart - Pharmacy Management Backend

**Medicart** is a Django-based backend for a complete online pharmacy store and management system. It supports API endpoints for customer interaction, inventory management, sales tracking, and delivery operations. This backend is designed to work seamlessly with a React frontend or any modern frontend framework.

---

## 🌐 Project Overview
Medicart is designed to power a full-featured online pharmacy platform, offering the following:

- A user-facing **online store** for browsing and ordering medicines
- Backend support for **inventory, sales**, and **delivery** modules used by pharmacy staff
- Authentication for users and staff
- Structured and secure database handling via MySQL

---

## 🧩 Project Structure
```
medicart-backend/
├── pharma/               # Main Django project folder
│   ├── inventory/        # Inventory, Sales, and Delivery logic
│   ├── onlinestore/      # Online store views and logic
│   ├── media/            # Media files (local storage)
│   ├── static/           # Static files (if used)
│   ├── pharma/           # Django project settings
│   ├── .env              # Environment configuration (Required)
│   ├── db.sqlite3        # (For development only, production uses MySQL)
│   ├── manage.py         # Django entry point
│   └── requirements.txt  # Project dependencies
└── venv/                 # Virtual environment
```

---

## 🔧 Core Modules & Features

### 1. Online Store (App: `onlinestore`)
- Browse medicines
- Search and filter by name/category
- Add items to cart
- Place orders
- Register/login/logout as a customer

### 2. Inventory (App: `inventory`)
- Add/update/delete medicines
- Track stock levels and generate orders to vendors
- Upload medicine images (stored locally)
- Add new categories or suppliers

### 3. Sales
- Track customer orders
- Verify payments
- Assign delivery personnel

### 4. Delivery
- Track delivery status
- Mark orders as delivered

---

## 🔐 Authentication & Role-Based Access
- Django's built-in authentication system is used
- Staff logins redirect them to their respective dashboards (Inventory, Sales, Delivery)
- Customers are taken to the user interface on login

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Bilal-Sheikh-30/medicart.git
cd medicart-backend
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows
```

### 3. Install Dependencies
```bash
cd pharma
pip install -r requirements.txt
```

### 4. Create a `.env` File (inside `pharma/` where `manage.py` exists)
```env
NAME=<db_name>
USER=<db_user>
PASSWORD=<db_password>
HOST=localhost
PORT=3306
EMAIL_HOST_USER=<admin_email>
EMAIL_HOST_PASSWORD=<gmail_app_password>
DEFAULT_FROM_EMAIL=<admin_email>
```

### 5. Run Migrations and Start Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 📬 API Access
All APIs follow RESTful conventions. Use a tool like Postman or integrate with a frontend (e.g., React) to interact.

---

## 🚀 Future Improvements
- Integrate Cloudinary or AWS S3 for image hosting
- Build a React frontend
- Add payment gateway support
- Improve role-based permissions using Django Groups