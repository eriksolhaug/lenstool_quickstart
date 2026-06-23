#!/usr/bin/env python
"""Format filtered catalog for lenstool input."""

import numpy as np
from astropy.io import ascii

# ============================================================================
# ## INPUT/OUTPUT
# ============================================================================

INPUT_CATALOG = 'catalogs/coolj1153_filtered.cat'
OUTPUT_CATALOG = 'catalogs/coolj1153_lenstool.cat'

# Pixel scale in arcsec/pixel (HST/ACS drizzled)
PIXEL_SCALE = 0.03

# ============================================================================


def make_lenstool_catalog(catalog, output_path, pixel_scale=PIXEL_SCALE):
    """
    Format catalog for lenstool.
    
    Output format:
    ID X_WORLD Y_WORLD A_WORLD B_WORLD THETA_WORLD MAG_ISO 0.0
    """
    
    # Extract columns
    obj_id = np.array(catalog['NUMBER'], dtype=int)
    x_world = np.array(catalog['X_WORLD'], dtype=float)
    y_world = np.array(catalog['Y_WORLD'], dtype=float)
    
    # Convert pixel sizes to arcsec
    a_image = np.array(catalog['A_IMAGE'], dtype=float)
    b_image = np.array(catalog['B_IMAGE'], dtype=float)
    a_world = a_image * pixel_scale
    b_world = b_image * pixel_scale
    
    theta = np.array(catalog['THETA_IMAGE'], dtype=float)
    mag = np.array(catalog['MAG_ISO'], dtype=float)
    
    # Write lenstool format
    with open(output_path, 'w') as f:
        for i in range(len(obj_id)):
            line = f"{obj_id[i]} {x_world[i]:.14g} {y_world[i]:.14g} {a_world[i]:.7g} {b_world[i]:.7g} {theta[i]:.1f} {mag[i]:.6f} 0.0\n"
            f.write(line)
    
    print(f"Wrote {len(obj_id)} objects to {output_path}")


def main():
    cat = ascii.read(INPUT_CATALOG)
    print(f"Loaded {len(cat)} objects from {INPUT_CATALOG}")
    
    # Format for lenstool
    make_lenstool_catalog(cat, OUTPUT_CATALOG, PIXEL_SCALE)


if __name__ == '__main__':
    main()
