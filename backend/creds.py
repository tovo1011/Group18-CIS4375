"""
Database Credentials and Configuration
Update these values based on your database setup
"""

class Creds:
    # MySQL Configuration
    # host = "cis4375spring26db2.c92e4wii2y91.us-east-2.rds.amazonaws.com"
    host = "18.116.171.249"
    user = "t4admin"
    password = "T4Scents_2026_Secure!"
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
