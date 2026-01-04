# Quick Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Setup Oracle Database

1. Open SQL Developer
2. Connect to your database:
   - Username: `carola`
   - Password: `carola`
   - Hostname: `localhost`
   - Port: `1521`
   - Service Name: `FREEPDB1`

3. Run the SQL scripts:
   - Open `tablebaru.sql` and execute it (creates all tables)
   - Open `databaru.sql` and execute it (inserts sample data)

## Step 3: Install Oracle Instant Client (if needed)

If you get Oracle client library errors:
- Download Oracle Instant Client from Oracle website
- Extract and add to PATH, or set in code:
  ```python
  import oracledb
  oracledb.init_oracle_client(lib_dir=r"C:\path\to\instantclient")
  ```

## Step 4: Run the Application

**Option 1: Using the batch file (Windows)**
```bash
start.bat
```

**Option 2: Direct Python command**
```bash
python app.py
```

## Step 5: Access the Website

Open your browser and go to:
```
http://localhost:5000
```

## Testing the Application

### Test Customer Account
- Username: `ahmadi`
- Password: `password123`

### Test Staff Account
- Username: `nurulh`
- Password: `staff123`

## Features to Test

1. **Registration**: Create a new customer account
2. **Browse Cars**: Filter by location, type, brand, price
3. **Book a Car**: Select dates and locations
4. **Make Payment**: Process payment for bookings
5. **View Bookings**: Check booking history
6. **Admin Dashboard**: Login as staff to view all bookings

## Troubleshooting

### Database Connection Error
- Verify Oracle Database is running
- Check connection details in `config.py`
- Ensure service name is correct (FREEPDB1)

### Port Already in Use
- Change port in `app.py` (line 414): `port=5001`

### Module Not Found
- Run: `pip install -r requirements.txt`

### Oracle Client Not Found
- Install Oracle Instant Client
- Or use full Oracle Database installation

## Next Steps

1. Add car images to `static/uploads/` folder
2. Update car records with image filenames in the `attachments` column
3. Customize the UI colors in `static/css/style.css`
4. Add more features as needed

---

**Ready to rent! 🚗**

