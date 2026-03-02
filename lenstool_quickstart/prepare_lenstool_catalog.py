#!/usr/bin/env python
"""
Filter galaxy catalog for lenstool input.
Selects galaxies (CLASS_STAR < 0.10) with r-z color between 1.0 and 1.5.
Outputs cj0221_decals-dr10.cat suitable for lenstool analysis.
"""

import os
import sys
import numpy as np
from astropy.io import ascii


def load_catalog(catalog_path):
    """Load SExtractor ASCII_HEAD catalog."""
    try:
        data = ascii.read(catalog_path, format='sextractor')
        return data
    except Exception as e:
        print(f"Error loading {catalog_path}: {e}")
        return None


def filter_and_save_catalog(r_cat, z_cat, color_min=1.0, color_max=1.5, 
                           star_threshold=0.10, output_path=None):
    """
    Filter catalogs for galaxy selection and save for lenstool.
    
    Selects galaxies within color range and saves to lenstool format.
    
    Parameters
    ----------
    r_cat : astropy Table
        R-band catalog
    z_cat : astropy Table
        Z-band catalog
    color_min : float
        Minimum r-z color
    color_max : float
        Maximum r-z color
    star_threshold : float
        CLASS_STAR threshold (default 0.10)
    output_path : str
        Output file path
    """
    
    if r_cat is None or z_cat is None:
        print("ERROR: Catalog is missing")
        return None
    
    # Get object IDs
    r_ids = np.array(r_cat['NUMBER'])
    z_ids = np.array(z_cat['NUMBER'])
    
    # Find common objects
    common_ids = np.intersect1d(r_ids, z_ids)
    print(f"\nTotal common objects: {len(common_ids)}")
    
    # Get indices for common objects
    r_idx = np.searchsorted(r_ids, common_ids)
    z_idx = np.searchsorted(z_ids, common_ids)
    
    # Extract data
    r_mag = np.array(r_cat['MAG_ISO'][r_idx])
    z_mag = np.array(z_cat['MAG_ISO'][z_idx])
    class_star_r = np.array(r_cat['CLASS_STAR'][r_idx])
    class_star_z = np.array(z_cat['CLASS_STAR'][z_idx])
    
    # Calculate color
    color = r_mag - z_mag
    
    # Create galaxy/star classification
    is_star = (class_star_r >= star_threshold) | (class_star_z >= star_threshold)
    is_galaxy = ~is_star
    
    print(f"Total stars: {np.sum(is_star)}")
    print(f"Total galaxies: {np.sum(is_galaxy)}")
    
    # Apply color cut
    in_color_range = (color >= color_min) & (color <= color_max)
    
    # Combined filter
    selected = is_galaxy & in_color_range
    
    print(f"\nFilters applied:")
    print(f"  CLASS_STAR < {star_threshold} (galaxy): {np.sum(is_galaxy)}")
    print(f"  {color_min} <= r-z <= {color_max}: {np.sum(in_color_range)}")
    print(f"  Combined (galaxies in color range): {np.sum(selected)}")
    
    # Get selected indices in original catalogs
    selected_r_idx = r_idx[selected]
    selected_z_idx = z_idx[selected]
    selected_ids = common_ids[selected]
    
    print(f"\nSelected {len(selected_ids)} objects for lenstool")
    
    # Build output catalog from r-band detections with z-band photometry
    output_catalog = {}
    
    # Essential columns for lenstool
    output_catalog['NUMBER'] = r_cat['NUMBER'][selected_r_idx]
    output_catalog['X_IMAGE'] = r_cat['X_IMAGE'][selected_r_idx]
    output_catalog['Y_IMAGE'] = r_cat['Y_IMAGE'][selected_r_idx]
    output_catalog['X_WORLD'] = r_cat['X_WORLD'][selected_r_idx]
    output_catalog['Y_WORLD'] = r_cat['Y_WORLD'][selected_r_idx]
    
    # Photometry columns
    output_catalog['MAG_R'] = r_cat['MAG_ISO'][selected_r_idx]
    output_catalog['MAGERR_R'] = r_cat['MAGERR_ISO'][selected_r_idx]
    output_catalog['MAG_Z'] = z_cat['MAG_ISO'][selected_z_idx]
    output_catalog['MAGERR_Z'] = z_cat['MAGERR_ISO'][selected_z_idx]
    
    # Color
    output_catalog['COLOR_R_Z'] = output_catalog['MAG_R'] - output_catalog['MAG_Z']
    
    # Morphological info
    output_catalog['CLASS_STAR'] = r_cat['CLASS_STAR'][selected_r_idx]
    output_catalog['A_IMAGE'] = r_cat['A_IMAGE'][selected_r_idx]
    output_catalog['B_IMAGE'] = r_cat['B_IMAGE'][selected_r_idx]
    
    # Save to file
    if output_path:
        # Create a structured array for writing
        col_names = list(output_catalog.keys())
        col_data = [output_catalog[col] for col in col_names]
        
        # Write as ASCII table
        ascii.write(
            [output_catalog[col] for col in col_names],
            output_path,
            names=col_names,
            format='commented_header',
            overwrite=True
        )
        
        print(f"\nCatalog saved to: {output_path}")
        
        # Also print summary statistics
        print(f"\nOutput catalog statistics:")
        print(f"  r-band mag range: {output_catalog['MAG_R'].min():.2f} to {output_catalog['MAG_R'].max():.2f}")
        print(f"  r-z color range: {output_catalog['COLOR_R_Z'].min():.2f} to {output_catalog['COLOR_R_Z'].max():.2f}")
        print(f"  Median r magnitude: {np.median(output_catalog['MAG_R']):.2f}")
    
    return output_catalog


if __name__ == '__main__':
    # Default paths - use z-band as primary detection image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data', 'catalogs')
    
    # z-band catalog (z-band single image detection/measurement)
    z_cat_path = os.path.join(data_dir, 'cj0221_sources_z.cat')
    # r-band catalog (dual-image with z-detection, r-measurement)
    r_cat_path = os.path.join(data_dir, 'cj0221_sources_z_rphot.cat')
    output_path = os.path.join(data_dir, 'cj0221_decals-dr10.cat')
    
    # Allow command-line overrides
    color_min = 1.0
    color_max = 1.5
    star_threshold = 0.10
    
    if len(sys.argv) > 1:
        color_min = float(sys.argv[1])
    if len(sys.argv) > 2:
        color_max = float(sys.argv[2])
    if len(sys.argv) > 3:
        star_threshold = float(sys.argv[3])
    if len(sys.argv) > 4:
        output_path = sys.argv[4]
    
    print(f"Loading z-band catalog: {z_cat_path}")
    z_cat = load_catalog(z_cat_path)
    if z_cat is None:
        sys.exit(1)
    
    print(f"Loading r-band catalog (dual-image): {r_cat_path}")
    r_cat = load_catalog(r_cat_path)
    if r_cat is None:
        sys.exit(1)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Filter and save
    print(f"\nFiltering catalog:")
    print(f"  Color range: {color_min} <= r-z <= {color_max}")
    print(f"  Star threshold: CLASS_STAR >= {star_threshold}")
    
    filtered_cat = filter_and_save_catalog(
        r_cat, z_cat,
        color_min=color_min,
        color_max=color_max,
        star_threshold=star_threshold,
        output_path=output_path
    )
