"""
Database Utilities
Handles database connections and query execution
"""
from mysql.connector import Error as MySQLError
from creds import Creds

# Initialize creds
creds = Creds()

def create_connection():
    """Create a MySQL database connection"""
    connection = None
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host=creds.host,
            user=creds.user,
            password=creds.password,
            database=creds.database
        )
        print("MySQL connection successful!")
    except Exception as e:
        print(f"Connection error: {e}")
    return connection

def execute_query(connection, query, values=None):
    """Execute a write query (INSERT, UPDATE, DELETE)"""
    try:
        cursor = connection.cursor()
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        connection.commit()
        print(f"Query executed successfully")
        return True
    except Exception as e:
        print(f"Query error: {e}")
        connection.rollback()
        return False

def execute_read_query(connection, query, values=None):
    """Execute a read query (SELECT)"""
    try:
        cursor = connection.cursor(dictionary=True)
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result if result else []
    except Exception as e:
        print(f"Read query error: {e}")
        return []

def init_db_schema(connection):
    """Initialize database schema with all required tables"""
    schema_queries = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'manager',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # Suppliers table
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            contact_info TEXT,
            website TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # Ingredients table
        """
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            supplier_id INTEGER NOT NULL,
            cost REAL NOT NULL,
            link TEXT,
            storage_location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
        """,
        # Scents table
        """
        CREATE TABLE IF NOT EXISTS scents (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            top_notes TEXT NOT NULL,
            middle_notes TEXT NOT NULL,
            base_notes TEXT NOT NULL,
            all_notes TEXT,
            essential_oils TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived_at TIMESTAMP
        )
        """,
        # Audit logs table
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            action TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            record_name TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    ]
    
    for query in schema_queries:
        try:
            execute_query(connection, query)
            print(f"Table created/verified successfully")
        except Exception as e:
            print(f"Schema initialization error: {e}")
    
    return connection
