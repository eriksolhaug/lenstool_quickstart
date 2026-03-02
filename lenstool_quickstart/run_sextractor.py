#!/usr/bin/env python
"""
Run SExtractor to extract sources from DECaLS imaging.

Uses z-band as detection image and measures photometry.
Requires SExtractor: http://www.astromatic.net/software/sextractor
Install via: brew install sextractor (macOS) or apt-get install sextractor (Linux)
"""

import sys
import argparse
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SExtractorRunner:
    """Wrapper for running SExtractor on images."""
    
    def __init__(self, config_file=None):
        """
        Initialize SExtractor runner.
        
        Parameters
        ----------
        config_file : str, optional
            Path to SExtractor config
        """
        self.config_file = config_file
        self._check_sextractor()
    
    def _check_sextractor(self):
        """Make sure SExtractor is installed and in PATH."""
        try:
            subprocess.run(['sex', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Can't find SExtractor. Install it with:")
            logger.error("  macOS: brew install sextractor")
            logger.error("  Linux: apt-get install sextractor")
            sys.exit(1)
    
    def extract(self, detection_image, measure_images=None, output_catalog='output.cat'):
        """
        Run SExtractor to extract sources.
        
        Parameters
        ----------
        detection_image : str
            Detection image path
        measure_images : list, optional
            Images to measure photometry on
        output_catalog : str, optional
            Output catalog filename
        """
        if measure_images is None:
            measure_images = [detection_image]
        
        # Build SExtractor command
        # Note: SExtractor takes detection image first, then measurement image(s)
        cmd = ['sex', detection_image]
        
        # Add measurement images (only one for basic photometry)
        # SExtractor has limitations on multiple measurement images in single call
        if len(measure_images) > 1:
            # Use the detection image for measurement, then we can add others separately
            cmd.append(measure_images[0])
        
        cmd.extend([
            '-CATALOG_NAME', output_catalog,
            '-CATALOG_TYPE', 'ASCII_HEAD',
        ])
        
        if self.config_file:
            cmd.extend(['-c', self.config_file])
        
        logger.info(f"Running SExtractor: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"SExtractor error: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, cmd)
            logger.info(f"Catalog written to {output_catalog}")
        except subprocess.CalledProcessError as e:
            logger.error(f"SExtractor failed: {e}")
            sys.exit(1)


def main():
    """Run source extraction."""
    parser = argparse.ArgumentParser(
        description='Extract sources with SExtractor'
    )
    parser.add_argument(
        '--detection',
        default='z',
        choices=['g', 'r', 'z'],
        help='Detection band (default: z)'
    )
    parser.add_argument(
        '--measure',
        nargs='+',
        default=['g', 'r', 'z'],
        help='Bands to measure photometry (default: g r z)'
    )
    parser.add_argument(
        '--data-dir',
        default='data/imaging',
        help='Directory with imaging data'
    )
    parser.add_argument(
        '--config',
        help='SExtractor configuration file'
    )
    parser.add_argument(
        '--output-dir',
        default='data/catalogs',
        help='Output directory for catalogs'
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = Path(args.data_dir)
    
    print("SExtractor Source Extraction")
    print(f"  Detection image: {args.detection}-band")
    print(f"  Measure bands: {', '.join(args.measure)}")
    print(f"  Output directory: {output_dir}")
    
    # Check for input images
    detection_image = data_dir / f"cj0221_{args.detection}.fits"
    if not detection_image.exists():
        print(f"\nWarning: Detection image not found: {detection_image}")
        print("Please run fetch_decals_data.py first")
        sys.exit(1)
    
    # Initialize SExtractor runner
    runner = SExtractorRunner(config_file=args.config)
    
    # Extract sources
    measure_images = [
        str(data_dir / f"cj0221_{band}.fits") for band in args.measure
    ]
    
    output_catalog = str(output_dir / "sources.cat")
    
    try:
        runner.extract(str(detection_image), measure_images, output_catalog)
        print(f"\nSourceExtraction complete!")
        print(f"Catalog: {output_catalog}")
        print("\nNext step: Filter catalog by stellarity and red sequence")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
