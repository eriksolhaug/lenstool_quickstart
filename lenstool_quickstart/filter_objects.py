#!/usr/bin/env python
"""Filter source catalog by CLASS_STAR, magnitude, and color."""

import numpy as np
from astropy.io import ascii


# ============================================================================
# ## FILTER
# Edit these parameters to change filtering behavior
# ============================================================================

INPUT_CATALOG_1 = 'catalogs/coolj1153_sources_f814w.cat'
INPUT_CATALOG_2 = 'catalogs/coolj1153_sources_f606w.cat'
OUTPUT_CATALOG = 'catalogs/coolj1153_filtered.cat'

# Galaxy selection: CLASS_STAR <= this value
CLASS_STAR_MAX = 0.95

# Magnitude filtering (in catalog 1)
MAG_MIN = 0.0
MAG_MAX = 27.0

# Color filtering
COLOR_MIN = 0.9
COLOR_MAX = 1.3

# Set to False to skip color filtering
USE_COLOR_FILTER = True

# ============================================================================


def load_catalog(path):
    """Load SExtractor ASCII catalog."""
    return ascii.read(path)


def match_catalogs_by_number(cat1, cat2):
    """Match two catalogs by NUMBER column.
    
    Returns indices into cat1 and cat2 of matching objects.
    """
    numbers1 = np.array(cat1['NUMBER'])
    numbers2 = np.array(cat2['NUMBER'])
    
    idx1_list = []
    idx2_list = []
    
    for i, num in enumerate(numbers1):
        # Find matching number in catalog 2
        match_idx = np.where(numbers2 == num)[0]
        if len(match_idx) > 0:
            idx1_list.append(i)
            idx2_list.append(match_idx[0])
    
    return np.array(idx1_list), np.array(idx2_list)


def main():
    # Load catalogs
    cat1 = load_catalog(INPUT_CATALOG_1)
    print(f"Loaded {len(cat1)} sources from {INPUT_CATALOG_1}")
    
    if USE_COLOR_FILTER:
        cat2 = load_catalog(INPUT_CATALOG_2)
        print(f"Loaded {len(cat2)} sources from {INPUT_CATALOG_2}")
        
        # Match catalogs
        idx1, idx2 = match_catalogs_by_number(cat1, cat2)
        print(f"Matched {len(idx1)} sources between catalogs")
    else:
        idx1 = np.arange(len(cat1))
    
    # Build filtering mask (start with all True, then AND conditions)
    mask = np.ones(len(cat1), dtype=bool)
    
    # Filter 1: Galaxy selection (CLASS_STAR <= threshold)
    mask_class = np.array(cat1['CLASS_STAR']) <= CLASS_STAR_MAX
    n_class = np.sum(mask_class)
    print(f"  CLASS_STAR <= {CLASS_STAR_MAX}: {n_class} objects")
    mask &= mask_class
    
    # Filter 2: Magnitude range
    mag = np.array(cat1['MAG_ISO'])
    mask_mag = (mag >= MAG_MIN) & (mag <= MAG_MAX)
    n_mag = np.sum(mask_mag)
    print(f"  Magnitude [{MAG_MIN:.1f}, {MAG_MAX:.1f}]: {n_mag} objects")
    mask &= mask_mag
    
    # Filter 3: Color range (if enabled)
    if USE_COLOR_FILTER:
        # Calculate color for matched objects
        mag1_matched = np.array(cat1['MAG_ISO'][idx1])
        mag2_matched = np.array(cat2['MAG_ISO'][idx2])
        color = mag2_matched - mag1_matched
        
        # Create color mask for matched objects
        color_mask_matched = (color >= COLOR_MIN) & (color <= COLOR_MAX)
        n_color_matched = np.sum(color_mask_matched)
        
        # Extend color mask to full catalog (unmatched objects are False)
        color_mask_full = np.zeros(len(cat1), dtype=bool)
        color_mask_full[idx1] = color_mask_matched
        
        print(f"  Color [{COLOR_MIN:.2f}, {COLOR_MAX:.2f}]: {n_color_matched} objects")
        print(f"  Color range in data: [{np.min(color):.2f}, {np.max(color):.2f}]")
        mask &= color_mask_full
    
    # Apply combined mask
    n_passing = np.sum(mask)
    print(f"\nTotal passing all filters: {n_passing}/{len(cat1)}")
    
    # Write output
    filtered = cat1[mask]
    ascii.write(filtered, OUTPUT_CATALOG, format='commented_header', overwrite=True)
    print(f"Wrote {len(filtered)} objects to {OUTPUT_CATALOG}")


if __name__ == '__main__':
    main()
