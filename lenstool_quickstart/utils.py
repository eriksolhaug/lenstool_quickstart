"""
Utility functions for image processing and visualization.

Helper functions for the heavy lifting: smoothing images, normalizing,
plotting results, etc. These make your life easier.
"""

from typing import Optional, Tuple
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from skimage import exposure


def preprocess_image(
    image: np.ndarray,
    smooth: bool = True,
    sigma: float = 1.0,
    normalize: bool = True,
) -> np.ndarray:
    """
    Preprocess imaging data.
    
    Gets your images ready for analysis: smooths out noise,
    normalizes to [0, 1] range. By default does everything,
    but you can turn off individual steps.
    
    Parameters
    ----------
    image : np.ndarray
        Input image array
    smooth : bool, optional
        Apply Gaussian smoothing (default: True)
    sigma : float, optional
        Gaussian smoothing sigma (default: 1.0)
    normalize : bool, optional
        Normalize to [0, 1] range (default: True)
    
    Returns
    -------
    np.ndarray
        Preprocessed image
    """
    processed = np.array(image, dtype=float)
    
    if smooth:
        processed = ndimage.gaussian_filter(processed, sigma=sigma)
    
    if normalize:
        processed = (processed - np.min(processed)) / (np.max(processed) - np.min(processed) + 1e-10)
    
    return processed


def equalize_histogram(image: np.ndarray, method: str = 'adaptive') -> np.ndarray:
    """
    Apply histogram equalization.
    
    Stretches the contrast so faint features show up better.
    'adaptive' is usually nicer for astronomy images.
    
    Parameters
    ----------
    image : np.ndarray
        Input image
    method : str, optional
        'adaptive' or 'global' (default: 'adaptive')
    
    Returns
    -------
    np.ndarray
        Equalized image
    """
    if method == 'global':
        return exposure.equalize_hist(image)
    elif method == 'adaptive':
        return exposure.equalize_adapthist(image)
    else:
        raise ValueError(f"Unknown method: {method}")


def plot_lens_model(
    image: np.ndarray,
    parameters: dict,
    title: str = "Lens Model",
    figsize: Tuple[int, int] = (10, 8),
    cmap: str = 'viridis',
) -> plt.Figure:
    """
    Plot image with lens model overlay.
    
    Makes a nice visualization of your data with the model
    overlaid on top. Useful for checking if things look reasonable.
    
    Parameters
    ----------
    image : np.ndarray
        Image data
    parameters : dict
        Lens model parameters
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (default: (10, 8))
    cmap : str, optional
        Colormap (default: 'viridis')
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(image, cmap=cmap, origin='lower')
    
    if 'x0' in parameters and 'y0' in parameters:
        ax.plot(
            parameters['x0'],
            parameters['y0'],
            'r+',
            markersize=15,
            markeredgewidth=2,
            label='Lens center'
        )
    
    if 'theta_e' in parameters:
        theta_e = parameters['theta_e']
        circle = plt.Circle(
            (parameters['x0'], parameters['y0']),
            theta_e,
            fill=False,
            color='red',
            linestyle='--',
            label=f'Einstein radius: {theta_e:.1f} px'
        )
        ax.add_patch(circle)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    plt.colorbar(im, ax=ax, label='Intensity')
    ax.legend(loc='upper right')
    
    return fig


def combine_bands(
    images: dict,
    weights: Optional[dict] = None,
) -> np.ndarray:
    """
    Combine multi-band imaging data.
    
    Parameters
    ----------
    images : dict
        Dictionary of images by band
    weights : dict, optional
        Optional weights for each band
    
    Returns
    -------
    np.ndarray
        Combined image
    """
    if weights is None:
        weights = {band: 1.0 for band in images.keys()}
    
    combined = np.zeros_like(list(images.values())[0], dtype=float)
    total_weight = 0.0
    
    for band, image in images.items():
        w = weights.get(band, 1.0)
        combined += w * image
        total_weight += w
    
    return combined / total_weight


def measure_snr(image: np.ndarray, mask: Optional[np.ndarray] = None) -> float:
    """
    Estimate signal-to-noise ratio.
    
    Parameters
    ----------
    image : np.ndarray
        Image data
    mask : np.ndarray, optional
        Signal region mask
    
    Returns
    -------
    float
        SNR estimate
    """
    if mask is None:
        signal = np.max(image)
        noise = np.std(image[image < np.percentile(image, 50)])
    else:
        signal = np.mean(image[mask])
        noise = np.std(image[~mask])
    
    snr = signal / (noise + 1e-10)
    return float(snr)
