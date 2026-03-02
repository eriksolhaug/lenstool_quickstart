"""
Data fetching utilities for DECaLS survey imaging.

This module handles pulling imaging data from the DECaLS survey.
Just give it coordinates and it'll grab the data for you.
"""

import warnings
from typing import Tuple, Optional
import numpy as np
import requests
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u


class DECaLSFetcher:
    """
    Fetch imaging data from the DECaLS survey.
    
    Just initialize this with sky coordinates and a cutout size,
    then call fetch() to get the images. It'll grab g, r, and z-band
    data by default, but you can specify which bands you want.
    
    Parameters
    ----------
    ra : float
        Right ascension in degrees (ICRS)
    dec : float
        Declination in degrees (ICRS)
    size : int, optional
        Size of cutout in pixels (default: 300)
    bands : list of str, optional
        Which bands to retrieve ('g', 'r', 'z'; default: all)
    """
    
    DECALS_BASE_URL = "https://www.legacysurvey.org/data/cutouts"
    
    def __init__(
        self,
        ra: float,
        dec: float,
        size: int = 300,
        bands: Optional[list] = None,
    ):
        """Initialize DECaLS fetcher."""
        self.ra = ra
        self.dec = dec
        self.size = size
        self.bands = bands or ["g", "r", "z"]
        
        # Quick sanity check on the coordinates
        if not (-90 <= dec <= 90):
            raise ValueError(f"Declination out of range: {dec}")
        if not (0 <= ra < 360):
            raise ValueError(f"RA out of range: {ra}")
    
    def fetch(self) -> dict:
        """
        Fetch imaging data from DECaLS.
        
        Grabs the images and some metadata about what we got.
        Returns a dict with 'images' (the actual image data) and
        'metadata' (info about the cutout location and bands).
        
        Returns
        -------
        dict
            Dictionary with keys 'images' and 'metadata'
        """
        images = {}
        metadata = {
            'ra': self.ra,
            'dec': self.dec,
            'size': self.size,
            'bands': self.bands,
        }
        
        for band in self.bands:
            try:
                url = self._construct_url(band)
                hdul = fits.open(url)
                images[band] = hdul[0].data
                hdul.close()
            except Exception as e:
                # If one band fails, warn but keep going
                warnings.warn(f"Couldn't get {band}-band data: {e}")
        
        return {
            'images': images,
            'metadata': metadata,
        }
    
    def _construct_url(self, band: str) -> str:
        """Build the DECaLS cutout URL for a given band."""
        if band not in self.bands:
            raise ValueError(f"Invalid band: {band}")
        return f"{self.DECALS_BASE_URL}/url?ra={self.ra}&dec={self.dec}&size={self.size}&band={band}"


class LSSTFetcher:
    """
    Placeholder for future LSST data fetching.
    """
    
    def __init__(self, ra: float, dec: float, size: int = 300):
        """Initialize LSST fetcher."""
        self.ra = ra
        self.dec = dec
        self.size = size
        raise NotImplementedError("LSST data fetching not yet available")
