#!/usr/bin/env python
"""
Visualize FITS image with detected objects marked with circles.
Reads r-band FITS image and overlays circles for all detected objects.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.io import ascii
from matplotlib.patches import Circle


def latex_formatting():
    """Apply LaTeX formatting to matplotlib plots."""
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10


def should_use_latex():
    """Check if LaTeX formatting should be applied."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    formatting_file = os.path.join(script_dir, 'formatting_on.txt')
    
    if os.path.exists(formatting_file):
        with open(formatting_file, 'r') as f:
            content = f.read().strip().lower()
            return content == 'true'
    
    return False


def load_fits_image(fits_path):
    """Load FITS image."""
    try:
        with fits.open(fits_path) as hdul:
            data = hdul[0].data
            header = hdul[0].header
        return data, header
    except Exception as e:
        print(f"Error loading FITS: {e}")
        return None, None


def load_catalog(catalog_path):
    """Load SExtractor ASCII_HEAD catalog or simple catalog with column headers."""
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
            print(f"Error loading catalog: {e}")
            return None


def plot_image_with_objects(fits_image, header, catalog, 
                           circle_radius=10, output_path=None):
    """
    Overlay detected objects on FITS image.
    
    Parameters
    ----------
    fits_image : ndarray
        2D image data
    header : fits.Header
        FITS header
    catalog : astropy Table
        Source catalog with X_IMAGE and Y_IMAGE
    circle_radius : float
        Circle radius in pixels (default 10)
    output_path : str
        Where to save plot
    """
    
    if fits_image is None or catalog is None:
        print("ERROR: Image or catalog is missing")
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
    
    # Draw circles around objects
    for x, y in zip(x_pos, y_pos):
        circle = Circle((x, y), circle_radius, 
                       fill=False, edgecolor='red', linewidth=1.5, alpha=0.7)
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
    
    # Use z-band image with red sequence objects from lenstool catalog
    fits_path = os.path.join(data_dir, 'cj0221_z.fits')
    catalog_path = os.path.join(data_dir, 'catalogs', 'cj0221_decals-dr10.cat')
    output_path = os.path.join(project_dir, 'outputs', 'plots', 'detections_z.pdf')
    
    circle_radius = 10
    
    # Allow command-line overrides
    if len(sys.argv) > 1:
        fits_path = sys.argv[1]
    if len(sys.argv) > 2:
        catalog_path = sys.argv[2]
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    if len(sys.argv) > 4:
        circle_radius = float(sys.argv[4])
    
    print(f"Loading FITS image: {fits_path}")
    fits_image, header = load_fits_image(fits_path)
    if fits_image is None:
        sys.exit(1)
    
    print(f"Image shape: {fits_image.shape}")
    print(f"Image min/max: {fits_image.min():.2f} / {fits_image.max():.2f}")
    
    print(f"\nLoading catalog: {catalog_path}")
    catalog = load_catalog(catalog_path)
    if catalog is None:
        sys.exit(1)
    
    print(f"Objects detected: {len(catalog)}")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Plot
    print(f"\nCreating visualization (circle radius: {circle_radius} pixels)...")
    plot_image_with_objects(fits_image, header, catalog, 
                           circle_radius=circle_radius, 
                           output_path=output_path)
