#!/usr/bin/env python
"""
Step 5: Run lenstool for lens modeling.

Once you've got your catalog ready, this script runs lenstool to fit
the lens model to your data. Make sure you have lenstool installed first.

Note: Requires lenstool - install from http://projets.lam.fr/projects/lenstool
"""

import sys
import argparse
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LenstoolRunner:
    """Wrapper for running lenstool. Handles setup and execution."""
    
    def __init__(self, config_file):
        """
        Initialize the lenstool runner.
        
        Parameters
        ----------
        config_file : str
            Path to your lenstool configuration file
        """
        self.config_file = Path(config_file)
        self._check_lenstool()
    
    def _check_lenstool(self):
        """Make sure lenstool is installed and accessible."""
        try:
            subprocess.run(['lenstool', '--help'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Can't find lenstool. Install it from:")
            logger.error("  http://projets.lam.fr/projects/lenstool")
            sys.exit(1)
    
    def run(self, output_dir=None):
        """
        Execute lenstool.
        
        Parameters
        ----------
        output_dir : str, optional
            Where to put the output files. If not specified,
            lenstool uses whatever's in the config file.
        """
        if not self.config_file.exists():
            logger.error(f"Can't find config file: {self.config_file}")
            sys.exit(1)
        
        cmd = ['lenstool', str(self.config_file)]
        
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Running lenstool with: {' '.join(cmd)}")
        logger.info("This might take a few minutes, so go grab some coffee...")
        
        try:
            result = subprocess.run(cmd, capture_output=False)
            if result.returncode == 0:
                logger.info("Done! lenstool finished successfully")
            else:
                logger.error(f"Oops, lenstool exited with code {result.returncode}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Something went wrong running lenstool: {e}")
            sys.exit(1)


def create_default_config(output_file):
    """
    Create a template lenstool configuration file.
    
    This gives you a starting point - adjust the parameters
    for your specific lens system.
    
    Parameters
    ----------
    output_file : str
        Where to save the template configuration
    """
    template = """# lenstool configuration file for COOLJ0221
# See http://projets.lam.fr/projects/lenstool for full documentation

# Image properties
image {
    pixel_size 0.262  # DECaLS pixel size in arcsec
    xnum 300          # x dimension of images
    ynum 300          # y dimension of images
}

# Background source model
source {
    type 0            # 0=pointmass, 1=sphere, 2=NFW, etc.
    x 150.0           # Source x position (pixels)
    y 150.0           # Source y position (pixels)
    radius 0.1        # Source radius
}

# Lens model
potential {
    name coreNFW      # NFW with cored center
    x 150.0           # Lens x position (pixels)
    y 150.0           # Lens y position (pixels)
    vx 0.0            # Velocity dispersion x component
    vy 0.0            # Velocity dispersion y component
    b0 1000.0         # Core radius
    epsilon 0.3       # Ellipticity
    theta 0.0         # Position angle (degrees)
}

# Optimization
optimize {
    method levenbergmarquardt  # Optimization algorithm
    niter 100                   # Maximum iterations
    convergence 1e-4           # Convergence criterion
}

# Output
output {
    file best_model.out
}
"""
    
    with open(output_file, 'w') as f:
        f.write(template)
    logger.info(f"Created template config: {output_file}")


def main():
    """Set up and run lens modeling with lenstool."""
    parser = argparse.ArgumentParser(description='Run lenstool lens modeling')
    parser.add_argument(
        '--config',
        default='config/lenstool_config.txt',
        help='lenstool configuration file'
    )
    parser.add_argument(
        '--create-template',
        action='store_true',
        help='Create a template configuration file'
    )
    parser.add_argument(
        '--output-dir',
        default='outputs/models',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Create template if requested
    if args.create_template:
        create_default_config(args.config)
        print(f"\nTemplate created: {args.config}")
        print("Edit this file with your lens/source parameters and then run again.")
        sys.exit(0)
    
    print("lenstool Lens Modeling")
    print(f"  Config: {args.config}")
    print(f"  Output: {args.output_dir}")
    
    try:
        runner = LenstoolRunner(args.config)
        runner.run(args.output_dir)
        
        print(f"\nLens modeling complete!")
        print(f"Results in {args.output_dir}/")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
