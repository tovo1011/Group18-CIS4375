"""
Database Credentials and Configuration
Update these values based on your database setup
"""

class Creds:
    # MySQL Configuration
    db_type = "mysql"
    host = "your-mysql-host.com"
    user = "your-username"
    password = "your-password"
    database = "perfume_store"
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-in-production"
    JWT_EXPIRATION_HOURS = 24
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
