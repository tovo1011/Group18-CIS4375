"""
Perfume Store Dashboard API
Flask-based REST API with authentication, suppliers, ingredients, scents, and audit logging
"""

import flask
from flask import jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

from creds import Creds
from sql import create_connection, execute_query, execute_read_query, init_db_schema

# Initialize Flask app
app = flask.Flask(__name__)
app.config["debug"] = Creds.DEBUG

# Initialize CORS for frontend integration
CORS(app)

# Initialize database connection
conn = create_connection()
if conn:
    init_db_schema(conn)
    print("Database initialized successfully")

# ==================== Helper Functions ====================

def get_db_connection():
    """Get a valid database connection, reconnecting if necessary"""
    global conn
    try:
        if conn is None or not conn.is_connected():
            print("Reconnecting to database...")
            conn = create_connection()
    except Exception as e:
        print(f"Connection check error: {e}")
        conn = create_connection()
    return conn

def token_required(f):
    """Decorator to check JWT token on protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Ensure we have a valid database connection
        db_conn = get_db_connection()
        
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, Creds.SECRET_KEY, algorithms=['HS256'])
            # Get current user from database
            query = "SELECT * FROM Users WHERE UserID = %s"
            users = execute_read_query(db_conn, query, (data['user_id'],))
            if not users:
                return jsonify({'message': 'User not found'}), 401
            current_user = users[0]
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def create_token(user):
    """Create a JWT token for a user"""
    payload = {
        'user_id': user['UserID'],
        'email': user['Email'],
        'exp': datetime.utcnow() + timedelta(hours=Creds.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Creds.SECRET_KEY, algorithm='HS256')

def log_audit(user_id, action, table_name, record_id):
    """Log an audit entry for data modifications"""
    db_conn = get_db_connection()
    query = """
    INSERT INTO AuditLog (UserID, Timestamp, AuditAction, TableName, RecordID)
    VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s)
    """
    values = (user_id, action, table_name, record_id)
    execute_query(db_conn, query, values)

# ==================== Auth Routes ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login - only owner can access the dashboard"""
    db_conn = get_db_connection()
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required'}), 400
    
    # Only allow owner to log in
    if data['email'] != Creds.OWNER_EMAIL:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Verify password
    if data['password'] != Creds.OWNER_PASSWORD:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Ensure owner exists in database
    query = "SELECT * FROM Users WHERE Email = %s"
    users = execute_read_query(db_conn, query, (Creds.OWNER_EMAIL,))
    user = users[0] if users else None
    
    # Create owner account if doesn't exist
    if not user:
        password_hash = generate_password_hash(Creds.OWNER_PASSWORD)
        insert_query = """
        INSERT INTO Users (Email, PasswordHash, Username, UserRole, Status)
        VALUES (%s, %s, %s, 'admin', 'active')
        """
        created = execute_query(db_conn, insert_query, (Creds.OWNER_EMAIL, password_hash, 'Owner'))
        if not created:
            return jsonify({'message': 'Unable to initialize owner account'}), 500
        
        # Fetch the newly created user
        users = execute_read_query(db_conn, query, (Creds.OWNER_EMAIL,))
        if not users:
            return jsonify({'message': 'Owner account creation failed'}), 500
        user = users[0]
    
    # Generate token
    token = create_token(user)
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['UserID'],
            'email': user['Email'],
            'name': user['Username'],
            'role': user['UserRole']
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current authenticated user"""
    return jsonify({
        'id': current_user['UserID'],
        'email': current_user['Email'],
        'name': current_user['Username'],
        'role': current_user['UserRole']
    }), 200

# ==================== Supplier Routes ====================

@app.route('/api/suppliers', methods=['GET'])
@token_required
def get_suppliers(current_user):
    """Get all suppliers"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Suppliers"
    suppliers = execute_read_query(db_conn, query)
    return jsonify([{
        'id': s['supplier_ID'],
        'name': s['SupplierName'],
        'contactInfo': s['Email'],
        'phone': s['Phone'],
        'website': s['Address'],
        'createdAt': s.get('CreatedDate', None)
    } for s in suppliers]), 200

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
@token_required
def get_supplier(current_user, supplier_id):
    """Get supplier by ID"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Suppliers WHERE supplier_ID = %s"
    suppliers = execute_read_query(db_conn, query, (supplier_id,))
    
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    s = suppliers[0]
    return jsonify({
        'id': s['supplier_ID'],
        'name': s['SupplierName'],
        'contactInfo': s['Email'],
        'phone': s['Phone'],
        'website': s['Address'],
        'createdAt': s.get('CreatedDate', None)
    }), 200

@app.route('/api/suppliers', methods=['POST'])
@token_required
def create_supplier(current_user):
    """Create new supplier"""
    db_conn = get_db_connection()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Supplier name is required'}), 400
    
    query = """
    INSERT INTO Suppliers (SupplierName, ContactName, Email, Phone, Address)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (data['name'], data.get('name'), data.get('contactInfo'), data.get('phone'), data.get('website'))
    execute_query(db_conn, query, values)
    
    # Get the newly created supplier
    select_query = "SELECT * FROM Suppliers WHERE SupplierName = %s ORDER BY supplier_ID DESC LIMIT 1"
    suppliers = execute_read_query(db_conn, select_query, (data['name'],))
    supplier = suppliers[0]
    
    log_audit(current_user['UserID'], 'CREATE', 'Suppliers', supplier['supplier_ID'])
    
    return jsonify({
        'id': supplier['supplier_ID'],
        'name': supplier['SupplierName'],
        'contactInfo': supplier['Email'],
        'phone': supplier['Phone'],
        'website': supplier['Address'],
        'createdAt': supplier.get('CreatedDate', None)
    }), 201

@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
@token_required
def update_supplier(current_user, supplier_id):
    """Update supplier"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Suppliers WHERE supplier_ID = %s"
    suppliers = execute_read_query(db_conn, query, (supplier_id,))
    
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    data = request.get_json()
    supplier = suppliers[0]
    old_name = supplier['SupplierName']
    
    update_query = """
    UPDATE Suppliers
    SET SupplierName = %s, ContactName = %s, Email = %s, Phone = %s, Address = %s
    WHERE supplier_ID = %s
    """
    values = (
        data.get('name', supplier['SupplierName']),
        data.get('name', supplier.get('ContactName', '')),
        data.get('contactInfo', supplier['Email']),
        data.get('phone', supplier['Phone']),
        data.get('website', supplier.get('Address', '')),
        supplier_id
    )
    execute_query(db_conn, update_query, values)
    
    log_audit(current_user['UserID'], 'UPDATE', 'Suppliers', supplier_id)
    
    # Return updated supplier
    suppliers = execute_read_query(db_conn, "SELECT * FROM Suppliers WHERE supplier_ID = %s", (supplier_id,))
    s = suppliers[0]
    return jsonify({
        'id': s['supplier_ID'],
        'name': s['SupplierName'],
        'contactInfo': s['Email'],
        'phone': s['Phone'],
        'website': s['Address'],
        'createdAt': s.get('CreatedDate', None)
    }), 200

@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
@token_required
def delete_supplier(current_user, supplier_id):
    """Delete supplier"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Suppliers WHERE supplier_ID = %s"
    suppliers = execute_read_query(db_conn, query, (supplier_id,))
    
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    supplier = suppliers[0]
    supplier_name = supplier['SupplierName']
    
    delete_query = "DELETE FROM Suppliers WHERE supplier_ID = %s"
    execute_query(db_conn, delete_query, (supplier_id,))
    
    log_audit(current_user['UserID'], 'DELETE', 'Suppliers', supplier_id)
    
    return jsonify({'message': 'Supplier deleted'}), 200

# ==================== Scent Helper Functions ====================

INGREDIENT_CATEGORIES = {
    'top': ['lemon', 'mandarin', 'bergamot', 'orange peel', 'grapefruit', 'lime', 'mint', 'ginger', 'pepper', 'citrus', 'raspberry', 'berry', 'blackberry', 'green', 'fresh', 'zest'],
    'middle': ['jasmine', 'rose', 'carnation', 'lavender', 'peach', 'strawberry', 'plum', 'cinnamon', 'nutmeg', 'clove', 'floral', 'blossom', 'tuberose', 'geranium', 'iris', 'ylang'],
    'base': ['sandalwood', 'cedarwood', 'musk', 'tonka', 'amber', 'coffee', 'honey', 'caramel', 'cocoa', 'vanilla', 'patchouli', 'vetiver', 'oud', 'leather', 'wood', 'bean', 'almond', 'oats']
}

def categorize_scent_notes(all_notes_str):
    """
    Auto-split ingredient list into top, middle, and base notes based on perfume pyramid.
    Each ingredient is categorized exactly once - never duplicated across categories.
    Matching order: top → base → middle → (default to middle if no match)
    """
    if not all_notes_str:
        return '', '', ''
    
    # Split ingredients and normalize
    ingredients = [ing.strip() for ing in all_notes_str.split(',') if ing.strip()]
    if not ingredients:
        return '', '', ''
    
    top, middle, base = [], [], []
    
    for ing in ingredients:
        ing_lower = ing.lower()
        matched = False
        
        # Check top notes first
        if any(keyword in ing_lower for keyword in INGREDIENT_CATEGORIES['top']):
            top.append(ing)
            matched = True
        # Check base notes second (before middle since some keywords could conflict)
        elif any(keyword in ing_lower for keyword in INGREDIENT_CATEGORIES['base']):
            base.append(ing)
            matched = True
        # Check middle notes third
        elif any(keyword in ing_lower for keyword in INGREDIENT_CATEGORIES['middle']):
            middle.append(ing)
            matched = True
        
        # If no keyword matched, default to middle notes
        if not matched:
            middle.append(ing)
    
    return (
        ', '.join(top) if top else '',
        ', '.join(middle) if middle else '',
        ', '.join(base) if base else ''
    )

# ==================== Scent Routes ====================

def clean_notes(text):
    """Strip surrounding parentheses, brackets, and extra whitespace from notes."""
    if not text:
        return ''
    return text.strip().strip('()[]').strip()

def format_scent(s):
    """Format a scent row, auto-categorizing notes if individual fields are empty."""
    top = clean_notes(s['top_notes'] or '')
    middle = clean_notes(s['middle_notes'] or '')
    base = clean_notes(s['base_notes'] or '')
    all_notes = clean_notes(s.get('all_notes', '') or '')

    if not (top or middle or base) and all_notes:
        top, middle, base = categorize_scent_notes(all_notes)

    return {
        'id': s['id'],
        'name': s['name'],
        'topNotes': top,
        'middleNotes': middle,
        'baseNotes': base,
        'allNotes': all_notes,
        'essentialOils': s.get('essential_oils', ''),
        'createdBy': s['created_by'],
        'createdAt': s['created_at'],
        'archivedAt': s['archived_at']
    }

@app.route('/api/scents', methods=['GET'])
@token_required
def get_scents(current_user):
    """Get all active scents (not archived)"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Scents WHERE archived_at IS NULL"
    scents = execute_read_query(db_conn, query)
    return jsonify([format_scent(s) for s in scents]), 200

@app.route('/api/scents/<int:scent_id>', methods=['GET'])
@token_required
def get_scent(current_user, scent_id):
    """Get single scent by ID"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Scents WHERE id = %s"
    scents = execute_read_query(db_conn, query, (scent_id,))

    if not scents:
        return jsonify({'message': 'Scent not found'}), 404

    return jsonify(format_scent(scents[0])), 200

@app.route('/api/scents', methods=['POST'])
@token_required
def create_scent(current_user):
    """Create new scent"""
    db_conn = get_db_connection()
    data = request.get_json()
    
    # Name is required, note details are optional (will be auto-categorized if needed)
    if not data or not data.get('name'):
        return jsonify({'message': 'Scent name is required'}), 400
    
    # Check for duplicate scent name (case-insensitive)
    dup_query = "SELECT * FROM Scents WHERE LOWER(name) = LOWER(%s) AND archived_at IS NULL"
    duplicates = execute_read_query(db_conn, dup_query, (data['name'],))
    if duplicates:
        return jsonify({'message': f'Scent "{data["name"]}" already exists'}), 409
    
    # Auto-categorize notes if not provided individually
    top_notes = data.get('topNotes', '')
    middle_notes = data.get('middleNotes', '')
    base_notes = data.get('baseNotes', '')
    
    all_notes = data.get('allNotes', '') or data.get('essentialOils', '')
    
    # If individual notes not provided, auto-categorize from allNotes
    if not (top_notes and middle_notes and base_notes) and all_notes:
        top_notes, middle_notes, base_notes = categorize_scent_notes(all_notes)
    
    query = """
    INSERT INTO Scents (name, top_notes, middle_notes, base_notes, all_notes, essential_oils, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data['name'],
        top_notes,
        middle_notes,
        base_notes,
        all_notes,
        data.get('essentialOils', ''),
        current_user['Email']
    )
    execute_query(db_conn, query, values)
    
    # Get the newly created scent
    select_query = "SELECT * FROM Scents WHERE name = %s ORDER BY id DESC LIMIT 1"
    scents = execute_read_query(db_conn, select_query, (data['name'],))
    scent = scents[0]
    
    log_audit(current_user['UserID'], 'CREATE', 'Scents', scent['id'])
    
    return jsonify({
        'id': scent['id'],
        'name': scent['name'],
        'topNotes': scent['top_notes'],
        'middleNotes': scent['middle_notes'],
        'baseNotes': scent['base_notes'],
        'allNotes': scent.get('all_notes', ''),
        'essentialOils': scent.get('essential_oils', ''),
        'createdBy': scent['created_by'],
        'createdAt': scent['created_at'],
        'archivedAt': scent['archived_at']
    }), 201

@app.route('/api/scents/<int:scent_id>', methods=['PUT'])
@token_required
def update_scent(current_user, scent_id):
    """Update scent"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Scents WHERE id = %s"
    scents = execute_read_query(db_conn, query, (scent_id,))
    
    if not scents:
        return jsonify({'message': 'Scent not found'}), 404
    
    data = request.get_json()
    scent = scents[0]
    old_name = scent['name']
    
    update_query = """
    UPDATE Scents
    SET name = %s, top_notes = %s, middle_notes = %s, base_notes = %s, all_notes = %s, essential_oils = %s
    WHERE id = %s
    """
    values = (
        data.get('name', scent['name']),
        data.get('topNotes', scent['top_notes']),
        data.get('middleNotes', scent['middle_notes']),
        data.get('baseNotes', scent['base_notes']),
        data.get('allNotes', scent.get('all_notes', '')),
        data.get('essentialOils', scent.get('essential_oils', '')),
        scent_id
    )
    execute_query(db_conn, update_query, values)
    
    log_audit(current_user['UserID'], 'UPDATE', 'Scents', scent_id)
    
    # Return updated scent
    scents = execute_read_query(db_conn, "SELECT * FROM Scents WHERE id = %s", (scent_id,))
    s = scents[0]
    return jsonify({
        'id': s['id'],
        'name': s['name'],
        'topNotes': s['top_notes'],
        'middleNotes': s['middle_notes'],
        'baseNotes': s['base_notes'],
        'allNotes': s.get('all_notes', ''),
        'essentialOils': s.get('essential_oils', ''),
        'createdBy': s['created_by'],
        'createdAt': s['created_at'],
        'archivedAt': s['archived_at']
    }), 200

@app.route('/api/scents/<int:scent_id>', methods=['DELETE'])
@token_required
def delete_scent(current_user, scent_id):
    """Archive scent (soft delete)"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Scents WHERE id = %s"
    scents = execute_read_query(db_conn, query, (scent_id,))
    
    if not scents:
        return jsonify({'message': 'Scent not found'}), 404
    
    scent = scents[0]
    
    update_query = "UPDATE Scents SET archived_at = CURRENT_TIMESTAMP WHERE id = %s"
    execute_query(db_conn, update_query, (scent_id,))
    
    log_audit(current_user['UserID'], 'DELETE', 'Scents', scent_id)
    
    return jsonify({'message': 'Scent archived'}), 200

@app.route('/api/scents/preview-import', methods=['POST'])
@token_required
def preview_import_scents(current_user):
    """Preview scent categorization before import - returns processed scents ready for user review"""
    try:
        data = request.get_json()
        
        if not data or 'scents' not in data:
            return jsonify({'error': 'No scents data provided'}), 400
        
        scents_list = data.get('scents', [])
        
        if not isinstance(scents_list, list) or len(scents_list) == 0:
            return jsonify({'error': 'Invalid scents data format'}), 400
        
        preview_results = []
        
        for index, scent_data in enumerate(scents_list):
            # Get name
            name = scent_data.get('name', '').strip()
            if not name:
                preview_results.append({
                    'rowIndex': index,
                    'name': '',
                    'error': 'Missing scent name'
                })
                continue
            
            # Get note values - prefer already-categorized, fall back to auto-categorize
            top_notes = scent_data.get('topNotes', '').strip() or scent_data.get('top_notes', '').strip()
            middle_notes = scent_data.get('middleNotes', '').strip() or scent_data.get('middle_notes', '').strip()
            base_notes = scent_data.get('baseNotes', '').strip() or scent_data.get('base_notes', '').strip()
            all_notes = scent_data.get('allNotes', '').strip() or scent_data.get('all_notes', '').strip()
            
            # Auto-categorize if individual notes not provided
            if not (top_notes and middle_notes and base_notes) and all_notes:
                top_notes, middle_notes, base_notes = categorize_scent_notes(all_notes)
            
            preview_results.append({
                'rowIndex': index,
                'name': name,
                'topNotes': top_notes,
                'middleNotes': middle_notes,
                'baseNotes': base_notes,
                'allNotes': all_notes,
                'essentialOils': scent_data.get('essentialOils', '').strip() or scent_data.get('essential_oils', '').strip()
            })
        
        return jsonify({
            'scents': preview_results,
            'total': len(scents_list),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500

@app.route('/api/scents/import', methods=['POST'])
@token_required
def import_scents(current_user):
    """Import scents from CSV/Excel file"""
    try:
        db_conn = get_db_connection()
        data = request.get_json()
        
        if not data or 'scents' not in data:
            return jsonify({'error': 'No scents data provided'}), 400
        
        scents_list = data.get('scents', [])
        filename = data.get('filename', 'unknown')
        
        if not isinstance(scents_list, list) or len(scents_list) == 0:
            return jsonify({'error': 'Invalid scents data format'}), 400
        
        imported_count = 0
        errors = []
        
        for index, scent_data in enumerate(scents_list):
            try:
                # Validate required fields
                if not scent_data.get('name'):
                    errors.append(f"Row {index + 1}: Missing scent name")
                    continue
                
                # Check for duplicates (case-insensitive to match single insert behavior)
                dup_query = "SELECT * FROM Scents WHERE LOWER(name) = LOWER(%s) AND archived_at IS NULL"
                duplicates = execute_read_query(db_conn, dup_query, (scent_data['name'],))
                if duplicates:
                    errors.append(f"Row {index + 1}: Scent '{scent_data['name']}' already exists")
                    continue
                
                # Get note values
                all_notes = scent_data.get('allNotes', '').strip() or scent_data.get('all_notes', '').strip()
                top_notes = scent_data.get('topNotes', '').strip() or scent_data.get('top_notes', '').strip()
                middle_notes = scent_data.get('middleNotes', '').strip() or scent_data.get('middle_notes', '').strip()
                base_notes = scent_data.get('baseNotes', '').strip() or scent_data.get('base_notes', '').strip()

                # If separate notes weren't provided, auto-categorize from all_notes
                if not (top_notes or middle_notes or base_notes) and all_notes:
                    top_notes, middle_notes, base_notes = categorize_scent_notes(all_notes)

                insert_query = """
                INSERT INTO Scents (name, top_notes, middle_notes, base_notes, all_notes, essential_oils, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    scent_data.get('name', '').strip(),
                    top_notes,
                    middle_notes,
                    base_notes,
                    all_notes,
                    scent_data.get('essentialOils', '').strip() or scent_data.get('essential_oils', '').strip(),
                    current_user['Email']
                )
                
                execute_query(db_conn, insert_query, values)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Log audit
        log_audit(
            current_user['UserID'],
            'CREATE',
            'Scents',
            0
        )
        
        return jsonify({
            'imported': imported_count,
            'total': len(scents_list),
            'errors': errors if errors else None,
            'message': f'Successfully imported {imported_count} scents'
        }), 200
        
    except Exception as e:
        log_audit(
            current_user['UserID'],
            'CREATE',
            'Scents',
            0
        )
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

# ==================== Essential Oils Routes ====================

@app.route('/api/essential-oils', methods=['GET'])
@token_required
def get_essential_oils(current_user):
    """Get all essential oils"""
    db_conn = get_db_connection()
    query = """
    SELECT eo.*, s.SupplierName 
    FROM Essential_oil eo
    LEFT JOIN Suppliers s ON eo.supplier_ID = s.supplier_ID
    """
    oils = execute_read_query(db_conn, query)
    return jsonify([{
        'id': oil['oil_ID'],
        'name': oil['oil_name'],
        'supplierId': oil['supplier_ID'],
        'supplierName': oil.get('SupplierName', ''),
        'unitCost': oil['unit_cost'],
        'description': oil['oil_description'],
        'status': oil['oil_status']
    } for oil in oils]), 200

@app.route('/api/essential-oils/<int:oil_id>', methods=['GET'])
@token_required
def get_essential_oil(current_user, oil_id):
    """Get essential oil by ID"""
    db_conn = get_db_connection()
    query = """
    SELECT eo.*, s.SupplierName 
    FROM Essential_oil eo
    LEFT JOIN Suppliers s ON eo.supplier_ID = s.supplier_ID
    WHERE eo.oil_ID = %s
    """
    oils = execute_read_query(db_conn, query, (oil_id,))
    
    if not oils:
        return jsonify({'message': 'Essential oil not found'}), 404
    
    oil = oils[0]
    return jsonify({
        'id': oil['oil_ID'],
        'name': oil['oil_name'],
        'supplierId': oil['supplier_ID'],
        'supplierName': oil.get('SupplierName', ''),
        'unitCost': oil['unit_cost'],
        'description': oil['oil_description'],
        'status': oil['oil_status']
    }), 200

@app.route('/api/essential-oils', methods=['POST'])
@token_required
def create_essential_oil(current_user):
    """Create new essential oil"""
    db_conn = get_db_connection()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Oil name is required'}), 400
    
    # Check for duplicate oil name (case-insensitive)
    dup_query = "SELECT * FROM Essential_oil WHERE LOWER(oil_name) = LOWER(%s)"
    duplicates = execute_read_query(db_conn, dup_query, (data['name'],))
    if duplicates:
        return jsonify({'message': f'Oil "{data["name"]}" already exists'}), 409
    
    query = """
    INSERT INTO Essential_oil (supplier_ID, oil_name, oil_description, unit_cost, oil_status)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        data.get('supplierId'),
        data['name'],
        data.get('description', ''),
        data.get('unitCost', 0),
        data.get('status', 'active')
    )
    execute_query(db_conn, query, values)
    
    # Get the newly created oil
    select_query = "SELECT * FROM Essential_oil WHERE oil_name = %s ORDER BY oil_ID DESC LIMIT 1"
    oils = execute_read_query(db_conn, select_query, (data['name'],))
    oil = oils[0]
    
    log_audit(current_user['UserID'], 'CREATE', 'Essential_oil', oil['oil_ID'])
    
    return jsonify({
        'id': oil['oil_ID'],
        'name': oil['oil_name'],
        'supplierId': oil['supplier_ID'],
        'unitCost': oil['unit_cost'],
        'description': oil['oil_description'],
        'status': oil['oil_status']
    }), 201

@app.route('/api/essential-oils/<int:oil_id>', methods=['PUT'])
@token_required
def update_essential_oil(current_user, oil_id):
    """Update essential oil"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Essential_oil WHERE oil_ID = %s"
    oils = execute_read_query(db_conn, query, (oil_id,))
    
    if not oils:
        return jsonify({'message': 'Essential oil not found'}), 404
    
    data = request.get_json()
    oil = oils[0]
    old_name = oil['oil_name']
    
    update_query = """
    UPDATE Essential_oil
    SET supplier_ID = %s, oil_name = %s, oil_description = %s, unit_cost = %s, oil_status = %s
    WHERE oil_ID = %s
    """
    values = (
        data.get('supplierId', oil['supplier_ID']),
        data.get('name', oil['oil_name']),
        data.get('description', oil['oil_description']),
        data.get('unitCost', oil['unit_cost']),
        data.get('status', oil['oil_status']),
        oil_id
    )
    execute_query(db_conn, update_query, values)
    
    log_audit(current_user['UserID'], 'UPDATE', 'Essential_oil', oil_id)
    
    # Return updated oil
    oils = execute_read_query(db_conn, "SELECT * FROM Essential_oil WHERE oil_ID = %s", (oil_id,))
    oil = oils[0]
    return jsonify({
        'id': oil['oil_ID'],
        'name': oil['oil_name'],
        'supplierId': oil['supplier_ID'],
        'unitCost': oil['unit_cost'],
        'description': oil['oil_description'],
        'status': oil['oil_status']
    }), 200

@app.route('/api/essential-oils/<int:oil_id>', methods=['DELETE'])
@token_required
def delete_essential_oil(current_user, oil_id):
    """Delete essential oil"""
    db_conn = get_db_connection()
    query = "SELECT * FROM Essential_oil WHERE oil_ID = %s"
    oils = execute_read_query(db_conn, query, (oil_id,))
    
    if not oils:
        return jsonify({'message': 'Essential oil not found'}), 404
    
    oil = oils[0]
    oil_name = oil['oil_name']
    
    delete_query = "DELETE FROM Essential_oil WHERE oil_ID = %s"
    execute_query(db_conn, delete_query, (oil_id,))
    
    log_audit(current_user['UserID'], 'DELETE', 'Essential_oil', oil_id)
    
    return jsonify({'message': 'Essential oil deleted'}), 200

# ==================== Bulk Delete Routes ====================

@app.route('/api/suppliers/bulk-delete', methods=['POST'])
@token_required
def bulk_delete_suppliers(current_user):
    """Bulk delete multiple suppliers"""
    db_conn = get_db_connection()
    data = request.get_json()
    supplier_ids = data.get('ids', [])
    
    if not supplier_ids:
        return jsonify({'message': 'No suppliers selected'}), 400
    
    deleted_count = 0
    for supplier_id in supplier_ids:
        try:
            delete_query = "DELETE FROM Suppliers WHERE supplier_ID = %s"
            result = execute_query(db_conn, delete_query, (supplier_id,))
            if result:
                deleted_count += 1
                try:
                    log_audit(current_user['UserID'], 'DELETE', 'Suppliers', supplier_id)
                except Exception as audit_error:
                    print(f"Warning: Audit log failed for supplier {supplier_id}: {audit_error}")
        except Exception as e:
            print(f"Error deleting supplier {supplier_id}: {e}")
    
    return jsonify({
        'message': f'Successfully deleted {deleted_count} supplier(s)',
        'deletedCount': deleted_count,
        'requestedCount': len(supplier_ids)
    }), 200

@app.route('/api/scents/bulk-delete', methods=['POST'])
@token_required
def bulk_delete_scents(current_user):
    """Bulk archive multiple scents (soft delete)"""
    db_conn = get_db_connection()
    data = request.get_json()
    scent_ids = data.get('ids', [])
    
    if not scent_ids:
        return jsonify({'message': 'No scents selected'}), 400
    
    deleted_count = 0
    for scent_id in scent_ids:
        try:
            update_query = "UPDATE Scents SET archived_at = CURRENT_TIMESTAMP WHERE id = %s"
            result = execute_query(db_conn, update_query, (scent_id,))
            if result:
                deleted_count += 1
                try:
                    log_audit(current_user['UserID'], 'DELETE', 'Scents', scent_id)
                except Exception as audit_error:
                    print(f"Warning: Audit log failed for scent {scent_id}: {audit_error}")
        except Exception as e:
            print(f"Error archiving scent {scent_id}: {e}")
    
    return jsonify({
        'message': f'Successfully archived {deleted_count} scent(s)',
        'deletedCount': deleted_count,
        'requestedCount': len(scent_ids)
    }), 200

@app.route('/api/essential-oils/bulk-delete', methods=['POST'])
@token_required
def bulk_delete_oils(current_user):
    """Bulk delete multiple essential oils"""
    db_conn = get_db_connection()
    data = request.get_json()
    oil_ids = data.get('ids', [])
    
    if not oil_ids:
        return jsonify({'message': 'No oils selected'}), 400
    
    deleted_count = 0
    for oil_id in oil_ids:
        try:
            delete_query = "DELETE FROM Essential_oil WHERE oil_ID = %s"
            result = execute_query(db_conn, delete_query, (oil_id,))
            if result:
                deleted_count += 1
                try:
                    log_audit(current_user['UserID'], 'DELETE', 'Essential_oil', oil_id)
                except Exception as audit_error:
                    print(f"Warning: Audit log failed for oil {oil_id}: {audit_error}")
        except Exception as e:
            print(f"Error deleting oil {oil_id}: {e}")
    
    return jsonify({
        'message': f'Successfully deleted {deleted_count} oil(s)',
        'deletedCount': deleted_count,
        'requestedCount': len(oil_ids)
    }), 200

# ==================== Audit Log Routes ====================

@app.route('/api/audit-logs', methods=['GET'])
@token_required
def get_audit_logs(current_user):
    """Get all audit logs"""
    db_conn = get_db_connection()
    query = """
    SELECT a.AuditID, a.UserID, u.Email as UserEmail, a.AuditAction, a.TableName, a.RecordID, a.Timestamp
    FROM AuditLog a
    LEFT JOIN Users u ON a.UserID = u.UserID
    ORDER BY a.Timestamp DESC
    """
    logs = execute_read_query(db_conn, query)
    return jsonify([{
        'id': log['AuditID'],
        'userId': log['UserID'],
        'userName': log['UserEmail'],
        'action': log['AuditAction'],
        'tableName': log['TableName'],
        'recordId': log['RecordID'],
        'timestamp': log['Timestamp']
    } for log in logs]), 200

@app.route('/api/audit-logs/filter', methods=['GET'])
@token_required
def filter_audit_logs(current_user):
    """Filter audit logs by action, table, or user"""
    db_conn = get_db_connection()
    action = request.args.get('action')
    table = request.args.get('table')
    user = request.args.get('user')
    
    query = "SELECT a.AuditID, a.UserID, u.Email as UserEmail, a.AuditAction, a.TableName, a.RecordID, a.Timestamp FROM AuditLog a LEFT JOIN Users u ON a.UserID = u.UserID WHERE 1=1"
    values = []
    
    if action:
        query += " AND a.AuditAction = %s"
        values.append(action)
    if table:
        query += " AND a.TableName = %s"
        values.append(table)
    if user:
        query += " AND u.Email LIKE %s"
        values.append(f"%{user}%")
    
    query += " ORDER BY a.Timestamp DESC"
    
    logs = execute_read_query(db_conn, query, tuple(values) if values else None)
    return jsonify([{
        'id': log['AuditID'],
        'userId': log['UserID'],
        'userName': log['UserEmail'],
        'action': log['AuditAction'],
        'tableName': log['TableName'],
        'recordId': log['RecordID'],
        'timestamp': log['Timestamp']
    } for log in logs]), 200

# ==================== Import/Export Routes ====================

@app.route('/api/export', methods=['GET'])
@token_required
def export_data(current_user):
    """Export all data as JSON"""
    db_conn = get_db_connection()
    suppliers = execute_read_query(db_conn, "SELECT * FROM suppliers")
    
    ingredients_query = """
    SELECT i.*, s.name as supplier_name 
    FROM ingredients i
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    """
    ingredients = execute_read_query(db_conn, ingredients_query)
    
    scents = execute_read_query(db_conn, "SELECT * FROM Scents WHERE archived_at IS NULL")
    logs = execute_read_query(db_conn, "SELECT * FROM AuditLog ORDER BY Timestamp DESC")
    
    export_data = {
        'suppliers': [{
            'id': s['id'],
            'name': s['name'],
            'contactInfo': s['contact_info'],
            'website': s['website'],
            'phone': s['phone'],
            'createdAt': s['created_at']
        } for s in suppliers],
        'ingredients': [{
            'id': ing['id'],
            'name': ing['name'],
            'supplierId': ing['supplier_id'],
            'supplierName': ing['supplier_name'],
            'cost': ing['cost'],
            'link': ing['link'],
            'storageLocation': ing['storage_location'],
            'createdAt': ing['created_at']
        } for ing in ingredients],
        'scents': [{
            'id': s['id'],
            'name': s['name'],
            'topNotes': s['top_notes'],
            'middleNotes': s['middle_notes'],
            'baseNotes': s['base_notes'],
            'createdBy': s['created_by'],
            'createdAt': s['created_at'],
            'archivedAt': s['archived_at']
        } for s in scents],
        'auditLogs': [{
            'id': log['id'],
            'userId': log['user_id'],
            'userName': log['user_name'],
            'action': log['action'],
            'tableName': log['table_name'],
            'recordId': log['record_id'],
            'recordName': log['record_name'],
            'details': log['details'],
            'timestamp': log['timestamp']
        } for log in logs]
    }
    
    return jsonify(export_data), 200

@app.route('/api/import', methods=['POST'])
@token_required
def import_data(current_user):
    """Import data from JSON"""
    db_conn = get_db_connection()
    data = request.get_json()
    
    try:
        # Import suppliers
        for sup in data.get('suppliers', []):
            existing_query = "SELECT * FROM suppliers WHERE name = %s"
            existing = execute_read_query(db_conn, existing_query, (sup['name'],))
            if not existing:
                insert_query = """
                INSERT INTO suppliers (name, contact_info, website, phone)
                VALUES (%s, %s, %s, %s)
                """
                values = (sup['name'], sup.get('contactInfo'), sup.get('website'), sup.get('phone'))
                execute_query(db_conn, insert_query, values)
        
        # Import ingredients
        for ing in data.get('ingredients', []):
            existing_query = "SELECT * FROM ingredients WHERE name = %s"
            existing = execute_read_query(db_conn, existing_query, (ing['name'],))
            if not existing:
                insert_query = """
                INSERT INTO ingredients (name, supplier_id, cost, link, storage_location)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    ing['name'],
                    ing['supplierId'],
                    ing['cost'],
                    ing.get('link'),
                    ing.get('storageLocation')
                )
                execute_query(db_conn, insert_query, values)
        
        # Import scents
        for scent in data.get('scents', []):
            existing_query = "SELECT * FROM Scents WHERE name = %s"
            existing = execute_read_query(db_conn, existing_query, (scent['name'],))
            if not existing:
                insert_query = """
                INSERT INTO scents (name, top_notes, middle_notes, base_notes, created_by)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    scent['name'],
                    scent['topNotes'],
                    scent['middleNotes'],
                    scent['baseNotes'],
                    scent.get('createdBy', current_user['Email'])
                )
                execute_query(db_conn, insert_query, values)
        
        log_audit(current_user['UserID'], 'CREATE', 'import', 0)
        
        return jsonify({'message': 'Data imported successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Import failed: {str(e)}'}), 400

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(_):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(_):
    return jsonify({'message': 'Server error'}), 500

# ==================== Database Init Route ====================

@app.route('/api/init-db', methods=['POST'])
def init_db():
    """Initialize database with sample data"""
    db_conn = get_db_connection()
    
    try:
        # Check if data already exists
        query = "SELECT COUNT(*) as count FROM users"
        result = execute_read_query(db_conn, query)
        if result and result[0]['count'] > 0:
            return jsonify({'message': 'Database already initialized'}), 200
        
        # Create sample users
        users_query = """
        INSERT INTO users (email, password_hash, name, role)
        VALUES (%s, %s, %s, %s)
        """
        admin_hash = generate_password_hash('admin123')
        manager_hash = generate_password_hash('manager123')
        
        execute_query(db_conn, users_query, ('admin@t4scents.com', admin_hash, 'Admin', 'admin'))
        execute_query(db_conn, users_query, ('manager@t4scents.com', manager_hash, 'Manager', 'manager'))
        
        # Create sample suppliers
        suppliers_query = """
        INSERT INTO suppliers (name, contact_info, website, phone)
        VALUES (%s, %s, %s, %s)
        """
        execute_query(db_conn, suppliers_query, ('Global Florals Inc', 'contact@globalflorals.com', 'https://www.globalflorals.com', '+1-800-555-0101'))
        execute_query(db_conn, suppliers_query, ('Citrus Trading Co', 'sales@citrustrading.com', 'https://www.citrustrading.com', '+1-800-555-0102'))
        execute_query(db_conn, suppliers_query, ('Essence Importers Ltd', 'info@essenceimporters.com', 'https://www.essenceimporters.com', '+1-800-555-0103'))
        
        # Create sample ingredients
        ingredients_query = """
        INSERT INTO ingredients (name, supplier_id, cost, link, storage_location)
        VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(db_conn, ingredients_query, ('Rose Oil', 1, 45.99, 'https://www.globalflorals.com/rose-oil', 'Rack A1'))
        execute_query(db_conn, ingredients_query, ('Bergamot Oil', 2, 32.50, 'https://www.citrustrading.com/bergamot', 'Rack B2'))
        execute_query(db_conn, ingredients_query, ('Sandalwood Oil', 1, 89.99, 'https://www.globalflorals.com/sandalwood', 'Rack A3'))
        
        # Create sample scents
        scents_query = """
        INSERT INTO scents (name, top_notes, middle_notes, base_notes, created_by)
        VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(db_conn, scents_query, ('Rose Elegance', 'Bergamot, Lemon', 'Rose, Jasmine', 'Sandalwood, Musk', 'admin@t4scents.com'))
        execute_query(db_conn, scents_query, ('Ocean Breeze', 'Sea Salt, Grapefruit', 'Aquatic Notes, Jasmine', 'Cedarwood, Amber', 'admin@t4scents.com'))
        
        return jsonify({'message': 'Database initialized with sample data'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Initialization failed: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=Creds.DEBUG, host=Creds.HOST, port=Creds.PORT)
