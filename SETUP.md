# Perfume Store Dashboard - Complete Setup Guide

This document provides step-by-step instructions to set up and run the entire Perfume Store Dashboard project (frontend + backend) with the **new database schema**.

**Database**: MySQL 5.7+ (Required - not SQLite compatible)

## Project Structure

```
Group18-CIS4375/
├── backend/                  # Flask REST API
│   ├── app.py              # Main Flask application
│   ├── sql.py              # Database utilities & schema initialization
│   ├── creds.py            # Configuration & credentials
│   ├── db_schema.sql       # Complete database schema (reference)
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

## Database Schema

The application uses the following **11 tables** (all created automatically on first run):

1. **Users** - User accounts and authentication
2. **Suppliers** - Ingredient suppliers and vendor information
3. **Essential_oil** - Essential oils/ingredients inventory
4. **Scent_Essential_Oil** - Junction table linking scents to essential oils
5. **Scents** - Scent formulas and compositions
6. **Products** - Product variants of scents
7. **DashBoardMetrics** - Dashboard analytics
8. **AuditLog** - Complete audit trail of all actions
9. **Customers** - Customer information
10. **Order** - Customer orders
11. **Order_Item** - Individual items in orders

### Important Column Names

- **Users**: `UserID`, `Email`, `PasswordHash`, `Username`, `UserRole`
- **Suppliers**: `supplier_ID`, `SupplierName`, `Email`, `Phone`, `Address`
- **Scents**: `id`, `name`, `top_notes`, `middle_notes`, `base_notes`, `all_notes`, `essential_oils`, `created_by`, `created_at`, `archived_at`
- **AuditLog**: `AuditID`, `UserID`, `AuditAction`, `TableName`, `Timestamp`

## Prerequisites

- **Backend**: Python 3.8+, pip
- **Frontend**: Node.js 16+, npm or yarn
- **Database**: MySQL 5.7+ **(Required - SQLite not supported)**
  - **For local development**: Install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
  - **Windows**: Use [MySQL Installer](https://dev.mysql.com/downloads/windows/installer/)
  - **macOS**: `brew install mysql`
  - **Linux**: `apt-get install mysql-server`
- **Verify MySQL is running** before starting the backend

## Setup Instructions

### 1. Backend Setup

#### 1.1 Verify MySQL is Running

**Windows**:
```powershell
# Check if MySQL is running
Get-Service MySQL*
```

**macOS/Linux**:
```bash
mysql --version
```

#### 1.2 Create the Database

Open a terminal and connect to MySQL:

```bash
mysql -u root -p
```

Enter your MySQL password, then run:

```sql
CREATE DATABASE IF NOT EXISTS perfume_store;
EXIT;
```

#### 1.3 Configure Backend Credentials

Edit `backend/creds.py` with your MySQL connection details:

```python
class Creds:
    # MySQL Configuration
    host = "127.0.0.1"              # localhost for local development
    user = "root"                     # Your MySQL username
    password = "your_password"        # Your MySQL password
    database = "perfume_store"        # Database name created above
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-in-production-min-32-chars"  # Must be at least 32 characters for security
    JWT_EXPIRATION_HOURS = 24
    DEBUG = True                      # Set to False in production
    HOST = "0.0.0.0"
    PORT = 5000
```

**Important**: 
- Replace `password` with your actual MySQL password
- Replace `SECRET_KEY` with a **minimum 32 characters** long random string (recommended: 64+ characters) to avoid JWT warnings

#### 1.4 Install Python Dependencies

Open a terminal in the `backend` folder:

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `flask` - Web framework
- `flask-cors` - Cross-origin requests
- `PyJWT` - Authentication tokens  
- `mysql-connector-python` - MySQL database driver
- `werkzeug` - Password hashing

#### 1.5 Start the Backend Server

```bash
python app.py
```

You should see:
```
MySQL connection successful!
Database initialized successfully
Table 'Users' created or verified successfully
Table 'Scents' created or verified successfully
[...more tables...]
WARNING: This is a development server. Do not use it in production.
Running on http://127.0.0.1:5000
```

The backend is now ready on `http://localhost:5000`.

**Troubleshooting**:
- If you see `Connection error`, check MySQL is running and credentials in `creds.py` are correct
- If you see `ModuleNotFoundError`, run `pip install -r requirements.txt` again
- If you see MySQL error, verify the `perfume_store` database exists

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

1. **Start the backend** (in one terminal):
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open the app**:
   - Open `http://localhost:5173` in your browser
   - To login, use **any email and password**:
     - Email: `test@example.com`
     - Password: `any_password`
   - The backend will automatically create a user account for demo purposes

4. **You should see the dashboard with**:
   - **Suppliers** - Manage suppliers and vendors
   - **Scents** - Create and manage scent formulas
   - **Audit Logs** - Complete audit trail of all actions

5. **Try these features**:
   - Click **"+ Add Supplier"** to create a new supplier
   - Click **"+ Add Scent"** to create a new scent formula
   - View **Audit Logs** to see all recorded actions

## How the Integration Works

### API Flow

```
Vue Component
    ↓
Click button (e.g., "Add Supplier")
    ↓
Pinia Store (e.g., useSupplierStore)
    ↓
Axios API Call with JWT Token
    ↓
Backend Flask Route (@token_required decorator)
    ↓
Verify User from Database
    ↓
Execute SQL Operation
    ↓
Log to AuditLog Table
    ↓
Return JSON Response
    ↓
Pinia Updates State
    ↓
Vue Component Re-renders
```

### Example: Adding a Supplier

1. **Frontend** (`SuppliersView.vue`):
   ```javascript
   const supplierStore = useSupplierStore()
   await supplierStore.addSupplier({
     name: 'Global Florals Inc',
     contactInfo: 'contact@global-florals.com',
     phone: '+1-800-555-0100',
     website: 'https://global-florals.com'
   })
   ```

2. **Pinia Store** (`src/stores/suppliers.js`):
   ```javascript
   const addSupplier = async (supplier) => {
     const response = await axios.post(
       `${API_URL}/suppliers`,
       supplier,
       { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } }
     )
     suppliers.value.push(response.data)
     return response.data
   }
   ```

3. **Backend Route** (`app.py`):
   ```python
   @app.route('/api/suppliers', methods=['POST'])
   @token_required
   def create_supplier(current_user):
       data = request.get_json()
       # Insert into Suppliers table
       # Log to AuditLog table
       # Return created supplier with capitalized columns
       return jsonify({
           'id': supplier['supplier_ID'],
           'name': supplier['SupplierName'],
           'contactInfo': supplier['Email'],
           # ...
       }), 201
   ```

4. **Database** (`sql.py`):
   - Executes INSERT into `Suppliers` table
   - Automatically records entry in `AuditLog` table  
   - Returns data in JSON format to frontend

## Switching to AWS RDS MySQL

When you're ready to use AWS RDS instead of local MySQL:

### Step 1: Update Backend Configuration

Edit `backend/creds.py` with your RDS endpoint:

```python
class Creds:
    # MySQL Configuration (AWS RDS)
    host = "your-rds-endpoint.us-east-1.rds.amazonaws.com"
    user = "admin"
    password = "your_secure_password"
    database = "perfume_store"
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-in-production"
    JWT_EXPIRATION_HOURS = 24
    DEBUG = False  # Important: set to False in production
    HOST = "0.0.0.0"
    PORT = 5000
```

### Step 2: Create Database on RDS

Connect to your RDS instance:

```bash
mysql -h your-rds-endpoint.us-east-1.rds.amazonaws.com -u admin -p
```

Then:

```sql
CREATE DATABASE IF NOT EXISTS perfume_store;
EXIT;
```

### Step 3: Restart Backend

```bash
python app.py
```

The backend will automatically create all 11 tables in RDS during first run.

### Step 4: Update Frontend (if deploying)

Edit `frontend/.env.local`:

```env
VITE_API_URL=https://your-api-domain.com/api
```

## API Testing

### Test Login (creates user automatically)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "any_password"}'
```

Response:
```json
{
  "token": "eyJhbGc...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "test",
    "role": "manager"
  }
}
```

### Get All Suppliers (requires token)

```bash
curl http://localhost:5000/api/suppliers \
  -H "Authorization: Bearer eyJhbGc..."
```

### Create Supplier (requires token)

```bash
curl -X POST http://localhost:5000/api/suppliers \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Essential Botanicals",
    "contactInfo": "info@botanicals.com",
    "phone": "+1-800-555-0200",
    "website": "https://botanicals.com"
  }'
```

### Create Scent (requires token)

```bash
curl -X POST http://localhost:5000/api/scents \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rose Romance",
    "topNotes": "Bergamot, Lemon",
    "middleNotes": "Rose, Geranium",
    "baseNotes": "Sandalwood, Musk",
    "allNotes": "Bergamot, Lemon, Rose, Geranium, Sandalwood, Musk",
    "essentialOils": "Rose oil, Sandalwood oil"
  }'
```

### Get Audit Logs (requires token)

```bash
curl http://localhost:5000/api/audit-logs \
  -H "Authorization: Bearer eyJhbGc..."
```

## CSV/Excel Import - Smart Note Parsing & Essential Oils

The Import/Export feature includes intelligent parsing for fragrance notes AND automatic essential oils extraction. This means you can import scent data in two formats:

### Format 1: Separated Note Columns (Recommended)

**Most explicit and recommended format:**

| Name | Top Notes | Middle Notes | Base Notes | Essential Oils |
|------|-----------|--------------|-----------|-----------------|
| Rose Romance | Bergamot, Lemon | Rose, Jasmine | Sandalwood, Musk | Rose oil, Sandalwood |
| Ocean Breeze | Lemon, Sea Water | Waterlily, Kelp | Amberwood, Musk | - |

The backend will use these columns exactly as provided. **Essential oils from each row will be automatically extracted and added to your Essential Oils library.**

### Format 2: Combined Notes (Auto-Parsed)

**If your data only has a "Notes" or "Fragrance Notes" column:**

| Name | Fragrance Notes |
|------|-----------------|
| Rose Romance | (Bergamot, Lemon, Rose, Jasmine, Sandalwood, Musk) |
| Ocean Breeze | Lemon, Sea Water, Waterlily, Kelp, Amberwood, Musk |

**The app will automatically split the notes into thirds:**
- **Position 1/3** → Top Notes  
- **Position 2/3** → Middle Notes  
- **Position 3/3** → Base Notes

**Example parsing:**
```
Input:  "(light apple, rose, carnation, jasmine, suede, musk, wood)"
↓
Parsed into 7 notes: [light apple, rose, carnation, jasmine, suede, musk, wood]
↓
Split into thirds:
  Top (1-3):     light apple, rose, carnation
  Middle (4-5):  jasmine, suede
  Base (6-7):    musk, wood
```

### Accepted Column Names

The import parser recognizes these column name variations (case-insensitive):

| Field | Accepted Names |
|-------|-----------------|
| Scent Name | Name, Scent Name, name, scentName |
| Top Notes | Top Notes, topNotes, topnotes, top |
| Middle Notes | Middle Notes, middleNotes, middlenotes, middle |
| Base Notes | Base Notes, baseNotes, basenotes, base |
| Combined Notes | Fragrance Notes, All Notes, allNotes, notes, fragrance |
| Oils/Ingredients | Essential Oils, essentialOils, oils, ingredients |

### Import Tips

1. **Use Format 1 for best results** - Separate columns give you full control over note categorization
2. **Essential Oils will be auto-imported** - Any oils listed in the "Essential Oils" column will be automatically added to your Essential Oils library
3. **Keep note lists short** - 3-7 notes per scent works best for auto-parsing
4. **Use commas as separators** - The parser splits by commas, so use them consistently
5. **Remove extra parentheses** - The auto-parser removes `()`, but keep them minimal
6. **File size limit** - Maximum 10MB per import

### How Essential Oils Import Works

When you upload a CSV/Excel file with an "Essential Oils" column:

1. **Scent data is imported** and each scent formula is created
2. **Essential oils are extracted** from the "Essential Oils" column (comma-separated values)
3. **Unique oils are identified** - duplicates are automatically removed
4. **Oils are added to the Essential Oils library** with "active" status
5. **Import summary shows** how many scents and oils were created

Example: If you import 50 scents with oils, but only 25 unique oils are mentioned, you'll see:
- ✅ Successfully imported 50 scents and added 25 essential oils

### Example CSV for Import

```csv
Name,Top Notes,Middle Notes,Base Notes,Essential Oils
Rose Elegance,Bergamot Lemon,Rose Geranium,Sandalwood Musk,Rose oil Sandalwood
Citrus Dream,Lemon Grapefruit,Orange Blossom Neroli,Cedarwood Amber,Lemon oil Orange
Floral Secret,Bergamot,Jasmine Iris,Oakmoss Vetiver,Jasmine Iris oil
Ocean Breeze,Lemon Sea Water,Waterlily Kelp,Amberwood Musk,"Kelp oil, Sea salt"
```

**What happens during import:**
- 4 scent formulas are created
- 8 unique essential oils are extracted and added to the Essential Oils library:
  - Rose oil, Sandalwood, Lemon oil, Orange, Jasmine, Iris oil, Kelp oil, Sea salt
- Any duplicate oil names are automatically skipped

### 1. Connection error: 'NoneType' object has no attribute 'cursor'

**Error**: Backend throws error when trying to login or access API

**Solution**:
- Check that **MySQL is running**: `mysql -u root -p` (or use MySQL Workbench)
- Verify credentials in `backend/creds.py` match your MySQL setup
- Ensure the `perfume_store` database exists: `CREATE DATABASE perfume_store;`
- Verify `mysql-connector-python` is installed: `pip install mysql-connector-python`

### 2. Frontend can't reach backend

**Error**: `Cannot GET http://localhost:5000/api/...` or CORS errors

**Solution**:
- Ensure backend is running: `python app.py` (should show "Running on http://127.0.0.1:5000")
- Check `.env.local` has correct `VITE_API_URL`: `http://localhost:5000/api`
- Check CORS is enabled in `app.py`: `CORS(app)` (it is by default)
- Try accessing backend directly: `curl http://localhost:5000/api/auth/login`

### 3. JWT token errors

**Error**: `401 Invalid token`, `401 Token is missing`, or `401 Token has expired`

**Solutions**:
- Token has expired: Login again to get a new token (expires after 24 hours by default)
- Invalid format: Ensure `Authorization` header is: `Bearer <token_here>` (with space)
- Missing header: Check that Pinia store is saving token: `localStorage.getItem('authToken')`

### 4. Module not found errors

**Error**: `ModuleNotFoundError: No module named 'flask'` or `mysql`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### 5. "Unknown column" errors (e.g., 'password_hash' in 'field list')

**Error**: Backend throws error when trying to login

**Solution**: 
- Clear Python cache: Delete `backend/__pycache__` folder
- Restart backend: `python app.py`
- This happens when old bytecode is cached after schema updates

### 6. Multiple table creation errors on startup

**Error**: "Table 'X' already exists"

**Solution**: 
- This is normal on first run - the schema initializes all 11 tables
- If you see repeated errors, drop and recreate the database:
  ```sql
  DROP DATABASE perfume_store;
  CREATE DATABASE perfume_store;
  ```
  Then restart the backend

### 7. Supplier/Scent creation fails

**Error**: `500 Internal Server Error` when trying to add supplier or scent

**Solutions**:
- Check backend logs for specific error message
- Ensure all required fields are provided (e.g., "name" is required)
- Check that Suppliers table exists: `SHOW TABLES;` in MySQL
- Try a simpler test: `curl -X POST http://localhost:5000/api/suppliers -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"name":"Test"}'`

## File Descriptions

### Backend Files

- **app.py** (700+ lines)
  - Flask REST API with all routes
  - Authentication routes (`/api/auth/login`, `/api/auth/me`)
  - CRUD endpoints for suppliers and scents
  - Audit logging for all actions
  - Token verification with `@token_required` decorator
  - CORS enabled for frontend integration

- **sql.py** (150+ lines)
  - Database connection management
  - Query execution with error handling
  - `create_connection()` - Establish MySQL connection
  - `execute_query()` - Write operations (INSERT, UPDATE, DELETE)
  - `execute_read_query()` - Read operations (SELECT)
  - `init_db_schema()` - Automatically creates all 11 tables
  - Automatic row-to-dictionary conversion

- **creds.py** (20 lines)
  - Centralized configuration management
  - MySQL connection details
  - Flask settings (debug mode, secret key, etc.)
  - JWT configuration
  - Easy to switch between local MySQL and AWS RDS

- **db_schema.sql** (Reference file)
  - Complete SQL schema for all 11 tables
  - For reference only - tables are created automatically by `init_db_schema()`
  - Useful for understanding table structure

- **requirements.txt**
  - `Flask` - Web server framework
  - `Flask-CORS` - Cross-origin requests (frontend integration)
  - `PyJWT` - JWT token creation and verification
  - `mysql-connector-python` - MySQL database driver
  - `Werkzeug` - Password hashing and utilities

### Frontend Files

- **src/stores/auth.js**
  - JWT token management and persistence
  - User login/logout/authentication
  - Automatic token refresh on page reload
  - API integration for auth endpoints

- **src/stores/suppliers.js**
  - Suppliers CRUD operations (Create, Read, Update, Delete)
  - API calls to `/api/suppliers` endpoints
  - State management for suppliers list
  - Error handling

- **src/stores/scents.js**
  - Scents management (formulas)
  - API integration with `/api/scents` endpoints
  - Soft-delete (archive) functionality
  - Create, update, search scents

- **src/stores/audit.js**
  - Audit log retrieval and filtering
  - API integration with `/api/audit-logs`
  - Search and filter audit logs by action, table, user

- **src/views/SuppliersView.vue**
  - Manage suppliers table and modal forms
  - Search/filter functionality
  - Role-based UI (edit/delete buttons)
  - Calls supplier store for API operations

- **src/views/ScentLibrary.vue**
  - Manage scent formulas
  - Create/edit/delete scents
  - Display scent notes (top, middle, base)
  - Calls scent store for API operations

- **src/views/AuditLogs.vue**
  - View complete audit trail
  - Search and filter logs
  - Display user actions with timestamps

- **src/components/SupplierModal.vue**
  - Reusable modal for adding/editing suppliers
  - Form validation
  - Emits submit event to parent component

- **src/components/ScentModal.vue**
  - Reusable modal for adding/editing scents
  - Form for scent notes
  - Emits submit event to parent component

- **.env.local**
  - Backend API URL: `VITE_API_URL=http://localhost:5000/api`
  - Other Vue configuration variables

- **vite.config.js**
  - Vite build configuration
  - Vue 3 plugin setup
  - Development server settings

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
