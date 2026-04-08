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
        ("users", """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'manager',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Suppliers table
        ("suppliers", """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            contact_info TEXT,
            website VARCHAR(255),
            phone VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Ingredients table
        ("ingredients", """
        CREATE TABLE IF NOT EXISTS ingredients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            supplier_id INT NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            link VARCHAR(512),
            storage_location VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Scents table
        ("scents", """
        CREATE TABLE IF NOT EXISTS scents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            top_notes TEXT NOT NULL,
            middle_notes TEXT NOT NULL,
            base_notes TEXT NOT NULL,
            all_notes TEXT,
            essential_oils TEXT,
            created_by VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived_at TIMESTAMP NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Audit logs table
        ("audit_logs", """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            action VARCHAR(100) NOT NULL,
            table_name VARCHAR(100) NOT NULL,
            record_id INT NOT NULL,
            record_name VARCHAR(255) NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
    ]
    
    for table_name, query in schema_queries:
        try:
            execute_query(connection, query)
            print(f"Table '{table_name}' created or verified successfully")
        except Exception as e:
            print(f"Schema initialization error for {table_name}: {e}")
    
    return connection
