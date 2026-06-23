# Extract HST photometric zeropoints from FITS header
# Works for HST/ACS, WFC3, and other calibrated HST data

import argparse
import numpy as np
from astropy.io import fits

def extract_zeropoints_from_fits(fits_file):
    """
    Extract photometric calibration keywords from HST FITS header.
    
    Returns dictionary with PHOTFLAM, PHOTZPT, PHOTPLAM and calculated magnitude systems.
    """
    with fits.open(fits_file) as hdul:
        header = hdul[0].header
        
        # Extract primary calibration keywords (from HST pipeline)
        photflam = header.get('PHOTFLAM', None)
        photzpt = header.get('PHOTZPT', None)
        photplam = header.get('PHOTPLAM', None)
        photcorr = header.get('PHOTCORR', None)
        
        if photflam is None or photzpt is None or photplam is None:
            print(f"WARNING: Missing photometric keywords in {fits_file}")
            print(f"  PHOTFLAM: {photflam}")
            print(f"  PHOTZPT: {photzpt}")
            print(f"  PHOTPLAM: {photplam}")
            return None
        
        print(f"File: {fits_file}")
        print(f"Calibration Status: {photcorr}")
        print(f"\nRaw FITS Keywords:")
        print(f"  PHOTFLAM (ergs/cm²/Å/electron): {photflam:.6e}")
        print(f"  PHOTZPT (ST mag): {photzpt:.4f}")
        print(f"  PHOTPLAM (Angstroms): {photplam:.2f}")
        
        # STMAG zeropoint (already in header, just report it)
        stmag_zp = photzpt
        
        # Calculate ABMAG zeropoint
        # Formula: ABMAG_ZP = STMAG_ZP - 5*log10(PHOTPLAM) + 18.6921
        abmag_zp = stmag_zp - 5 * np.log10(photplam) + 18.6921
        
        # VEGAMAG zeropoint (requires Vega spectrum, approximate as -0.48 below ABMAG)
        # For better accuracy, you would need the Vega spectrum calibration
        vegamag_zp = abmag_zp - 0.48  # Rough approximation
        
        print(f"\nCalculated Zeropoints:")
        print(f"  STMAG ZP: {stmag_zp:.4f}")
        print(f"  ABMAG ZP: {abmag_zp:.4f}")
        print(f"  VEGAMAG ZP (approx): {vegamag_zp:.4f}")
        
        return {
            'photflam': photflam,
            'photzpt': photzpt,
            'photplam': photplam,
            'stmag_zp': stmag_zp,
            'abmag_zp': abmag_zp,
            'vegamag_zp': vegamag_zp
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract HST photometric zeropoints from FITS header'
    )
    parser.add_argument('fits_file', help='Path to HST FITS image')
    args = parser.parse_args()
    
    extract_zeropoints_from_fits(args.fits_file)

