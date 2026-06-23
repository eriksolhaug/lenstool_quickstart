#!/usr/bin/env python
"""
Create interactive color-magnitude diagram from dual-band source catalogs.

Loads two SExtractor ASCII catalogs (detection and measurement bands),
matches objects by NUMBER, and creates an interactive color-magnitude plot
with stars and galaxies displayed in different colors.

Uses Computer Modern Serif font if formatting_on.txt is present and set to 'true'.
Supports matplotlib interactive mode for adjusting plot limits and zooming.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('MacOSX')  # Use native macOS backend for interactive display
import matplotlib.pyplot as plt
from astropy.io import ascii


def latex_formatting():
    """Apply LaTeX formatting to matplotlib plots with Computer Modern Serif."""
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Computer Modern']
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10


def should_use_latex():
    """Check if LaTeX formatting should be applied by looking for formatting_on.txt."""
    # Check current working directory first
    if os.path.exists('formatting_on.txt'):
        with open('formatting_on.txt', 'r') as f:
            content = f.read().strip().lower()
            return content == 'true'
    
    # Then check script's parent directory
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    formatting_file = os.path.join(script_dir, 'formatting_on.txt')
    
    if os.path.exists(formatting_file):
        with open(formatting_file, 'r') as f:
            content = f.read().strip().lower()
            return content == 'true'
    
    return False


def load_catalog(catalog_path):
    """Load SExtractor ASCII catalog."""
    try:
        data = ascii.read(catalog_path, format='sextractor')
        return data
    except Exception as e:
        print(f"Error loading {catalog_path}: {e}")
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


def plot_cmd(band1_cat, band2_cat, output_path=None, class_star_threshold=0.10):
    """
    Create color-magnitude diagram.
    
    x-axis: band1 magnitude
    y-axis: band2-band1 color
    
    Stars (CLASS_STAR >= class_star_threshold) in red, galaxies in black.
    """
    # Apply LaTeX formatting if enabled
    if should_use_latex():
        latex_formatting()
    
    # Match catalogs by NUMBER
    band1_idx, band2_idx = match_catalogs_by_number(band1_cat, band2_cat)
    band1_mag = np.array(band1_cat['MAG_ISO'][band1_idx])
    band2_mag = np.array(band2_cat['MAG_ISO'][band2_idx])
    class_star_band1 = np.array(band1_cat['CLASS_STAR'][band1_idx])
    class_star_band2 = np.array(band2_cat['CLASS_STAR'][band2_idx])
    
    # Classify stars (if either band indicates star)
    is_star = (class_star_band1 >= class_star_threshold) | (class_star_band2 >= class_star_threshold)
    
    # Calculate color
    color = band2_mag - band1_mag
    
    # Use SourceExtractor's CLASS_STAR for star-galaxy separation
    stars = is_star
    galaxies = ~is_star
    print(f"\nTotal objects: {len(band1_mag)}")
    print(f"  Stars (CLASS_STAR >= {class_star_threshold}): {np.sum(stars)}")
    print(f"  Galaxies: {np.sum(galaxies)}")
    print(f"\nBand1 magnitude range: {band1_mag.min():.2f} to {band1_mag.max():.2f}")
    print(f"Band2-Band1 color range: {color.min():.2f} to {color.max():.2f}")
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot galaxies as black
    if np.sum(galaxies) > 0:
        ax.scatter(band1_mag[galaxies], color[galaxies], 
                  c='black', marker='o', s=30, alpha=0.6, edgecolors='none',
                  label=rf'Galaxies (CLASS_STAR $< {class_star_threshold}$)')
    
    # Plot stars as red
    if np.sum(stars) > 0:
        ax.scatter(band1_mag[stars], color[stars], 
                  c='red', marker='+', s=50, alpha=0.8, edgecolors='none',
                  label=rf'Stars (CLASS_STAR $>= {class_star_threshold}$)')
    
    ax.set_xlabel('Band1 Magnitude')
    ax.set_ylabel('Band2-Band1 Color')
    ax.set_title('Color-Magnitude Diagram')
    ax.grid(False)
    ax.legend(loc='best', framealpha=0.9)
    
    # Configure ticks: inside, on all sides
    ax.tick_params(direction='in', which='both', top=True, right=True)
    
    plt.tight_layout()
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {output_path}")
    
    # Show interactive window (blocking on macOS)
    print("Plot displayed. Close the window to exit.")
    plt.show()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Create color-magnitude diagram from dual-band catalogs')
    parser.add_argument('--band1-catalog', dest='band1_catalog', required=True,
                        help='Path to band1 (detection) catalog')
    parser.add_argument('--band2-catalog', dest='band2_catalog', required=True,
                        help='Path to band2 (measurement) catalog')
    parser.add_argument('--output', required=True, help='Output plot path')
    parser.add_argument('--class-star-threshold', dest='class_star_threshold', type=float, default=0.10,
                        help='CLASS_STAR threshold for star/galaxy separation (default: 0.10)')
    
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
    
    # Create plot
    print(f"\nCreating color-magnitude diagram...")
    plot_cmd(band1_cat, band2_cat, output_path, args.class_star_threshold)
