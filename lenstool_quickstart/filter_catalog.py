#!/usr/bin/env python
"""Filter source catalog by CLASS_STAR and magnitude."""

import sys
import numpy as np
import argparse
from astropy.io import ascii


def load_catalog(path):
    """Load SExtractor ASCII catalog."""
    try:
        return ascii.read(path)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Filter source catalog')
    parser.add_argument('--catalog', required=True, help='Input catalog')
    parser.add_argument('--output', required=True, help='Output catalog')
    parser.add_argument('--class-star-max', type=float, default=0.5,
                        help='Maximum CLASS_STAR (galaxies only)')
    parser.add_argument('--mag-min', type=float, default=15.0,
                        help='Minimum magnitude')
    parser.add_argument('--mag-max', type=float, default=28.0,
                        help='Maximum magnitude')
    
    args = parser.parse_args()
    
    cat = load_catalog(args.catalog)
    print(f"Loaded {len(cat)} sources")
    
    # Filter by CLASS_STAR (galaxies)
    mask_gal = cat['CLASS_STAR'] <= args.class_star_max
    print(f"  Galaxies (CLASS_STAR <= {args.class_star_max}): {np.sum(mask_gal)}")
    
    # Filter by magnitude
    mask_mag = (cat['MAG_ISO'] >= args.mag_min) & (cat['MAG_ISO'] <= args.mag_max)
    print(f"  Magnitude range {args.mag_min}-{args.mag_max}: {np.sum(mask_mag)}")
    
    # Combined
    mask = mask_gal & mask_mag
    print(f"Total passing: {np.sum(mask)}/{len(cat)}")
    
    # Write
    filtered = cat[mask]
    ascii.write(filtered, args.output, format='ascii.commented_header', overwrite=True)
    print(f"Wrote {args.output}")


if __name__ == '__main__':
    main()
