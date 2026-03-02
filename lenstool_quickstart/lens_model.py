"""
Lens model fitting and analysis.

This is where the real work happens - fitting lens models to your data.
Supports simple profiles like SIS and NFW.
"""

import warnings
from typing import Optional, Tuple, Dict, Any
import numpy as np
from scipy import optimize
from scipy.ndimage import gaussian_filter


class LensModel:
    """
    Basic lens model for gravitational lensing analysis.
    
    I built this to handle common lens model profiles.
    Currently supports SIS (Singular Isothermal Sphere) and NFW.
    Initialize with your choice of profile, then call fit() to
    fit it to your imaging data.
    
    Parameters
    ----------
    profile : str, optional
        Which profile to use: 'SIS' or 'NFW' (default: 'SIS')
    """
    
    SUPPORTED_PROFILES = ['SIS', 'NFW']
    
    def __init__(self, profile: str = 'SIS'):
        """Initialize lens model."""
        if profile not in self.SUPPORTED_PROFILES:
            raise ValueError(f"Profile must be one of {self.SUPPORTED_PROFILES}")
        
        self.profile = profile
        self.parameters = None
        self.covariance = None
        self.fitted = False
    
    def fit(
        self,
        images: Dict[str, np.ndarray],
        einstein_radius_guess: Optional[float] = None,
        **kwargs
    ) -> dict:
        """
        Fit the lens model to your imaging data.
        
        If you pass multiple bands, they'll be combined (averaged).
        You can give an initial guess for the Einstein radius if you want,
        otherwise I'll just guess something reasonable.
        
        Parameters
        ----------
        images : dict
            Dictionary of imaging data by band
        einstein_radius_guess : float, optional
            Initial guess for Einstein radius (in pixels)
        
        Returns
        -------
        dict
            Dictionary with fit results including the profile type and parameters
        """
        # Combine images if multiple bands provided
        if isinstance(images, dict):
            image_data = np.mean([img for img in images.values()], axis=0)
        else:
            image_data = images
        
        # Normalize image
        image_normalized = image_data / np.max(image_data)
        
        # Set initial guess
        if einstein_radius_guess is None:
            einstein_radius_guess = image_data.shape[0] / 8
        
        # Fit model
        if self.profile == 'SIS':
            self.parameters = self._fit_sis(
                image_normalized,
                einstein_radius_guess
            )
        elif self.profile == 'NFW':
            self.parameters = self._fit_nfw(
                image_normalized,
                einstein_radius_guess
            )
        
        self.fitted = True
        
        return {
            'profile': self.profile,
            'parameters': self.parameters,
            'success': True,
        }
    
    def _fit_sis(
        self,
        image: np.ndarray,
        einstein_radius_guess: float
    ) -> dict:
        """Fit Singular Isothermal Sphere model."""
        center = np.array(image.shape) / 2
        
        def residual(params):
            theta_e, x0, y0 = params
            model = self._sis_profile(image.shape, theta_e, x0, y0)
            return np.sum((image - model) ** 2)
        
        result = optimize.minimize(
            residual,
            [einstein_radius_guess, center[1], center[0]],
            method='Nelder-Mead'
        )
        
        theta_e, x0, y0 = result.x
        return {
            'theta_e': float(theta_e),
            'x0': float(x0),
            'y0': float(y0),
        }
    
    def _fit_nfw(
        self,
        image: np.ndarray,
        einstein_radius_guess: float
    ) -> dict:
        """Fit NFW profile model."""
        center = np.array(image.shape) / 2
        
        def residual(params):
            r_s, x0, y0 = params
            model = self._nfw_profile(image.shape, r_s, x0, y0)
            return np.sum((image - model) ** 2)
        
        result = optimize.minimize(
            residual,
            [einstein_radius_guess / 2, center[1], center[0]],
            method='Nelder-Mead'
        )
        
        r_s, x0, y0 = result.x
        return {
            'r_s': float(r_s),
            'x0': float(x0),
            'y0': float(y0),
        }
    
    def _sis_profile(
        self,
        shape: Tuple[int, int],
        theta_e: float,
        x0: float,
        y0: float
    ) -> np.ndarray:
        """Generate SIS lens profile."""
        y, x = np.ogrid[:shape[0], :shape[1]]
        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        r[r == 0] = 1  # Avoid division by zero
        profile = theta_e / r
        return profile / np.max(profile)
    
    def _nfw_profile(
        self,
        shape: Tuple[int, int],
        r_s: float,
        x0: float,
        y0: float
    ) -> np.ndarray:
        """Generate NFW lens profile."""
        y, x = np.ogrid[:shape[0], :shape[1]]
        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        
        x_var = r / r_s
        # Avoid singularities
        x_var[x_var == 0] = 1e-3
        
        profile = np.zeros_like(r)
        mask1 = x_var < 1
        mask2 = x_var > 1
        
        profile[mask1] = (np.log(x_var[mask1] / 2) ** 2 - np.arctanh(
            np.sqrt(1 - x_var[mask1] ** 2)
        ) ** 2) / (x_var[mask1] ** 2 - 1)
        
        profile[mask2] = (np.log(x_var[mask2] / 2) ** 2 - np.arctan(
            np.sqrt(x_var[mask2] ** 2 - 1)
        ) ** 2) / (x_var[mask2] ** 2 - 1)
        
        return profile / (np.max(profile) + 1e-10)
    
    def predict(self, coordinates: np.ndarray) -> np.ndarray:
        """
        Predict magnification at given coordinates.
        
        Parameters
        ----------
        coordinates : np.ndarray
            Array of shape (N, 2) with (x, y) coordinates
        
        Returns
        -------
        np.ndarray
            Magnification values
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        if self.profile == 'SIS':
            theta_e = self.parameters['theta_e']
            x0 = self.parameters['x0']
            y0 = self.parameters['y0']
            
            r = np.sqrt((coordinates[:, 0] - x0) ** 2 + (coordinates[:, 1] - y0) ** 2)
            magnification = theta_e / r
        else:
            magnification = np.ones(len(coordinates))
        
        return magnification
