# Car Types Images Guide

## How to Add Images to the Car Types Section

### Step 1: Prepare Your Car Type Images

1. **Get or create images** for each car type:
   - Sedan
   - SUV
   - Hatchback
   - MPV
   - Pickup
   - Luxury

2. **Recommended specifications:**
   - **Format:** JPG or PNG
   - **Size:** 400x300 pixels or larger (maintain 4:3 or 16:9 aspect ratio)
   - **File size:** Under 200KB for faster loading
   - **Content:** Side view or 3/4 view of a representative car of that type

### Step 2: Place Image Files

Save your car type images in the following folder:
```
static/uploads/car-types/
```

**File naming convention** (must match exactly):
- `sedan.jpg` (or `.png`)
- `suv.jpg`
- `hatchback.jpg`
- `mpv.jpg`
- `pickup.jpg`
- `luxury.jpg`

### Step 3: File Structure

Your folder structure should look like this:
```
static/
  uploads/
    brands/
      (brand logos here)
    car-types/
      sedan.jpg
      suv.jpg
      hatchback.jpg
      mpv.jpg
      pickup.jpg
      luxury.jpg
    (car images here)
```

### Step 4: Add Images

Simply copy your car type image files to:
```
static/uploads/car-types/[filename]
```

For example:
- `static/uploads/car-types/sedan.jpg`
- `static/uploads/car-types/suv.jpg`
- etc.

### Step 5: Verify

1. Make sure your image files are in `static/uploads/car-types/`
2. Verify the filenames match exactly (case-sensitive):
   - `sedan.jpg` ✓
   - `Sedan.jpg` ✗ (wrong case)
3. Refresh the homepage
4. The images should appear in the car types section with labels overlaid at the bottom

### How It Works

- If an image file exists, it will be displayed with the car type name overlaid at the bottom
- If an image file doesn't exist, the car type name will be shown as text in a card
- Images have a gradient overlay at the bottom showing the car type name
- Images zoom slightly on hover for a nice interactive effect

### Image Suggestions

You can find car type images from:
- Stock photo websites (Unsplash, Pexels, Pixabay)
- Car manufacturer websites
- Create your own using design tools

**Example search terms:**
- "sedan car side view"
- "SUV car white background"
- "hatchback car profile"
- "MPV minivan side"
- "pickup truck side view"
- "luxury sedan car"

### Adding New Car Types

If you add a new car type in the database, update the `carTypeImages` mapping in `templates/index.html`:

```javascript
const carTypeImages = {
    'Sedan': 'sedan.jpg',
    'SUV': 'suv.jpg',
    // ... existing types
    'NewType': 'newtype.jpg'  // Add new type here
};
```

### Troubleshooting

**Image not showing?**
1. Check filename matches exactly (case-sensitive)
2. Verify file is in `static/uploads/car-types/` folder
3. Check file extension (.jpg, .png, etc.)
4. Clear browser cache and refresh

**Image looks distorted?**
- Use images with proper aspect ratio (4:3 or 16:9)
- Recommended size: 400x300px or larger
- Ensure original image is high quality

**Label not showing?**
- The label should appear automatically with a dark gradient overlay
- Check that the image is loading correctly
- Verify CSS is loaded properly





