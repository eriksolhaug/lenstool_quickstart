'''
Calculate HST zero point given the keywords in the header of the fits file,
using this formula 
ZPAB=−2.5∗log10(PHOTFLAM)−5∗log10(PHOTPLAM)−2.408
from https://www.stsci.edu/hst/instrumentation/acs/data-analysis/zeropoints
'''

# Initialize main
if __name__ == "__main__":
    import argparse
    import astropy.io.fits as fits
    import numpy as np

    parser = argparse.ArgumentParser(description='Calculate HST zero point from fits header')
    parser.add_argument('fits_file', type=str, help='Path to the fits file')
    args = parser.parse_args()

    # Open the fits file and read the header
    with fits.open(args.fits_file) as hdul:
        header = hdul[0].header

    # Extract PHOTFLAM and PHOTPLAM from the header
    photflam = header.get('PHOTFLAM')
    photplam = header.get('PHOTPLAM')

    if photflam is None or photplam is None:
        raise ValueError("PHOTFLAM or PHOTPLAM not found in the FITS header.")

    # Calculate the zero point
    zpab = -2.5 * np.log10(photflam) - 5 * np.log10(photplam) - 2.408

    print(f"HST Zero Point (ZPAB): {zpab:.4f}")