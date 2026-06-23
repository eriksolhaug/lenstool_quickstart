#!/usr/bin/env python
"""Create DS9 region file for filtered objects."""

import argparse
import numpy as np
from astropy.io import ascii


def main():
    parser = argparse.ArgumentParser(description='Create DS9 region file for filtered objects')
    parser.add_argument('--catalog', required=True, help='Filtered catalog')
    parser.add_argument('--output', required=True, help='Output region file')
    parser.add_argument('--radius', type=float, default=1.0,
                        help='Radius of circles in arcseconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Load catalog
    cat = ascii.read(args.catalog)
    print(f"Loaded {len(cat)} objects from {args.catalog}")
    
    # Extract world coordinates
    ra = np.array(cat['X_WORLD'])
    dec = np.array(cat['Y_WORLD'])
    
    # Write DS9 region file
    with open(args.output, 'w') as f:
        # DS9 header
        f.write("# Region file format: DS9 version 4.1\n")
        f.write("global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal\" ")
        f.write("select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n")
        f.write("fk5\n")
        
        # Write circles for all filtered objects
        for i in range(len(ra)):
            f.write(f"circle({ra[i]:.6f},{dec[i]:.6f},{args.radius}\") # color=orange\n")
    
    print(f"Wrote {len(cat)} regions to {args.output}")


if __name__ == '__main__':
    main()
