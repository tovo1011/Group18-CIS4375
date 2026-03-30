# Perfume Store Dashboard - Complete Setup Guide

This document provides step-by-step instructions to set up and run the entire Perfume Store Dashboard project (frontend + backend).

## Project Structure

```
Group18-CIS4375/
├── backend/                  # Flask REST API
│   ├── app.py              # Main Flask application
│   ├── sql.py              # Database utilities & schema
│   ├── creds.py            # Configuration & credentials
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Backend documentation
├── frontend/               # Vue 3 + Vite
│   ├── src/
│   │   ├── stores/         # Pinia stores (connected to API)
│   │   ├── views/          # Vue components
│   │   ├── components/     # Reusable components
│   │   └── App.vue
│   ├── package.json        # Node dependencies
│   ├── .env.local          # Local configuration
│   └── vite.config.js      # Vite configuration
└── README.md               # Project overview
```

## Architecture Overview

The backend uses a **three-file architecture** for clean separation of concerns:

1. **creds.py** - All configuration and credentials in one place
   - Database connection settings
   - Flask configuration
   - Easy to switch between SQLite and AWS RDS

2. **sql.py** - Database abstraction layer
   - `create_connection()` - Establish DB connection
   - `execute_query()` - Write operations
   - `execute_read_query()` - Read operations
   - `init_db_schema()` - Create all tables

3. **app.py** - Flask REST API
   - Imports from creds and sql
   - All API routes and business logic
   - Authentication, CRUD, audit logging

The frontend uses **Pinia stores** that connect to the backend API instead of using mock data.

## Prerequisites

- **Backend**: Python 3.8+, pip
- **Frontend**: Node.js 16+, npm or yarn
- **Database**: MySQL 5.7+ (local or remote)
  - For local development: Install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
  - For Windows: Use [MySQL Installer](https://dev.mysql.com/downloads/windows/installer/)

## Setup Instructions

### 1. Backend Setup

#### 1.1 Configure Database Credentials

First, you must update `backend/creds.py` with your MySQL database connection details.

Edit `backend/creds.py`:

```python
class Creds:
    # MySQL Configuration
    db_type = "mysql"
    host = "127.0.0.1"              # Your MySQL host (localhost for local dev)
    user = "root"                     # Your MySQL username
    password = "your_password"        # Your MySQL password
    database = "perfume_store"        # Database name
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-in-production"
    JWT_EXPIRATION_HOURS = 24
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
```

**Important**: Replace `host`, `user`, `password` with your actual MySQL credentials.

#### 1.2 Create the Database

Before running the app, create the database in MySQL:

```bash
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE IF NOT EXISTS perfume_store;
```

#### 1.3 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 1.4 Start the Backend

```bash
python app.py
```

This starts the Flask server on `http://localhost:5000` connected to MySQL database.

#### 1.5 Load Sample Data

In a separate terminal:

```bash
curl -X POST http://localhost:5000/api/init-db
```

Or with Python:

```bash
python -c "import requests; requests.post('http://localhost:5000/api/init-db')"
```

You should see the response:
```json
{"message": "Database initialized with sample data"}
```

If you see errors, check:
- MySQL is running
- Database credentials in `creds.py` are correct
- Backend server is running

### 2. Frontend Setup

#### 2.1 Install Node Dependencies

```bash
cd frontend
npm install
```

#### 2.2 Configure API URL

The `.env.local` file is already configured to use the local backend:

```env
VITE_API_URL=http://localhost:5000/api
```

If you need to use a different backend URL (e.g., deployed API), edit this file.

#### 2.3 Run Development Server

```bash
npm run dev
```

Frontend will run on `http://localhost:5173` (or another port if 5173 is busy).

### 3. Verify the Setup

1. Open `http://localhost:5173` in your browser
2. Click **Login** and use sample credentials:
   - Email: `manager@t4scents.com`
   - Password: `manager123` (or any password - demo mode creates users)
3. You should see the dashboard with:
   - **Suppliers** - example: Global Florals Inc
   - **Ingredients** - example: Rose Oil
   - **Scents** - example: Rose Elegance
   - **Audit Logs** - showing all your actions

## How the Integration Works

### API Flow

```
Vue Component
    ↓
Click button (e.g., "Add Ingredient")
    ↓
Pinia Store (e.g., useIngredientStore)
    ↓
Axios API Call
    ↓
Backend Flask Route
    ↓
SQL Database Operation
    ↓
Return JSON Response
    ↓
Pinia Updates State
    ↓
Vue Component Re-renders
```

### Example: Adding an Ingredient

1. **Frontend** (`IngredientsView.vue`):
   ```javascript
   const ingredientStore = useIngredientStore()
   await ingredientStore.addIngredient({
     name: 'Jasmine Oil',
     supplierId: 1,
     cost: 55.00,
     link: 'https://...',
     storageLocation: 'Rack C1'
   })
   ```

2. **Pinia Store** (`src/stores/ingredients.js`):
   ```javascript
   const addIngredient = async (ingredient) => {
     const response = await axios.post(
       `${API_URL}/ingredients`,
       ingredient,
       { headers: { 'Authorization': `Bearer ${token}` } }
     )
     ingredients.value.push(response.data)
   }
   ```

3. **Backend** (`app.py` route):
   ```python
   @app.route('/api/ingredients', methods=['POST'])
   @token_required
   def create_ingredient(current_user):
       # Validate and insert into database
       # Log the action in audit_logs table
       # Return created ingredient
   ```

4. **Database** (`sql.py`):
   - Insert new ingredient record
   - Automatically records audit log entry
   - Returns data to frontend

## Switching to AWS RDS MySQL

When you're ready to use AWS RDS instead of local MySQL:

### Step 1: Update Backend Configuration

Edit `backend/creds.py` with your RDS endpoint:

```python
class Creds:
    # MySQL Configuration (AWS RDS)
    db_type = "mysql"
    host = "your-rds-endpoint.us-east-1.rds.amazonaws.com"
    user = "admin"
    password = "your_password_here"
    database = "perfume_store"
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-in-production"
    JWT_EXPIRATION_HOURS = 24
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
```

### Step 2: Ensure Database Exists on RDS

Connect to your RDS instance and create the database:

```bash
mysql -h your-rds-endpoint.us-east-1.rds.amazonaws.com -u admin -p
```

Then:

```sql
CREATE DATABASE IF NOT EXISTS perfume_store;
```

### Step 3: Restart Backend

```bash
python app.py
```

The backend will automatically connect to your RDS instance.

### Step 4: Initialize RDS Database

```bash
curl -X POST http://localhost:5000/api/init-db
```

This creates all tables and sample data in RDS.

## API Testing

### Test Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@t4scents.com", "password": "test"}'
```

### Get Suppliers (requires token)

```bash
curl http://localhost:5000/api/suppliers \
  -H "Authorization: Bearer <your-token-here>"
```

### Create Ingredient (requires token)

```bash
curl -X POST http://localhost:5000/api/ingredients \
  -H "Authorization: Bearer <your-token-here>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Neroli Oil",
    "supplierId": 2,
    "cost": 75.00,
    "link": "https://example.com",
    "storageLocation": "Rack D2"
  }'
```

## Common Issues

### 1. Connection error: 'NoneType' object has no attribute 'cursor'

**Error**: Backend throws error when trying to login or access API

**Solution**:
- Check that MySQL is running
- Verify database credentials in `backend/creds.py` are correct
- Ensure the `perfume_store` database exists in MySQL
- Check that `mysql-connector-python` is installed: `pip install mysql-connector-python`

### 2. Frontend can't reach backend

**Error**: `Cannot GET http://localhost:5000/api/...`

**Solution**:
- Ensure backend is running: `python app.py`
- Check `.env.local` has correct `VITE_API_URL`: `http://localhost:5000/api`
- Check CORS is enabled in `app.py`: `CORS(app)`
- Check backend logs for connection errors

### 3. JWT token expired

**Error**: 401 Token has expired

**Solution**: Login again to get a new token. Tokens expire after 24 hours (configurable in `creds.py`).

### 4. Module not found errors

**Error**: `ModuleNotFoundError: No module named 'flask'` or `No module named 'mysql'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

## File Descriptions

### Backend Files

- **app.py** (500+ lines)
  - Flask application with all routes
  - Authentication with JWT
  - CRUD endpoints for suppliers, ingredients, scents
  - Audit logging system
  - Import/export functionality

- **sql.py** (150+ lines)
  - Database connection handler
  - Supports SQLite and MySQL
  - Query execution with error handling
  - Schema initialization
  - Row dictionary conversion

- **creds.py** (20 lines)
  - Centralized configuration
  - Database connection details
  - Flask settings
  - Easy to switch between environments

- **requirements.txt**
  - Flask - web framework
  - Flask-CORS - cross-origin requests
  - PyJWT - authentication tokens
  - mysql-connector-python - MySQL support

### Frontend Files

- **src/stores/auth.js**
  - JWT token management
  - Login/logout
  - User state persistence

- **src/stores/ingredients.js**
  - Ingredients CRUD operations
  - Real API integration
  - Search and filter logic

- **src/stores/suppliers.js**
  - Suppliers management
  - API integration

- **src/stores/scents.js**
  - Scent formulas management
  - Soft-delete (archive) functionality

- **src/stores/audit.js**
  - Audit log retrieval and filtering
  - API integration

- **.env.local**
  - Local development configuration
  - API URL pointer

- **vite.config.js**
  - Vite build configuration
  - Vue plugin setup

## Deployment Notes

### For Production

1. **Backend**:
   - Change `DEBUG = False` in `creds.py`
   - Set strong `SECRET_KEY`
   - Use AWS RDS instead of SQLite
   - Deploy to AWS (EC2, Elastic Beanstalk, etc.)
   - Set `CORS` to specific domain

2. **Frontend**:
   - Update `VITE_API_URL` to production backend URL
   - Build: `npm run build`
   - Deploy to S3, CloudFront, or static hosting

## Next Steps

1. ✅ Backend running on port 5000
2. ✅ Frontend running on port 5173
3. ✅ Sample data loaded
4. ✅ Able to login and view data

### To extend the project:

- Add role-based access control (admin vs manager)
- Add export to PDF/Excel
- Add advanced reporting
- Integrate with inventory management system
- Add email notifications
- Implement bulk operations

## Support

For issues or questions:

1. Check backend logs: `python app.py`
2. Check frontend console: F12 in browser
3. Check database: SQLite with `sqlite3 perfume_store.db`
4. Check API directly: `curl http://localhost:5000/api/suppliers`
