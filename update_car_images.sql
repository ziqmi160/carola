-- ============================================================================
-- UPDATE CAR IMAGES
-- ============================================================================
-- Instructions:
-- 1. Place your car images in the static/uploads/ folder
-- 2. Name them appropriately (e.g., car_1.jpg, car_2.jpg, etc.)
-- 3. Run these UPDATE statements to link images to cars
-- 4. Adjust the car_id and filename as needed
-- ============================================================================

-- Example: Update car images
-- Replace the filename with your actual image filename

-- Car ID 1 - Toyota Camry
UPDATE Car SET attachments = 'car_1.jpg' WHERE car_id = 1;

-- Car ID 2 - Toyota Vios
UPDATE Car SET attachments = 'car_2.jpg' WHERE car_id = 2;

-- Car ID 3 - Perodua Myvi
UPDATE Car SET attachments = 'car_3.jpg' WHERE car_id = 3;

-- Car ID 4 - Perodua Axia
UPDATE Car SET attachments = 'car_4.jpg' WHERE car_id = 4;

-- Car ID 5 - Toyota Fortuner (Diesel)
UPDATE Car SET attachments = 'car_5.jpg' WHERE car_id = 5;

-- Car ID 6 - Honda CR-V (Diesel)
UPDATE Car SET attachments = 'car_6.jpg' WHERE car_id = 6;

-- Car ID 7 - Nissan Navara (Diesel)
UPDATE Car SET attachments = 'car_7.jpg' WHERE car_id = 7;

-- Car ID 8 - Tesla Model 3 (Electric)
UPDATE Car SET attachments = 'car_8.jpg' WHERE car_id = 8;

-- Car ID 9 - Tesla Model Y (Electric)
UPDATE Car SET attachments = 'car_9.jpg' WHERE car_id = 9;

-- Car ID 10 - Honda Accord (Penang)
UPDATE Car SET attachments = 'car_10.jpg' WHERE car_id = 10;

-- Car ID 11 - Honda Civic (Penang)
UPDATE Car SET attachments = 'car_11.jpg' WHERE car_id = 11;

-- Car ID 12 - Proton X70 (Johor)
UPDATE Car SET attachments = 'car_12.jpg' WHERE car_id = 12;

-- Car ID 13 - Proton X50 (Johor)
UPDATE Car SET attachments = 'car_13.jpg' WHERE car_id = 13;

-- Car ID 14 - BMW 3 Series (Luxury)
UPDATE Car SET attachments = 'car_14.jpg' WHERE car_id = 14;

-- Car ID 15 - BMW 5 Series (Luxury)
UPDATE Car SET attachments = 'car_15.jpg' WHERE car_id = 15;

-- Car ID 16 - Mercedes C-Class (Luxury)
UPDATE Car SET attachments = 'car_16.jpg' WHERE car_id = 16;

COMMIT;

-- ============================================================================
-- To view which cars have images:
-- SELECT car_id, attachments FROM Car WHERE attachments IS NOT NULL;
-- ============================================================================

