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
        ("Users", """
        CREATE TABLE IF NOT EXISTS Users (
            UserID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(50) NOT NULL UNIQUE,
            Email VARCHAR(100) NOT NULL UNIQUE,
            PasswordHash VARCHAR(255) NOT NULL,
            FirstName VARCHAR(50),
            LastName VARCHAR(50),
            UserRole VARCHAR(20) NOT NULL,
            Status VARCHAR(20) NOT NULL,
            CreatedDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            LastLoginDate DATETIME NULL,
            UpdatedDate DATETIME NULL DEFAULT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Scents table
        ("Scents", """
        CREATE TABLE IF NOT EXISTS Scents (
            scent_ID INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(100),
            Scent_description VARCHAR(250),
            Scent_status VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Scent_Essential_Oil table
        ("Scent_Essential_Oil", """
        CREATE TABLE IF NOT EXISTS Scent_Essential_Oil (
            scent_oil_ID INT AUTO_INCREMENT PRIMARY KEY,
            scent_ID INT,
            oil_ID INT,
            note_type VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Essential_oil table
        ("Essential_oil", """
        CREATE TABLE IF NOT EXISTS Essential_oil (
            oil_ID INT AUTO_INCREMENT PRIMARY KEY,
            supplier_ID INT,
            oil_name VARCHAR(150),
            oil_description VARCHAR(150),
            unit_cost INT,
            oil_status VARCHAR(150)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Suppliers table
        ("Suppliers", """
        CREATE TABLE IF NOT EXISTS Suppliers (
            supplier_ID INT AUTO_INCREMENT PRIMARY KEY,
            SupplierName VARCHAR(100) NOT NULL UNIQUE,
            ContactName VARCHAR(100),
            Email VARCHAR(100),
            Phone VARCHAR(20),
            Address VARCHAR(200),
            Last_order_date DATETIME
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Products table
        ("Products", """
        CREATE TABLE IF NOT EXISTS Products (
            product_ID VARCHAR(50) PRIMARY KEY,
            scent_ID INT NOT NULL,
            product_name VARCHAR(100) NOT NULL,
            product_type VARCHAR(100) NOT NULL,
            price INT NOT NULL,
            FOREIGN KEY (scent_ID) REFERENCES Scents(scent_ID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # DashBoardMetrics table
        ("DashBoardMetrics", """
        CREATE TABLE IF NOT EXISTS DashBoardMetrics (
            MetricID INT AUTO_INCREMENT PRIMARY KEY,
            MetricType VARCHAR(50) NOT NULL,
            MetricValue DECIMAL(10,2) NOT NULL,
            ReferenceID INT,
            CalculatedDate DATETIME NOT NULL,
            UpdatedDate DATETIME
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # AuditLog table
        ("AuditLog", """
        CREATE TABLE IF NOT EXISTS AuditLog (
            AuditID INT AUTO_INCREMENT PRIMARY KEY,
            UserID INT NOT NULL,
            AuditAction VARCHAR(50) NOT NULL,
            TableName VARCHAR(50) NOT NULL,
            RecordID INT,
            old_Value TEXT,
            new_value TEXT,
            IP_address VARCHAR(50),
            Timestamp DATETIME NOT NULL,
            FOREIGN KEY (UserID) REFERENCES Users(UserID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Customers table
        ("Customers", """
        CREATE TABLE IF NOT EXISTS Customers (
            Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(150),
            last_name VARCHAR(150),
            email VARCHAR(150),
            phone VARCHAR(150),
            customer_address VARCHAR(150),
            customer_state VARCHAR(150),
            zip INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Order table
        ("Order", """
        CREATE TABLE IF NOT EXISTS `Order` (
            order_ID INT AUTO_INCREMENT PRIMARY KEY,
            customer_ID INT,
            order_date DATETIME,
            total_amount INT,
            order_status VARCHAR(50),
            FOREIGN KEY (customer_ID) REFERENCES Customers(Customer_ID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """),
        # Order_Item table
        ("Order_Item", """
        CREATE TABLE IF NOT EXISTS Order_Item (
            orderitem_ID INT AUTO_INCREMENT PRIMARY KEY,
            order_ID INT,
            product_ID INT,
            quantity INT,
            unit_price INT
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
