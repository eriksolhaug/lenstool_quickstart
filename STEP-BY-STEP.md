# lenstool-quickstart: Step-by-Step Guide

A complete workflow for building lens models from imaging data using Lenstool and DECaLS data (or your own imaging).

---

## Prerequisites

Before starting, ensure you have:
- Python 3.10+ environment with lenstool-quickstart installed
- SExtractor installed (`brew install sextractor` on macOS)
- Lenstool installed (from http://projets.lam.fr/projects/lenstool)
- FITS imaging data in your `data/` directory (or download via Step 1)

### Quick Setup

```bash
# Clone and navigate to repository
git clone https://github.com/yourusername/lenstool-quickstart.git
cd lenstool_quickstart

# Create conda environment
conda create -n lenstool_quickstart python=3.10
conda activate lenstool_quickstart

# Install package
pip install -e .
```

---

## Main Workflow

### Step 1: Get Imaging Data

#### Option A: Download from DECaLS Survey
If you don't have imaging data yet, download from DECaLS:

```bash
cd CJ0221  # or your cluster directory
python ../lenstool_quickstart/fetch_decals_data.py \
    --ra 35.3367 \
    --dec 2.6919 \
    --size 500 \
    --bands g r z \
    --output-dir data/imaging
```

**What this does:**
- Downloads g, r, and z-band images from DECaLS survey
- Saves FITS files to `data/imaging/`
- Centers on your specified coordinates

**Output files:**
- `data/imaging/decals_*.fits` (three FITS files for each band)

---

#### Option B: Use Your Own Imaging Data
If you already have FITS images, place them in your `data/` directory:

```bash
# Expected structure
CJ0221/
├── data/
│   ├── cj0221_g.fits
│   ├── cj0221_r.fits
│   └── cj0221_z.fits
```

---

### Step 2: Run SExtractor for Source Detection

Run SExtractor to detect sources and measure photometry. This uses the z-band as the detection image and performs photometry on r and z bands.

```bash
cd CJ0221
python ../lenstool_quickstart/run_sextractor.py \
    --detection-image data/cj0221_z.fits \
    --measure-image data/cj0221_r.fits \
    --config config/source_extractor.sex \
    --output catalogs/cj0221_sources.cat
```

**What this does:**
- Detects sources in z-band image
- Measures magnitudes in r-band and z-band for each source
- Creates a SExtractor catalog with source positions and photometry

**Output files:**
- `catalogs/cj0221_sources.cat` (SExtractor catalog)
- `catalogs/cj0221_sources.xml` (SExtractor XML output)

**Note:** See SExtractor manual for dual-mode operation details.

---

### Step 3: Visualize Detections

Create a visualization of detected objects overlaid on your image:

```bash
python ../lenstool_quickstart/visualize_detections.py \
    --image data/cj0221_r.fits \
    --catalog catalogs/cj0221_sources.cat \
    --output plots/detections.png
```

**What this does:**
- Loads FITS image
- Overlays circles for each detected source
- Saves visualization to `plots/`

**Output files:**
- `plots/detections.png` (visualization image)

---

### Step 4: Create Color-Magnitude Diagram

Plot detected sources in a color-magnitude diagram to identify the red sequence:

```bash
python ../lenstool_quickstart/plot_cmd.py \
    --r-catalog catalogs/cj0221_sources_r.cat \
    --z-catalog catalogs/cj0221_sources_z.cat \
    --output plots/color_magnitude_diagram.png
```

**What this does:**
- Loads r-band and z-band source catalogs
- Creates color-magnitude diagram (z-mag vs r-z color)
- Stars (CLASS_STAR ≥ 0.10) shown in red, galaxies in black
- Visualizes red sequence galaxies in the color range [1.0, 1.5]

**Output files:**
- `plots/color_magnitude_diagram.png` (color-magnitude plot)

**Next step:** Use this plot to verify your color cuts are appropriate for red sequence selection.

---

### Step 5: Create Red Sequence Catalog

Filter sources by color to identify red sequence galaxies:

```bash
python ../lenstool_quickstart/make_redsequence.py \
    --r-catalog catalogs/cj0221_sources_r.cat \
    --z-catalog catalogs/cj0221_sources_z.cat \
    --color-min 1.0 \
    --color-max 1.5 \
    --output catalogs/cj0221_redsequence.cat
```

**What this does:**
- Loads r-band and z-band catalogs
- Matches objects between catalogs
- Filters by r-z color (galaxies with 1.0 < r-z < 1.5)
- Excludes stars (CLASS_STAR < 0.10)
- Creates visualization of red sequence on image

**Output files:**
- `catalogs/cj0221_redsequence.cat` (red sequence catalog)
- `plots/redsequence_overlay.png` (visualization)

**Note:** Adjust color-min and color-max based on your CMD from Step 4.

---

### Step 6: Prepare Lenstool Catalog

Convert red sequence catalog to Lenstool input format:

```bash
python ../lenstool_quickstart/prepare_lenstool_catalog.py \
    --input catalogs/cj0221_redsequence.cat \
    --output lenstool/cats/cj0221.cat \
    --pixel-scale 0.262
```

**What this does:**
- Loads red sequence catalog
- Converts pixel coordinates to world coordinates
- Converts pixel sizes to arcseconds
- Creates DS9 region file (.reg)
- Outputs Lenstool format: `ID X_WORLD Y_WORLD A_WORLD B_WORLD THETA_WORLD MAG_ISO 0.0`

**Output files:**
- `lenstool/cats/cj0221.cat` (Lenstool format catalog)
- `lenstool/cats/cj0221.reg` (DS9 region file)

**Important Notes:**
- Ensure PIXEL_SCALE matches your imaging data (default 0.262 arcsec/pixel for DECaLS)
- You may need to adjust magnitudes - see README for details on magnitude calibration
- Check the .reg file in DS9 to verify catalog looks correct

---

### Step 7: Run Lenstool

Run the lens modeling with your prepared catalog:

```bash
python ../lenstool_quickstart/run_lenstool.py \
    --config lenstool/input.par \
    --output-dir lenstool/outputs
```

**What this does:**
- Runs Lenstool with your configuration file
- Fits lens model to your cluster data
- Generates best-fit parameters and models

**Output files:**
- `lenstool/outputs/best.par` (best-fit parameters)
- `lenstool/outputs/image.all` (model image)
- `lenstool/outputs/arcs/` (multiple model components)

**Configuration tips:**
- Edit `lenstool/input.par` before running to customize fitting
- Refer to Lenstool documentation for parameter explanations

---

## Utility Scripts

These scripts provide additional functionality:

### Calculate Magnitude Zero Point

Calculate magnitude zero point (mag0) for Lenstool:

```bash
python lenstool_quickstart/calc_mag0.py
```

Uses Blanton et al. 2003 with cosmology (H0=70, Ω_m=0.3) to calculate reference magnitudes.

---

### Convert Magnitude Between Redshifts

Convert apparent magnitudes between different redshifts:

```bash
python lenstool_quickstart/mag_convert.py
```

Example: Convert magnitude from z=0.4301 to z=0.588.

---

### Magnitude Conversion Specific (19.53)

For specific magnitude conversions:

```bash
python lenstool_quickstart/calc_mag0_19p53.py
```

---

### Filter Catalog

General catalog filtering by stellarity and color:

```bash
python lenstool_quickstart/filter_catalog.py \
    --catalog catalogs/your_catalog.cat \
    --star-threshold 0.10 \
    --color-min 1.0 \
    --color-max 1.5 \
    --output catalogs/filtered.cat
```

---

## Quick Reference: Complete Workflow

Run these commands in sequence:

```bash
cd CJ0221

# 1. Get data
python ../lenstool_quickstart/fetch_decals_data.py

# 2. Run SExtractor
python ../lenstool_quickstart/run_sextractor.py

# 3. Visualize
python ../lenstool_quickstart/visualize_detections.py

# 4. Color-magnitude diagram
python ../lenstool_quickstart/plot_cmd.py

# 5. Red sequence
python ../lenstool_quickstart/make_redsequence.py

# 6. Prepare for Lenstool
python ../lenstool_quickstart/prepare_lenstool_catalog.py

# 7. Run Lenstool
python ../lenstool_quickstart/run_lenstool.py
```

---

## Troubleshooting

**Issue:** "Can't find SExtractor"
- **Solution:** Install with `brew install sextractor` (macOS) or `apt-get install sextractor` (Linux)

**Issue:** "Can't find lenstool"
- **Solution:** Install from http://projets.lam.fr/projects/lenstool and ensure it's in your PATH

**Issue:** Magnitudes don't match Lenstool expectations
- **Solution:** See README section on magnitude calibration; use `calc_mag0.py` and `mag_convert.py` to compute corrections

**Issue:** Red sequence catalog is empty
- **Solution:** Adjust color-min and color-max based on your CMD; check that SExtractor ran successfully

---

## Output Directory Structure

After completing all steps, your output structure looks like:

```
CJ0221/
├── data/
│   └── imaging/        # FITS images
├── catalogs/           # Detected and filtered catalogs
│   ├── cj0221_sources.cat
│   └── cj0221_redsequence.cat
├── plots/              # Visualizations
│   ├── detections.png
│   ├── color_magnitude_diagram.png
│   └── redsequence_overlay.png
└── lenstool/
    ├── cats/           # Lenstool format catalogs
    │   └── cj0221.cat
    ├── input.par       # Configuration file
    └── outputs/        # Lens model results
        ├── best.par
        ├── image.all
        └── arcs/
```

---

## Next Steps

- Review your lens model results in `lenstool/outputs/`
- Check the DS9 region files to verify source positions
- Adjust parameters and re-run as needed for better fits
- See Lenstool documentation for advanced modeling techniques
