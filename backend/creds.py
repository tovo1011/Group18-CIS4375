"""
Database Credentials and Configuration
Update these values based on your database setup
"""

class Creds:
    
    host = "127.0.0.1"
    user = "t4admin"
    password = "ihatesql$%"
    database = "perfume_store"
    
    # Flask Configuration
    SECRET_KEY = "antenna-knife-family"
    JWT_EXPIRATION_HOURS = 24
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    
    # Owner Credentials
    OWNER_EMAIL = "t4owner@email.com"
    OWNER_PASSWORD = "p4ssword"
