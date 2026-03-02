#!/usr/bin/env python
"""
Create red sequence catalog by filtering z-band detections by color.

Loads up the z-band and r-band source catalogs, filters by r-z color
to pick out likely cluster red sequence galaxies, and saves a nice
visualization of what we found.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.io import ascii
from matplotlib.patches import Circle

# Color range for red sequence galaxies
COLOR_MIN = 1.0
COLOR_MAX = 1.5


def latex_formatting():
    """Set up matplotlib for LaTeX rendering (nicer looking plots)."""
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10


def should_use_latex():
    """Check if LaTeX formatting is enabled (looks for formatting_on.txt)."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    formatting_file = os.path.join(script_dir, 'formatting_on.txt')
    
    if os.path.exists(formatting_file):
        with open(formatting_file, 'r') as f:
            content = f.read().strip().lower()
            return content == 'true'
    
    return False


def load_catalog(catalog_path):
    """Load a catalog - handles SExtractor or simple ASCII formats."""
    try:
        # Try SExtractor format first
        data = ascii.read(catalog_path, format='sextractor')
        return data
    except:
        try:
            # Try simple format with comments for headers
            data = ascii.read(catalog_path, format='commented_header')
            return data
        except Exception as e:
            print(f"Couldn't load catalog: {e}")
            return None


def load_fits_image(fits_path):
    """Load a FITS image file."""
    try:
        with fits.open(fits_path) as hdul:
            data = hdul[0].data
            header = hdul[0].header
        return data, header
    except Exception as e:
        print(f"Couldn't read FITS file: {e}")
        return None, None


def match_catalogs_by_number(z_cat, r_cat):
    """
    Match z-band and r-band catalogs by NUMBER column.
    
    Finds which objects appear in both catalogs so we can
    compare their magnitudes across bands.
    
    Returns arrays of matched indices and magnitudes.
    """
    z_numbers = np.array(z_cat['NUMBER'])
    r_numbers = np.array(r_cat['NUMBER'])
    
    # Find which objects from z-band are in r-band
    matched_z_idx = []
    matched_r_idx = []
    
    for i, z_num in enumerate(z_numbers):
        # Look up this object number in the r-band catalog
        r_match = np.where(r_numbers == z_num)[0]
        if len(r_match) > 0:
            matched_z_idx.append(i)
            matched_r_idx.append(r_match[0])
    
    return np.array(matched_z_idx), np.array(matched_r_idx)


def filter_by_color(z_cat, r_cat, z_idx, r_idx, color_min=COLOR_MIN, color_max=COLOR_MAX):
    """
    Filter matched catalogs by r-z color range.
    
    Red sequence galaxies have specific colors, so we pick out
    only the objects that fall in that range.
    
    Returns indices of objects within color range.
    """
    z_mag = np.array(z_cat['MAG_ISO'][z_idx])
    r_mag = np.array(r_cat['MAG_ISO'][r_idx])
    
    color = r_mag - z_mag
    
    # Pick out objects with the right color (red sequence)
    color_mask = (color >= color_min) & (color <= color_max)
    
    return color_mask


def save_redsequence_catalog(z_cat, z_idx, color_mask, output_path):
    """
    Write the red sequence objects to a catalog file.
    
    Takes the filtered list of red sequence galaxies and saves
    them to a catalog file with all their z-band properties.
    """
    # Get filtered indices
    filtered_z_idx = z_idx[color_mask]
    
    # Create new catalog with filtered objects
    output_cat = z_cat[filtered_z_idx]
    
    # Write to file with header (preserves column names)
    output_cat.write(output_path, format='ascii', overwrite=True, comment=False)
    
    print(f"Red sequence catalog saved to: {output_path}")
    print(f"  Objects: {len(output_cat)}")
    
    return output_cat


def plot_image_with_objects(fits_image, header, catalog, 
                           circle_radius=10, output_path=None):
    """
    Plot FITS image with red sequence objects circled.
    
    Nice visualization showing exactly where the red sequence
    galaxies are on the actual image.
    
    Parameters:
    -----------
    fits_image : ndarray
        2D FITS image data
    header : fits.Header
        FITS header (for WCS info if available)
    catalog : astropy Table
        Source catalog with X_IMAGE and Y_IMAGE columns
    circle_radius : float
        How big to draw the circles (pixels, default 10)
    output_path : str
        Where to save the plot (optional)
    """
    
    if fits_image is None or catalog is None:
        print("ERROR: Image or catalog is None")
        return
    
    # Apply LaTeX formatting if enabled
    if should_use_latex():
        latex_formatting()
    
    # Create figure with appropriate size
    fig_size = max(8, min(12, fits_image.shape[0] / 50))
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    
    # Normalize image for display
    vmin = np.percentile(fits_image, 2)
    vmax = np.percentile(fits_image, 98)
    
    # Display image
    im = ax.imshow(fits_image, origin='lower', cmap='gray', 
                   vmin=vmin, vmax=vmax, interpolation='nearest')
    
    # Get object positions
    x_pos = np.array(catalog['X_IMAGE'])
    y_pos = np.array(catalog['Y_IMAGE'])
    
    # Draw red circles around objects
    for x, y in zip(x_pos, y_pos):
        circle = Circle((x, y), circle_radius, 
                       fill=False, edgecolor='red', linewidth=2.0, alpha=0.8)
        ax.add_patch(circle)
    
    # Labels and title
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    ax.set_title(f'COOLJ0221 z-band - {len(catalog)} red sequence objects')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Pixel Value')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Image saved to: {output_path}")
    else:
        plt.show()
    
    plt.close()


if __name__ == '__main__':
    # Default paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data')
    cat_dir = os.path.join(data_dir, 'catalogs')
    
    # Input catalogs
    z_cat_path = os.path.join(cat_dir, 'cj0221_sources_z.cat')
    r_cat_path = os.path.join(cat_dir, 'cj0221_sources_z_rphot.cat')
    
    # Output catalog
    redseq_cat_path = os.path.join(cat_dir, 'cj0221_redsequence.cat')
    
    # FITS image
    fits_path = os.path.join(data_dir, 'cj0221_z.fits')
    
    # Output plot
    output_path = os.path.join(project_dir, 'outputs', 'plots', 'redsequence.pdf')
    
    # Parameters
    color_min = COLOR_MIN
    color_max = COLOR_MAX
    circle_radius = 10
    
    # Allow command-line overrides
    if len(sys.argv) > 1:
        color_min = float(sys.argv[1])
    if len(sys.argv) > 2:
        color_max = float(sys.argv[2])
    if len(sys.argv) > 3:
        redseq_cat_path = sys.argv[3]
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
    
    print(f"\nz-band detections: {len(z_cat)} objects")
    print(f"r-band measurements: {len(r_cat)} objects")
    
    # Match catalogs by NUMBER
    print(f"\nMatching catalogs by NUMBER...")
    z_idx, r_idx = match_catalogs_by_number(z_cat, r_cat)
    print(f"Matched: {len(z_idx)} objects")
    
    # Filter by color
    print(f"\nFiltering by color: {color_min} <= r-z <= {color_max}")
    color_mask = filter_by_color(z_cat, r_cat, z_idx, r_idx, color_min, color_max)
    print(f"Red sequence objects: {np.sum(color_mask)}")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(redseq_cat_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save red sequence catalog
    print(f"\nSaving red sequence catalog...")
    redseq_cat = save_redsequence_catalog(z_cat, z_idx, color_mask, redseq_cat_path)
    
    # Load FITS image
    print(f"\nLoading FITS image: {fits_path}")
    fits_image, header = load_fits_image(fits_path)
    if fits_image is None:
        sys.exit(1)
    
    print(f"Image shape: {fits_image.shape}")
    print(f"Image min/max: {fits_image.min():.2f} / {fits_image.max():.2f}")
    
    # Plot
    print(f"\nCreating visualization (circle radius: {circle_radius} pixels)...")
    plot_image_with_objects(fits_image, header, redseq_cat, 
                           circle_radius=circle_radius, 
                           output_path=output_path)
