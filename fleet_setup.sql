-- ============================================================================
-- FLEET INVENTORY SETUP - ALL MODELS WITH VARIETY OF LOCATIONS
-- Run this to set up fleet inventory with multiple cars per model
-- ============================================================================

-- ============================================================================
-- STEP 1: ADD LOCATION_ID TO CAR TABLE
-- ============================================================================
DECLARE
    col_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO col_exists FROM user_tab_columns 
    WHERE table_name = 'CAR' AND column_name = 'LOCATION_ID';
    IF col_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Car ADD location_id NUMBER';
        DBMS_OUTPUT.PUT_LINE('Added location_id to Car table.');
    END IF;
END;
/

DECLARE
    constraint_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO constraint_exists FROM user_constraints 
    WHERE table_name = 'CAR' AND constraint_name = 'FK_CAR_LOCATION';
    IF constraint_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Car ADD CONSTRAINT fk_car_location FOREIGN KEY (location_id) REFERENCES Location(location_id)';
    END IF;
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

COMMIT;

-- ============================================================================
-- STEP 2: DELETE OLD CAR DATA
-- ============================================================================
DELETE FROM Payment WHERE booking_id IN (SELECT booking_id FROM Booking);
DELETE FROM Booking;
DELETE FROM Electric;
DELETE FROM Diesel;
DELETE FROM Petrol;
DELETE FROM Car;
COMMIT;

-- ============================================================================
-- STEP 3: INSERT FLEET INVENTORY - ALL MODELS
-- ============================================================================

-- ============================================================================
-- TOYOTA CAMRY (Sedan) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 180.00, 'Comfortable sedan for city and highway', 4, 3, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Camry' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 180.00, 'Comfortable sedan for city and highway', 4, 3, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Camry' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 180.00, 'Comfortable sedan for city and highway', 4, 3, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Camry' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 180.00, 'Comfortable sedan for city and highway', 4, 3, 5, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 'Available', 'JB Sentral', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Camry' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- TOYOTA VIOS (Sedan) - 5 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 120.00, 'Fuel-efficient sedan for daily use', 4, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Vios' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 120.00, 'Fuel-efficient sedan for daily use', 4, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA2'), 'Available', 'KLIA2', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Vios' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 120.00, 'Fuel-efficient sedan for daily use', 4, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Mid Valley'), 'Available', 'Mid Valley', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Vios' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 120.00, 'Fuel-efficient sedan for daily use', 4, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'Georgetown'), 'Available', 'Georgetown', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Vios' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 120.00, 'Fuel-efficient sedan for daily use', 4, 2, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Ipoh'), 'Available', 'Ipoh', 'Perak'
FROM Model m, CarType ct WHERE m.model_name = 'Vios' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- TOYOTA FORTUNER (SUV) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 280.00, 'Powerful SUV for family trips', 4, 6, 7, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Fortuner' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 280.00, 'Powerful SUV for family trips', 4, 6, 7, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 'Available', 'JB Sentral', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Fortuner' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 280.00, 'Powerful SUV for family trips', 4, 6, 7, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Fortuner' AND ct.carType_name = 'SUV';

-- ============================================================================
-- TOYOTA HILUX (Pickup) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 250.00, 'Heavy-duty pickup truck', 4, 4, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Hilux' AND ct.carType_name = 'Pickup';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 250.00, 'Heavy-duty pickup truck', 4, 4, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 'Available', 'JB Sentral', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Hilux' AND ct.carType_name = 'Pickup';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 250.00, 'Heavy-duty pickup truck', 4, 4, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Melaka'), 'Available', 'Melaka', 'Melaka'
FROM Model m, CarType ct WHERE m.model_name = 'Hilux' AND ct.carType_name = 'Pickup';

-- ============================================================================
-- HONDA ACCORD (Sedan) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 200.00, 'Mid-size sedan with excellent comfort', 4, 3, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Accord' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 200.00, 'Mid-size sedan with excellent comfort', 4, 3, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Accord' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 200.00, 'Mid-size sedan with excellent comfort', 4, 3, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Accord' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- HONDA CIVIC (Sedan) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 150.00, 'Sporty sedan with dynamic performance', 4, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Civic' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 150.00, 'Sporty sedan with dynamic performance', 4, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Civic' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 150.00, 'Sporty sedan with dynamic performance', 4, 2, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Senai Airport'), 'Available', 'Senai Airport', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Civic' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 150.00, 'Sporty sedan with dynamic performance', 4, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'Georgetown'), 'Available', 'Georgetown', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Civic' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- HONDA CR-V (SUV) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 220.00, 'Spacious SUV with safety features', 4, 5, 7, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'CR-V' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 220.00, 'Spacious SUV with safety features', 4, 5, 7, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'CR-V' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 220.00, 'Spacious SUV with safety features', 4, 5, 7, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'Mid Valley'), 'Available', 'Mid Valley', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'CR-V' AND ct.carType_name = 'SUV';

-- ============================================================================
-- HONDA CITY (Sedan) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 130.00, 'Compact sedan perfect for city driving', 4, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'City' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 130.00, 'Compact sedan perfect for city driving', 4, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'City' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 130.00, 'Compact sedan perfect for city driving', 4, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'Subang Airport'), 'Available', 'Subang Airport', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'City' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 130.00, 'Compact sedan perfect for city driving', 4, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Ipoh'), 'Available', 'Ipoh', 'Perak'
FROM Model m, CarType ct WHERE m.model_name = 'City' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- PERODUA MYVI (Hatchback) - 6 locations (most popular)
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 80.00, 'Popular compact car for city driving', 5, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Myvi' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 80.00, 'Popular compact car for city driving', 5, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA2'), 'Available', 'KLIA2', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Myvi' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 80.00, 'Popular compact car for city driving', 5, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Myvi' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 80.00, 'Popular compact car for city driving', 5, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Myvi' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 80.00, 'Popular compact car for city driving', 5, 2, 5, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 'Available', 'JB Sentral', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Myvi' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 80.00, 'Popular compact car for city driving', 5, 2, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Ipoh'), 'Available', 'Ipoh', 'Perak'
FROM Model m, CarType ct WHERE m.model_name = 'Myvi' AND ct.carType_name = 'Hatchback';

-- ============================================================================
-- PERODUA AXIA (Hatchback) - 5 locations (budget option)
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 70.00, 'Budget-friendly compact car', 5, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA2'), 'Available', 'KLIA2', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Axia' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 70.00, 'Budget-friendly compact car', 5, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Axia' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 70.00, 'Budget-friendly compact car', 5, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'Cyberjaya'), 'Available', 'Cyberjaya', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Axia' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 70.00, 'Budget-friendly compact car', 5, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Melaka'), 'Available', 'Melaka', 'Melaka'
FROM Model m, CarType ct WHERE m.model_name = 'Axia' AND ct.carType_name = 'Hatchback';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 70.00, 'Budget-friendly compact car', 5, 2, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Senai Airport'), 'Available', 'Senai Airport', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Axia' AND ct.carType_name = 'Hatchback';

-- ============================================================================
-- PERODUA ARUZ (MPV) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 140.00, 'Spacious MPV for large families', 5, 4, 7, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Aruz' AND ct.carType_name = 'MPV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 140.00, 'Spacious MPV for large families', 5, 4, 7, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Shah Alam'), 'Available', 'Shah Alam', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Aruz' AND ct.carType_name = 'MPV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 140.00, 'Spacious MPV for large families', 5, 4, 7, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Aruz' AND ct.carType_name = 'MPV';

-- ============================================================================
-- PERODUA BEZZA (Sedan) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 90.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Bezza' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 90.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Bezza' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 90.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Georgetown'), 'Available', 'Georgetown', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'Bezza' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 90.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'Petaling Jaya'), 'Available', 'Petaling Jaya', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Bezza' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- PROTON X70 (SUV) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 190.00, 'Modern SUV with premium features', 4, 5, 7, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'X70' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 190.00, 'Modern SUV with premium features', 4, 5, 7, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Mid Valley'), 'Available', 'Mid Valley', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'X70' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 190.00, 'Modern SUV with premium features', 4, 5, 7, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 'Available', 'JB Sentral', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'X70' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 190.00, 'Modern SUV with premium features', 4, 5, 7, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'Putrajaya'), 'Available', 'Putrajaya', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'X70' AND ct.carType_name = 'SUV';

-- ============================================================================
-- PROTON X50 (SUV) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 160.00, 'Compact SUV for urban adventures', 4, 4, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'X50' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 160.00, 'Compact SUV for urban adventures', 4, 4, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 'Available', 'Bangsar', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'X50' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 160.00, 'Compact SUV for urban adventures', 4, 4, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 'Available', 'Penang Airport', 'Penang'
FROM Model m, CarType ct WHERE m.model_name = 'X50' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 160.00, 'Compact SUV for urban adventures', 4, 4, 5, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'Senai Airport'), 'Available', 'Senai Airport', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'X50' AND ct.carType_name = 'SUV';

-- ============================================================================
-- PROTON SAGA (Sedan) - 5 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 100.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Saga' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 100.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Saga' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 100.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA2'), 'Available', 'KLIA2', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Saga' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 100.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 'Available', 'JB Sentral', 'Johor'
FROM Model m, CarType ct WHERE m.model_name = 'Saga' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 100.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'Melaka'), 'Available', 'Melaka', 'Melaka'
FROM Model m, CarType ct WHERE m.model_name = 'Saga' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- PROTON PERSONA (Sedan) - 4 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 110.00, 'Comfortable sedan with modern features', 4, 2, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Persona' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 110.00, 'Comfortable sedan with modern features', 4, 2, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 'Available', 'KL Sentral', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Persona' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 110.00, 'Comfortable sedan with modern features', 4, 2, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Subang Airport'), 'Available', 'Subang Airport', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Persona' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 110.00, 'Comfortable sedan with modern features', 4, 2, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Ipoh'), 'Available', 'Ipoh', 'Perak'
FROM Model m, CarType ct WHERE m.model_name = 'Persona' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- BMW 3 SERIES (Luxury) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 400.00, 'Luxury sports sedan', 4, 3, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = '3 Series' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 400.00, 'Luxury sports sedan', 4, 3, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = '3 Series' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 400.00, 'Luxury sports sedan', 4, 3, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 'Available', 'Bangsar', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = '3 Series' AND ct.carType_name = 'Luxury';

-- ============================================================================
-- BMW 5 SERIES (Luxury) - 2 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 500.00, 'Executive sedan with premium features', 4, 4, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = '5 Series' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 500.00, 'Executive sedan with premium features', 4, 4, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = '5 Series' AND ct.carType_name = 'Luxury';

-- ============================================================================
-- BMW X3 (Luxury SUV) - 2 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 450.00, 'Luxury SUV with premium comfort', 4, 5, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'X3' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 450.00, 'Luxury SUV with premium comfort', 4, 5, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 'Available', 'Bangsar', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'X3' AND ct.carType_name = 'Luxury';

-- ============================================================================
-- MERCEDES C-CLASS (Luxury) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 450.00, 'Premium luxury sedan', 4, 4, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'C-Class' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 450.00, 'Premium luxury sedan', 4, 4, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 'Available', 'Bangsar', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'C-Class' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 450.00, 'Premium luxury sedan', 4, 4, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'C-Class' AND ct.carType_name = 'Luxury';

-- ============================================================================
-- MERCEDES E-CLASS (Luxury) - 2 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 550.00, 'Premium executive sedan', 4, 4, 5, 'Black',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'E-Class' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 550.00, 'Premium executive sedan', 4, 4, 5, 'Silver',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'E-Class' AND ct.carType_name = 'Luxury';

-- ============================================================================
-- MERCEDES GLC (Luxury SUV) - 2 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 480.00, 'Luxury SUV with spacious interior', 4, 5, 5, 'Grey',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'GLC' AND ct.carType_name = 'Luxury';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 480.00, 'Luxury SUV with spacious interior', 4, 5, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 'Available', 'Bangsar', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'GLC' AND ct.carType_name = 'Luxury';

-- ============================================================================
-- TESLA MODEL 3 (Sedan - Electric) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 300.00, 'Premium electric sedan', 4, 3, 5, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Model 3' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 300.00, 'Premium electric sedan', 4, 3, 5, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'Cyberjaya'), 'Available', 'Cyberjaya', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Model 3' AND ct.carType_name = 'Sedan';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 300.00, 'Premium electric sedan', 4, 3, 5, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 'Available', 'Pavilion KL', 'Kuala Lumpur'
FROM Model m, CarType ct WHERE m.model_name = 'Model 3' AND ct.carType_name = 'Sedan';

-- ============================================================================
-- TESLA MODEL Y (SUV - Electric) - 3 locations
-- ============================================================================
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 350.00, 'Electric SUV for families', 4, 4, 7, 'White',
       (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 'Available', 'KLIA', 'Kuala Lumpur, Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Model Y' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 350.00, 'Electric SUV for families', 4, 4, 7, 'Red',
       (SELECT location_id FROM Location WHERE location_name = 'Putrajaya'), 'Available', 'Putrajaya', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Model Y' AND ct.carType_name = 'SUV';

INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, car_status, pickup_location, available_locations)
SELECT m.model_id, ct.carType_id, 350.00, 'Electric SUV for families', 4, 4, 7, 'Blue',
       (SELECT location_id FROM Location WHERE location_name = 'Cyberjaya'), 'Available', 'Cyberjaya', 'Selangor'
FROM Model m, CarType ct WHERE m.model_name = 'Model Y' AND ct.carType_name = 'SUV';

COMMIT;

-- ============================================================================
-- STEP 4: ADD FUEL TYPE DATA
-- ============================================================================

-- Petrol cars (Toyota, Honda, Perodua, Proton, BMW, Mercedes)
INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity)
SELECT car_id, 95, 50 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN Brand b ON m.brand_id = b.brand_id
WHERE b.brand_name IN ('Toyota', 'Honda', 'Perodua', 'Proton', 'BMW', 'Mercedes-Benz')
AND NOT EXISTS (SELECT 1 FROM Petrol WHERE car_id = c.car_id);

-- Electric cars (Tesla)
INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date)
SELECT car_id, 450, 250, SYSDATE FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN Brand b ON m.brand_id = b.brand_id
WHERE b.brand_name = 'Tesla'
AND NOT EXISTS (SELECT 1 FROM Electric WHERE car_id = c.car_id);

COMMIT;

-- ============================================================================
-- STEP 5: CREATE INDEX
-- ============================================================================
BEGIN
    EXECUTE IMMEDIATE 'CREATE INDEX idx_car_location ON Car(location_id)';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
SELECT '=== FLEET SUMMARY ===' as info FROM dual;
SELECT 'Total Cars: ' || COUNT(*) as result FROM Car;

SELECT '=== CARS BY MODEL ===' as info FROM dual;
SELECT b.brand_name || ' ' || m.model_name as model, COUNT(c.car_id) as units
FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN Brand b ON m.brand_id = b.brand_id
GROUP BY b.brand_name, m.model_name
ORDER BY b.brand_name, m.model_name;

SELECT '=== CARS BY LOCATION ===' as info FROM dual;
SELECT l.location_name, COUNT(c.car_id) as car_count 
FROM Location l 
LEFT JOIN Car c ON l.location_id = c.location_id 
GROUP BY l.location_name 
HAVING COUNT(c.car_id) > 0
ORDER BY car_count DESC;
