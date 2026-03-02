#!/usr/bin/env python
"""
Create color-magnitude diagram from dual-image SExtractor run.
Uses z-band as detection image and measures both r and z magnitudes.
x-axis: z-band magnitude
y-axis: r-z color (r_mag - z_mag)
Stars (CLASS_STAR >= 0.10) are plotted in red, galaxies in black.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii


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


def load_catalog(catalog_path):
    """Load SExtractor ASCII_HEAD catalog."""
    try:
        data = ascii.read(catalog_path, format='sextractor')
        return data
    except Exception as e:
        print(f"Error loading {catalog_path}: {e}")
        return None


def match_catalogs_by_number(z_cat, r_cat):
    """
    Match z-band and r-band catalogs by NUMBER column.
    Returns matched indices for both catalogs.
    """
    z_numbers = np.array(z_cat['NUMBER'])
    r_numbers = np.array(r_cat['NUMBER'])
    
    # Find indices in r_cat that match numbers in z_cat
    matched_z_idx = []
    matched_r_idx = []
    
    for i, z_num in enumerate(z_numbers):
        # Find this number in r_cat
        r_match = np.where(r_numbers == z_num)[0]
        if len(r_match) > 0:
            matched_z_idx.append(i)
            matched_r_idx.append(r_match[0])
    
    return np.array(matched_z_idx), np.array(matched_r_idx)


def plot_cmd(z_cat, r_cat, output_path=None):
    """
    Create color-magnitude diagram.
    
    x-axis: z-band magnitude
    y-axis: r-z color
    
    Stars (CLASS_STAR >= 0.10) in red, galaxies in black.
    """
    if z_cat is None or r_cat is None:
        print("ERROR: One or both catalogs are missing")
        return
    
    # Apply LaTeX formatting if enabled
    if should_use_latex():
        latex_formatting()
    
    # Match catalogs by NUMBER
    z_idx, r_idx = match_catalogs_by_number(z_cat, r_cat)
    
    # Extract magnitudes and classification
    z_mag = np.array(z_cat['MAG_ISO'][z_idx])
    r_mag = np.array(r_cat['MAG_ISO'][r_idx])
    class_star_z = np.array(z_cat['CLASS_STAR'][z_idx])
    class_star_r = np.array(r_cat['CLASS_STAR'][r_idx])
    
    # Classify stars (if either band indicates star)
    is_star = (class_star_z >= 0.10) | (class_star_r >= 0.10)
    
    # Calculate color
    color = r_mag - z_mag
    
    # Separate stars and galaxies
    stars = is_star
    galaxies = ~is_star
    
    print(f"\nTotal objects: {len(z_mag)}")
    print(f"  Stars (CLASS_STAR >= 0.10): {np.sum(stars)}")
    print(f"  Galaxies: {np.sum(galaxies)}")
    print(f"\nz-band magnitude range: {z_mag.min():.2f} to {z_mag.max():.2f}")
    print(f"r-z color range: {color.min():.2f} to {color.max():.2f}")
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot galaxies (black) first
    if np.sum(galaxies) > 0:
        ax.scatter(z_mag[galaxies], color[galaxies], 
                  c='black', marker='o', s=30, alpha=0.6, label='Galaxies')
    
    # Plot stars (red) on top
    if np.sum(stars) > 0:
        ax.scatter(z_mag[stars], color[stars], 
                  c='red', marker='*', s=200, alpha=0.8, label='Stars')
    
    ax.set_xlabel('z-band Magnitude')
    ax.set_ylabel('r-z Color')
    ax.set_title('COOLJ0221 - Color-Magnitude Diagram (z-band detection)')
    ax.grid(False)
    ax.legend(loc='best', framealpha=0.9)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {output_path}")
    else:
        plt.show()
    
    plt.close()


if __name__ == '__main__':
    # Default paths for dual-image workflow
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data', 'catalogs')
    
    # z-band catalog (z-band single image detection/measurement)
    z_cat_path = os.path.join(data_dir, 'cj0221_sources_z.cat')
    # r-band catalog (dual-image with z-detection, r-measurement)
    r_cat_path = os.path.join(data_dir, 'cj0221_sources_z_rphot.cat')
    output_path = os.path.join(project_dir, 'outputs', 'plots', 'cmd.pdf')
    
    # Allow command-line override
    if len(sys.argv) > 1:
        z_cat_path = sys.argv[1]
    if len(sys.argv) > 2:
        r_cat_path = sys.argv[2]
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    
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
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create plot
    print(f"\nCreating color-magnitude diagram...")
    plot_cmd(z_cat, r_cat, output_path)
