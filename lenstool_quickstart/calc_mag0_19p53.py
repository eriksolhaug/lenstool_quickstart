#!/usr/bin/env python
"""
Calculate L* = 19.53 at z=0.4301
Working backwards to see what this implies
"""

import numpy as np
from astropy.cosmology import FlatLambdaCDM
from astropy import units as u

cosmo = FlatLambdaCDM(H0=70, Om0=0.3)

# Target result
L_star_target = 19.53
z_target = 0.4301

# Get distance modulus at z_target
d_L_target = cosmo.luminosity_distance(z_target).to(u.Mpc).value
d_L_target_pc = d_L_target * 1e6
log_d_target_pc = np.log10(d_L_target_pc)
mu_target = 5.0 * log_d_target_pc - 5.0

# Work backwards: L_star = M_abs + mu
# So M_abs = L_star - mu
M_abs_implied = L_star_target - mu_target

# Now get back to M_star_obs
h = 0.7
h_corr = 5.0 * np.log10(h)
M_star_obs_implied = M_abs_implied + h_corr

print("To get L* = 19.53 at z=0.4301:")
print("  Distance modulus: mu = %.3f" % mu_target)
print("  Implied M_abs = %.4f" % M_abs_implied)
print("  Implied M*_0.1 - 5*log10(h) = %.2f" % M_star_obs_implied)
print("\nDifference from Blanton et al. 2003 (-21.18): %.2f mag" % (M_star_obs_implied - (-21.18)))

# Alternative: what if there's a K-correction or evolution?
print("\n--- Alternative explanation ---")
M_star_blanton = -21.18
h_corr = 5.0 * np.log10(h)
M_abs = M_star_blanton - h_corr
m_direct = M_abs + mu_target  # This is what we calculated before = 21.47

print("Direct calculation (no correction): m = %.2f" % m_direct)
print("Target value: L* = %.2f" % L_star_target)
print("Difference: %.2f mag" % (m_direct - L_star_target))

# What correction would we need?
correction_needed = L_star_target - m_direct
print("\nCorrection needed: %.2f mag (to make galaxy appear brighter)" % correction_needed)
