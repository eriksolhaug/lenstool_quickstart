#!/usr/bin/env python
"""
Create DS9 region file from dual-band source catalogs.

Loads two SExtractor ASCII catalogs (detection and measurement bands),
matches objects by NUMBER, and creates a DS9 region file with:
- Cyan circles for galaxies
- Red circles for stars

Stars are defined as objects with CLASS_STAR >= threshold in either band.
"""

import os
import sys
import numpy as np
from astropy.io import ascii


def load_catalog(catalog_path):
    """Load SExtractor ASCII_HEAD catalog using astropy."""
    try:
        cat = ascii.read(catalog_path)
        print(f"  Loaded {len(cat)} objects")
        return cat
    except Exception as e:
        print(f"  Error loading catalog: {e}")
        return None


def match_catalogs_by_number(band1_cat, band2_cat):
    """
    Match band1 and band2 catalogs by NUMBER column.
    Returns matched indices for both catalogs.
    """
    band1_numbers = np.array(band1_cat['NUMBER'])
    band2_numbers = np.array(band2_cat['NUMBER'])
    
    # Find indices in band2_cat that match numbers in band1_cat
    matched_band1_idx = []
    matched_band2_idx = []
    
    for i, band1_num in enumerate(band1_numbers):
        # Find this number in band2_cat
        band2_match = np.where(band2_numbers == band1_num)[0]
        if len(band2_match) > 0:
            matched_band1_idx.append(i)
            matched_band2_idx.append(band2_match[0])
    
    return np.array(matched_band1_idx), np.array(matched_band2_idx)


def make_ds9_regions(band1_cat, band2_cat, output_path, class_star_threshold=0.10, radius=1.0):
    """
    Create DS9 region file from dual-band source catalogs.
    
    Parameters
    ----------
    band1_cat : astropy.table.Table
        SExtractor catalog for band 1 (typically shorter wavelength)
    band2_cat : astropy.table.Table
        SExtractor catalog for band 2 (typically longer wavelength)
    output_path : str
        Path to save the region file
    class_star_threshold : float, optional
        CLASS_STAR threshold for star/galaxy classification. 
        Objects with CLASS_STAR >= threshold in either band are classified as stars.
        Default: 0.10
    radius : float, optional
        Radius of circles in arcseconds. Default: 1.0
    """
    # Match catalogs by NUMBER
    band1_idx, band2_idx = match_catalogs_by_number(band1_cat, band2_cat)
    
    # Extract world coordinates
    ra = np.array(band1_cat['X_WORLD'][band1_idx])
    dec = np.array(band1_cat['Y_WORLD'][band1_idx])
    
    # Extract classification
    class_star_band1 = np.array(band1_cat['CLASS_STAR'][band1_idx])
    class_star_band2 = np.array(band2_cat['CLASS_STAR'][band2_idx])
    
    # Classify stars (if either band indicates star)
    is_star = (class_star_band1 >= class_star_threshold) | (class_star_band2 >= class_star_threshold)
    
    # Separate stars and galaxies
    stars = is_star
    galaxies = ~is_star
    
    print(f"\nTotal matched objects: {len(ra)}")
    print(f"  Stars (CLASS_STAR >= {class_star_threshold}): {np.sum(stars)}")
    print(f"  Galaxies: {np.sum(galaxies)}")
    
    # Create region file
    with open(output_path, 'w') as f:
        # DS9 region file header
        f.write("# Region file format: DS9 version 4.1\n")
        f.write("global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal\" ")
        f.write("select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n")
        f.write("fk5\n")
        
        # Write galaxy regions (cyan circles)
        if np.sum(galaxies) > 0:
            for i in np.where(galaxies)[0]:
                f.write(f"circle({ra[i]:.6f},{dec[i]:.6f},{radius}\") # color=cyan\n")
        
        # Write star regions (red circles)
        if np.sum(stars) > 0:
            for i in np.where(stars)[0]:
                f.write(f"circle({ra[i]:.6f},{dec[i]:.6f},{radius}\") # color=red\n")
    
    print(f"\nRegion file saved to: {output_path}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Create DS9 region file from dual-band catalogs')
    parser.add_argument('--band1-catalog', dest='band1_catalog', required=True,
                        help='Path to band1 (detection) catalog')
    parser.add_argument('--band2-catalog', dest='band2_catalog', required=True,
                        help='Path to band2 (measurement) catalog')
    parser.add_argument('--output', required=True, help='Output region file path')
    parser.add_argument('--class-star-threshold', dest='class_star_threshold', type=float, default=0.10,
                        help='CLASS_STAR threshold for star/galaxy separation (default: 0.10)')
    parser.add_argument('--radius', type=float, default=1.0,
                        help='Radius of circles in arcseconds (default: 1.0)')
    
    args = parser.parse_args()
    
    band1_cat_path = args.band1_catalog
    band2_cat_path = args.band2_catalog
    output_path = args.output
    
    print(f"Loading band1 catalog: {band1_cat_path}")
    band1_cat = load_catalog(band1_cat_path)
    if band1_cat is None:
        sys.exit(1)
    
    print(f"Loading band2 catalog: {band2_cat_path}")
    band2_cat = load_catalog(band2_cat_path)
    if band2_cat is None:
        sys.exit(1)
    
    print(f"\nBand1 detections: {len(band1_cat)} objects")
    print(f"Band2 measurements: {len(band2_cat)} objects")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create region file
    print(f"\nCreating DS9 region file...")
    make_ds9_regions(band1_cat, band2_cat, output_path, args.class_star_threshold, args.radius)
