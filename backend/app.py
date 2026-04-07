"""
Perfume Store Dashboard API
Flask-based REST API with authentication, suppliers, ingredients, scents, and audit logging
"""

import flask
from flask import jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
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

def token_required(f):
    """Decorator to check JWT token on protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
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
            query = "SELECT * FROM users WHERE id = ?"
            users = execute_read_query(conn, query, (data['user_id'],))
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
        'user_id': user['id'],
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=Creds.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Creds.SECRET_KEY, algorithm='HS256')

def log_audit(user_id, user_name, action, table_name, record_id, record_name, details=''):
    """Log an audit entry for data modifications"""
    query = """
    INSERT INTO audit_logs (user_id, user_name, action, table_name, record_id, record_name, details)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    values = (user_id, user_name, action, table_name, record_id, record_name, details)
    execute_query(conn, query, values)

# ==================== Auth Routes ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login - creates token and returns user info"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required'}), 400
    
    # Check if user exists
    query = "SELECT * FROM users WHERE email = ?"
    users = execute_read_query(conn, query, (data['email'],))
    user = users[0] if users else None
    
    # For demo purposes: create user if doesn't exist
    if not user:
        password_hash = generate_password_hash(data['password'])
        name = data['email'].split('@')[0]
        insert_query = """
        INSERT INTO users (email, password_hash, name, role)
        VALUES (?, ?, ?, 'manager')
        """
        execute_query(conn, insert_query, (data['email'], password_hash, name))
        
        # Fetch the newly created user
        users = execute_read_query(conn, query, (data['email'],))
        user = users[0]
    
    elif not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate token
    token = create_token(user)
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current authenticated user"""
    return jsonify({
        'id': current_user['id'],
        'email': current_user['email'],
        'name': current_user['name'],
        'role': current_user['role']
    }), 200

# ==================== Supplier Routes ====================

@app.route('/api/suppliers', methods=['GET'])
@token_required
def get_suppliers(current_user):
    """Get all suppliers"""
    query = "SELECT * FROM suppliers"
    suppliers = execute_read_query(conn, query)
    return jsonify([{
        'id': s['id'],
        'name': s['name'],
        'contactInfo': s['contact_info'],
        'website': s['website'],
        'phone': s['phone'],
        'createdAt': s['created_at']
    } for s in suppliers]), 200

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
@token_required
def get_supplier(current_user, supplier_id):
    """Get supplier by ID"""
    query = "SELECT * FROM suppliers WHERE id = ?"
    suppliers = execute_read_query(conn, query, (supplier_id,))
    
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    s = suppliers[0]
    return jsonify({
        'id': s['id'],
        'name': s['name'],
        'contactInfo': s['contact_info'],
        'website': s['website'],
        'phone': s['phone'],
        'createdAt': s['created_at']
    }), 200

@app.route('/api/suppliers', methods=['POST'])
@token_required
def create_supplier(current_user):
    """Create new supplier"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Supplier name is required'}), 400
    
    query = """
    INSERT INTO suppliers (name, contact_info, website, phone)
    VALUES (?, ?, ?, ?)
    """
    values = (data['name'], data.get('contactInfo'), data.get('website'), data.get('phone'))
    execute_query(conn, query, values)
    
    # Get the newly created supplier
    select_query = "SELECT * FROM suppliers WHERE name = ? ORDER BY id DESC LIMIT 1"
    suppliers = execute_read_query(conn, select_query, (data['name'],))
    supplier = suppliers[0]
    
    log_audit(current_user['id'], current_user['email'], 'CREATE', 'suppliers', supplier['id'], supplier['name'], 'Added new supplier')
    
    return jsonify({
        'id': supplier['id'],
        'name': supplier['name'],
        'contactInfo': supplier['contact_info'],
        'website': supplier['website'],
        'phone': supplier['phone'],
        'createdAt': supplier['created_at']
    }), 201

@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
@token_required
def update_supplier(current_user, supplier_id):
    """Update supplier"""
    query = "SELECT * FROM suppliers WHERE id = ?"
    suppliers = execute_read_query(conn, query, (supplier_id,))
    
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    data = request.get_json()
    supplier = suppliers[0]
    old_name = supplier['name']
    
    update_query = """
    UPDATE suppliers
    SET name = ?, contact_info = ?, website = ?, phone = ?
    WHERE id = ?
    """
    values = (
        data.get('name', supplier['name']),
        data.get('contactInfo', supplier['contact_info']),
        data.get('website', supplier['website']),
        data.get('phone', supplier['phone']),
        supplier_id
    )
    execute_query(conn, update_query, values)
    
    log_audit(current_user['id'], current_user['email'], 'UPDATE', 'suppliers', supplier_id, old_name, f'Updated supplier')
    
    # Return updated supplier
    suppliers = execute_read_query(conn, "SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    s = suppliers[0]
    return jsonify({
        'id': s['id'],
        'name': s['name'],
        'contactInfo': s['contact_info'],
        'website': s['website'],
        'phone': s['phone'],
        'createdAt': s['created_at']
    }), 200

@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
@token_required
def delete_supplier(current_user, supplier_id):
    """Delete supplier"""
    query = "SELECT * FROM suppliers WHERE id = ?"
    suppliers = execute_read_query(conn, query, (supplier_id,))
    
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    supplier = suppliers[0]
    supplier_name = supplier['name']
    
    delete_query = "DELETE FROM suppliers WHERE id = ?"
    execute_query(conn, delete_query, (supplier_id,))
    
    log_audit(current_user['id'], current_user['email'], 'DELETE', 'suppliers', supplier_id, supplier_name, 'Deleted supplier')
    
    return jsonify({'message': 'Supplier deleted'}), 200

# ==================== Ingredient Routes ====================

@app.route('/api/ingredients', methods=['GET'])
@token_required
def get_ingredients(current_user):
    """Get all ingredients"""
    query = """
    SELECT i.*, s.name as supplier_name 
    FROM ingredients i
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    """
    ingredients = execute_read_query(conn, query)
    return jsonify([{
        'id': ing['id'],
        'name': ing['name'],
        'supplierId': ing['supplier_id'],
        'supplierName': ing['supplier_name'],
        'cost': ing['cost'],
        'link': ing['link'],
        'storageLocation': ing['storage_location'],
        'createdAt': ing['created_at']
    } for ing in ingredients]), 200

@app.route('/api/ingredients/<int:ingredient_id>', methods=['GET'])
@token_required
def get_ingredient(current_user, ingredient_id):
    """Get ingredient by ID"""
    query = """
    SELECT i.*, s.name as supplier_name 
    FROM ingredients i
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.id = ?
    """
    ingredients = execute_read_query(conn, query, (ingredient_id,))
    
    if not ingredients:
        return jsonify({'message': 'Ingredient not found'}), 404
    
    ing = ingredients[0]
    return jsonify({
        'id': ing['id'],
        'name': ing['name'],
        'supplierId': ing['supplier_id'],
        'supplierName': ing['supplier_name'],
        'cost': ing['cost'],
        'link': ing['link'],
        'storageLocation': ing['storage_location'],
        'createdAt': ing['created_at']
    }), 200

@app.route('/api/ingredients', methods=['POST'])
@token_required
def create_ingredient(current_user):
    """Create new ingredient"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('supplierId'):
        return jsonify({'message': 'Name and supplier ID are required'}), 400
    
    # Verify supplier exists
    supplier_query = "SELECT * FROM suppliers WHERE id = ?"
    suppliers = execute_read_query(conn, supplier_query, (data['supplierId'],))
    if not suppliers:
        return jsonify({'message': 'Supplier not found'}), 404
    
    query = """
    INSERT INTO ingredients (name, supplier_id, cost, link, storage_location)
    VALUES (?, ?, ?, ?, ?)
    """
    values = (
        data['name'],
        data['supplierId'],
        data.get('cost', 0),
        data.get('link'),
        data.get('storageLocation')
    )
    execute_query(conn, query, values)
    
    # Get the newly created ingredient
    select_query = "SELECT * FROM ingredients WHERE name = ? ORDER BY id DESC LIMIT 1"
    ingredients = execute_read_query(conn, select_query, (data['name'],))
    ingredient = ingredients[0]
    
    log_audit(current_user['id'], current_user['email'], 'CREATE', 'ingredients', ingredient['id'], ingredient['name'], f'Added new ingredient')
    
    return jsonify({
        'id': ingredient['id'],
        'name': ingredient['name'],
        'supplierId': ingredient['supplier_id'],
        'cost': ingredient['cost'],
        'link': ingredient['link'],
        'storageLocation': ingredient['storage_location'],
        'createdAt': ingredient['created_at']
    }), 201

@app.route('/api/ingredients/<int:ingredient_id>', methods=['PUT'])
@token_required
def update_ingredient(current_user, ingredient_id):
    """Update ingredient"""
    query = "SELECT * FROM ingredients WHERE id = ?"
    ingredients = execute_read_query(conn, query, (ingredient_id,))
    
    if not ingredients:
        return jsonify({'message': 'Ingredient not found'}), 404
    
    data = request.get_json()
    ingredient = ingredients[0]
    old_name = ingredient['name']
    
    update_query = """
    UPDATE ingredients
    SET name = ?, supplier_id = ?, cost = ?, link = ?, storage_location = ?
    WHERE id = ?
    """
    values = (
        data.get('name', ingredient['name']),
        data.get('supplierId', ingredient['supplier_id']),
        data.get('cost', ingredient['cost']),
        data.get('link', ingredient['link']),
        data.get('storageLocation', ingredient['storage_location']),
        ingredient_id
    )
    execute_query(conn, update_query, values)
    
    log_audit(current_user['id'], current_user['email'], 'UPDATE', 'ingredients', ingredient_id, old_name, 'Updated ingredient')
    
    # Return updated ingredient
    ingredients = execute_read_query(conn, "SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
    ing = ingredients[0]
    return jsonify({
        'id': ing['id'],
        'name': ing['name'],
        'supplierId': ing['supplier_id'],
        'cost': ing['cost'],
        'link': ing['link'],
        'storageLocation': ing['storage_location'],
        'createdAt': ing['created_at']
    }), 200

@app.route('/api/ingredients/<int:ingredient_id>', methods=['DELETE'])
@token_required
def delete_ingredient(current_user, ingredient_id):
    """Delete ingredient"""
    query = "SELECT * FROM ingredients WHERE id = ?"
    ingredients = execute_read_query(conn, query, (ingredient_id,))
    
    if not ingredients:
        return jsonify({'message': 'Ingredient not found'}), 404
    
    ingredient = ingredients[0]
    ingredient_name = ingredient['name']
    
    delete_query = "DELETE FROM ingredients WHERE id = ?"
    execute_query(conn, delete_query, (ingredient_id,))
    
    log_audit(current_user['id'], current_user['email'], 'DELETE', 'ingredients', ingredient_id, ingredient_name, 'Deleted ingredient')
    
    return jsonify({'message': 'Ingredient deleted'}), 200

# ==================== Scent Routes ====================

@app.route('/api/scents', methods=['GET'])
@token_required
def get_scents(current_user):
    """Get all active scents (not archived)"""
    query = "SELECT * FROM scents WHERE archived_at IS NULL"
    scents = execute_read_query(conn, query)
    return jsonify([{
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
    } for s in scents]), 200

@app.route('/api/scents/<int:scent_id>', methods=['GET'])
@token_required
def get_scent(current_user, scent_id):
    """Get scent by ID"""
    query = "SELECT * FROM scents WHERE id = ?"
    scents = execute_read_query(conn, query, (scent_id,))
    
    if not scents:
        return jsonify({'message': 'Scent not found'}), 404
    
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

@app.route('/api/scents', methods=['POST'])
@token_required
def create_scent(current_user):
    """Create new scent"""
    data = request.get_json()
    
    required_fields = ['name', 'topNotes', 'middleNotes', 'baseNotes']
    if not data or not all(data.get(field) for field in required_fields):
        return jsonify({'message': 'Name and all note types are required'}), 400
    
    query = """
    INSERT INTO scents (name, top_notes, middle_notes, base_notes, all_notes, essential_oils, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        data['name'],
        data['topNotes'],
        data['middleNotes'],
        data['baseNotes'],
        data.get('allNotes', ''),
        data.get('essentialOils', ''),
        current_user['email']
    )
    execute_query(conn, query, values)
    
    # Get the newly created scent
    select_query = "SELECT * FROM scents WHERE name = ? ORDER BY id DESC LIMIT 1"
    scents = execute_read_query(conn, select_query, (data['name'],))
    scent = scents[0]
    
    log_audit(current_user['id'], current_user['email'], 'CREATE', 'scents', scent['id'], scent['name'], 'Created new scent formula')
    
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
    query = "SELECT * FROM scents WHERE id = ?"
    scents = execute_read_query(conn, query, (scent_id,))
    
    if not scents:
        return jsonify({'message': 'Scent not found'}), 404
    
    data = request.get_json()
    scent = scents[0]
    old_name = scent['name']
    
    update_query = """
    UPDATE scents
    SET name = ?, top_notes = ?, middle_notes = ?, base_notes = ?, all_notes = ?, essential_oils = ?
    WHERE id = ?
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
    execute_query(conn, update_query, values)
    
    log_audit(current_user['id'], current_user['email'], 'UPDATE', 'scents', scent_id, old_name, 'Updated scent formula')
    
    # Return updated scent
    scents = execute_read_query(conn, "SELECT * FROM scents WHERE id = ?", (scent_id,))
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
    query = "SELECT * FROM scents WHERE id = ?"
    scents = execute_read_query(conn, query, (scent_id,))
    
    if not scents:
        return jsonify({'message': 'Scent not found'}), 404
    
    scent = scents[0]
    
    update_query = "UPDATE scents SET archived_at = CURRENT_TIMESTAMP WHERE id = ?"
    execute_query(conn, update_query, (scent_id,))
    
    log_audit(current_user['id'], current_user['email'], 'DELETE', 'scents', scent_id, scent['name'], 'Archived scent')
    
    return jsonify({'message': 'Scent archived'}), 200

@app.route('/api/scents/import', methods=['POST'])
@token_required
def import_scents(current_user):
    """Import scents from CSV/Excel file"""
    try:
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
                
                # Check for duplicates
                dup_query = "SELECT * FROM scents WHERE name = ? AND archived_at IS NULL"
                duplicates = execute_read_query(conn, dup_query, (scent_data['name'],))
                if duplicates:
                    errors.append(f"Row {index + 1}: Scent '{scent_data['name']}' already exists")
                    continue
                
                # Insert scent
                insert_query = """
                INSERT INTO scents (name, top_notes, middle_notes, base_notes, all_notes, essential_oils, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                values = (
                    scent_data.get('name', '').strip(),
                    scent_data.get('topNotes', '').strip() or scent_data.get('top_notes', '').strip(),
                    scent_data.get('middleNotes', '').strip() or scent_data.get('middle_notes', '').strip(),
                    scent_data.get('baseNotes', '').strip() or scent_data.get('base_notes', '').strip(),
                    scent_data.get('allNotes', '').strip() or scent_data.get('all_notes', '').strip(),
                    scent_data.get('essentialOils', '').strip() or scent_data.get('essential_oils', '').strip(),
                    current_user['email']
                )
                
                execute_query(conn, insert_query, values)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Log audit
        log_audit(
            current_user['id'],
            current_user['email'],
            'CREATE',
            'scents',
            0,
            filename,
            f"Imported {imported_count} scents from {filename}. Errors: {len(errors)}"
        )
        
        return jsonify({
            'imported': imported_count,
            'total': len(scents_list),
            'errors': errors if errors else None,
            'message': f'Successfully imported {imported_count} scents'
        }), 200
        
    except Exception as e:
        log_audit(
            current_user['id'],
            current_user['email'],
            'CREATE',
            'scents',
            0,
            'import_error',
            f"Import failed: {str(e)}"
        )
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

# ==================== Audit Log Routes ====================

@app.route('/api/audit-logs', methods=['GET'])
@token_required
def get_audit_logs(current_user):
    """Get all audit logs"""
    query = "SELECT * FROM audit_logs ORDER BY timestamp DESC"
    logs = execute_read_query(conn, query)
    return jsonify([{
        'id': log['id'],
        'userId': log['user_id'],
        'userName': log['user_name'],
        'action': log['action'],
        'tableName': log['table_name'],
        'recordId': log['record_id'],
        'recordName': log['record_name'],
        'details': log['details'],
        'timestamp': log['timestamp']
    } for log in logs]), 200

@app.route('/api/audit-logs/filter', methods=['GET'])
@token_required
def filter_audit_logs(current_user):
    """Filter audit logs by action, table, or user"""
    action = request.args.get('action')
    table = request.args.get('table')
    user = request.args.get('user')
    
    query = "SELECT * FROM audit_logs WHERE 1=1"
    values = []
    
    if action:
        query += " AND action = ?"
        values.append(action)
    if table:
        query += " AND table_name = ?"
        values.append(table)
    if user:
        query += " AND user_name LIKE ?"
        values.append(f"%{user}%")
    
    query += " ORDER BY timestamp DESC"
    
    logs = execute_read_query(conn, query, tuple(values) if values else None)
    return jsonify([{
        'id': log['id'],
        'userId': log['user_id'],
        'userName': log['user_name'],
        'action': log['action'],
        'tableName': log['table_name'],
        'recordId': log['record_id'],
        'recordName': log['record_name'],
        'details': log['details'],
        'timestamp': log['timestamp']
    } for log in logs]), 200

# ==================== Import/Export Routes ====================

@app.route('/api/export', methods=['GET'])
@token_required
def export_data(current_user):
    """Export all data as JSON"""
    suppliers = execute_read_query(conn, "SELECT * FROM suppliers")
    
    ingredients_query = """
    SELECT i.*, s.name as supplier_name 
    FROM ingredients i
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    """
    ingredients = execute_read_query(conn, ingredients_query)
    
    scents = execute_read_query(conn, "SELECT * FROM scents WHERE archived_at IS NULL")
    logs = execute_read_query(conn, "SELECT * FROM audit_logs ORDER BY timestamp DESC")
    
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
    data = request.get_json()
    
    try:
        # Import suppliers
        for sup in data.get('suppliers', []):
            existing_query = "SELECT * FROM suppliers WHERE name = ?"
            existing = execute_read_query(conn, existing_query, (sup['name'],))
            if not existing:
                insert_query = """
                INSERT INTO suppliers (name, contact_info, website, phone)
                VALUES (?, ?, ?, ?)
                """
                values = (sup['name'], sup.get('contactInfo'), sup.get('website'), sup.get('phone'))
                execute_query(conn, insert_query, values)
        
        # Import ingredients
        for ing in data.get('ingredients', []):
            existing_query = "SELECT * FROM ingredients WHERE name = ?"
            existing = execute_read_query(conn, existing_query, (ing['name'],))
            if not existing:
                insert_query = """
                INSERT INTO ingredients (name, supplier_id, cost, link, storage_location)
                VALUES (?, ?, ?, ?, ?)
                """
                values = (
                    ing['name'],
                    ing['supplierId'],
                    ing['cost'],
                    ing.get('link'),
                    ing.get('storageLocation')
                )
                execute_query(conn, insert_query, values)
        
        # Import scents
        for scent in data.get('scents', []):
            existing_query = "SELECT * FROM scents WHERE name = ?"
            existing = execute_read_query(conn, existing_query, (scent['name'],))
            if not existing:
                insert_query = """
                INSERT INTO scents (name, top_notes, middle_notes, base_notes, created_by)
                VALUES (?, ?, ?, ?, ?)
                """
                values = (
                    scent['name'],
                    scent['topNotes'],
                    scent['middleNotes'],
                    scent['baseNotes'],
                    scent.get('createdBy', current_user['email'])
                )
                execute_query(conn, insert_query, values)
        
        log_audit(current_user['id'], current_user['email'], 'CREATE', 'import', 0, 'Data Import', 'Imported suppliers, ingredients, and scents')
        
        return jsonify({'message': 'Data imported successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Import failed: {str(e)}'}), 400

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'message': 'Server error'}), 500

# ==================== Database Init Route ====================

@app.route('/api/init-db', methods=['POST'])
def init_db():
    """Initialize database with sample data"""
    
    try:
        # Check if data already exists
        query = "SELECT COUNT(*) as count FROM users"
        result = execute_read_query(conn, query)
        if result and result[0]['count'] > 0:
            return jsonify({'message': 'Database already initialized'}), 200
        
        # Create sample users
        users_query = """
        INSERT INTO users (email, password_hash, name, role)
        VALUES (?, ?, ?, ?)
        """
        admin_hash = generate_password_hash('admin123')
        manager_hash = generate_password_hash('manager123')
        
        execute_query(conn, users_query, ('admin@t4scents.com', admin_hash, 'Admin', 'admin'))
        execute_query(conn, users_query, ('manager@t4scents.com', manager_hash, 'Manager', 'manager'))
        
        # Create sample suppliers
        suppliers_query = """
        INSERT INTO suppliers (name, contact_info, website, phone)
        VALUES (?, ?, ?, ?)
        """
        execute_query(conn, suppliers_query, ('Global Florals Inc', 'contact@globalflorals.com', 'https://www.globalflorals.com', '+1-800-555-0101'))
        execute_query(conn, suppliers_query, ('Citrus Trading Co', 'sales@citrustrading.com', 'https://www.citrustrading.com', '+1-800-555-0102'))
        execute_query(conn, suppliers_query, ('Essence Importers Ltd', 'info@essenceimporters.com', 'https://www.essenceimporters.com', '+1-800-555-0103'))
        
        # Create sample ingredients
        ingredients_query = """
        INSERT INTO ingredients (name, supplier_id, cost, link, storage_location)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(conn, ingredients_query, ('Rose Oil', 1, 45.99, 'https://www.globalflorals.com/rose-oil', 'Rack A1'))
        execute_query(conn, ingredients_query, ('Bergamot Oil', 2, 32.50, 'https://www.citrustrading.com/bergamot', 'Rack B2'))
        execute_query(conn, ingredients_query, ('Sandalwood Oil', 1, 89.99, 'https://www.globalflorals.com/sandalwood', 'Rack A3'))
        
        # Create sample scents
        scents_query = """
        INSERT INTO scents (name, top_notes, middle_notes, base_notes, created_by)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(conn, scents_query, ('Rose Elegance', 'Bergamot, Lemon', 'Rose, Jasmine', 'Sandalwood, Musk', 'admin@t4scents.com'))
        execute_query(conn, scents_query, ('Ocean Breeze', 'Sea Salt, Grapefruit', 'Aquatic Notes, Jasmine', 'Cedarwood, Amber', 'admin@t4scents.com'))
        
        return jsonify({'message': 'Database initialized with sample data'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Initialization failed: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=Creds.DEBUG, host=Creds.HOST, port=Creds.PORT)
