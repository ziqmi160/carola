# Carola Car Rental Website

A fully functional car rental website built with Flask and Oracle Database. This application provides complete functionality from user registration to booking management and payment processing.

## Features

- **User Authentication**
  - Customer registration and login
  - Staff login
  - Session management

- **Car Browsing**
  - Browse available cars with filters
  - Filter by location, car type, brand, and price range
  - View detailed car information including specifications

- **Booking System**
  - Create bookings with pickup/drop-off dates and locations
  - Automatic price calculation based on rental period
  - Conflict detection (prevents double booking)
  - View booking history

- **Payment Processing**
  - Process payments for bookings
  - Payment status tracking

- **Admin Dashboard**
  - Staff can view all bookings
  - Customer information display
  - Payment status monitoring

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: Oracle Database
- **Frontend**: HTML5, CSS3, JavaScript
- **Database Driver**: oracledb

## Prerequisites

1. Python 3.8 or higher
2. Oracle Database (with SQL Developer)
3. Oracle Instant Client (for oracledb)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Oracle Database Setup

1. Open SQL Developer and connect to your Oracle database using:
   - Username: `carola`
   - Password: `carola`
   - Hostname: `localhost`
   - Port: `1521`
   - Service Name: `FREEPDB1`

2. Run the SQL scripts in order:
   ```sql
   -- First, create tables
   @tablebaru.sql
   
   -- Then, insert sample data
   @databaru.sql
   ```

   Or copy and paste the contents of `tablebaru.sql` and `databaru.sql` into SQL Developer and execute them.

### 3. Configure Database Connection

The database configuration is in `config.py`. Default settings:
- User: `carola`
- Password: `carola`
- DSN: `localhost:1521/FREEPDB1`

If your database settings differ, update `config.py` accordingly.

### 4. Install Oracle Instant Client

Download and install Oracle Instant Client from Oracle's website:
- Windows: https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html
- Extract to a folder and add to PATH

Alternatively, if you have Oracle Database installed, the client libraries should already be available.

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### For Customers

1. **Register**: Create a new account at `/register`
2. **Login**: Login with your credentials at `/login`
3. **Browse Cars**: View available cars at `/cars`
4. **Book a Car**: Click "Book Now" on any car, select dates and locations
5. **Make Payment**: Go to "My Bookings" and click "Pay Now" for pending bookings
6. **View Bookings**: Check your booking history at `/my-bookings`

### For Staff

1. **Login**: Use staff credentials at `/login` (select "Staff" as user type)
2. **Dashboard**: View all bookings at `/admin`
3. **Monitor**: Track customer bookings and payment status

### Sample Credentials

**Customers:**
- Username: `ahmadi`, Password: `password123`
- Username: `sitia`, Password: `password123`
- Username: `limwm`, Password: `password123`

**Staff:**
- Username: `nurulh`, Password: `staff123`
- Username: `rajk`, Password: `staff123`
- Username: `chanly`, Password: `staff123`

## Project Structure

```
carolascratch/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── db.py                  # Database connection module
├── requirements.txt       # Python dependencies
├── tablebaru.sql          # Database schema
├── databaru.sql           # Sample data
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── cars.html
│   ├── booking.html
│   ├── my_bookings.html
│   └── admin.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── uploads/           # Car images (optional)
```

## Database Schema

The application uses the following main tables:
- `Customer` - Customer information
- `Staff` - Staff information
- `Brand` - Car brands
- `Model` - Car models
- `CarType` - Car types (Sedan, SUV, etc.)
- `Car` - Car inventory with location details
- `Petrol`, `Diesel`, `Electric` - Car fuel type subtypes
- `Booking` - Booking records
- `Payment` - Payment records

## Features in Detail

### Car Filtering
- Filter by location (e.g., Kuala Lumpur, Penang)
- Filter by car type (Sedan, SUV, Hatchback, etc.)
- Filter by brand (Toyota, Honda, etc.)
- Filter by price range

### Booking System
- Automatic conflict detection
- Price calculation based on daily rate and number of days
- Support for different pickup and drop-off locations (when allowed)
- Date validation

### Payment System
- One-to-one relationship with bookings
- Payment status tracking
- Automatic payment date recording

## Troubleshooting

### Database Connection Issues

If you encounter connection errors:
1. Verify Oracle Database is running
2. Check connection details in `config.py`
3. Ensure Oracle Instant Client is installed and in PATH
4. Verify the service name is correct (FREEPDB1)

### Port Already in Use

If port 5000 is already in use:
- Change the port in `app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

### Oracle Client Library Not Found

Install Oracle Instant Client and ensure it's in your system PATH, or set the library path:
```python
import oracledb
oracledb.init_oracle_client(lib_dir=r"C:\path\to\instantclient")
```

## Development

To run in development mode with auto-reload:
```bash
python app.py
```

The application runs in debug mode by default, which enables:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

## Security Notes

⚠️ **Important**: This is a development application. For production use:
- Change the secret key in `app.py`
- Implement proper password hashing (bcrypt, etc.)
- Use HTTPS
- Add input validation and sanitization
- Implement CSRF protection
- Use environment variables for sensitive configuration

## License

This project is created for educational purposes.

## Support

For issues or questions, please check:
1. Database connection settings
2. SQL scripts execution
3. Python dependencies installation
4. Oracle Instant Client installation

---

**Enjoy renting cars with Carola! 🚗**

