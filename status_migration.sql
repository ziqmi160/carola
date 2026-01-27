-- ============================================================================
-- STATUS TRACKING MIGRATION SCRIPT (IDEMPOTENT - Safe to run multiple times)
-- Adds status fields to Car and Booking tables
-- ============================================================================

-- ============================================================================
-- STEP 1: ADD CAR STATUS COLUMN (if not exists)
-- ============================================================================
DECLARE
    col_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO col_exists FROM user_tab_columns 
    WHERE table_name = 'CAR' AND column_name = 'CAR_STATUS';
    IF col_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Car ADD car_status VARCHAR2(20) DEFAULT ''Available''';
        DBMS_OUTPUT.PUT_LINE('Added car_status column.');
    ELSE
        DBMS_OUTPUT.PUT_LINE('car_status column already exists.');
    END IF;
END;
/

-- Add constraint (if not exists)
DECLARE
    constraint_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO constraint_exists FROM user_constraints 
    WHERE constraint_name = 'CHK_CAR_STATUS';
    IF constraint_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Car ADD CONSTRAINT chk_car_status CHECK (car_status IN (''Available'', ''Rented'', ''Maintenance'', ''Dirty''))';
        DBMS_OUTPUT.PUT_LINE('Added car_status constraint.');
    END IF;
END;
/

-- ============================================================================
-- STEP 2: ADD BOOKING STATUS COLUMN (if not exists)
-- ============================================================================
DECLARE
    col_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO col_exists FROM user_tab_columns 
    WHERE table_name = 'BOOKING' AND column_name = 'BOOKING_STATUS';
    IF col_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Booking ADD booking_status VARCHAR2(20) DEFAULT ''Confirmed''';
        DBMS_OUTPUT.PUT_LINE('Added booking_status column.');
    ELSE
        DBMS_OUTPUT.PUT_LINE('booking_status column already exists.');
    END IF;
    
    SELECT COUNT(*) INTO col_exists FROM user_tab_columns 
    WHERE table_name = 'BOOKING' AND column_name = 'CREATED_AT';
    IF col_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Booking ADD created_at DATE DEFAULT SYSDATE';
        DBMS_OUTPUT.PUT_LINE('Added created_at column.');
    END IF;
END;
/

-- Add constraint (if not exists)
DECLARE
    constraint_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO constraint_exists FROM user_constraints 
    WHERE constraint_name = 'CHK_BOOKING_STATUS';
    IF constraint_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Booking ADD CONSTRAINT chk_booking_status CHECK (booking_status IN (''Confirmed'', ''In Progress'', ''Completed'', ''Cancelled''))';
        DBMS_OUTPUT.PUT_LINE('Added booking_status constraint.');
    END IF;
END;
/

COMMIT;

-- ============================================================================
-- STEP 3: UPDATE EXISTING DATA (safe to run multiple times)
-- ============================================================================

-- Update cars with active bookings to 'Rented'
UPDATE Car c
SET car_status = 'Rented'
WHERE car_status = 'Available'
AND EXISTS (
    SELECT 1 FROM Booking b 
    WHERE b.car_id = c.car_id 
    AND TRUNC(SYSDATE) BETWEEN TRUNC(b.pickup_date) AND TRUNC(b.dropoff_date)
    AND NVL(b.booking_status, 'Confirmed') IN ('Confirmed', 'In Progress')
);

-- Update completed bookings
UPDATE Booking b
SET booking_status = 'Completed'
WHERE TRUNC(b.dropoff_date) < TRUNC(SYSDATE)
AND EXISTS (SELECT 1 FROM Payment p WHERE p.booking_id = b.booking_id)
AND NVL(booking_status, 'Confirmed') NOT IN ('Completed', 'Cancelled');

-- Update in-progress bookings
UPDATE Booking b
SET booking_status = 'In Progress'
WHERE TRUNC(SYSDATE) BETWEEN TRUNC(b.pickup_date) AND TRUNC(b.dropoff_date)
AND NVL(booking_status, 'Confirmed') NOT IN ('Completed', 'Cancelled', 'In Progress');

COMMIT;

-- ============================================================================
-- STEP 4: CREATE INDEXES (if not exist)
-- ============================================================================
DECLARE
    idx_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO idx_exists FROM user_indexes WHERE index_name = 'IDX_CAR_STATUS';
    IF idx_exists = 0 THEN
        EXECUTE IMMEDIATE 'CREATE INDEX idx_car_status ON Car(car_status)';
        DBMS_OUTPUT.PUT_LINE('Created idx_car_status.');
    END IF;
    
    SELECT COUNT(*) INTO idx_exists FROM user_indexes WHERE index_name = 'IDX_BOOKING_STATUS';
    IF idx_exists = 0 THEN
        EXECUTE IMMEDIATE 'CREATE INDEX idx_booking_status ON Booking(booking_status)';
        DBMS_OUTPUT.PUT_LINE('Created idx_booking_status.');
    END IF;
    
    SELECT COUNT(*) INTO idx_exists FROM user_indexes WHERE index_name = 'IDX_BOOKING_CREATED_AT';
    IF idx_exists = 0 THEN
        EXECUTE IMMEDIATE 'CREATE INDEX idx_booking_created_at ON Booking(created_at)';
        DBMS_OUTPUT.PUT_LINE('Created idx_booking_created_at.');
    END IF;
END;
/

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
SELECT 'Car status distribution:' as info FROM dual;
SELECT NVL(car_status, 'NULL') as status, COUNT(*) as count FROM Car GROUP BY car_status;

SELECT 'Booking status distribution:' as info FROM dual;
SELECT NVL(booking_status, 'NULL') as status, COUNT(*) as count FROM Booking GROUP BY booking_status;
