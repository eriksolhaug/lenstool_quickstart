#!/usr/bin/env python
"""
Filter catalog by stellarity and red sequence.

Separates stars from galaxies and selects the red sequence
galaxies that we care about for the lens modeling.
"""

import sys
import argparse
from pathlib import Path
import logging

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CatalogFilter:
    """Filter astronomical catalogs by various criteria."""
    
    def __init__(self, catalog_file):
        """
        Initialize the catalog filter.
        
        Parameters
        ----------
        catalog_file : str
            Path to your catalog file
        """
        self.catalog_file = Path(catalog_file)
        self.data = None
    
    def load_catalog(self):
        """Load the catalog from file."""
        try:
            # Read as a structured array - adapt if format is different
            self.data = np.genfromtxt(
                self.catalog_file,
                dtype=None,
                encoding='utf-8',
                skip_header=30,  # SExtractor headers
                names=True
            )
            logger.info(f"Loaded {len(self.data)} sources")
        except Exception as e:
            logger.error(f"Couldn't load catalog: {e}")
            raise
    
    def filter_stellarity(self, min_stellarity=0.0, max_stellarity=0.5):
        """
        Filter by stellarity (CLASS_STAR parameter).
        
        Parameters
        ----------
        min_stellarity : float
            Minimum stellarity (0=galaxy, 1=star)
        max_stellarity : float
            Maximum stellarity
        
        Returns
        -------
        np.ndarray
            Boolean mask for sources passing the filter
        """
        try:
            class_star = self.data['CLASS_STAR']
            mask = (class_star >= min_stellarity) & (class_star <= max_stellarity)
            logger.info(f"Stellarity filter: {np.sum(mask)}/{len(self.data)} sources pass")
            return mask
        except KeyError:
            logger.warning("CLASS_STAR not found - skipping stellarity filter")
            return np.ones(len(self.data), dtype=bool)
    
    def filter_red_sequence(self, color_column_1='MAG_G', color_column_2='MAG_Z',
                          min_color=0.0, max_color=2.0):
        """
        Filter by red sequence color cut.
        
        Parameters
        ----------
        color_column_1 : str
            First magnitude column (shorter wavelength)
        color_column_2 : str
            Second magnitude column (longer wavelength)
        min_color : float
            Minimum color
        max_color : float
            Maximum color
        
        Returns
        -------
        np.ndarray
            Boolean mask for red sequence galaxies
        """
        try:
            mag1 = self.data[color_column_1]
            mag2 = self.data[color_column_2]
            color = mag1 - mag2
            mask = (color >= min_color) & (color <= max_color)
            logger.info(f"Red sequence filter: {np.sum(mask)}/{len(self.data)} sources pass")
            return mask
        except KeyError as e:
            logger.warning(f"Color columns not found: {e}")
            return np.ones(len(self.data), dtype=bool)
    
    def filter_magnitude(self, mag_column='MAG_AUTO', min_mag=0.0, max_mag=30.0):
        """
        Filter by magnitude.
        
        Parameters
        ----------
        mag_column : str
            Magnitude column name
        min_mag : float
            Minimum magnitude
        max_mag : float
            Maximum magnitude
        
        Returns
        -------
        np.ndarray
            Mask of sources in magnitude range
        """
        try:
            mag = self.data[mag_column]
            mask = (mag >= min_mag) & (mag <= max_mag)
            logger.info(f"Magnitude filter: {np.sum(mask)}/{len(self.data)} sources pass")
            return mask
        except KeyError:
            logger.warning(f"Magnitude column '{mag_column}' not found")
            return np.ones(len(self.data), dtype=bool)
    
    def write_filtered_catalog(self, mask, output_file):
        """
        Write filtered catalog to file.
        
        Parameters
        ----------
        mask : np.ndarray
            Boolean mask of sources to keep
        output_file : str
            Output catalog filename
        """
        filtered_data = self.data[mask]
        np.savetxt(output_file, filtered_data, fmt='%s')
        logger.info(f"Wrote {len(filtered_data)} sources to {output_file}")


def main():
    """Run catalog filtering."""
    parser = argparse.ArgumentParser(description='Filter catalog')
    parser.add_argument(
        '--catalog',
        default='data/catalogs/sources.cat',
        help='Input catalog file'
    )
    parser.add_argument(
        '--min-stellarity',
        type=float,
        default=0.0,
        help='Minimum stellarity (0=galaxy, 1=star; default: 0.0)'
    )
    parser.add_argument(
        '--max-stellarity',
        type=float,
        default=0.5,
        help='Maximum stellarity (default: 0.5, selects galaxies)'
    )
    parser.add_argument(
        '--min-color',
        type=float,
        default=0.0,
        help='Minimum g-z color (default: 0.0)'
    )
    parser.add_argument(
        '--max-color',
        type=float,
        default=2.0,
        help='Maximum g-z color (default: 2.0)'
    )
    parser.add_argument(
        '--min-mag',
        type=float,
        default=15.0,
        help='Minimum magnitude (default: 15.0)'
    )
    parser.add_argument(
        '--max-mag',
        type=float,
        default=28.0,
        help='Maximum magnitude (default: 28.0)'
    )
    parser.add_argument(
        '--output',
        default='sources_filtered.cat',
        help='Output filtered catalog'
    )
    
    args = parser.parse_args()
    
    print("Catalog Filtering")
    print(f"  Input: {args.catalog}")
    print(f"  Stellarity: {args.min_stellarity} - {args.max_stellarity}")
    print(f"  Color (g-z): {args.min_color} - {args.max_color}")
    print(f"  Magnitude: {args.min_mag} - {args.max_mag}")
    
    try:
        # Load and filter
        filter_obj = CatalogFilter(args.catalog)
        filter_obj.load_catalog()
        
        # Apply filters
        mask_stellar = filter_obj.filter_stellarity(
            args.min_stellarity,
            args.max_stellarity
        )
        mask_color = filter_obj.filter_red_sequence(
            min_color=args.min_color,
            max_color=args.max_color
        )
        mask_mag = filter_obj.filter_magnitude(
            min_mag=args.min_mag,
            max_mag=args.max_mag
        )
        
        # Combine masks
        combined_mask = mask_stellar & mask_color & mask_mag
        logger.info(f"Total: {np.sum(combined_mask)}/{len(filter_obj.data)} sources pass all filters")
        
        # Write output
        filter_obj.write_filtered_catalog(combined_mask, args.output)
        
        print(f"\nFiltering complete!")
        print(f"Output: {args.output}")
        print("\nNext step: Convert to lenstool format")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
