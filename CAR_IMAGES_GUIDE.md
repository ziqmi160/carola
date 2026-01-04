# Car Images Guide

## Where to Add Car Images

### Step 1: Place Image Files

Place your car image files in the following folder:
```
static/uploads/
```

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

**Recommended naming:** 
- `car_1.jpg`, `car_2.jpg`, etc. (matching car_id)
- Or descriptive names like `toyota_camry_silver.jpg`

### Step 2: Link Images to Cars in Database

You have **two options** to link images to cars:

#### Option A: Using SQL (Recommended)

1. Open SQL Developer
2. Connect to your database
3. Run UPDATE statements like this:

```sql
-- Update a specific car's image
UPDATE Car SET attachments = 'car_1.jpg' WHERE car_id = 1;

-- Update multiple cars
UPDATE Car SET attachments = 'toyota_camry.jpg' WHERE car_id = 1;
UPDATE Car SET attachments = 'honda_civic.jpg' WHERE car_id = 2;
-- ... and so on

COMMIT;
```

Or use the provided `update_car_images.sql` file and modify it with your image filenames.

#### Option B: Using the Admin Interface (If Available)

1. Login as staff
2. Navigate to car management (if implemented)
3. Upload images through the web interface

### Step 3: Verify Images

After updating the database:

1. Restart your Flask application (if running)
2. Browse to the cars page: `http://localhost:5000/cars`
3. The images should now display instead of placeholders

## Example Workflow

1. **Get car images** (download or take photos)
2. **Rename them** appropriately (e.g., `car_1.jpg`)
3. **Copy to** `static/uploads/car_1.jpg`
4. **Update database:**
   ```sql
   UPDATE Car SET attachments = 'car_1.jpg' WHERE car_id = 1;
   COMMIT;
   ```
5. **Refresh** the website to see the image

## Finding Car IDs

To see which car_id corresponds to which car:

```sql
SELECT car_id, 
       (SELECT brand_name FROM Brand WHERE brand_id = 
        (SELECT brand_id FROM Model WHERE model_id = c.model_id)) || ' ' ||
       (SELECT model_name FROM Model WHERE model_id = c.model_id) as car_name
FROM Car c
ORDER BY car_id;
```

## Image Requirements

- **Recommended size:** 800x600 pixels or larger
- **Aspect ratio:** 4:3 or 16:9 works best
- **File size:** Keep under 2MB for faster loading
- **Format:** JPG for photos, PNG for graphics

## Troubleshooting

### Image not showing?
1. Check the filename in database matches the file in `static/uploads/`
2. Check file permissions
3. Verify the file extension is allowed (jpg, png, gif, webp)
4. Clear browser cache and refresh

### Image path issues?
- Make sure images are in `static/uploads/` (not `static/`)
- Filenames are case-sensitive on some systems
- Avoid spaces in filenames (use underscores)

### Database update not working?
- Make sure you COMMIT after UPDATE
- Verify car_id exists: `SELECT car_id FROM Car WHERE car_id = 1;`
- Check for typos in the filename

## Quick Reference

**Image Location:** `static/uploads/`  
**Database Column:** `Car.attachments`  
**URL Path:** `/uploads/{filename}`  
**Example:** If filename is `car_1.jpg`, URL is `/uploads/car_1.jpg`

---

**Need help?** Check the main README.md for more information.

