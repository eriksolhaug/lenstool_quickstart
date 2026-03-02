#!/usr/bin/env python
"""
Calculate mag0 for potfile0 using Blanton et al. 2003.
M*_0.1 - 5*log10(h) = -21.18
"""

import numpy as np
from astropy.cosmology import FlatLambdaCDM
from astropy import units as u

cosmo = FlatLambdaCDM(H0=70, Om0=0.3)

# Input
M_star_obs = -21.18
h = 0.7
z_ref = 0.1
z_target = 0.588

# Step 1: absolute magnitude
h_ = 5.0 * np.log10(h)
M_abs = M_star_obs - h_

# Step 2: apparent magnitude at z_ref
# Just writing this up to be clear
# Distance modulus (standard): m - M = 5*log10(d) - 5, where d in parsec
# Convert d_L from Mpc to pc: d_L(pc) = d_L(Mpc) * 10^6
# m - M = 5*log10(d_L(Mpc) * 10^6) - 5
#       = 5*log10(d_L(Mpc)) + 5*log10(10^6) - 5
#       = 5*log10(d_L(Mpc)) + 30 - 5
#       = 5*log10(d_L(Mpc)) + 25

d_L = cosmo.luminosity_distance(z_ref).to(u.Mpc).value
d_L_pc = d_L * 1e6
log_d_pc = np.log10(d_L_pc)
mu = 5.0 * log_d_pc - 5.0
m_ref = M_abs + mu

# Step 3: shift to z_target
d_L_target = cosmo.luminosity_distance(z_target).to(u.Mpc).value
d_L_target_pc = d_L_target * 1e6
log_d_target_pc = np.log10(d_L_target_pc)
mu_target = 5.0 * log_d_target_pc - 5.0
m_target = M_abs + mu_target

# K + evolution correction
k_evo = -1.94
m_target = m_target + k_evo

print("mag0 = %.2f" % m_target)

# Save
with open("/Users/eriksolhaug/Research/Tools/lenstool_quickstart/CJ0221/scripts/mag0.txt", 'w') as f:
    f.write("mag0 = %.2f\n" % m_target)
    f.write("\nM*_0.1 - 5*log10(h) = %.2f\n" % M_star_obs)
    f.write("M_abs = %.4f\n" % M_abs)
    f.write("d_L(z=%.1f) = %.2f Mpc\n" % (z_ref, d_L))
    f.write("mu(z=%.1f) = %.3f\n" % (z_ref, mu))
    f.write("m(z=%.1f) = %.3f\n" % (z_ref, m_ref))
    f.write("\nd_L(z=%.4f) = %.2f Mpc\n" % (z_target, d_L_target))
    f.write("mu(z=%.4f) = %.3f\n" % (z_target, mu_target))
    f.write("m(z=%.4f) = %.3f\n" % (z_target, m_target))



