# lenstool-quickstart

A toolkit for getting quickly set up with a lens model using DECaLS survey imaging data (or any existing imaging data at your disposal) with Lenstool. This package handles everything from fetching data to building lens models, so you can focus on the science. Below, I only describe the steps for making a red sequence catalog, but be aware that there are some scripts here that have other useful purposes you may want to check out. These live in `./lenstool_quickstart/`.

## Installation & Setup

### Step 1: Clone the Repository

First, get a copy of the code:

```bash
git clone https://github.com/yourusername/lenstool-quickstart.git
cd lenstool_quickstart
```

### Step 2: Create a Conda Environment

Creating a separate environment keeps all the dependencies organized and prevents conflicts with other projects.

```bash
# Create a new conda enviro# Create a new conda enviro# Create a new conda enviro# Createn=3.10

# Activate the environment
conda activate lenstool_quickstart
```

### Step 3: Install the Package

Now install lenstool-quickstart and all its dependencies:

```bash
# Make sure you're in the lenstool-quickstart directory
cd lenstool_quickstart

# Install in development mode (lets you edit code and see changes immediately)
pip install -e .
```

This installs the package plus all required dependencies.
The installation might take a couple minutes. When it's done, you should see something like:
```
Successfully installed lenstool-quickstart-0.1.0
```

### Step 4: Verify Installation

Test that everything works:

```bash
python -c "import lenstool_quickstart; print(lenstool_quickstart.__version__)"
```

If you see `0.1.0`, you're all set!

## Quick Start: Analyzing COOLJ0221

Let me walk you through a complete example using the included COOLJ0221 dataset.

### Step 1: Create a Red Sequence Catalog

Red sequence galaxies are a key tracer of the galaxy cluster. The included script filters galaxies by their r-z color to pick out red sequence members. But first, you will need to run Source Extractor specifying by 1) running it on one of the images you will use (e.g. r-band) -- this will be your "detection" image, and 2) run Source Extractor in dual mode, specifying your detection image and the other image you want to perform photometry on, given the sources identified in the detection image. Please see the Source Extractor manual for more information on dual mode.

NOTE: Place your cj0221_g.fits, cj0221_r.fits, cj0221_z.fits (only two of them needed, depending on which you want to use for the color-magnitude red sequence plots) inside your CJ0221/data/ directory.

```bash
cd CJ0221/scripts
python make_redsequence.py
```

What this does:
1. Loads the r-band and z-band source catalogs from the data directory
2. Matches objects between catalogs
3. Filters by r-z color (red sequence galaxies have specific colors)
4. Saves a catalog of red sequence objects
5. Creates a visualization showing where these galaxies are on the image

Check the output:
```bash
ls -la ../outputs/catalogs/
```

You should see a `cj0221_redsequence.cat` file.

### Step 2: Prepare Lenstool Catalog

Convert the red sequence catalog into the format that lenstool expects:

```bash
python prepare_lenstool_catalog.py
```

This script:
1. Takes the red sequence catalog
2. Creates a catalog in `../lenstool/cats/`

NOTE: You will have to modify this a bit to read the magnitudes correctly with respect to the pivot parameter. See my Slack post in the COOL-LAMPS \#pythonaskanything channel for useful info.

### Step 3: Run Lenstool

Now run the actual lens modeling:

```bash
cd ../lenstool
lenstool input.par -n
```

## Using Your Own Data

### Fetch Data from DECaLS

```python
from lenstool_quickstart import DECaLSFetcher

# Define your region of interest
fetcher = DECaLSFetcher(
    ra=35.28,        # Right ascension in degrees
    dec=-66.39,      # Declination in degrees  
    size=300         # Cutout size in pixels
)

# Fetch the images
data = fetcher.fetch()
images = data['images']  # Dict with 'g', 'r', 'z' bands

# Save to FITS files
from astropy.io import fits
fits.PrimaryHDU(images['r']).writeto('my_image_r.fits', overwrite=True)
```

### Preprocess Images

```python
from lenstool_quickstart.utils import preprocess_image
import matplotlib.pyplot as plt

# Load and preprocess
image = images['r']
processed = preprocess_image(image, smooth=True, sigma=1.0, normalize=True)

# Visualize
plt.imshow(processed, cmap='viridis')
plt.colorbar()
plt.title('Preprocessed Image')
plt.savefig('preprocessed.png')
plt.show()
```

## Author

Erik Solhaug