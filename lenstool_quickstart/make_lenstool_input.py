#!/usr/bin/env python
"""
Convert red sequence catalog to lenstool input format and create DS9 region file.

Lenstool format:
ID X_WORLD Y_WORLD A_WORLD B_WORLD THETA_WORLD MAG_ISO ZEROS

A_WORLD and B_WORLD are semi-major and semi-minor axes in arcsec.
"""

import os
import sys
import numpy as np
from astropy.io import ascii

# Pixel scale in arcsec/pixel (from config)
PIXEL_SCALE = 0.262


def load_catalog(catalog_path):
    """Load catalog from space-delimited file with header."""
    try:
        # First line is header
        data = ascii.read(catalog_path, comment=None)
        return data
    except Exception as e:
        print(f"Couldn't read catalog: {e}")
        return None


def convert_pixels_to_arcsec(pixels, pixel_scale=PIXEL_SCALE):
    """Convert pixel measurements to arcsec."""
    return pixels * pixel_scale


def make_lenstool_catalog(catalog, output_path, pixel_scale=PIXEL_SCALE):
    """
    Convert catalog to lenstool input format.
    
    Output format:
    ID X_WORLD Y_WORLD A_WORLD B_WORLD THETA_WORLD MAG_ISO 0.0
    """
    
    if catalog is None:
        print("ERROR: Catalog is None")
        return
    
    # Extract columns and convert to float
    object_id = np.array(catalog['NUMBER'], dtype=float)
    x_world = np.array(catalog['X_WORLD'], dtype=float)
    y_world = np.array(catalog['Y_WORLD'], dtype=float)
    
    # Convert pixel sizes to arcsec
    a_image = np.array(catalog['A_IMAGE'], dtype=float)
    b_image = np.array(catalog['B_IMAGE'], dtype=float)
    a_world = convert_pixels_to_arcsec(a_image, pixel_scale)
    b_world = convert_pixels_to_arcsec(b_image, pixel_scale)
    
    theta_world = np.array(catalog['THETA_IMAGE'], dtype=float)
    mag_iso = np.array(catalog['MAG_ISO'], dtype=float)
    
    # Write lenstool format
    with open(output_path, 'w') as f:
        for i in range(len(object_id)):
            # Format: ID X_WORLD Y_WORLD A_WORLD B_WORLD THETA_WORLD MAG_ISO 0.000000
            line = f"{int(object_id[i])} {x_world[i]:.14g} {y_world[i]:.14g} {a_world[i]:.7g} {b_world[i]:.7g} {theta_world[i]:.1f} {mag_iso[i]:.6f} 0.000000\n"
            f.write(line)
    
    print(f"Lenstool catalog saved to: {output_path}")
    print(f"  Objects: {len(object_id)}")
    print(f"  Pixel scale: {pixel_scale} arcsec/pixel")


def make_ds9_region(catalog, output_path, pixel_scale=PIXEL_SCALE):
    """
    Create DS9 region file (.reg) for visualization.
    Circles with radius = semi-major axis.
    """
    
    if catalog is None:
        print("ERROR: Catalog is None")
        return
    
    # Extract columns and convert to float
    x_world = np.array(catalog['X_WORLD'], dtype=float)
    y_world = np.array(catalog['Y_WORLD'], dtype=float)
    a_image = np.array(catalog['A_IMAGE'], dtype=float)
    
    # Convert radius from pixels to arcsec
    radius_arcsec = convert_pixels_to_arcsec(a_image, pixel_scale)
    
    # Write DS9 format
    with open(output_path, 'w') as f:
        f.write("global color=red dashlist=8 3 width=2 font=\"helvetica 10 normal\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n")
        f.write("fk5\n")
        
        for i in range(len(x_world)):
            # Format: circle(X_WORLD, Y_WORLD, radius")
            line = f"circle({x_world[i]:.6f},{y_world[i]:.6f},{radius_arcsec[i]:.4f}\")\n"
            f.write(line)
    
    print(f"DS9 region file saved to: {output_path}")
    print(f"  Objects: {len(x_world)}")


if __name__ == '__main__':
    # Default paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data')
    cat_dir = os.path.join(data_dir, 'catalogs')
    
    # Input catalog
    redseq_cat_path = os.path.join(cat_dir, 'cj0221_redsequence.cat')
    
    # Output files - save to lenstool directory structure
    lenstool_cat_path = os.path.join(project_dir, 'outputs', 'lenstool', 'cats', 'cj0221.cat')
    ds9_reg_path = os.path.join(cat_dir, 'redsequence.reg')
    
    # Pixel scale
    pixel_scale = PIXEL_SCALE
    
    # Allow command-line overrides
    if len(sys.argv) > 1:
        redseq_cat_path = sys.argv[1]
    if len(sys.argv) > 2:
        lenstool_cat_path = sys.argv[2]
    if len(sys.argv) > 3:
        ds9_reg_path = sys.argv[3]
    if len(sys.argv) > 4:
        pixel_scale = float(sys.argv[4])
    
    print(f"Loading red sequence catalog: {redseq_cat_path}")
    catalog = load_catalog(redseq_cat_path)
    if catalog is None:
        sys.exit(1)
    
    print(f"Objects: {len(catalog)}")
    
    # Create lenstool catalog
    print(f"\nCreating lenstool catalog...")
    make_lenstool_catalog(catalog, lenstool_cat_path, pixel_scale)
    
    # Create DS9 region file
    print(f"\nCreating DS9 region file...")
    make_ds9_region(catalog, ds9_reg_path, pixel_scale)
    
    print(f"\nDone!")
