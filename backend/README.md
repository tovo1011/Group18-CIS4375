# Perfume Store Dashboard - Backend API

A Flask-based REST API for the Perfume Store Dashboard. Follows a modular architecture similar to the `final-project` structure with separated credentials, database utilities, and application logic.

## Architecture Overview

The backend is organized into three main files following best practices for separation of concerns:

### 1. **creds.py** - Configuration & Credentials
Stores all configuration settings and credentials in a single location:
- Database connection details
- Flask configuration
- Environment-specific settings
- Ready for AWS RDS integration when needed (just uncomment and fill in values)

### 2. **sql.py** - Database Utilities
Provides database abstraction layer:
- `create_connection()` - Establishes database connection (SQLite or MySQL)
- `execute_query()` - Runs write operations (INSERT, UPDATE, DELETE)
- `execute_read_query()` - Runs read operations (SELECT)
- `init_db_schema()` - Creates all required tables
- Supports both SQLite (development) and MySQL/RDS (production)

### 3. **app.py** - Flask Application
Main application with all API routes and business logic:
- Imports from `creds` for configuration
- Imports from `sql` for database operations
- Contains all API endpoints
- Handles authentication, CRUD operations, audit logging

## Features

- ✅ **JWT Authentication** - Secure token-based login
- ✅ **CRUD Operations** - Suppliers, Ingredients, Scents management
- ✅ **Audit Logging** - Track all changes with user info and timestamps
- ✅ **Import/Export** - Bulk data operations
- ✅ **Database Abstraction** - Easy switching between SQLite and MySQL/RDS
- ✅ **CORS Support** - Ready for frontend integration
- ✅ **Sample Data** - Initialize DB with demo data

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python app.py
# Server runs on 0
```http://localhost:500

Then make a POST request to initialize:
```bash
curl -X POST http://localhost:5000/api/init-db
```

Or in Python:
```python
from app import app, conn, init_db_schema
with app.app_context():
    init_db_schema(conn)
```

### 3. Run the Server
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Switching to AWS RDS

When ready to use AWS RDS MySQL:

1. **Update `creds.py`**:
```python
class Creds:
    db_type = "mysql"
    host = "your-rds-endpoint.us-east-1.rds.amazonaws.com"
    user = "admin"
    password = "your_password_here"
    database = "perfume_store"
```

2. **Install MySQL connector** (already in requirements.txt):
```bash
pip install mysql-connector-python
```

3. **Restart the app** - It will automatically use RDS instead of SQLite

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password, returns JWT token
- `GET /api/auth/me` - Get current user info (requires token)

### Suppliers
- `GET /api/suppliers` - Get all suppliers
- `GET /api/suppliers/<id>` - Get supplier by ID
- `POST /api/suppliers` - Create new supplier
- `PUT /api/suppliers/<id>` - Update supplier
- `DELETE /api/suppliers/<id>` - Delete supplier

### Ingredients
- `GET /api/ingredients` - Get all ingredients
- `GET /api/ingredients/<id>` - Get ingredient by ID
- `POST /api/ingredients` - Create new ingredient
- `PUT /api/ingredients/<id>` - Update ingredient
- `DELETE /api/ingredients/<id>` - Delete ingredient

### Scents
- `GET /api/scents` - Get all active scents
- `GET /api/scents/<id>` - Get scent by ID
- `POST /api/scents` - Create new scent
- `PUT /api/scents/<id>` - Update scent
- `DELETE /api/scents/<id>` - Archive scent

### Audit Logs
- `GET /api/audit-logs` - Get all audit logs (most recent first)
- `GET /api/audit-logs/filter` - Filter by action, table, or user

### Import/Export
- `GET /api/export` - Export all data as JSON
- `POST /api/import` - Import data from JSON

### Database
- `POST /api/init-db` - Initialize database with sample data

## Request Format

All API requests should include:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Example: Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@t4scents.com", "password": "manager123"}'
```

Response:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 2,
    "email": "manager@t4scents.com",
    "name": "Manager",
    "role": "manager"
  }
}
```

### Example: Create Supplier (requires token)
```bash
curl -X POST http://localhost:5000/api/suppliers \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Supplier",
    "contactInfo": "contact@example.com",
    "website": "https://example.com",
    "phone": "+1-800-000-0000"
  }'
```

## Sample Data

The `/api/init-db` endpoint automatically creates:

**Users:**
- admin@t4scents.com (password: admin123, role: admin)
- manager@t4scents.com (password: manager123, role: manager)

**Suppliers:**
- Global Florals Inc
- Citrus Trading Co
- Essence Importers Ltd

**Ingredients:**
- Rose Oil, Bergamot Oil, Sandalwood Oil

**Scents:**
- Rose Elegance, Ocean Breeze

## Database Schema

### users
```
id (INTEGER PK)
email (TEXT, unique)
password_hash (TEXT)
name (TEXT)
role (TEXT) - admin, manager, viewer
created_at (TIMESTAMP)
```

### suppliers
```
id (INTEGER PK)
name (TEXT)
contact_info (TEXT)
website (TEXT)
phone (TEXT)
created_at (TIMESTAMP)
```

### ingredients
```
id (INTEGER PK)
name (TEXT)
supplier_id (FK -> suppliers)
cost (REAL)
link (TEXT)
storage_location (TEXT)
created_at (TIMESTAMP)
```

### scents
```
id (INTEGER PK)
name (TEXT)
top_notes (TEXT)
middle_notes (TEXT)
base_notes (TEXT)
created_by (TEXT)
created_at (TIMESTAMP)
archived_at (TIMESTAMP nullable) - soft delete
```

### audit_logs
```
id (INTEGER PK)
user_id (FK -> users)
user_name (TEXT)
action (TEXT) - CREATE, UPDATE, DELETE
table_name (TEXT)
record_id (INTEGER)
record_name (TEXT)
details (TEXT)
timestamp (TIMESTAMP)
```

## Configuration

Edit `creds.py` to customize:
- Database type and connection details
- Flask debug mode
- Server host and port
- JWT expiration time
- Secret key

## Notes

- Scents use soft-delete (archived rather than hard-deleted)
- All timestamps are automatically set by the database
- Audit logs are created automatically for all modifications
- Demo mode: Login creates users automatically if they don't exist
- Foreign keys are enforced for data integrity

## Troubleshooting

**"Module not found" error**:
```bash
pip install -r requirements.txt
```

**Database connection failed**:
- Check that `creds.py` has correct database settings
- For SQLite: ensure write permissions in backend directory
- For MySQL: verify RDS endpoint, credentials, and security groups

**Token expired**:
- Login again to get a new token
- JWT tokens expire every 24 hours (configurable in `creds.py`)
