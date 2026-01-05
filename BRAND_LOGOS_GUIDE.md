# Brand Logos Guide

## How to Add Brand Logos to the Brands Section

### Step 1: Prepare Your Logo Images

1. **Download or create logo images** for each brand:
   - Toyota
   - Honda
   - Perodua
   - Proton
   - BMW
   - Mercedes-Benz
   - Tesla

2. **Recommended specifications:**
   - **Format:** PNG (with transparent background preferred) or JPG
   - **Size:** 200x100 pixels or larger (maintain aspect ratio)
   - **File size:** Under 100KB for faster loading
   - **Background:** Transparent PNG works best

### Step 2: Place Logo Files

Save your logo files in the following folder:
```
static/uploads/brands/
```

**File naming convention** (must match exactly):
- `toyota-logo.png`
- `honda-logo.png`
- `perodua-logo.png`
- `proton-logo.png`
- `bmw-logo.png`
- `mercedes-logo.png`
- `tesla-logo.png`

### Step 3: File Structure

Your folder structure should look like this:
```
static/
  uploads/
    brands/
      toyota-logo.png
      honda-logo.png
      perodua-logo.png
      proton-logo.png
      bmw-logo.png
      mercedes-logo.png
      tesla-logo.png
    (car images here)
```

### Step 4: Add Logos

Simply copy your logo image files to:
```
static/uploads/brands/[logo-filename]
```

For example:
- `static/uploads/brands/toyota-logo.png`
- `static/uploads/brands/honda-logo.png`
- etc.

### Step 5: Verify

1. Make sure your logo files are in `static/uploads/brands/`
2. Verify the filenames match exactly (case-sensitive):
   - `toyota-logo.png` ✓
   - `Toyota-Logo.png` ✗ (wrong case)
3. Refresh the homepage
4. The logos should appear in the brands section

### How It Works

- If a logo file exists, it will be displayed
- If a logo file doesn't exist, the brand name will be shown as text instead
- Logos are displayed in grayscale by default and become colored on hover
- Logos automatically scale to fit the brand card

### Adding New Brands

If you add a new brand in the database, update the `brandLogos` mapping in `templates/index.html`:

```javascript
const brandLogos = {
    'Toyota': 'toyota-logo.png',
    'Honda': 'honda-logo.png',
    // ... existing brands
    'NewBrand': 'newbrand-logo.png'  // Add new brand here
};
```

### Troubleshooting

**Logo not showing?**
1. Check filename matches exactly (case-sensitive)
2. Verify file is in `static/uploads/brands/` folder
3. Check file extension (.png, .jpg, etc.)
4. Clear browser cache and refresh

**Logo looks blurry?**
- Use higher resolution images (at least 200x100px)
- Use PNG format for better quality
- Ensure original logo is high quality

**Logo not centered?**
- The CSS automatically centers logos
- Make sure logo has proper aspect ratio
- Transparent backgrounds work best

### Example Logo Sources

You can find brand logos from:
- Official brand websites (download press kits)
- Logo databases (like logowik.com, brandsoftheworld.com)
- Create your own using design tools

**Note:** Make sure you have permission to use the logos (for commercial use, check licensing requirements).


