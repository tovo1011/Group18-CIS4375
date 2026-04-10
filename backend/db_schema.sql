CREATE TABLE Users (
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

CREATE TABLE Scents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    top_notes VARCHAR(500),
    middle_notes VARCHAR(500),
    base_notes VARCHAR(500),
    all_notes VARCHAR(1000),
    essential_oils VARCHAR(500),
    created_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    archived_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Scent_Essential_Oil (
    scent_oil_ID INT AUTO_INCREMENT PRIMARY KEY,
    id INT,
    oil_ID INT,
    note_type VARCHAR(100),
    FOREIGN KEY (id) REFERENCES Scents(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Essential_oil (
    oil_ID INT AUTO_INCREMENT PRIMARY KEY,
    supplier_ID INT,
    oil_name VARCHAR(150),
    oil_description VARCHAR(150),
    unit_cost INT,
    oil_status VARCHAR(150)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Suppliers (
    supplier_ID INT AUTO_INCREMENT PRIMARY KEY,
    SupplierName VARCHAR(100) NOT NULL UNIQUE,
    ContactName VARCHAR(100),
    Email VARCHAR(100),
    Phone VARCHAR(20),
    Address VARCHAR(200),
    Last_order_date DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Products (
    product_ID VARCHAR(50) PRIMARY KEY,
    id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    price INT NOT NULL,
    FOREIGN KEY (id) REFERENCES Scents(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE DashBoardMetrics (
    MetricID INT AUTO_INCREMENT PRIMARY KEY,
    MetricType VARCHAR(50) NOT NULL,
    MetricValue DECIMAL(10,2) NOT NULL,
    ReferenceID INT,
    CalculatedDate DATETIME NOT NULL,
    UpdatedDate DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE AuditLog (
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

CREATE TABLE Customers (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(150),
    phone VARCHAR(150),
    customer_address VARCHAR(150),
    customer_state VARCHAR(150),
    zip INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Order` (
    order_ID INT AUTO_INCREMENT PRIMARY KEY,
    customer_ID INT,
    order_date DATETIME,
    total_amount INT,
    order_status VARCHAR(50),
    FOREIGN KEY (customer_ID) REFERENCES Customers(Customer_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Order_Item (
    orderitem_ID INT AUTO_INCREMENT PRIMARY KEY,
    order_ID INT,
    product_ID INT,
    quantity INT,
    unit_price INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
