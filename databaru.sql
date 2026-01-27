-- ============================================================================
-- SAMPLE DATA FOR CAROLA CAR RENTAL DATABASE - MALAYSIA
-- Run this AFTER creating the tables (tablebaru.sql)
-- Realistic combinations only - 7 brands, 20-30 cars
-- ============================================================================

-- ============================================================================
-- CLEAR EXISTING DATA (except Staff and Customer)
-- Delete in reverse order of dependencies
-- ============================================================================
DELETE FROM Payment;
DELETE FROM Booking;
DELETE FROM Electric;
DELETE FROM Diesel;
DELETE FROM Petrol;
DELETE FROM Car;
DELETE FROM Model;
DELETE FROM CarType;
DELETE FROM Brand;
DELETE FROM Location;

COMMIT;

-- ============================================================================
-- INSERT LOCATIONS (Based on car pickup/dropoff locations)
-- ============================================================================

-- Airports (24-hour service)
INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('KLIA', 'KL International Airport, Departure Hall Level 3', 'Sepang', 'Selangor', '64000', '+60-3-8787-3000', 'klia@carola.my', '00:00', '23:59', 1);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('KLIA2', 'KL International Airport 2, Arrival Hall', 'Sepang', 'Selangor', '64000', '+60-3-8787-4000', 'klia2@carola.my', '00:00', '23:59', 1);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Subang Airport', 'Sultan Abdul Aziz Shah Airport', 'Subang', 'Selangor', '47200', '+60-3-7846-7890', 'subang@carola.my', '06:00', '23:00', 1);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Penang Airport', 'Penang International Airport, Arrival Hall', 'Bayan Lepas', 'Penang', '11900', '+60-4-643-4411', 'penang@carola.my', '00:00', '23:59', 1);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Senai Airport', 'Senai International Airport, Arrival Hall', 'Senai', 'Johor', '81250', '+60-7-599-4500', 'senai@carola.my', '00:00', '23:59', 1);

-- Kuala Lumpur & Selangor
INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('KL Sentral', 'Stesen Sentral Kuala Lumpur, Level G', 'Kuala Lumpur', 'Wilayah Persekutuan', '50470', '+60-3-2260-1000', 'klsentral@carola.my', '07:00', '23:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Mid Valley', 'Mid Valley Megamall, Basement 2', 'Kuala Lumpur', 'Wilayah Persekutuan', '59200', '+60-3-2938-3333', 'midvalley@carola.my', '10:00', '22:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Pavilion KL', 'Pavilion Kuala Lumpur, Level B2', 'Kuala Lumpur', 'Wilayah Persekutuan', '55100', '+60-3-2118-8833', 'pavilion@carola.my', '10:00', '22:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Bangsar', 'Bangsar Village II, Ground Floor', 'Kuala Lumpur', 'Wilayah Persekutuan', '59100', '+60-3-2282-1808', 'bangsar@carola.my', '10:00', '22:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Cyberjaya', 'D''Pulze Shopping Centre', 'Cyberjaya', 'Selangor', '63000', '+60-3-8320-8888', 'cyberjaya@carola.my', '10:00', '22:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Putrajaya', 'IOI City Mall, Level LG', 'Putrajaya', 'Wilayah Persekutuan', '62502', '+60-3-8328-8888', 'putrajaya@carola.my', '10:00', '22:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Petaling Jaya', 'Jaya One, Jalan Universiti', 'Petaling Jaya', 'Selangor', '46200', '+60-3-7960-0288', 'pj@carola.my', '09:00', '21:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Shah Alam', 'SACC Mall, Seksyen 7', 'Shah Alam', 'Selangor', '40000', '+60-3-5510-6868', 'shahalam@carola.my', '10:00', '22:00', 0);

-- Penang
INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Georgetown', 'Komtar, Level 3', 'Georgetown', 'Penang', '10000', '+60-4-262-6262', 'georgetown@carola.my', '10:00', '22:00', 0);

-- Johor
INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('JB Sentral', 'JB Sentral, Ground Floor', 'Johor Bahru', 'Johor', '80000', '+60-7-226-6666', 'jbsentral@carola.my', '06:00', '23:00', 0);

-- Other States
INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Ipoh', 'Ipoh Parade, Ground Floor', 'Ipoh', 'Perak', '30000', '+60-5-255-8888', 'ipoh@carola.my', '10:00', '22:00', 0);

INSERT INTO Location (location_name, address, city, state, postal_code, phone, email, opening_time, closing_time, is_airport)
VALUES ('Melaka', 'Dataran Pahlawan, Level G', 'Melaka', 'Melaka', '75000', '+60-6-282-8888', 'melaka@carola.my', '10:00', '22:00', 0);

COMMIT;

-- ============================================================================
-- INSERT BRANDS (7 brands only)
-- ============================================================================
INSERT INTO Brand (brand_name) VALUES ('Toyota');
INSERT INTO Brand (brand_name) VALUES ('Honda');
INSERT INTO Brand (brand_name) VALUES ('Perodua');
INSERT INTO Brand (brand_name) VALUES ('Proton');
INSERT INTO Brand (brand_name) VALUES ('BMW');
INSERT INTO Brand (brand_name) VALUES ('Mercedes-Benz');
INSERT INTO Brand (brand_name) VALUES ('Tesla');

COMMIT;

-- ============================================================================
-- INSERT MODELS (using subqueries to find brand_id by name)
-- ============================================================================
-- Toyota Models
INSERT INTO Model (model_name, brand_id) SELECT 'Camry', brand_id FROM Brand WHERE brand_name = 'Toyota';
INSERT INTO Model (model_name, brand_id) SELECT 'Vios', brand_id FROM Brand WHERE brand_name = 'Toyota';
INSERT INTO Model (model_name, brand_id) SELECT 'Fortuner', brand_id FROM Brand WHERE brand_name = 'Toyota';
INSERT INTO Model (model_name, brand_id) SELECT 'Hilux', brand_id FROM Brand WHERE brand_name = 'Toyota';

-- Honda Models
INSERT INTO Model (model_name, brand_id) SELECT 'Accord', brand_id FROM Brand WHERE brand_name = 'Honda';
INSERT INTO Model (model_name, brand_id) SELECT 'Civic', brand_id FROM Brand WHERE brand_name = 'Honda';
INSERT INTO Model (model_name, brand_id) SELECT 'CR-V', brand_id FROM Brand WHERE brand_name = 'Honda';
INSERT INTO Model (model_name, brand_id) SELECT 'City', brand_id FROM Brand WHERE brand_name = 'Honda';

-- Perodua Models
INSERT INTO Model (model_name, brand_id) SELECT 'Myvi', brand_id FROM Brand WHERE brand_name = 'Perodua';
INSERT INTO Model (model_name, brand_id) SELECT 'Axia', brand_id FROM Brand WHERE brand_name = 'Perodua';
INSERT INTO Model (model_name, brand_id) SELECT 'Aruz', brand_id FROM Brand WHERE brand_name = 'Perodua';
INSERT INTO Model (model_name, brand_id) SELECT 'Bezza', brand_id FROM Brand WHERE brand_name = 'Perodua';

-- Proton Models
INSERT INTO Model (model_name, brand_id) SELECT 'X70', brand_id FROM Brand WHERE brand_name = 'Proton';
INSERT INTO Model (model_name, brand_id) SELECT 'X50', brand_id FROM Brand WHERE brand_name = 'Proton';
INSERT INTO Model (model_name, brand_id) SELECT 'Saga', brand_id FROM Brand WHERE brand_name = 'Proton';
INSERT INTO Model (model_name, brand_id) SELECT 'Persona', brand_id FROM Brand WHERE brand_name = 'Proton';

-- BMW Models
INSERT INTO Model (model_name, brand_id) SELECT '3 Series', brand_id FROM Brand WHERE brand_name = 'BMW';
INSERT INTO Model (model_name, brand_id) SELECT '5 Series', brand_id FROM Brand WHERE brand_name = 'BMW';
INSERT INTO Model (model_name, brand_id) SELECT 'X3', brand_id FROM Brand WHERE brand_name = 'BMW';

-- Mercedes-Benz Models
INSERT INTO Model (model_name, brand_id) SELECT 'C-Class', brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz';
INSERT INTO Model (model_name, brand_id) SELECT 'E-Class', brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz';
INSERT INTO Model (model_name, brand_id) SELECT 'GLC', brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz';

-- Tesla Models
INSERT INTO Model (model_name, brand_id) SELECT 'Model 3', brand_id FROM Brand WHERE brand_name = 'Tesla';
INSERT INTO Model (model_name, brand_id) SELECT 'Model Y', brand_id FROM Brand WHERE brand_name = 'Tesla';

COMMIT;

-- ============================================================================
-- INSERT CARTYPES
-- ============================================================================
INSERT INTO CarType (carType_name, carType_description) VALUES ('Sedan', 'Four-door passenger car');
INSERT INTO CarType (carType_name, carType_description) VALUES ('SUV', 'Sport Utility Vehicle');
INSERT INTO CarType (carType_name, carType_description) VALUES ('Hatchback', 'Compact car with rear door');
INSERT INTO CarType (carType_name, carType_description) VALUES ('MPV', 'Multi-Purpose Vehicle');
INSERT INTO CarType (carType_name, carType_description) VALUES ('Pickup', 'Pickup truck');
INSERT INTO CarType (carType_name, carType_description) VALUES ('Luxury', 'Premium comfort vehicle');

COMMIT;

-- ============================================================================
-- INSERT CARS (Using location_id foreign key)
-- Each row = one physical car unit at a specific location
-- ============================================================================

-- TOYOTA CARS
-- Petrol Sedan - Camry at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 180.00, 'Comfortable and reliable sedan perfect for city and highway driving', 4, 3, 5, 'Silver', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Camry' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'Sedan';

-- Petrol Sedan - Vios at KL Sentral
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 120.00, 'Fuel-efficient sedan ideal for daily commutes and city driving', 4, 2, 5, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Vios' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'Sedan';

-- Petrol SUV - Fortuner at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 280.00, 'Powerful SUV perfect for family trips and off-road adventures', 4, 6, 7, 'Black', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Fortuner' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'SUV';

-- Diesel SUV - Fortuner at Penang Airport
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 290.00, 'Diesel-powered SUV with excellent fuel economy for long journeys', 4, 6, 7, 'Grey', 
        (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Fortuner' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'SUV';

-- Diesel Pickup - Hilux at JB Sentral
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 250.00, 'Heavy-duty pickup truck with excellent towing capacity', 4, 4, 5, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Hilux' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'Pickup';

-- HONDA CARS
-- Petrol Sedan - Accord at Georgetown
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 200.00, 'Mid-size sedan with excellent comfort and reliability', 4, 3, 5, 'Black', 
        (SELECT location_id FROM Location WHERE location_name = 'Georgetown'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Accord' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan';

-- Petrol Sedan - Civic at Penang Airport
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 150.00, 'Sporty sedan with dynamic performance', 4, 2, 5, 'Red', 
        (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Civic' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan';

-- Petrol Sedan - City at KL Sentral
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 130.00, 'Compact sedan perfect for city driving', 4, 2, 5, 'Blue', 
        (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'City' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan';

-- Diesel SUV - CR-V at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 220.00, 'Spacious SUV with advanced safety features', 4, 5, 7, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'CR-V' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'SUV';

-- Electric Sedan - Civic Electric at Cyberjaya
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 180.00, 'Electric sedan with zero emissions and smooth driving', 4, 2, 5, 'Blue', 
        (SELECT location_id FROM Location WHERE location_name = 'Cyberjaya'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Civic' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan';

-- PERODUA CARS
-- Petrol Hatchback - Myvi at Subang Airport
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 80.00, 'Popular Malaysian compact car, perfect for city navigation', 5, 2, 5, 'Red', 
        (SELECT location_id FROM Location WHERE location_name = 'Subang Airport'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Myvi' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'Hatchback';

-- Petrol Hatchback - Axia at KLIA2
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 70.00, 'Budget-friendly compact car for economical travel', 5, 2, 5, 'Blue', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA2'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Axia' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'Hatchback';

-- Petrol Sedan - Bezza at KL Sentral
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 90.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Silver', 
        (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Bezza' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'Sedan';

-- Petrol MPV - Aruz at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 140.00, 'Spacious MPV perfect for large families', 5, 4, 7, 'Silver', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Aruz' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'MPV';

-- Diesel MPV - Aruz at Penang Airport
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 150.00, 'Diesel MPV with excellent fuel efficiency for long trips', 5, 4, 7, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'Penang Airport'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Aruz' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'MPV';

-- PROTON CARS
-- Petrol SUV - X70 at Senai Airport
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 190.00, 'Modern Malaysian SUV with premium features', 4, 5, 7, 'Grey', 
        (SELECT location_id FROM Location WHERE location_name = 'Senai Airport'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'X70' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'SUV';

-- Petrol SUV - X50 at JB Sentral
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 160.00, 'Compact SUV perfect for urban adventures', 4, 4, 5, 'Blue', 
        (SELECT location_id FROM Location WHERE location_name = 'JB Sentral'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'X50' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'SUV';

-- Petrol Sedan - Saga at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 100.00, 'Affordable sedan with reliable performance', 4, 2, 5, 'Red', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Saga' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'Sedan';

-- Petrol Sedan - Persona at KL Sentral
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 110.00, 'Comfortable sedan with modern features', 4, 2, 5, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'KL Sentral'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Persona' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'Sedan';

-- Diesel SUV - X70 at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 200.00, 'Diesel SUV with powerful engine and great mileage', 4, 5, 7, 'Black', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'X70' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'SUV';

-- BMW CARS
-- Petrol Luxury Sedan - 3 Series at Pavilion KL
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 400.00, 'Luxury sports sedan with dynamic performance', 4, 3, 5, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 0
FROM Model m, CarType ct
WHERE m.model_name = '3 Series' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury';

-- Petrol Luxury Sedan - 5 Series at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 500.00, 'Executive sedan with premium features', 4, 4, 5, 'Black', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 0
FROM Model m, CarType ct
WHERE m.model_name = '5 Series' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury';

-- Diesel Luxury Sedan - 3 Series at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 420.00, 'Diesel luxury sedan with exceptional fuel economy', 4, 3, 5, 'Silver', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = '3 Series' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury';

-- Petrol Luxury SUV - X3 at Bangsar
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 450.00, 'Luxury SUV with premium comfort and technology', 4, 5, 5, 'Blue', 
        (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'X3' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury';

-- MERCEDES-BENZ CARS
-- Petrol Luxury Sedan - C-Class at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 450.00, 'Luxury sedan with cutting-edge technology', 4, 4, 5, 'Silver', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'C-Class' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury';

-- Petrol Luxury Sedan - E-Class at Pavilion KL
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 550.00, 'Premium executive sedan with ultimate comfort', 4, 4, 5, 'Black', 
        (SELECT location_id FROM Location WHERE location_name = 'Pavilion KL'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'E-Class' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury';

-- Diesel Luxury Sedan - C-Class at Mid Valley
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 470.00, 'Diesel luxury sedan with superior performance', 4, 4, 5, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'Mid Valley'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'C-Class' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury';

-- Petrol Luxury SUV - GLC at Bangsar
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 480.00, 'Luxury SUV with spacious interior and premium features', 4, 5, 5, 'Grey', 
        (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'GLC' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury';

-- TESLA CARS (Electric ONLY)
-- Electric Sedan - Model 3 at KLIA
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 300.00, 'Premium electric sedan with impressive range and technology', 4, 3, 5, 'Blue', 
        (SELECT location_id FROM Location WHERE location_name = 'KLIA'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Model 3' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Tesla')
  AND ct.carType_name = 'Sedan';

-- Electric SUV - Model Y at Cyberjaya
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 350.00, 'Versatile electric SUV perfect for eco-conscious families', 4, 4, 7, 'White', 
        (SELECT location_id FROM Location WHERE location_name = 'Cyberjaya'), 1
FROM Model m, CarType ct
WHERE m.model_name = 'Model Y' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Tesla')
  AND ct.carType_name = 'SUV';

-- Electric Luxury Sedan - Model 3 at Bangsar
INSERT INTO Car (model_id, carType_id, rate, description, door, suitcase, seat, colour, location_id, allows_different_dropoff) 
SELECT m.model_id, ct.carType_id, 380.00, 'Luxury electric sedan with premium features', 4, 3, 5, 'Red', 
        (SELECT location_id FROM Location WHERE location_name = 'Bangsar'), 0
FROM Model m, CarType ct
WHERE m.model_name = 'Model 3' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Tesla')
  AND ct.carType_name = 'Luxury';

COMMIT;

-- ============================================================================
-- INSERT FUEL TYPE DATA
-- Using subqueries to match cars by model, carType, and rate
-- ============================================================================

-- Petrol Cars
INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 60 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Camry' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'Sedan' AND c.rate = 180.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 92, 50 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Vios' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'Sedan' AND c.rate = 120.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 70 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Fortuner' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'SUV' AND c.rate = 280.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 60 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Accord' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan' AND c.rate = 200.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 55 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Civic' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan' AND c.rate = 150.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 50 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'City' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan' AND c.rate = 130.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 40 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Myvi' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'Hatchback' AND c.rate = 80.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 92, 35 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Axia' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'Hatchback' AND c.rate = 70.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 50 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Bezza' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'Sedan' AND c.rate = 90.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 50 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Aruz' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'MPV' AND c.rate = 140.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 60 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'X70' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'SUV' AND c.rate = 190.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 52 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'X50' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'SUV' AND c.rate = 160.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 92, 45 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Saga' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'Sedan' AND c.rate = 100.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 95, 48 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Persona' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'Sedan' AND c.rate = 110.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 98, 65 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = '3 Series' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury' AND c.rate = 400.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 98, 70 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = '5 Series' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury' AND c.rate = 500.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 98, 68 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'X3' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury' AND c.rate = 450.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 98, 65 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'C-Class' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury' AND c.rate = 450.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 98, 70 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'E-Class' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury' AND c.rate = 550.00;

INSERT INTO Petrol (car_id, octane_rating, fuel_tank_capacity) 
SELECT car_id, 98, 72 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'GLC' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury' AND c.rate = 480.00;

-- Diesel Cars
INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 6', 70 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Fortuner' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'SUV' AND c.rate = 290.00;

INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 5', 90 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Hilux' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Toyota')
  AND ct.carType_name = 'Pickup' AND c.rate = 250.00;

INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 6', 60 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'CR-V' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'SUV' AND c.rate = 220.00;

INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 5', 55 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Aruz' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND ct.carType_name = 'MPV' AND c.rate = 150.00;

INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 5', 75 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'X70' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Proton')
  AND ct.carType_name = 'SUV' AND c.rate = 200.00;

INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 6', 65 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = '3 Series' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'BMW')
  AND ct.carType_name = 'Luxury' AND c.rate = 420.00;

INSERT INTO Diesel (car_id, diesel_emission, fuel_tank_capacity) 
SELECT car_id, 'Euro 6', 68 FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'C-Class' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Mercedes-Benz')
  AND ct.carType_name = 'Luxury' AND c.rate = 470.00;

-- Electric Cars (NO Petrol Tesla, NO Electric Myvi)
INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date) 
SELECT car_id, 400, 200, TO_DATE('2026-01-03', 'YYYY-MM-DD') FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Civic' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Honda')
  AND ct.carType_name = 'Sedan' AND c.rate = 180.00 AND c.description LIKE '%Electric%';

INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date) 
SELECT car_id, 450, 250, TO_DATE('2026-01-03', 'YYYY-MM-DD') FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Model 3' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Tesla')
  AND ct.carType_name = 'Sedan' AND c.rate = 300.00;

INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date) 
SELECT car_id, 500, 250, TO_DATE('2026-01-03', 'YYYY-MM-DD') FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Model Y' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Tesla')
  AND ct.carType_name = 'SUV' AND c.rate = 350.00;

INSERT INTO Electric (car_id, battery_range, charging_rate_kw, last_charging_date) 
SELECT car_id, 480, 250, TO_DATE('2026-01-03', 'YYYY-MM-DD') FROM Car c
JOIN Model m ON c.model_id = m.model_id
JOIN CarType ct ON c.carType_id = ct.carType_id
WHERE m.model_name = 'Model 3' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Tesla')
  AND ct.carType_name = 'Luxury' AND c.rate = 380.00;

-- ============================================================================
-- INSERT SAMPLE BOOKINGS AND PAYMENTS
-- ============================================================================

-- Note: This assumes you have at least one Customer and one Staff in the database
-- If not, you'll need to add them first

-- Get first customer and staff IDs (assuming they exist)
-- Insert sample bookings using location_id foreign keys
INSERT INTO Booking (cust_id, staff_id, car_id, pickup_date, dropoff_date, pickup_location_id, dropoff_location_id, price)
SELECT 
    (SELECT MIN(cust_id) FROM Customer) as cust_id,
    (SELECT MIN(staff_id) FROM Staff) as staff_id,
    c.car_id,
    TO_DATE('2026-01-08', 'YYYY-MM-DD') as pickup_date,
    TO_DATE('2026-01-13', 'YYYY-MM-DD') as dropoff_date,
    (SELECT location_id FROM Location WHERE location_name = 'KL Sentral') as pickup_location_id,
    (SELECT location_id FROM Location WHERE location_name = 'KL Sentral') as dropoff_location_id,
    c.rate * 5 as price
FROM Car c
JOIN Model m ON c.model_id = m.model_id
WHERE m.model_name = 'Axia' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND c.rate = 70.00
  AND ROWNUM = 1;

INSERT INTO Booking (cust_id, staff_id, car_id, pickup_date, dropoff_date, pickup_location_id, dropoff_location_id, price)
SELECT 
    (SELECT MIN(cust_id) FROM Customer) as cust_id,
    (SELECT MIN(staff_id) FROM Staff) as staff_id,
    c.car_id,
    TO_DATE('2026-01-05', 'YYYY-MM-DD') as pickup_date,
    TO_DATE('2026-01-06', 'YYYY-MM-DD') as dropoff_date,
    (SELECT location_id FROM Location WHERE location_name = 'Subang Airport') as pickup_location_id,
    (SELECT location_id FROM Location WHERE location_name = 'Subang Airport') as dropoff_location_id,
    c.rate * 1 as price
FROM Car c
JOIN Model m ON c.model_id = m.model_id
WHERE m.model_name = 'Myvi' AND m.brand_id = (SELECT brand_id FROM Brand WHERE brand_name = 'Perodua')
  AND c.rate = 80.00
  AND ROWNUM = 1;

-- Insert payments for some bookings (making them "Paid")
INSERT INTO Payment (booking_id, amount, payment_date)
SELECT booking_id, price, TO_DATE('2026-01-08', 'YYYY-MM-DD')
FROM Booking
WHERE pickup_date = TO_DATE('2026-01-08', 'YYYY-MM-DD')
  AND ROWNUM = 1;

-- The second booking remains unpaid (Pending status)

-- Commit all changes
COMMIT;
