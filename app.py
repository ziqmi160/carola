from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from db import Database
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
import json

app = Flask(__name__)
app.secret_key = 'carola-secret-key-2024'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Session timeout configuration (15 minutes)
SESSION_TIMEOUT_MINUTES = 15
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== SESSION MANAGEMENT ====================

# Payment timeout configuration (15 minutes)
PAYMENT_TIMEOUT_MINUTES = 15

def auto_cancel_expired_bookings():
    """Auto-cancel bookings that have been pending payment for more than 15 minutes"""
    try:
        # Find bookings that are:
        # 1. Not yet paid (no payment record)
        # 2. Created more than 15 minutes ago
        # 3. Still in 'Confirmed' status (not yet cancelled)
        expired_bookings_query = """
            SELECT b.booking_id, b.car_id 
            FROM Booking b
            WHERE b.booking_status = 'Confirmed'
            AND b.created_at < SYSDATE - INTERVAL '15' MINUTE
            AND NOT EXISTS (SELECT 1 FROM Payment p WHERE p.booking_id = b.booking_id)
        """
        expired_bookings = Database.execute_query(expired_bookings_query)
        
        if expired_bookings:
            for booking in expired_bookings:
                booking_id = booking['BOOKING_ID']
                car_id = booking['CAR_ID']
                
                # Cancel the booking
                Database.execute_query(
                    "UPDATE Booking SET booking_status = 'Cancelled' WHERE booking_id = :booking_id",
                    {'booking_id': booking_id},
                    fetch=False
                )
                
                # Check if car has other active bookings before setting to Available
                active_bookings = Database.execute_query(
                    """SELECT COUNT(*) as cnt FROM Booking 
                       WHERE car_id = :car_id 
                       AND booking_id != :booking_id
                       AND booking_status IN ('Confirmed', 'In Progress')
                       AND TRUNC(SYSDATE) BETWEEN TRUNC(pickup_date) AND TRUNC(dropoff_date)""",
                    {'car_id': car_id, 'booking_id': booking_id}
                )
                
                if not active_bookings or active_bookings[0]['CNT'] == 0:
                    Database.execute_query(
                        "UPDATE Car SET car_status = 'Available' WHERE car_id = :car_id",
                        {'car_id': car_id},
                        fetch=False
                    )
                
            print(f"[Auto-Cancel] Cancelled {len(expired_bookings)} expired booking(s)")
    except Exception as e:
        print(f"[Auto-Cancel Error] {str(e)}")

@app.before_request
def check_session_timeout():
    """Check and update session activity timestamp"""
    # Run auto-cancel check on relevant endpoints
    if request.endpoint in ['get_my_bookings', 'admin_get_bookings', 'admin']:
        auto_cancel_expired_bookings()
    
    # Skip for static files, login, register, and public pages
    exempt_routes = ['static', 'login', 'register', 'index', 'cars', 'get_cars', 'get_car', 'get_filters', 'check_session']
    if request.endpoint in exempt_routes:
        return
    
    # If user is logged in, check for timeout
    if 'user_id' in session:
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            if datetime.now() - last_activity_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                # Session expired due to inactivity
                session.clear()
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Session expired', 'session_expired': True}), 401
                return redirect(url_for('login', next=request.url, expired=1))
        
        # Update last activity time
        session['last_activity'] = datetime.now().isoformat()

@app.route('/api/check-session', methods=['GET'])
def check_session():
    """API endpoint to check if session is still valid"""
    if 'user_id' not in session:
        return jsonify({'valid': False, 'message': 'Not logged in'})
    
    last_activity = session.get('last_activity')
    if last_activity:
        last_activity_time = datetime.fromisoformat(last_activity)
        time_remaining = timedelta(minutes=SESSION_TIMEOUT_MINUTES) - (datetime.now() - last_activity_time)
        
        if time_remaining.total_seconds() <= 0:
            session.clear()
            return jsonify({'valid': False, 'message': 'Session expired'})
        
        # Update activity time on check
        session['last_activity'] = datetime.now().isoformat()
        
        return jsonify({
            'valid': True,
            'user_type': session.get('user_type'),
            'name': session.get('name'),
            'time_remaining_seconds': int(time_remaining.total_seconds()),
            'timeout_minutes': SESSION_TIMEOUT_MINUTES
        })
    
    return jsonify({'valid': True, 'user_type': session.get('user_type')})

@app.route('/api/extend-session', methods=['POST'])
def extend_session():
    """Extend user session on activity"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    session['last_activity'] = datetime.now().isoformat()
    return jsonify({'success': True, 'message': 'Session extended'})

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

def validate_password(password):
    """Validate password: minimum 8 characters with at least one number"""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number'
    return True, ''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        try:
            # Validate password
            password = data['password']
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                return jsonify({'success': False, 'message': error_msg}), 400
            
            # Check if email already exists
            email_check = Database.execute_query(
                "SELECT COUNT(*) as cnt FROM Customer WHERE cust_email = :email",
                {'email': data['email']}
            )
            if email_check and email_check[0]['CNT'] > 0:
                return jsonify({'success': False, 'message': 'Email already registered. Please use a different email or login.'}), 400
            
            # Check if username already exists
            username_check = Database.execute_query(
                "SELECT COUNT(*) as cnt FROM Customer WHERE cust_username = :username",
                {'username': data['username']}
            )
            if username_check and username_check[0]['CNT'] > 0:
                return jsonify({'success': False, 'message': 'Username already taken. Please choose a different username.'}), 400
            
            query = """
                INSERT INTO Customer (cust_fname, cust_lname, cust_age, cust_email, cust_phone, cust_username, cust_password)
                VALUES (:fname, :lname, :age, :email, :phone, :username, :password)
            """
            params = {
                'fname': data['fname'],
                'lname': data['lname'],
                'age': data.get('age'),
                'email': data['email'],
                'phone': data.get('phone'),
                'username': data['username'],
                'password': password
            }
            Database.execute_query(query, params, fetch=False)
            return jsonify({'success': True, 'message': 'Registration successful!'})
        except Exception as e:
            error_msg = str(e)
            # Handle common database errors with user-friendly messages
            if 'CUST_EMAIL' in error_msg and 'unique constraint' in error_msg.lower():
                return jsonify({'success': False, 'message': 'Email already registered. Please use a different email or login.'}), 400
            if 'CUST_USERNAME' in error_msg and 'unique constraint' in error_msg.lower():
                return jsonify({'success': False, 'message': 'Username already taken. Please choose a different username.'}), 400
            return jsonify({'success': False, 'message': 'Registration failed. Please try again.'}), 400
    
    # Get the 'next' parameter for redirect after registration
    next_url = request.args.get('next', '')
    return render_template('register.html', next_url=next_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        
        try:
            username = data['username']
            password = data['password']
            
            # First, try to find user in Customer table
            customer_query = "SELECT cust_id, cust_fname, cust_lname, cust_email, cust_username FROM Customer WHERE cust_username = :username AND cust_password = :password"
            customer_result = Database.execute_query(customer_query, {'username': username, 'password': password})
            
            if customer_result:
                # User is a customer
                user = customer_result[0]
                session.permanent = True  # Enable session timeout
                session['user_id'] = user['CUST_ID']
                session['username'] = user['CUST_USERNAME']
                session['name'] = f"{user['CUST_FNAME']} {user['CUST_LNAME']}"
                session['user_type'] = 'customer'
                session['last_activity'] = datetime.now().isoformat()
                return jsonify({'success': True, 'user_type': 'customer', 'message': 'Login successful!'})
            
            # If not found in Customer, try Staff table
            staff_query = "SELECT staff_id, staff_fname, staff_lname, staff_email, staff_username, staff_dept FROM Staff WHERE staff_username = :username AND staff_password = :password"
            staff_result = Database.execute_query(staff_query, {'username': username, 'password': password})
            
            if staff_result:
                # User is staff
                user = staff_result[0]
                session.permanent = True  # Enable session timeout
                session['user_id'] = user['STAFF_ID']
                session['username'] = user['STAFF_USERNAME']
                session['name'] = f"{user['STAFF_FNAME']} {user['STAFF_LNAME']}"
                session['dept'] = user.get('STAFF_DEPT', '')
                session['user_type'] = 'staff'
                session['last_activity'] = datetime.now().isoformat()
                
                # Check if this staff is a manager (has staff reporting to them)
                manager_check = Database.execute_query(
                    "SELECT COUNT(*) as cnt FROM Staff WHERE manager_id = :staff_id",
                    {'staff_id': user['STAFF_ID']}
                )
                session['is_manager'] = manager_check[0]['CNT'] > 0 if manager_check else False
                
                return jsonify({'success': True, 'user_type': 'staff', 'message': 'Login successful!'})
            
            # If not found in either table
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    # Get the 'next' parameter for redirect after login
    next_url = request.args.get('next', '')
    return render_template('login.html', next_url=next_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== CAR ROUTES ====================

@app.route('/cars')
def cars():
    return render_template('cars.html')

@app.route('/api/cars', methods=['GET'])
def get_cars():
    try:
        location = request.args.get('location', '')
        location_id = request.args.get('location_id', '')
        car_type = request.args.get('type', '')
        brand = request.args.get('brand', '')
        fuel_type = request.args.get('fuel_type', '')
        seats = request.args.get('seats', '')
        bags = request.args.get('bags', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        
        # When filtering by location, show one car per model at that location
        # Otherwise, show one car per model (grouped view)
        if location_id:
            # Show specific cars at selected location
            # Note: Show all cars except 'In Maintenance' - rented/dirty cars can still be booked for future dates
            query = """
                SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                       c.pickup_location, c.dropoff_location, c.available_locations, c.allows_different_dropoff,
                       m.attachments, NVL(c.car_status, 'Available') as car_status,
                       c.location_id,
                       l.location_name as home_location, l.city as home_city,
                       m.model_id, m.model_name, b.brand_name, ct.carType_name,
                       CASE 
                           WHEN EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id) THEN 'Petrol'
                           WHEN EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id) THEN 'Diesel'
                           WHEN EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id) THEN 'Electric'
                           ELSE 'N/A'
                       END as fuel_type
                FROM Car c
                JOIN Model m ON c.model_id = m.model_id
                JOIN Brand b ON m.brand_id = b.brand_id
                JOIN CarType ct ON c.carType_id = ct.carType_id
                LEFT JOIN Location l ON c.location_id = l.location_id
                WHERE NVL(c.car_status, 'Available') NOT IN ('In Maintenance')
                AND c.location_id = :location_id
            """
            params = {'location_id': int(location_id)}
        else:
            # Show one car per model (grouped view for browsing)
            # Note: Count all cars except 'In Maintenance' - rented/dirty cars can still be booked for future dates
            query = """
                SELECT * FROM (
                    SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                           c.pickup_location, c.dropoff_location, c.available_locations, c.allows_different_dropoff,
                           m.attachments, NVL(c.car_status, 'Available') as car_status,
                           c.location_id,
                           l.location_name as home_location, l.city as home_city,
                           m.model_id, m.model_name, b.brand_name, ct.carType_name,
                           CASE 
                               WHEN EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id) THEN 'Petrol'
                               WHEN EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id) THEN 'Diesel'
                               WHEN EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id) THEN 'Electric'
                               ELSE 'N/A'
                           END as fuel_type,
                           (SELECT COUNT(*) FROM Car c2 WHERE c2.model_id = c.model_id AND NVL(c2.car_status, 'Available') NOT IN ('In Maintenance')) as available_count,
                           (SELECT COUNT(DISTINCT c3.location_id) FROM Car c3 WHERE c3.model_id = c.model_id AND NVL(c3.car_status, 'Available') NOT IN ('In Maintenance')) as location_count,
                           ROW_NUMBER() OVER (PARTITION BY m.model_id ORDER BY c.rate) as rn
                    FROM Car c
                    JOIN Model m ON c.model_id = m.model_id
                    JOIN Brand b ON m.brand_id = b.brand_id
                    JOIN CarType ct ON c.carType_id = ct.carType_id
                    LEFT JOIN Location l ON c.location_id = l.location_id
                    WHERE NVL(c.car_status, 'Available') NOT IN ('In Maintenance')
                ) WHERE rn = 1
            """
            params = {}
        
        if car_type:
            if location_id:
                query += " AND ct.carType_id = :car_type"
            else:
                query = query.replace("WHERE rn = 1", "WHERE rn = 1 AND CARTYPE_NAME IN (SELECT carType_name FROM CarType WHERE carType_id = :car_type)")
            params['car_type'] = int(car_type)
        
        if brand:
            if location_id:
                query += " AND b.brand_id = :brand"
            else:
                query = query.replace("WHERE rn = 1", "WHERE rn = 1 AND BRAND_NAME IN (SELECT brand_name FROM Brand WHERE brand_id = :brand)")
            params['brand'] = int(brand)
        
        if fuel_type:
            fuel_filter = ""
            if fuel_type == 'Petrol':
                fuel_filter = "FUEL_TYPE = 'Petrol'"
            elif fuel_type == 'Diesel':
                fuel_filter = "FUEL_TYPE = 'Diesel'"
            elif fuel_type == 'Electric':
                fuel_filter = "FUEL_TYPE = 'Electric'"
            if fuel_filter:
                if location_id:
                    if fuel_type == 'Petrol':
                        query += " AND EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id)"
                    elif fuel_type == 'Diesel':
                        query += " AND EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id)"
                    elif fuel_type == 'Electric':
                        query += " AND EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id)"
                else:
                    query = query.replace("WHERE rn = 1", f"WHERE rn = 1 AND {fuel_filter}")
        
        if seats:
            if location_id:
                query += " AND c.seat = :seats"
            else:
                query = query.replace("WHERE rn = 1", "WHERE rn = 1 AND SEAT = :seats")
            params['seats'] = int(seats)
        
        if bags:
            if location_id:
                query += " AND c.suitcase = :bags"
            else:
                query = query.replace("WHERE rn = 1", "WHERE rn = 1 AND SUITCASE = :bags")
            params['bags'] = int(bags)
        
        if min_price:
            if location_id:
                query += " AND c.rate >= :min_price"
            else:
                query = query.replace("WHERE rn = 1", "WHERE rn = 1 AND RATE >= :min_price")
            params['min_price'] = float(min_price)
        
        if max_price:
            if location_id:
                query += " AND c.rate <= :max_price"
            else:
                query = query.replace("WHERE rn = 1", "WHERE rn = 1 AND RATE <= :max_price")
            params['max_price'] = float(max_price)
        
        query += " ORDER BY RATE"
        
        cars = Database.execute_query(query, params)
        
        # Convert Oracle NUMBER to Python int/float
        for car in cars:
            for key, value in car.items():
                if isinstance(value, (int, float)):
                    car[key] = float(value) if '.' in str(value) else int(value)
        
        return jsonify({'success': True, 'cars': cars})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/car/<int:car_id>', methods=['GET'])
def get_car(car_id):
    try:
        query = """
            SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                   c.pickup_location, c.dropoff_location, c.available_locations, c.allows_different_dropoff,
                   m.attachments, c.location_id,
                   l.location_name as home_location, l.city as home_city, l.is_airport,
                   m.model_name, b.brand_name, ct.carType_name,
                   CASE 
                       WHEN EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id) THEN 'Petrol'
                       WHEN EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id) THEN 'Diesel'
                       WHEN EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id) THEN 'Electric'
                       ELSE 'N/A'
                   END as fuel_type,
                   p.octane_rating, p.fuel_tank_capacity as petrol_tank,
                   d.diesel_emission, d.fuel_tank_capacity as diesel_tank,
                   e.battery_range, e.charging_rate_kw, e.last_charging_date
            FROM Car c
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand b ON m.brand_id = b.brand_id
            JOIN CarType ct ON c.carType_id = ct.carType_id
            LEFT JOIN Location l ON c.location_id = l.location_id
            LEFT JOIN Petrol p ON c.car_id = p.car_id
            LEFT JOIN Diesel d ON c.car_id = d.car_id
            LEFT JOIN Electric e ON c.car_id = e.car_id
            WHERE c.car_id = :car_id
        """
        result = Database.execute_query(query, {'car_id': car_id})
        
        if result:
            car = result[0]
            # Convert Oracle types
            for key, value in car.items():
                if isinstance(value, (int, float)):
                    car[key] = float(value) if '.' in str(value) else int(value)
                elif hasattr(value, 'isoformat'):  # Date object
                    car[key] = value.isoformat() if value else None
            return jsonify({'success': True, 'car': car})
        else:
            return jsonify({'success': False, 'message': 'Car not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all active locations from the Location table"""
    try:
        locations_query = """
            SELECT location_id, location_name, address, city, state, postal_code,
                   phone, email, opening_time, closing_time, is_airport 
            FROM Location 
            WHERE is_active = 1 
            ORDER BY state, city, location_name
        """
        locations_result = Database.execute_query(locations_query)
        
        locations = [{
            'location_id': row['LOCATION_ID'],
            'location_name': row['LOCATION_NAME'],
            'address': row['ADDRESS'],
            'city': row['CITY'],
            'state': row['STATE'],
            'postal_code': row['POSTAL_CODE'],
            'phone': row['PHONE'],
            'email': row['EMAIL'],
            'opening_time': row['OPENING_TIME'],
            'closing_time': row['CLOSING_TIME'],
            'is_airport': row['IS_AIRPORT'],
            'display_name': f"{row['LOCATION_NAME']} ({row['CITY']})"
        } for row in locations_result] if locations_result else []
        
        return jsonify({'success': True, 'locations': locations})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/filters', methods=['GET'])
def get_filters():
    try:
        brands = Database.execute_query("SELECT brand_id, brand_name FROM Brand ORDER BY brand_name")
        types = Database.execute_query("SELECT carType_id, carType_name FROM CarType ORDER BY carType_name")
        
        # Get locations that have bookable cars (not in maintenance)
        locations_query = """
            SELECT DISTINCT l.location_id, l.location_name, l.city, l.state, l.is_airport
            FROM Location l
            JOIN Car c ON l.location_id = c.location_id
            WHERE l.is_active = 1
            AND NVL(c.car_status, 'Available') NOT IN ('In Maintenance')
            ORDER BY l.state, l.city, l.location_name
        """
        locations_result = Database.execute_query(locations_query)
        
        # Format locations with full details
        locations = [{
            'location_id': row['LOCATION_ID'],
            'location_name': row['LOCATION_NAME'],
            'city': row['CITY'],
            'state': row['STATE'],
            'is_airport': row['IS_AIRPORT'],
            'display_name': f"{'✈️ ' if row['IS_AIRPORT'] == 1 else ''}{row['LOCATION_NAME']} ({row['CITY']})"
        } for row in locations_result] if locations_result else []
        
        # Get unique seats
        seats_query = "SELECT DISTINCT seat FROM Car WHERE seat IS NOT NULL ORDER BY seat"
        seats_result = Database.execute_query(seats_query)
        seats = [{'seat': int(row['SEAT'])} for row in seats_result]
        
        # Get unique bags (suitcase)
        bags_query = "SELECT DISTINCT suitcase FROM Car WHERE suitcase IS NOT NULL ORDER BY suitcase"
        bags_result = Database.execute_query(bags_query)
        bags = [{'bag': int(row['SUITCASE'])} for row in bags_result]
        
        return jsonify({
            'success': True,
            'brands': brands,
            'types': types,
            'locations': locations,
            'seats': seats,
            'bags': bags
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== BOOKING ROUTES ====================

@app.route('/book/<int:car_id>')
def book_car(car_id):
    if 'user_id' not in session:
        # Not logged in - redirect to login
        return redirect(url_for('login', next=f'/book/{car_id}'))
    
    if session.get('user_type') == 'staff':
        # Staff cannot book cars - redirect to cars page with message
        return redirect(url_for('cars', staff_booking_error=1))
    
    return render_template('booking.html', car_id=car_id, model_id=None)

@app.route('/book/model/<int:model_id>')
def book_model(model_id):
    """Book by model - allows choosing pickup location"""
    if 'user_id' not in session:
        return redirect(url_for('login', next=f'/book/model/{model_id}'))
    
    if session.get('user_type') == 'staff':
        return redirect(url_for('cars', staff_booking_error=1))
    
    return render_template('booking.html', car_id=None, model_id=model_id)

@app.route('/api/model/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """Get model details and available locations"""
    try:
        # Get model info
        model_query = """
            SELECT m.model_id, m.model_name, m.attachments, b.brand_name, ct.carType_name,
                   c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                   c.allows_different_dropoff
            FROM Model m
            JOIN Brand b ON m.brand_id = b.brand_id
            JOIN Car c ON c.model_id = m.model_id
            JOIN CarType ct ON c.carType_id = ct.carType_id
            WHERE m.model_id = :model_id
            AND ROWNUM = 1
        """
        model_result = Database.execute_query(model_query, {'model_id': model_id})
        
        if not model_result:
            return jsonify({'success': False, 'message': 'Model not found'}), 404
        
        model = model_result[0]
        
        # Get bookable locations for this model (not in maintenance)
        locations_query = """
            SELECT DISTINCT l.location_id, l.location_name, l.city, l.state, l.is_airport,
                   COUNT(c.car_id) as available_count
            FROM Car c
            JOIN Location l ON c.location_id = l.location_id
            WHERE c.model_id = :model_id
            AND NVL(c.car_status, 'Available') NOT IN ('In Maintenance')
            AND l.is_active = 1
            GROUP BY l.location_id, l.location_name, l.city, l.state, l.is_airport
            ORDER BY l.state, l.city
        """
        locations_result = Database.execute_query(locations_query, {'model_id': model_id})
        
        locations = [{
            'location_id': row['LOCATION_ID'],
            'location_name': row['LOCATION_NAME'],
            'city': row['CITY'],
            'state': row['STATE'],
            'is_airport': row['IS_AIRPORT'],
            'available_count': row['AVAILABLE_COUNT'],
            'display_name': f"{'✈️ ' if row['IS_AIRPORT'] == 1 else '📍 '}{row['LOCATION_NAME']} ({row['CITY']}) - {row['AVAILABLE_COUNT']} available"
        } for row in locations_result] if locations_result else []
        
        # Get fuel type
        fuel_query = """
            SELECT CASE 
                WHEN EXISTS (SELECT 1 FROM Petrol p JOIN Car c ON p.car_id = c.car_id WHERE c.model_id = :model_id) THEN 'Petrol'
                WHEN EXISTS (SELECT 1 FROM Diesel d JOIN Car c ON d.car_id = c.car_id WHERE c.model_id = :model_id) THEN 'Diesel'
                WHEN EXISTS (SELECT 1 FROM Electric e JOIN Car c ON e.car_id = c.car_id WHERE c.model_id = :model_id) THEN 'Electric'
                ELSE 'N/A'
            END as fuel_type FROM DUAL
        """
        fuel_result = Database.execute_query(fuel_query, {'model_id': model_id})
        fuel_type = fuel_result[0]['FUEL_TYPE'] if fuel_result else 'N/A'
        
        return jsonify({
            'success': True,
            'model': {
                'MODEL_ID': model['MODEL_ID'],
                'MODEL_NAME': model['MODEL_NAME'],
                'BRAND_NAME': model['BRAND_NAME'],
                'CARTYPE_NAME': model['CARTYPE_NAME'],
                'RATE': float(model['RATE']) if model['RATE'] else 0,
                'DESCRIPTION': model['DESCRIPTION'],
                'DOOR': model['DOOR'],
                'SUITCASE': model['SUITCASE'],
                'SEAT': model['SEAT'],
                'COLOUR': model['COLOUR'],
                'ALLOWS_DIFFERENT_DROPOFF': model['ALLOWS_DIFFERENT_DROPOFF'],
                'ATTACHMENTS': model['ATTACHMENTS'],
                'FUEL_TYPE': fuel_type
            },
            'locations': locations
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return jsonify({'success': False, 'message': 'Please login as customer'}), 401
    
    try:
        data = request.json
        cust_id = session['user_id']
        
        # Parse dates first
        pickup_date = datetime.strptime(data['pickup_date'], '%Y-%m-%dT%H:%M')
        dropoff_date = datetime.strptime(data['dropoff_date'], '%Y-%m-%dT%H:%M')
        pickup_location_id = data['pickup_location_id']
        dropoff_location_id = data['dropoff_location_id']
        
        # Determine car_id: either provided directly or find from model_id
        car_id = data.get('car_id')
        
        if not car_id and data.get('model_id'):
            # MODEL-BASED BOOKING: Find an available car of this model at the pickup location
            # Note: We check date conflicts, NOT car_status (a car rented today can be booked for next week)
            find_car_query = """
                SELECT c.car_id, c.rate 
                FROM Car c
                WHERE c.model_id = :model_id
                AND c.location_id = :location_id
                AND NVL(c.car_status, 'Available') NOT IN ('In Maintenance')
                AND c.car_id NOT IN (
                    SELECT b.car_id FROM Booking b
                    WHERE b.booking_status NOT IN ('Cancelled', 'Completed')
                    AND ((b.pickup_date <= :pickup_date AND b.dropoff_date >= :pickup_date)
                         OR (b.pickup_date <= :dropoff_date AND b.dropoff_date >= :dropoff_date)
                         OR (b.pickup_date >= :pickup_date AND b.dropoff_date <= :dropoff_date))
                )
                AND ROWNUM = 1
            """
            car_result = Database.execute_query(find_car_query, {
                'model_id': data['model_id'],
                'location_id': pickup_location_id,
                'pickup_date': pickup_date,
                'dropoff_date': dropoff_date
            })
            
            if not car_result:
                return jsonify({'success': False, 'message': 'No available car of this model at selected location for these dates'}), 400
            
            car_id = car_result[0]['CAR_ID']
            rate = float(car_result[0]['RATE'])
        else:
            # SPECIFIC CAR BOOKING: Use provided car_id
            car_query = "SELECT rate FROM Car WHERE car_id = :car_id"
            car_result = Database.execute_query(car_query, {'car_id': car_id})
            if not car_result:
                return jsonify({'success': False, 'message': 'Car not found'}), 404
            rate = float(car_result[0]['RATE'])
            
            # Check for conflicts
            conflict_query = """
                SELECT COUNT(*) as cnt FROM Booking
                WHERE car_id = :car_id
                AND booking_status NOT IN ('Cancelled', 'Completed')
                AND ((pickup_date <= :pickup_date AND dropoff_date >= :pickup_date)
                     OR (pickup_date <= :dropoff_date AND dropoff_date >= :dropoff_date)
                     OR (pickup_date >= :pickup_date AND dropoff_date <= :dropoff_date))
            """
            conflict_result = Database.execute_query(conflict_query, {
                'car_id': car_id,
                'pickup_date': pickup_date,
                'dropoff_date': dropoff_date
            })
            
            if conflict_result and conflict_result[0]['CNT'] > 0:
                return jsonify({'success': False, 'message': 'Car is not available for selected dates'}), 400
        
        # Get first available staff
        staff_query = "SELECT staff_id FROM Staff WHERE ROWNUM = 1"
        staff_result = Database.execute_query(staff_query)
        if not staff_result:
            return jsonify({'success': False, 'message': 'No staff available'}), 400
        staff_id = staff_result[0]['STAFF_ID']
        
        # Calculate price
        diff_hours = (dropoff_date - pickup_date).total_seconds() / 3600
        days = max(1, int((diff_hours + 23) // 24))  # Round up to full days
        price = rate * days
        
        # Create booking
        booking_query = """
            INSERT INTO Booking (cust_id, staff_id, car_id, pickup_date, dropoff_date, pickup_location_id, dropoff_location_id, price)
            VALUES (:cust_id, :staff_id, :car_id, :pickup_date, :dropoff_date, :pickup_location_id, :dropoff_location_id, :price)
        """
        Database.execute_query(booking_query, {
            'cust_id': cust_id,
            'staff_id': staff_id,
            'car_id': car_id,
            'pickup_date': pickup_date,
            'dropoff_date': dropoff_date,
            'pickup_location_id': pickup_location_id,
            'dropoff_location_id': dropoff_location_id,
            'price': price
        }, fetch=False)
        
        # Update car status to Rented if pickup date is today or past
        if pickup_date.date() <= datetime.now().date():
            Database.execute_query(
                "UPDATE Car SET car_status = 'Rented' WHERE car_id = :car_id",
                {'car_id': car_id},
                fetch=False
            )
        
        # Get the booking_id
        booking_id_query = "SELECT booking_id FROM (SELECT booking_id FROM Booking WHERE cust_id = :cust_id ORDER BY booking_id DESC) WHERE ROWNUM = 1"
        booking_result = Database.execute_query(booking_id_query, {'cust_id': cust_id})
        booking_id = booking_result[0]['BOOKING_ID'] if booking_result else None
        
        return jsonify({
            'success': True,
            'booking_id': int(booking_id) if booking_id else None,
            'price': price,
            'message': 'Booking created successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/my-bookings', methods=['GET'])
def get_my_bookings():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login'}), 401
    
    try:
        if session.get('user_type') == 'customer':
            query = """
                SELECT b.booking_id, b.pickup_date, b.dropoff_date, b.price,
                       b.booking_status, b.created_at,
                       pl.location_name as pickup_location, pl.city as pickup_city,
                       dl.location_name as dropoff_location, dl.city as dropoff_city,
                       c.car_id, m.model_name, br.brand_name, c.colour, c.rate,
                       CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
                FROM Booking b
                JOIN Car c ON b.car_id = c.car_id
                JOIN Model m ON c.model_id = m.model_id
                JOIN Brand br ON m.brand_id = br.brand_id
                LEFT JOIN Location pl ON b.pickup_location_id = pl.location_id
                LEFT JOIN Location dl ON b.dropoff_location_id = dl.location_id
                LEFT JOIN Payment p ON b.booking_id = p.booking_id
                WHERE b.cust_id = :user_id
                AND NVL(b.booking_status, 'Confirmed') != 'Cancelled'
                ORDER BY b.pickup_date DESC
            """
            params = {'user_id': session['user_id']}
        else:
            query = """
                SELECT b.booking_id, b.pickup_date, b.dropoff_date, b.price,
                       b.booking_status, b.created_at,
                       pl.location_name as pickup_location, pl.city as pickup_city,
                       dl.location_name as dropoff_location, dl.city as dropoff_city,
                       c.car_id, c.car_status, m.model_name, br.brand_name, c.colour, c.rate,
                       cu.cust_fname || ' ' || cu.cust_lname as customer_name, cu.cust_email, cu.cust_phone,
                       CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
                FROM Booking b
                JOIN Car c ON b.car_id = c.car_id
                JOIN Model m ON c.model_id = m.model_id
                JOIN Brand br ON m.brand_id = br.brand_id
                JOIN Customer cu ON b.cust_id = cu.cust_id
                LEFT JOIN Location pl ON b.pickup_location_id = pl.location_id
                LEFT JOIN Location dl ON b.dropoff_location_id = dl.location_id
                LEFT JOIN Payment p ON b.booking_id = p.booking_id
                ORDER BY b.pickup_date DESC
            """
            params = {}
        
        bookings = Database.execute_query(query, params)
        
        # Convert Oracle types
        for booking in bookings:
            for key, value in booking.items():
                if isinstance(value, (int, float)):
                    booking[key] = float(value) if '.' in str(value) else int(value)
                elif hasattr(value, 'isoformat'):
                    booking[key] = value.isoformat() if value else None
        
        return jsonify({'success': True, 'bookings': bookings})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== CUSTOMER PROFILE ====================

@app.route('/profile')
def profile():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get customer profile data"""
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        cust_id = session['user_id']
        
        # Get customer details
        profile_query = """
            SELECT cust_id, cust_fname, cust_lname, cust_age, cust_email, cust_phone, cust_username
            FROM Customer
            WHERE cust_id = :cust_id
        """
        result = Database.execute_query(profile_query, {'cust_id': cust_id})
        
        if not result:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
        profile = result[0]
        
        # Get booking statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_bookings,
                NVL(SUM(b.price), 0) as total_spent,
                SUM(CASE WHEN p.booking_id IS NOT NULL THEN 1 ELSE 0 END) as completed_bookings
            FROM Booking b
            LEFT JOIN Payment p ON b.booking_id = p.booking_id
            WHERE b.cust_id = :cust_id
        """
        stats_result = Database.execute_query(stats_query, {'cust_id': cust_id})
        
        stats = {
            'total_bookings': int(stats_result[0]['TOTAL_BOOKINGS'] or 0),
            'total_spent': float(stats_result[0]['TOTAL_SPENT'] or 0),
            'completed_bookings': int(stats_result[0]['COMPLETED_BOOKINGS'] or 0)
        }
        
        return jsonify({
            'success': True,
            'profile': {
                'cust_id': profile['CUST_ID'],
                'fname': profile['CUST_FNAME'],
                'lname': profile['CUST_LNAME'],
                'age': profile['CUST_AGE'],
                'email': profile['CUST_EMAIL'],
                'phone': profile['CUST_PHONE'],
                'username': profile['CUST_USERNAME']
            },
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update customer profile"""
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        cust_id = session['user_id']
        
        # Check if email already exists (exclude current user)
        if 'email' in data:
            email_check = Database.execute_query(
                "SELECT COUNT(*) as cnt FROM Customer WHERE cust_email = :email AND cust_id != :cust_id",
                {'email': data['email'], 'cust_id': cust_id}
            )
            if email_check and email_check[0]['CNT'] > 0:
                return jsonify({'success': False, 'message': 'Email already in use'}), 400
        
        # Build update query
        update_fields = []
        params = {'cust_id': cust_id}
        
        if 'fname' in data:
            update_fields.append('cust_fname = :fname')
            params['fname'] = data['fname']
        if 'lname' in data:
            update_fields.append('cust_lname = :lname')
            params['lname'] = data['lname']
        if 'email' in data:
            update_fields.append('cust_email = :email')
            params['email'] = data['email']
        if 'phone' in data:
            update_fields.append('cust_phone = :phone')
            params['phone'] = data['phone']
        if 'age' in data:
            update_fields.append('cust_age = :age')
            params['age'] = data['age']
        
        if update_fields:
            query = f"UPDATE Customer SET {', '.join(update_fields)} WHERE cust_id = :cust_id"
            Database.execute_query(query, params, fetch=False)
            
            # Update session name if changed
            if 'fname' in data or 'lname' in data:
                new_fname = data.get('fname', session.get('name', '').split()[0])
                new_lname = data.get('lname', session.get('name', '').split()[-1] if len(session.get('name', '').split()) > 1 else '')
                session['name'] = f"{new_fname} {new_lname}"
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile/password', methods=['PUT'])
def change_password():
    """Change customer password"""
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        cust_id = session['user_id']
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verify current password
        verify_query = "SELECT cust_id FROM Customer WHERE cust_id = :cust_id AND cust_password = :password"
        result = Database.execute_query(verify_query, {'cust_id': cust_id, 'password': current_password})
        
        if not result:
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        # Validate new password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Update password
        update_query = "UPDATE Customer SET cust_password = :password WHERE cust_id = :cust_id"
        Database.execute_query(update_query, {'password': new_password, 'cust_id': cust_id}, fetch=False)
        
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('my_bookings.html')

@app.route('/api/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking (only if unpaid and pickup date is in the future)"""
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        cust_id = session['user_id']
        
        # Get booking details and verify ownership
        booking_query = """
            SELECT b.booking_id, b.pickup_date, 
                   CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
            FROM Booking b
            LEFT JOIN Payment p ON b.booking_id = p.booking_id
            WHERE b.booking_id = :booking_id AND b.cust_id = :cust_id
        """
        result = Database.execute_query(booking_query, {
            'booking_id': booking_id,
            'cust_id': cust_id
        })
        
        if not result:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        booking = result[0]
        
        # Check if already paid
        if booking['PAYMENT_STATUS'] == 'Paid':
            return jsonify({'success': False, 'message': 'Cannot cancel a paid booking. Please contact support.'}), 400
        
        # Check if pickup date is in the future
        pickup_date = booking['PICKUP_DATE']
        from datetime import datetime
        if pickup_date <= datetime.now():
            return jsonify({'success': False, 'message': 'Cannot cancel booking after pickup date has passed'}), 400
        
        # Delete the booking
        delete_query = "DELETE FROM Booking WHERE booking_id = :booking_id"
        Database.execute_query(delete_query, {'booking_id': booking_id}, fetch=False)
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/booking-confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return redirect(url_for('login'))
    
    # Verify the booking belongs to this customer
    verify_query = "SELECT booking_id FROM Booking WHERE booking_id = :booking_id AND cust_id = :cust_id"
    result = Database.execute_query(verify_query, {
        'booking_id': booking_id,
        'cust_id': session['user_id']
    })
    
    if not result:
        return redirect(url_for('my_bookings'))
    
    return render_template('booking_confirm.html', booking_id=booking_id)

@app.route('/api/booking-details/<int:booking_id>', methods=['GET'])
def get_booking_details(booking_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login'}), 401
    
    try:
        query = """
            SELECT b.booking_id, b.pickup_date, b.dropoff_date, b.price,
                   b.booking_status, b.created_at,
                   pl.location_name as pickup_location, pl.city as pickup_city, pl.address as pickup_address,
                   dl.location_name as dropoff_location, dl.city as dropoff_city, dl.address as dropoff_address,
                   c.car_id, c.rate, c.colour, c.door, c.seat, c.suitcase, m.attachments,
                   m.model_name, br.brand_name, ct.carType_name,
                   cu.cust_fname, cu.cust_lname, cu.cust_email, cu.cust_phone,
                   CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
            FROM Booking b
            JOIN Car c ON b.car_id = c.car_id
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand br ON m.brand_id = br.brand_id
            JOIN CarType ct ON c.carType_id = ct.carType_id
            JOIN Customer cu ON b.cust_id = cu.cust_id
            LEFT JOIN Location pl ON b.pickup_location_id = pl.location_id
            LEFT JOIN Location dl ON b.dropoff_location_id = dl.location_id
            LEFT JOIN Payment p ON b.booking_id = p.booking_id
            WHERE b.booking_id = :booking_id AND b.cust_id = :cust_id
        """
        result = Database.execute_query(query, {
            'booking_id': booking_id,
            'cust_id': session['user_id']
        })
        
        if result:
            booking = result[0]
            # Convert Oracle types
            for key, value in booking.items():
                if isinstance(value, (int, float)):
                    booking[key] = float(value) if '.' in str(value) else int(value)
                elif hasattr(value, 'isoformat'):
                    booking[key] = value.isoformat() if value else None
            return jsonify({'success': True, 'booking': booking})
        else:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== PAYMENT ROUTES ====================

@app.route('/payment/<int:booking_id>')
def payment_page(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return redirect(url_for('login'))
    
    # Verify the booking belongs to this customer and check status
    verify_query = """
        SELECT b.booking_id, b.booking_status, b.created_at,
               CASE WHEN EXISTS (SELECT 1 FROM Payment p WHERE p.booking_id = b.booking_id) THEN 1 ELSE 0 END as is_paid
        FROM Booking b 
        WHERE b.booking_id = :booking_id AND b.cust_id = :cust_id
    """
    result = Database.execute_query(verify_query, {
        'booking_id': booking_id,
        'cust_id': session['user_id']
    })
    
    if not result:
        return redirect(url_for('my_bookings'))
    
    booking = result[0]
    
    # If already paid or cancelled, redirect to my bookings
    if booking['IS_PAID'] == 1:
        return redirect(url_for('my_bookings'))
    
    if booking['BOOKING_STATUS'] == 'Cancelled':
        return redirect(url_for('my_bookings'))
    
    return render_template('payment.html', booking_id=booking_id, payment_timeout_minutes=PAYMENT_TIMEOUT_MINUTES)

@app.route('/api/booking/<int:booking_id>/time-remaining', methods=['GET'])
def get_booking_time_remaining(booking_id):
    """Get remaining time before booking auto-cancels"""
    try:
        query = """
            SELECT b.created_at, b.booking_status,
                   CASE WHEN EXISTS (SELECT 1 FROM Payment p WHERE p.booking_id = b.booking_id) THEN 1 ELSE 0 END as is_paid
            FROM Booking b 
            WHERE b.booking_id = :booking_id
        """
        result = Database.execute_query(query, {'booking_id': booking_id})
        
        if not result:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        booking = result[0]
        
        if booking['IS_PAID'] == 1:
            return jsonify({'success': True, 'status': 'paid', 'message': 'Already paid'})
        
        if booking['BOOKING_STATUS'] == 'Cancelled':
            return jsonify({'success': True, 'status': 'cancelled', 'message': 'Booking cancelled'})
        
        created_at = booking['CREATED_AT']
        if created_at:
            expiry_time = created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
            time_remaining = (expiry_time - datetime.now()).total_seconds()
            
            if time_remaining <= 0:
                return jsonify({'success': True, 'status': 'expired', 'seconds_remaining': 0, 'message': 'Payment time expired'})
            
            return jsonify({
                'success': True, 
                'status': 'pending',
                'seconds_remaining': int(time_remaining),
                'message': f'{int(time_remaining // 60)} minutes remaining'
            })
        
        return jsonify({'success': True, 'status': 'unknown'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login'}), 401
    
    try:
        data = request.json
        booking_id = data['booking_id']
        
        # Verify booking belongs to user
        verify_query = "SELECT price FROM Booking WHERE booking_id = :booking_id AND cust_id = :cust_id"
        verify_result = Database.execute_query(verify_query, {
            'booking_id': booking_id,
            'cust_id': session['user_id']
        })
        
        if not verify_result:
            return jsonify({'success': False, 'message': 'Booking not found or unauthorized'}), 404
        
        # Check if already paid
        payment_check = Database.execute_query(
            "SELECT booking_id FROM Payment WHERE booking_id = :booking_id",
            {'booking_id': booking_id}
        )
        
        if payment_check:
            return jsonify({'success': False, 'message': 'Payment already processed'}), 400
        
        # Create payment
        amount = float(verify_result[0]['PRICE'])
        payment_query = """
            INSERT INTO Payment (booking_id, amount, payment_date)
            VALUES (:booking_id, :amount, SYSDATE)
        """
        Database.execute_query(payment_query, {
            'booking_id': booking_id,
            'amount': amount
        }, fetch=False)
        
        return jsonify({'success': True, 'message': 'Payment processed successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ADMIN/STAFF ROUTES ====================

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    return render_template('admin.html')

# Admin: Get dashboard statistics
@app.route('/api/admin/stats', methods=['GET'])
def admin_get_stats():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        stats = {}
        
        # Total revenue (sum of all payments)
        revenue_query = "SELECT NVL(SUM(amount), 0) as total_revenue FROM Payment"
        revenue_result = Database.execute_query(revenue_query)
        stats['total_revenue'] = float(revenue_result[0]['TOTAL_REVENUE']) if revenue_result else 0
        
        # Revenue this month
        monthly_revenue_query = """
            SELECT NVL(SUM(amount), 0) as monthly_revenue 
            FROM Payment 
            WHERE EXTRACT(MONTH FROM payment_date) = EXTRACT(MONTH FROM SYSDATE)
            AND EXTRACT(YEAR FROM payment_date) = EXTRACT(YEAR FROM SYSDATE)
        """
        monthly_result = Database.execute_query(monthly_revenue_query)
        stats['monthly_revenue'] = float(monthly_result[0]['MONTHLY_REVENUE']) if monthly_result else 0
        
        # Booking counts
        booking_counts_query = """
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN p.booking_id IS NOT NULL THEN 1 ELSE 0 END) as paid_bookings,
                SUM(CASE WHEN p.booking_id IS NULL THEN 1 ELSE 0 END) as pending_bookings
            FROM Booking b
            LEFT JOIN Payment p ON b.booking_id = p.booking_id
        """
        counts_result = Database.execute_query(booking_counts_query)
        if counts_result:
            stats['total_bookings'] = int(counts_result[0]['TOTAL_BOOKINGS'] or 0)
            stats['paid_bookings'] = int(counts_result[0]['PAID_BOOKINGS'] or 0)
            stats['pending_bookings'] = int(counts_result[0]['PENDING_BOOKINGS'] or 0)
        
        # Total cars
        cars_query = "SELECT COUNT(*) as total_cars FROM Car"
        cars_result = Database.execute_query(cars_query)
        stats['total_cars'] = int(cars_result[0]['TOTAL_CARS']) if cars_result else 0
        
        # Total customers
        customers_query = "SELECT COUNT(*) as total_customers FROM Customer"
        customers_result = Database.execute_query(customers_query)
        stats['total_customers'] = int(customers_result[0]['TOTAL_CUSTOMERS']) if customers_result else 0
        
        # Popular brands (top 5 by bookings)
        popular_brands_query = """
            SELECT br.brand_name, COUNT(b.booking_id) as booking_count
            FROM Booking b
            JOIN Car c ON b.car_id = c.car_id
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand br ON m.brand_id = br.brand_id
            GROUP BY br.brand_name
            ORDER BY booking_count DESC
            FETCH FIRST 5 ROWS ONLY
        """
        popular_brands = Database.execute_query(popular_brands_query)
        stats['popular_brands'] = [{'name': b['BRAND_NAME'], 'count': int(b['BOOKING_COUNT'])} for b in popular_brands]
        
        # Monthly revenue trend (last 6 months)
        monthly_trend_query = """
            SELECT 
                TO_CHAR(payment_date, 'Mon YYYY') as month_name,
                TO_CHAR(payment_date, 'YYYY-MM') as month_sort,
                SUM(amount) as revenue
            FROM Payment
            WHERE payment_date >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -5)
            GROUP BY TO_CHAR(payment_date, 'Mon YYYY'), TO_CHAR(payment_date, 'YYYY-MM')
            ORDER BY month_sort
        """
        monthly_trend = Database.execute_query(monthly_trend_query)
        stats['monthly_trend'] = [{'month': m['MONTH_NAME'], 'revenue': float(m['REVENUE'])} for m in monthly_trend]
        
        # Recent bookings (last 5)
        recent_bookings_query = """
            SELECT b.booking_id, b.pickup_date, b.price,
                   cu.cust_fname || ' ' || cu.cust_lname as customer_name,
                   br.brand_name || ' ' || m.model_name as car_name,
                   CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as status
            FROM Booking b
            JOIN Customer cu ON b.cust_id = cu.cust_id
            JOIN Car c ON b.car_id = c.car_id
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand br ON m.brand_id = br.brand_id
            LEFT JOIN Payment p ON b.booking_id = p.booking_id
            ORDER BY b.booking_id DESC
            FETCH FIRST 5 ROWS ONLY
        """
        recent_bookings = Database.execute_query(recent_bookings_query)
        stats['recent_bookings'] = [{
            'booking_id': rb['BOOKING_ID'],
            'pickup_date': rb['PICKUP_DATE'].isoformat() if rb['PICKUP_DATE'] else None,
            'price': float(rb['PRICE']),
            'customer_name': rb['CUSTOMER_NAME'],
            'car_name': rb['CAR_NAME'],
            'status': rb['STATUS']
        } for rb in recent_bookings]
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Get all cars
@app.route('/api/admin/cars', methods=['GET'])
def admin_get_cars():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        query = """
            SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                   m.attachments, c.pickup_location, c.dropoff_location, c.available_locations,
                   NVL(c.car_status, 'Available') as car_status,
                   c.location_id,
                   l.location_name as home_location, l.city as home_city,
                   m.model_id, m.model_name, b.brand_id, b.brand_name, ct.carType_id, ct.carType_name,
                   CASE 
                       WHEN EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id) THEN 'Petrol'
                       WHEN EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id) THEN 'Diesel'
                       WHEN EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id) THEN 'Electric'
                       ELSE 'N/A'
                   END as fuel_type
            FROM Car c
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand b ON m.brand_id = b.brand_id
            JOIN CarType ct ON c.carType_id = ct.carType_id
            LEFT JOIN Location l ON c.location_id = l.location_id
            ORDER BY b.brand_name, m.model_name, l.location_name
        """
        cars = Database.execute_query(query)
        
        for car in cars:
            for key, value in car.items():
                if isinstance(value, (int, float)):
                    car[key] = float(value) if '.' in str(value) else int(value)
        
        return jsonify({'success': True, 'cars': cars})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Get single car with all details
@app.route('/api/admin/car/<int:car_id>', methods=['GET'])
def admin_get_car(car_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        query = """
            SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                   m.attachments, c.pickup_location, c.dropoff_location, c.available_locations,
                   c.allows_different_dropoff, NVL(c.car_status, 'Available') as car_status,
                   c.location_id,
                   m.model_id, m.model_name, b.brand_id, b.brand_name, ct.carType_id, ct.carType_name,
                   CASE 
                       WHEN EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id) THEN 'Petrol'
                       WHEN EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id) THEN 'Diesel'
                       WHEN EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id) THEN 'Electric'
                       ELSE 'N/A'
                   END as fuel_type,
                   p.octane_rating, p.fuel_tank_capacity as petrol_tank,
                   d.diesel_emission, d.fuel_tank_capacity as diesel_tank,
                   e.battery_range, e.charging_rate_kw, e.last_charging_date
            FROM Car c
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand b ON m.brand_id = b.brand_id
            JOIN CarType ct ON c.carType_id = ct.carType_id
            LEFT JOIN Petrol p ON c.car_id = p.car_id
            LEFT JOIN Diesel d ON c.car_id = d.car_id
            LEFT JOIN Electric e ON c.car_id = e.car_id
            WHERE c.car_id = :car_id
        """
        result = Database.execute_query(query, {'car_id': car_id})
        
        if result:
            car = result[0]
            for key, value in car.items():
                if isinstance(value, (int, float)):
                    car[key] = float(value) if '.' in str(value) else int(value)
                elif hasattr(value, 'isoformat'):
                    car[key] = value.isoformat() if value else None
            return jsonify({'success': True, 'car': car})
        else:
            return jsonify({'success': False, 'message': 'Car not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Create new car
@app.route('/api/admin/car', methods=['POST'])
def admin_create_car():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        model_id = int(request.form.get('model_id'))
        carType_id = int(request.form.get('carType_id'))
        rate = float(request.form.get('rate'))
        fuel_type = request.form.get('fuel_type')
        description = request.form.get('description', '')
        door = request.form.get('door')
        suitcase = request.form.get('suitcase')
        seat = request.form.get('seat')
        colour = request.form.get('colour', '')
        location_id = request.form.get('location_id')  # Single location where car is
        allows_different_dropoff = 1 if request.form.get('allows_different_dropoff') == '1' else 0
        
        # Handle image upload
        filename = None
        if 'attachments' in request.files:
            file = request.files['attachments']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
        
        # Insert car with location_id
        car_query = """
            INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour,
                           attachments, location_id, allows_different_dropoff)
            VALUES (:model_id, :carType_id, :rate, :description, :door, :suitcase, :seat, :colour,
                   :attachments, :location_id, :allows_different_dropoff)
        """
        
        car_params = {
            'model_id': model_id,
            'carType_id': carType_id,
            'rate': rate,
            'description': description if description else None,
            'door': int(door) if door else None,
            'suitcase': int(suitcase) if suitcase else None,
            'seat': int(seat) if seat else None,
            'colour': colour if colour else None,
            'attachments': filename,
            'location_id': int(location_id) if location_id else None,
            'allows_different_dropoff': allows_different_dropoff
        }
        
        Database.execute_query(car_query, car_params, fetch=False)
        
        # Get the inserted car_id
        get_id_query = "SELECT car_id FROM Car WHERE ROWID = (SELECT MAX(ROWID) FROM Car)"
        car_result = Database.execute_query(get_id_query)
        car_id = car_result[0]['CAR_ID'] if car_result else None
        
        if not car_id:
            return jsonify({'success': False, 'message': 'Failed to create car'}), 500
        
        # Insert fuel type specific data
        if fuel_type == 'Petrol':
            octane_rating = request.form.get('octane_rating')
            fuel_tank = request.form.get('petrol_tank_capacity')
            if octane_rating or fuel_tank:
                petrol_query = """
                    INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity)
                    VALUES (:car_id, :octane_rating, :fuel_tank_capacity)
                """
                Database.execute_query(petrol_query, {
                    'car_id': car_id,
                    'octane_rating': int(octane_rating) if octane_rating else None,
                    'fuel_tank_capacity': float(fuel_tank) if fuel_tank else None
                }, fetch=False)
        
        elif fuel_type == 'Diesel':
            diesel_emission = request.form.get('diesel_emission')
            fuel_tank = request.form.get('diesel_tank_capacity')
            if diesel_emission or fuel_tank:
                diesel_query = """
                    INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity)
                    VALUES (:car_id, :diesel_emission, :fuel_tank_capacity)
                """
                Database.execute_query(diesel_query, {
                    'car_id': car_id,
                    'diesel_emission': diesel_emission if diesel_emission else None,
                    'fuel_tank_capacity': float(fuel_tank) if fuel_tank else None
                }, fetch=False)
        
        elif fuel_type == 'Electric':
            battery_range = request.form.get('battery_range')
            charging_rate = request.form.get('charging_rate_kw')
            last_charging = request.form.get('last_charging_date')
            if battery_range or charging_rate or last_charging:
                if last_charging:
                    electric_query = """
                        INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date)
                        VALUES (:car_id, :battery_range, :charging_rate_kw, TO_DATE(:last_charging_date, 'YYYY-MM-DD'))
                    """
                else:
                    electric_query = """
                        INSERT INTO Electric (car_id, battery_range, charging_rate_kw)
                        VALUES (:car_id, :battery_range, :charging_rate_kw)
                    """
                electric_params = {
                    'car_id': car_id,
                    'battery_range': int(battery_range) if battery_range else None,
                    'charging_rate_kw': float(charging_rate) if charging_rate else None
                }
                if last_charging:
                    electric_params['last_charging_date'] = last_charging
                Database.execute_query(electric_query, electric_params, fetch=False)
        
        return jsonify({'success': True, 'message': 'Car created successfully', 'car_id': car_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Update car
@app.route('/api/admin/car/<int:car_id>', methods=['PUT'])
def admin_update_car(car_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        model_id = int(request.form.get('model_id'))
        carType_id = int(request.form.get('carType_id'))
        rate = float(request.form.get('rate'))
        fuel_type = request.form.get('fuel_type')
        description = request.form.get('description', '')
        door = request.form.get('door')
        suitcase = request.form.get('suitcase')
        seat = request.form.get('seat')
        colour = request.form.get('colour', '')
        location_id = request.form.get('location_id')  # Single location where car is
        allows_different_dropoff = 1 if request.form.get('allows_different_dropoff') == '1' else 0
        
        # Handle image upload
        filename = None
        if 'attachments' in request.files:
            file = request.files['attachments']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
        
        # Update car
        car_params = {
            'car_id': car_id,
            'model_id': model_id,
            'carType_id': carType_id,
            'rate': rate,
            'description': description if description else None,
            'door': int(door) if door else None,
            'suitcase': int(suitcase) if suitcase else None,
            'seat': int(seat) if seat else None,
            'colour': colour if colour else None,
            'location_id': int(location_id) if location_id else None,
            'allows_different_dropoff': allows_different_dropoff
        }
        
        if filename:
            car_params['attachments'] = filename
            car_query = """
                UPDATE Car SET model_id = :model_id, carType_id = :carType_id, rate = :rate,
                             description = :description, door = :door, suitcase = :suitcase, seat = :seat,
                             colour = :colour, attachments = :attachments,
                             location_id = :location_id, allows_different_dropoff = :allows_different_dropoff
                WHERE car_id = :car_id
            """
        else:
            car_query = """
                UPDATE Car SET model_id = :model_id, carType_id = :carType_id, rate = :rate,
                             description = :description, door = :door, suitcase = :suitcase, seat = :seat,
                             colour = :colour,
                             location_id = :location_id, allows_different_dropoff = :allows_different_dropoff
                WHERE car_id = :car_id
            """
        
        Database.execute_query(car_query, car_params, fetch=False)
        
        # Delete old fuel type records
        Database.execute_query("DELETE FROM Petrol WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        Database.execute_query("DELETE FROM Diesel WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        Database.execute_query("DELETE FROM Electric WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        
        # Insert new fuel type specific data
        if fuel_type == 'Petrol':
            octane_rating = request.form.get('octane_rating')
            fuel_tank = request.form.get('petrol_tank_capacity')
            if octane_rating or fuel_tank:
                petrol_query = """
                    INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity)
                    VALUES (:car_id, :octane_rating, :fuel_tank_capacity)
                """
                Database.execute_query(petrol_query, {
                    'car_id': car_id,
                    'octane_rating': int(octane_rating) if octane_rating else None,
                    'fuel_tank_capacity': float(fuel_tank) if fuel_tank else None
                }, fetch=False)
        
        elif fuel_type == 'Diesel':
            diesel_emission = request.form.get('diesel_emission')
            fuel_tank = request.form.get('diesel_tank_capacity')
            if diesel_emission or fuel_tank:
                diesel_query = """
                    INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity)
                    VALUES (:car_id, :diesel_emission, :fuel_tank_capacity)
                """
                Database.execute_query(diesel_query, {
                    'car_id': car_id,
                    'diesel_emission': diesel_emission if diesel_emission else None,
                    'fuel_tank_capacity': float(fuel_tank) if fuel_tank else None
                }, fetch=False)
        
        elif fuel_type == 'Electric':
            battery_range = request.form.get('battery_range')
            charging_rate = request.form.get('charging_rate_kw')
            last_charging = request.form.get('last_charging_date')
            if battery_range or charging_rate or last_charging:
                if last_charging:
                    electric_query = """
                        INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date)
                        VALUES (:car_id, :battery_range, :charging_rate_kw, TO_DATE(:last_charging_date, 'YYYY-MM-DD'))
                    """
                else:
                    electric_query = """
                        INSERT INTO Electric (car_id, battery_range, charging_rate_kw)
                        VALUES (:car_id, :battery_range, :charging_rate_kw)
                    """
                electric_params = {
                    'car_id': car_id,
                    'battery_range': int(battery_range) if battery_range else None,
                    'charging_rate_kw': float(charging_rate) if charging_rate else None
                }
                if last_charging:
                    electric_params['last_charging_date'] = last_charging
                Database.execute_query(electric_query, electric_params, fetch=False)
        
        return jsonify({'success': True, 'message': 'Car updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Delete car
@app.route('/api/admin/car/<int:car_id>', methods=['DELETE'])
def admin_delete_car(car_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Check if car has bookings
        booking_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Booking WHERE car_id = :car_id",
            {'car_id': car_id}
        )
        
        if booking_check and booking_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete car with existing bookings'}), 400
        
        # Delete fuel type records first (due to foreign keys)
        Database.execute_query("DELETE FROM Petrol WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        Database.execute_query("DELETE FROM Diesel WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        Database.execute_query("DELETE FROM Electric WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        
        # Delete car
        Database.execute_query("DELETE FROM Car WHERE car_id = :car_id", {'car_id': car_id}, fetch=False)
        
        return jsonify({'success': True, 'message': 'Car deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Update car status
@app.route('/api/admin/car/<int:car_id>/status', methods=['PUT'])
def admin_update_car_status(car_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        new_status = data.get('status')
        
        valid_statuses = ['Available', 'Rented', 'Maintenance', 'Dirty']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        Database.execute_query(
            "UPDATE Car SET car_status = :status WHERE car_id = :car_id",
            {'status': new_status, 'car_id': car_id},
            fetch=False
        )
        
        return jsonify({'success': True, 'message': f'Car status updated to {new_status}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Update booking status
@app.route('/api/admin/booking/<int:booking_id>/status', methods=['PUT'])
def admin_update_booking_status(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        new_status = data.get('status')
        
        valid_statuses = ['Confirmed', 'In Progress', 'Completed', 'Cancelled']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Get the booking to check car_id
        booking = Database.execute_query(
            "SELECT car_id FROM Booking WHERE booking_id = :booking_id",
            {'booking_id': booking_id}
        )
        
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        car_id = booking[0]['CAR_ID']
        
        # Update booking status
        Database.execute_query(
            "UPDATE Booking SET booking_status = :status WHERE booking_id = :booking_id",
            {'status': new_status, 'booking_id': booking_id},
            fetch=False
        )
        
        # Get booking dates to check if rental period has started
        booking_dates = Database.execute_query(
            "SELECT pickup_date, dropoff_date FROM Booking WHERE booking_id = :booking_id",
            {'booking_id': booking_id}
        )
        pickup_date = booking_dates[0]['PICKUP_DATE'] if booking_dates else None
        
        # Auto-update car status based on booking status
        if new_status == 'In Progress':
            # Car is now rented
            Database.execute_query(
                "UPDATE Car SET car_status = 'Rented' WHERE car_id = :car_id",
                {'car_id': car_id},
                fetch=False
            )
        elif new_status == 'Confirmed':
            # If pickup date has started, car should be Rented
            if pickup_date and pickup_date.date() <= datetime.now().date():
                Database.execute_query(
                    "UPDATE Car SET car_status = 'Rented' WHERE car_id = :car_id",
                    {'car_id': car_id},
                    fetch=False
                )
        elif new_status in ['Completed', 'Cancelled']:
            # Check if car has any other active bookings
            active_bookings = Database.execute_query(
                """SELECT COUNT(*) as cnt FROM Booking 
                   WHERE car_id = :car_id 
                   AND booking_id != :booking_id
                   AND NVL(booking_status, 'Confirmed') IN ('Confirmed', 'In Progress')
                   AND TRUNC(SYSDATE) BETWEEN TRUNC(pickup_date) AND TRUNC(dropoff_date)""",
                {'car_id': car_id, 'booking_id': booking_id}
            )
            
            if not active_bookings or active_bookings[0]['CNT'] == 0:
                # No other active bookings, set car to Available (or Dirty if completed)
                car_status = 'Dirty' if new_status == 'Completed' else 'Available'
                Database.execute_query(
                    "UPDATE Car SET car_status = :status WHERE car_id = :car_id",
                    {'status': car_status, 'car_id': car_id},
                    fetch=False
                )
        
        return jsonify({'success': True, 'message': f'Booking status updated to {new_status}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Get models by brand
@app.route('/api/models', methods=['GET'])
def get_models():
    brand_id = request.args.get('brand_id')
    if not brand_id:
        return jsonify({'success': False, 'message': 'brand_id required'}), 400
    
    try:
        query = "SELECT model_id, model_name FROM Model WHERE brand_id = :brand_id ORDER BY model_name"
        models = Database.execute_query(query, {'brand_id': int(brand_id)})
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Add brand
@app.route('/api/admin/brand', methods=['POST'])
def admin_add_brand():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        brand_name = data.get('brand_name')
        if not brand_name:
            return jsonify({'success': False, 'message': 'Brand name required'}), 400
        
        query = "INSERT INTO Brand (brand_name) VALUES (:brand_name)"
        Database.execute_query(query, {'brand_name': brand_name}, fetch=False)
        
        # Get the newly created brand ID
        id_query = "SELECT brand_id FROM Brand WHERE brand_name = :brand_name"
        result = Database.execute_query(id_query, {'brand_name': brand_name})
        brand_id = result[0]['BRAND_ID'] if result else None
        
        return jsonify({'success': True, 'message': 'Brand added successfully', 'brand_id': brand_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/brand/upload-logo', methods=['POST'])
def admin_upload_brand_logo():
    """Upload brand logo"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    brand_id = request.form.get('brand_id')
    
    if not brand_id:
        return jsonify({'success': False, 'message': 'Brand ID required'}), 400
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Create brands folder if it doesn't exist
        brands_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'brands')
        os.makedirs(brands_folder, exist_ok=True)
        
        # Save with consistent naming: brand_{id}.png
        filename = f"brand_{brand_id}.png"
        filepath = os.path.join(brands_folder, filename)
        
        # Remove old logo if exists
        if os.path.exists(filepath):
            os.remove(filepath)
        
        file.save(filepath)
        return jsonify({'success': True, 'message': 'Logo uploaded successfully', 'filename': filename})
    
    return jsonify({'success': False, 'message': 'Invalid file type. Please upload an image.'}), 400

# Admin: Update brand
@app.route('/api/admin/brand/<int:brand_id>', methods=['PUT'])
def admin_update_brand(brand_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        brand_name = data.get('brand_name')
        if not brand_name:
            return jsonify({'success': False, 'message': 'Brand name required'}), 400
        
        query = "UPDATE Brand SET brand_name = :brand_name WHERE brand_id = :brand_id"
        Database.execute_query(query, {'brand_name': brand_name, 'brand_id': brand_id}, fetch=False)
        return jsonify({'success': True, 'message': 'Brand updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Delete brand
@app.route('/api/admin/brand/<int:brand_id>', methods=['DELETE'])
def admin_delete_brand(brand_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Check if brand has models
        model_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Model WHERE brand_id = :brand_id",
            {'brand_id': brand_id}
        )
        if model_check and model_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete brand with existing models. Delete the models first.'}), 400
        
        query = "DELETE FROM Brand WHERE brand_id = :brand_id"
        Database.execute_query(query, {'brand_id': brand_id}, fetch=False)
        return jsonify({'success': True, 'message': 'Brand deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Add model
@app.route('/api/admin/model', methods=['POST'])
def admin_add_model():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        model_name = data.get('model_name')
        brand_id = data.get('brand_id')
        if not model_name or not brand_id:
            return jsonify({'success': False, 'message': 'Model name and brand_id required'}), 400
        
        query = "INSERT INTO Model (model_name, brand_id) VALUES (:model_name, :brand_id)"
        Database.execute_query(query, {'model_name': model_name, 'brand_id': int(brand_id)}, fetch=False)
        return jsonify({'success': True, 'message': 'Model added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Update model
@app.route('/api/admin/model/<int:model_id>', methods=['PUT'])
def admin_update_model(model_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        model_name = data.get('model_name')
        brand_id = data.get('brand_id')
        if not model_name or not brand_id:
            return jsonify({'success': False, 'message': 'Model name and brand_id required'}), 400
        
        query = "UPDATE Model SET model_name = :model_name, brand_id = :brand_id WHERE model_id = :model_id"
        Database.execute_query(query, {
            'model_name': model_name, 
            'brand_id': int(brand_id),
            'model_id': model_id
        }, fetch=False)
        return jsonify({'success': True, 'message': 'Model updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Delete model
@app.route('/api/admin/model/<int:model_id>', methods=['DELETE'])
def admin_delete_model(model_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Check if model has cars
        car_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Car WHERE model_id = :model_id",
            {'model_id': model_id}
        )
        if car_check and car_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete model with existing cars. Delete the cars first.'}), 400
        
        query = "DELETE FROM Model WHERE model_id = :model_id"
        Database.execute_query(query, {'model_id': model_id}, fetch=False)
        return jsonify({'success': True, 'message': 'Model deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Get all models with brands
@app.route('/api/admin/models', methods=['GET'])
def admin_get_all_models():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        query = """
            SELECT m.model_id, m.model_name, m.attachments, b.brand_id, b.brand_name
            FROM Model m
            JOIN Brand b ON m.brand_id = b.brand_id
            ORDER BY b.brand_name, m.model_name
        """
        models = Database.execute_query(query)
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin: Upload model image
@app.route('/api/admin/model/<int:model_id>/image', methods=['POST'])
def admin_upload_model_image(model_id):
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        if 'attachments' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['attachments']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create filename based on model_id
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"model_{model_id}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Update model with new attachment
            query = "UPDATE Model SET attachments = :attachments WHERE model_id = :model_id"
            Database.execute_query(query, {
                'attachments': filename,
                'model_id': model_id
            }, fetch=False)
            
            return jsonify({'success': True, 'message': 'Model image uploaded successfully', 'filename': filename})
        else:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Get model image
@app.route('/api/model/<int:model_id>/image', methods=['GET'])
def get_model_image(model_id):
    try:
        query = "SELECT attachments FROM Model WHERE model_id = :model_id"
        result = Database.execute_query(query, {'model_id': model_id})
        
        if result and result[0]['ATTACHMENTS']:
            return send_from_directory(app.config['UPLOAD_FOLDER'], result[0]['ATTACHMENTS'])
        else:
            # Return placeholder
            return redirect('https://via.placeholder.com/300x200?text=No+Image')
    except Exception as e:
        return redirect('https://via.placeholder.com/300x200?text=Error')

# Admin: Update payment status
@app.route('/api/admin/booking/payment-status', methods=['PUT'])
def admin_update_payment_status():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        booking_id = data.get('booking_id')
        payment_status = data.get('payment_status')
        
        if not booking_id or not payment_status:
            return jsonify({'success': False, 'message': 'booking_id and payment_status required'}), 400
        
        # Get booking price
        booking_query = "SELECT price FROM Booking WHERE booking_id = :booking_id"
        booking_result = Database.execute_query(booking_query, {'booking_id': int(booking_id)})
        
        if not booking_result:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        booking_price = booking_result[0]['PRICE']
        
        # Check if payment exists
        payment_check = Database.execute_query(
            "SELECT booking_id FROM Payment WHERE booking_id = :booking_id",
            {'booking_id': int(booking_id)}
        )
        
        if payment_status == 'Paid':
            # Create payment if it doesn't exist
            if not payment_check:
                payment_query = """
                    INSERT INTO Payment (booking_id, amount, payment_date)
                    VALUES (:booking_id, :amount, SYSDATE)
                """
                Database.execute_query(payment_query, {
                    'booking_id': int(booking_id),
                    'amount': float(booking_price)
                }, fetch=False)
        else:  # Pending
            # Delete payment if it exists
            if payment_check:
                delete_query = "DELETE FROM Payment WHERE booking_id = :booking_id"
                Database.execute_query(delete_query, {'booking_id': int(booking_id)}, fetch=False)
        
        return jsonify({'success': True, 'message': 'Payment status updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== STAFF MANAGEMENT (FOR MANAGERS) ====================

@app.route('/api/admin/check-manager', methods=['GET'])
def check_manager():
    """Check if current user is a manager"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'is_manager': False})
    
    return jsonify({'success': True, 'is_manager': session.get('is_manager', False)})

@app.route('/api/admin/staff', methods=['GET'])
def get_managed_staff():
    """Get staff members under the current manager"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if not session.get('is_manager'):
        return jsonify({'success': False, 'message': 'Only managers can access this'}), 403
    
    try:
        manager_id = session['user_id']
        query = """
            SELECT s.staff_id, s.staff_fname, s.staff_lname, s.staff_email, 
                   s.staff_phone, s.staff_dept, s.staff_username,
                   (SELECT COUNT(*) FROM Staff sub WHERE sub.manager_id = s.staff_id) as subordinate_count
            FROM Staff s
            WHERE s.manager_id = :manager_id
            ORDER BY s.staff_fname, s.staff_lname
        """
        staff = Database.execute_query(query, {'manager_id': manager_id})
        return jsonify({'success': True, 'staff': staff})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/staff', methods=['POST'])
def add_staff():
    """Add new staff member under current manager"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if not session.get('is_manager'):
        return jsonify({'success': False, 'message': 'Only managers can add staff'}), 403
    
    try:
        data = request.json
        manager_id = session['user_id']
        
        # Validate password
        password = data.get('password', '')
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Check if username already exists
        username_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Staff WHERE staff_username = :username",
            {'username': data['username']}
        )
        if username_check and username_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Check if email already exists
        email_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Staff WHERE staff_email = :email",
            {'email': data['email']}
        )
        if email_check and email_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        query = """
            INSERT INTO Staff (staff_fname, staff_lname, staff_email, staff_phone, staff_dept, staff_username, staff_password, manager_id)
            VALUES (:fname, :lname, :email, :phone, :dept, :username, :password, :manager_id)
        """
        Database.execute_query(query, {
            'fname': data['fname'],
            'lname': data['lname'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'dept': data.get('dept', ''),
            'username': data['username'],
            'password': data['password'],
            'manager_id': manager_id
        }, fetch=False)
        
        return jsonify({'success': True, 'message': 'Staff added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/staff/<int:staff_id>', methods=['GET'])
def get_staff_member(staff_id):
    """Get single staff member details"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if not session.get('is_manager'):
        return jsonify({'success': False, 'message': 'Only managers can access this'}), 403
    
    try:
        manager_id = session['user_id']
        query = """
            SELECT staff_id, staff_fname, staff_lname, staff_email, staff_phone, staff_dept, staff_username
            FROM Staff
            WHERE staff_id = :staff_id AND manager_id = :manager_id
        """
        result = Database.execute_query(query, {'staff_id': staff_id, 'manager_id': manager_id})
        
        if not result:
            return jsonify({'success': False, 'message': 'Staff not found or not under your management'}), 404
        
        return jsonify({'success': True, 'staff': result[0]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update staff member under current manager"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if not session.get('is_manager'):
        return jsonify({'success': False, 'message': 'Only managers can update staff'}), 403
    
    try:
        data = request.json
        manager_id = session['user_id']
        
        # Verify staff is under this manager
        verify = Database.execute_query(
            "SELECT staff_id FROM Staff WHERE staff_id = :staff_id AND manager_id = :manager_id",
            {'staff_id': staff_id, 'manager_id': manager_id}
        )
        if not verify:
            return jsonify({'success': False, 'message': 'Staff not found or not under your management'}), 404
        
        # Check if username already exists (exclude current staff)
        if 'username' in data:
            username_check = Database.execute_query(
                "SELECT COUNT(*) as cnt FROM Staff WHERE staff_username = :username AND staff_id != :staff_id",
                {'username': data['username'], 'staff_id': staff_id}
            )
            if username_check and username_check[0]['CNT'] > 0:
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Check if email already exists (exclude current staff)
        if 'email' in data:
            email_check = Database.execute_query(
                "SELECT COUNT(*) as cnt FROM Staff WHERE staff_email = :email AND staff_id != :staff_id",
                {'email': data['email'], 'staff_id': staff_id}
            )
            if email_check and email_check[0]['CNT'] > 0:
                return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Build update query
        update_fields = []
        params = {'staff_id': staff_id}
        
        if 'fname' in data:
            update_fields.append('staff_fname = :fname')
            params['fname'] = data['fname']
        if 'lname' in data:
            update_fields.append('staff_lname = :lname')
            params['lname'] = data['lname']
        if 'email' in data:
            update_fields.append('staff_email = :email')
            params['email'] = data['email']
        if 'phone' in data:
            update_fields.append('staff_phone = :phone')
            params['phone'] = data['phone']
        if 'dept' in data:
            update_fields.append('staff_dept = :dept')
            params['dept'] = data['dept']
        if 'username' in data:
            update_fields.append('staff_username = :username')
            params['username'] = data['username']
        if 'password' in data and data['password']:
            # Validate new password
            is_valid, error_msg = validate_password(data['password'])
            if not is_valid:
                return jsonify({'success': False, 'message': error_msg}), 400
            update_fields.append('staff_password = :password')
            params['password'] = data['password']
        
        if update_fields:
            query = f"UPDATE Staff SET {', '.join(update_fields)} WHERE staff_id = :staff_id"
            Database.execute_query(query, params, fetch=False)
        
        return jsonify({'success': True, 'message': 'Staff updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """Delete staff member under current manager"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if not session.get('is_manager'):
        return jsonify({'success': False, 'message': 'Only managers can delete staff'}), 403
    
    try:
        manager_id = session['user_id']
        
        # Verify staff is under this manager
        verify = Database.execute_query(
            "SELECT staff_id FROM Staff WHERE staff_id = :staff_id AND manager_id = :manager_id",
            {'staff_id': staff_id, 'manager_id': manager_id}
        )
        if not verify:
            return jsonify({'success': False, 'message': 'Staff not found or not under your management'}), 404
        
        # Check if staff has subordinates
        subordinate_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Staff WHERE manager_id = :staff_id",
            {'staff_id': staff_id}
        )
        if subordinate_check and subordinate_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete staff with subordinates. Reassign their staff first.'}), 400
        
        # Check if staff has bookings
        booking_check = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM Booking WHERE staff_id = :staff_id",
            {'staff_id': staff_id}
        )
        if booking_check and booking_check[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete staff with existing bookings'}), 400
        
        # Delete staff
        Database.execute_query(
            "DELETE FROM Staff WHERE staff_id = :staff_id",
            {'staff_id': staff_id},
            fetch=False
        )
        
        return jsonify({'success': True, 'message': 'Staff deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== STATIC FILES ====================

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload-car-image', methods=['POST'])
def upload_car_image():
    """Upload car image and update database"""
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    car_id = request.form.get('car_id')
    
    if not car_id:
        return jsonify({'success': False, 'message': 'Car ID required'}), 400
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"car_{car_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update database
        try:
            update_query = "UPDATE Car SET attachments = :filename WHERE car_id = :car_id"
            Database.execute_query(update_query, {
                'filename': filename,
                'car_id': int(car_id)
            }, fetch=False)
            return jsonify({'success': True, 'message': 'Image uploaded successfully', 'filename': filename})
        except Exception as e:
            # Delete file if database update fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

