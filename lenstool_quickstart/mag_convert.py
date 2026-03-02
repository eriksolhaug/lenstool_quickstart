#!/usr/bin/env python
"""
Convert magnitude from z1=0.4301 to z2=0.588
mag1 = 19.53 at z1=0.4301
"""

import numpy as np
from astropy.cosmology import FlatLambdaCDM
from astropy import units as u

cosmo = FlatLambdaCDM(H0=70, Om0=0.3)

mag1 = 19.53
z1 = 0.4301
z2 = 0.588

# Distance modulus difference
d_L_z1 = cosmo.luminosity_distance(z1).to(u.Mpc).value
d_L_z2 = cosmo.luminosity_distance(z2).to(u.Mpc).value
delta_mu = 5.0 * np.log10(d_L_z2 / d_L_z1)

# Calculate mag2
mag2 = mag1 + delta_mu

print("Convert magnitude from z1=%.4f to z2=%.4f" % (z1, z2))
print("  mag1 = %.2f" % mag1)
print("\nDistance modulus change:")
print("  d_L(z1) = %.2f Mpc" % d_L_z1)
print("  d_L(z2) = %.2f Mpc" % d_L_z2)
print("  delta_mu = 5*log10(%.2f/%.2f) = %.3f mag" % (d_L_z2, d_L_z1, delta_mu))
print("\nmag2 = mag1 + delta_mu")
print("mag2 = %.2f + %.3f = %.2f" % (mag1, delta_mu, mag2))
