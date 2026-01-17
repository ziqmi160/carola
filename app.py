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

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                session['user_id'] = user['CUST_ID']
                session['username'] = user['CUST_USERNAME']
                session['name'] = f"{user['CUST_FNAME']} {user['CUST_LNAME']}"
                session['user_type'] = 'customer'
                return jsonify({'success': True, 'user_type': 'customer', 'message': 'Login successful!'})
            
            # If not found in Customer, try Staff table
            staff_query = "SELECT staff_id, staff_fname, staff_lname, staff_email, staff_username, staff_dept FROM Staff WHERE staff_username = :username AND staff_password = :password"
            staff_result = Database.execute_query(staff_query, {'username': username, 'password': password})
            
            if staff_result:
                # User is staff
                user = staff_result[0]
                session['user_id'] = user['STAFF_ID']
                session['username'] = user['STAFF_USERNAME']
                session['name'] = f"{user['STAFF_FNAME']} {user['STAFF_LNAME']}"
                session['dept'] = user.get('STAFF_DEPT', '')
                session['user_type'] = 'staff'
                
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
        car_type = request.args.get('type', '')
        brand = request.args.get('brand', '')
        fuel_type = request.args.get('fuel_type', '')
        seats = request.args.get('seats', '')
        bags = request.args.get('bags', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        
        query = """
            SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                   c.pickup_location, c.dropoff_location, c.available_locations, c.allows_different_dropoff,
                   c.attachments,
                   m.model_name, b.brand_name, ct.carType_name,
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
            WHERE 1=1
        """
        params = {}
        
        if location:
            query += " AND (UPPER(c.available_locations) LIKE UPPER(:location) OR UPPER(c.pickup_location) LIKE UPPER(:location))"
            params['location'] = f'%{location}%'
        
        if car_type:
            query += " AND ct.carType_id = :car_type"
            params['car_type'] = int(car_type)
        
        if brand:
            query += " AND b.brand_id = :brand"
            params['brand'] = int(brand)
        
        if fuel_type:
            if fuel_type == 'Petrol':
                query += " AND EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id)"
            elif fuel_type == 'Diesel':
                query += " AND EXISTS (SELECT 1 FROM Diesel WHERE car_id = c.car_id)"
            elif fuel_type == 'Electric':
                query += " AND EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id)"
        
        if seats:
            query += " AND c.seat = :seats"
            params['seats'] = int(seats)
        
        if bags:
            query += " AND c.suitcase = :bags"
            params['bags'] = int(bags)
        
        if min_price:
            query += " AND c.rate >= :min_price"
            params['min_price'] = float(min_price)
        
        if max_price:
            query += " AND c.rate <= :max_price"
            params['max_price'] = float(max_price)
        
        query += " ORDER BY c.rate"
        
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
                   c.attachments,
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

@app.route('/api/filters', methods=['GET'])
def get_filters():
    try:
        brands = Database.execute_query("SELECT brand_id, brand_name FROM Brand ORDER BY brand_name")
        types = Database.execute_query("SELECT carType_id, carType_name FROM CarType ORDER BY carType_name")
        
        # Get all available_locations from cars
        locations_query = "SELECT DISTINCT available_locations FROM Car WHERE available_locations IS NOT NULL"
        locations_result = Database.execute_query(locations_query)
        
        # Extract unique locations and clean them
        locations_set = set()
        for row in locations_result:
            if row.get('AVAILABLE_LOCATIONS'):
                # Split by comma and clean each location
                locs = row['AVAILABLE_LOCATIONS'].split(',')
                for loc in locs:
                    clean_loc = loc.strip()
                    if clean_loc:
                        locations_set.add(clean_loc)
        
        locations = sorted(list(locations_set))
        
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
            'locations': [{'location': loc} for loc in locations],
            'seats': seats,
            'bags': bags
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== BOOKING ROUTES ====================

@app.route('/book/<int:car_id>')
def book_car(car_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        # Store the intended destination so user can be redirected after login
        return redirect(url_for('login', next=f'/book/{car_id}'))
    return render_template('booking.html', car_id=car_id)

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        return jsonify({'success': False, 'message': 'Please login as customer'}), 401
    
    try:
        data = request.json
        cust_id = session['user_id']
        
        # Get first available staff
        staff_query = "SELECT staff_id FROM Staff WHERE ROWNUM = 1"
        staff_result = Database.execute_query(staff_query)
        if not staff_result:
            return jsonify({'success': False, 'message': 'No staff available'}), 400
        staff_id = staff_result[0]['STAFF_ID']
        
        # Calculate price
        car_query = "SELECT rate FROM Car WHERE car_id = :car_id"
        car_result = Database.execute_query(car_query, {'car_id': data['car_id']})
        if not car_result:
            return jsonify({'success': False, 'message': 'Car not found'}), 404
        
        rate = float(car_result[0]['RATE'])
        # Handle datetime-local format (YYYY-MM-DDTHH:MM)
        pickup_date = datetime.strptime(data['pickup_date'], '%Y-%m-%dT%H:%M')
        dropoff_date = datetime.strptime(data['dropoff_date'], '%Y-%m-%dT%H:%M')
        # Calculate days (minimum 1 day, round up partial days)
        diff_hours = (dropoff_date - pickup_date).total_seconds() / 3600
        days = max(1, int((diff_hours + 23) // 24))  # Round up to full days
        price = rate * days
        
        # Check for conflicts
        conflict_query = """
            SELECT COUNT(*) as cnt FROM Booking
            WHERE car_id = :car_id
            AND ((pickup_date <= :pickup_date AND dropoff_date >= :pickup_date)
                 OR (pickup_date <= :dropoff_date AND dropoff_date >= :dropoff_date)
                 OR (pickup_date >= :pickup_date AND dropoff_date <= :dropoff_date))
        """
        conflict_result = Database.execute_query(conflict_query, {
            'car_id': data['car_id'],
            'pickup_date': pickup_date,
            'dropoff_date': dropoff_date
        })
        
        if conflict_result and conflict_result[0]['CNT'] > 0:
            return jsonify({'success': False, 'message': 'Car is not available for selected dates'}), 400
        
        # Create booking
        booking_query = """
            INSERT INTO Booking (cust_id, staff_id, car_id, pickup_date, dropoff_date, pickup_location, dropoff_location, price)
            VALUES (:cust_id, :staff_id, :car_id, :pickup_date, :dropoff_date, :pickup_location, :dropoff_location, :price)
        """
        Database.execute_query(booking_query, {
            'cust_id': cust_id,
            'staff_id': staff_id,
            'car_id': data['car_id'],
            'pickup_date': pickup_date,
            'dropoff_date': dropoff_date,
            'pickup_location': data['pickup_location'],
            'dropoff_location': data['dropoff_location'],
            'price': price
        }, fetch=False)
        
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
                SELECT b.booking_id, b.pickup_date, b.dropoff_date, b.pickup_location, b.dropoff_location, b.price,
                       c.car_id, m.model_name, br.brand_name, c.colour, c.rate,
                       CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
                FROM Booking b
                JOIN Car c ON b.car_id = c.car_id
                JOIN Model m ON c.model_id = m.model_id
                JOIN Brand br ON m.brand_id = br.brand_id
                LEFT JOIN Payment p ON b.booking_id = p.booking_id
                WHERE b.cust_id = :user_id
                ORDER BY b.pickup_date DESC
            """
            params = {'user_id': session['user_id']}
        else:
            query = """
                SELECT b.booking_id, b.pickup_date, b.dropoff_date, b.pickup_location, b.dropoff_location, b.price,
                       c.car_id, m.model_name, br.brand_name, c.colour, c.rate,
                       cu.cust_fname || ' ' || cu.cust_lname as customer_name, cu.cust_email, cu.cust_phone,
                       CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
                FROM Booking b
                JOIN Car c ON b.car_id = c.car_id
                JOIN Model m ON c.model_id = m.model_id
                JOIN Brand br ON m.brand_id = br.brand_id
                JOIN Customer cu ON b.cust_id = cu.cust_id
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

@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('my_bookings.html')

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
            SELECT b.booking_id, b.pickup_date, b.dropoff_date, b.pickup_location, b.dropoff_location, b.price,
                   c.car_id, c.rate, c.colour, c.door, c.seat, c.suitcase, c.attachments,
                   m.model_name, br.brand_name, ct.carType_name,
                   cu.cust_fname, cu.cust_lname, cu.cust_email, cu.cust_phone,
                   CASE WHEN p.booking_id IS NOT NULL THEN 'Paid' ELSE 'Pending' END as payment_status
            FROM Booking b
            JOIN Car c ON b.car_id = c.car_id
            JOIN Model m ON c.model_id = m.model_id
            JOIN Brand br ON m.brand_id = br.brand_id
            JOIN CarType ct ON c.carType_id = ct.carType_id
            JOIN Customer cu ON b.cust_id = cu.cust_id
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
    
    # Verify the booking belongs to this customer
    verify_query = "SELECT booking_id FROM Booking WHERE booking_id = :booking_id AND cust_id = :cust_id"
    result = Database.execute_query(verify_query, {
        'booking_id': booking_id,
        'cust_id': session['user_id']
    })
    
    if not result:
        return redirect(url_for('my_bookings'))
    
    return render_template('payment.html', booking_id=booking_id)

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

# Admin: Get all cars
@app.route('/api/admin/cars', methods=['GET'])
def admin_get_cars():
    if 'user_id' not in session or session.get('user_type') != 'staff':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        query = """
            SELECT c.car_id, c.rate, c.description, c.door, c.suitcase, c.seat, c.colour,
                   c.attachments, c.pickup_location, c.dropoff_location, c.available_locations,
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
            ORDER BY c.car_id DESC
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
                   c.attachments, c.pickup_location, c.dropoff_location, c.available_locations,
                   c.allows_different_dropoff,
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
        pickup_location = request.form.get('pickup_location', '')
        dropoff_location = request.form.get('dropoff_location', '')
        available_locations = request.form.get('available_locations', '')
        allows_different_dropoff = 1 if request.form.get('allows_different_dropoff') == '1' else 0
        
        # Handle image upload
        filename = None
        if 'attachments' in request.files:
            file = request.files['attachments']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
        
        # Insert car
        car_query = """
            INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour,
                           attachments, pickup_location, dropoff_location, available_locations, allows_different_dropoff)
            VALUES (:model_id, :carType_id, :rate, :description, :door, :suitcase, :seat, :colour,
                   :attachments, :pickup_location, :dropoff_location, :available_locations, :allows_different_dropoff)
            RETURNING car_id INTO :car_id
        """
        
        # Oracle doesn't support RETURNING in the same way, so we'll use a different approach
        car_query = """
            INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour,
                           attachments, pickup_location, dropoff_location, available_locations, allows_different_dropoff)
            VALUES (:model_id, :carType_id, :rate, :description, :door, :suitcase, :seat, :colour,
                   :attachments, :pickup_location, :dropoff_location, :available_locations, :allows_different_dropoff)
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
            'pickup_location': pickup_location if pickup_location else None,
            'dropoff_location': dropoff_location if dropoff_location else None,
            'available_locations': available_locations if available_locations else None,
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
            fuel_tank = request.form.get('fuel_tank_capacity')
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
            fuel_tank = request.form.get('fuel_tank_capacity')
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
        pickup_location = request.form.get('pickup_location', '')
        dropoff_location = request.form.get('dropoff_location', '')
        available_locations = request.form.get('available_locations', '')
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
            'pickup_location': pickup_location if pickup_location else None,
            'dropoff_location': dropoff_location if dropoff_location else None,
            'available_locations': available_locations if available_locations else None,
            'allows_different_dropoff': allows_different_dropoff
        }
        
        if filename:
            car_params['attachments'] = filename
            car_query = """
                UPDATE Car SET model_id = :model_id, carType_id = :carType_id, rate = :rate,
                             description = :description, door = :door, suitcase = :suitcase, seat = :seat,
                             colour = :colour, attachments = :attachments,
                             pickup_location = :pickup_location, dropoff_location = :dropoff_location,
                             available_locations = :available_locations, allows_different_dropoff = :allows_different_dropoff
                WHERE car_id = :car_id
            """
        else:
            car_query = """
                UPDATE Car SET model_id = :model_id, carType_id = :carType_id, rate = :rate,
                             description = :description, door = :door, suitcase = :suitcase, seat = :seat,
                             colour = :colour,
                             pickup_location = :pickup_location, dropoff_location = :dropoff_location,
                             available_locations = :available_locations, allows_different_dropoff = :allows_different_dropoff
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
            fuel_tank = request.form.get('fuel_tank_capacity')
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
            fuel_tank = request.form.get('fuel_tank_capacity')
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
        return jsonify({'success': True, 'message': 'Brand added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
            SELECT m.model_id, m.model_name, b.brand_id, b.brand_name
            FROM Model m
            JOIN Brand b ON m.brand_id = b.brand_id
            ORDER BY b.brand_name, m.model_name
        """
        models = Database.execute_query(query)
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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

