# creds.example.py
# INSTRUCTIONS: Copy this file, rename it to 'creds.py', and fill in the values.

class Creds:
    # MySQL Configuration
    db_type = "mysql"
    host = "REPLACE_WITH_LIGHTSAIL_IP"       # ask torin for IP address of the Lightsail instance
    user = "t4admin"                         # Use 't4admin' for remote AWS access
    password = "REPLACE_WITH_PASSWORD"       # ask torin for password
    database = "perfume_store"
    
    # Flask Configuration
    SECRET_KEY = "antenna-knife-family"
    JWT_EXPIRATION_HOURS = 24
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 5000