#!/usr/bin/env python
"""
Download DECaLS imaging for COOLJ0221.

Fetches g, r, and z-band imaging from the DECaLS survey.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import lenstool_quickstart
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lenstool_quickstart import DECaLSFetcher


def main():
    """Download DECaLS imaging data for the cluster."""
    parser = argparse.ArgumentParser(description='Download DECaLS imaging')
    parser.add_argument(
        '--ra',
        type=float,
        default=35.3367,  # COOLJ0221 RA
        help='Right ascension (degrees)'
    )
    parser.add_argument(
        '--dec',
        type=float,
        default=2.6919,  # COOLJ0221 Dec
        help='Declination (degrees)'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=500,
        help='Cutout size in pixels'
    )
    parser.add_argument(
        '--bands',
        nargs='+',
        default=['g', 'r', 'z'],
        help='Bands to download (default: g r z)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/imaging',
        help='Output directory for images'
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Fetching DECaLS imaging for COOLJ0221")
    print(f"  RA: {args.ra}, Dec: {args.dec}")
    print(f"  Bands: {', '.join(args.bands)}")
    print(f"  Size: {args.size} pixels")
    print(f"  Output: {output_dir}")
    
    try:
        fetcher = DECaLSFetcher(
            ra=args.ra,
            dec=args.dec,
            size=args.size,
            bands=args.bands
        )
        
        data = fetcher.fetch()
        images = data['images']
        
        print(f"\nSuccessfully fetched {len(images)} bands:")
        for band, image in images.items():
            print(f"  {band}-band: {image.shape} pixels")
        
        print("\nImages ready in data/imaging/")
        print("Next step: Run source extractor")
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
