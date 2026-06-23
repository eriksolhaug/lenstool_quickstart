#!/usr/bin/env python
"""
Plot cumulative distribution of WSUS (Wide-field SDSS Ultra-deep Spectroscopy) 
discoveries over time. Reproduces the cumulative discovery plot with black 
coloring and Computer Modern font formatting.
"""

import matplotlib.pyplot as plt
import numpy as np


def latex_formatting():
    """Apply LaTeX formatting to matplotlib plots with Computer Modern font."""
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Computer Modern']
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10


def plot_wsus_cumulative():
    """Plot cumulative WSUS discoveries."""
    latex_formatting()
    
    # Data extracted from the image: (year, cumulative_count, discovery_id, discovery_year)
    # First discovery group (early, shown in green in original)
    discoveries_group1 = [
        (2004, 1, 'SDSS J1004+0112', 'Dec 2003'),
        (2007, 2, 'SDSS J1029+2623', 'Dec 2006'),
    ]
    
    # Second discovery group (later, shown in magenta in original)
    discoveries_group2 = [
        (2013, 2.5, 'SDSS 1222+2745', 'Aug 2013'),
        (2017, 3, 'SDSS J0901+4449', 'Nov 2018'),
        (2018, 3.5, 'SDSS J1326+4806', 'Nov 2019'),
        (2019, 4, 'SDSS J0335-1927', 'Sep 2023'),
        (2024, 6.5, 'COOL J1153+0755', 'May 2024'),
    ]
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Build cumulative data for step plot
    years = []
    cumulative = []
    
    # Add initial point
    years.append(2002)
    cumulative.append(0)
    
    # First group of discoveries
    for year, count, _, _ in discoveries_group1:
        years.append(year)
        cumulative.append(cumulative[-1])
        years.append(year)
        cumulative.append(count)
    
    # Add gap before second group
    years.append(2012)
    cumulative.append(cumulative[-1])
    
    # Second group of discoveries
    for year, count, _, _ in discoveries_group2:
        years.append(year)
        cumulative.append(cumulative[-1])
        years.append(year)
        cumulative.append(count)
    
    # Extend to end of plot
    years.append(2026)
    cumulative.append(cumulative[-1])
    
    # Plot step function in black
    ax.plot(years, cumulative, 'k-', linewidth=2, where='post', drawstyle='steps-post')
    
    # Add annotations for discoveries (group 1 in black, right-aligned)
    annotations_group1 = [
        (2004, 1, 'SDSS J1004+0112\nDec 2003'),
        (2007, 2, 'SDSS J1029+2623\nDec 2006'),
    ]
    
    for year, count, label in annotations_group1:
        ax.annotate(label, xy=(year, count), xytext=(year - 0.5, count + 0.3),
                   fontsize=9, color='black', ha='right', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor='none', alpha=0.8))
    
    # Add annotations for discoveries (group 2 in black, right-aligned)
    annotations_group2 = [
        (2013, 2.5, 'SDSS \\textbf{1222}+2745\nAug 2013', -0.3),
        (2018, 3.5, 'SDSS J0901+4449\nNov 2018', -0.3),
        (2019, 4.0, 'SDSS J1326+4806\nNov 2019', -0.3),
        (2023, 6.5, 'SDSS J0335-1927\nSep 2023', 0.5),
        (2024, 6.5, 'COOL J1153+0755\nMay 2024', 0.5),
    ]
    
    for year, count, label, offset in annotations_group2:
        ax.annotate(label, xy=(year, count), xytext=(year + offset, count + 0.5),
                   fontsize=9, color='black', ha='left' if offset > 0 else 'right',
                   va='bottom',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor='none', alpha=0.8))
    
    # Format axes
    ax.set_xlabel('Year', fontsize=12, color='black')
    ax.set_ylabel('WSUS Discoveries (Cumulative)', fontsize=12, color='black')
    
    # Set axis limits
    ax.set_xlim(2002, 2026)
    ax.set_ylim(0, 8.5)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Set tick colors to black
    ax.tick_params(axis='both', which='major', labelcolor='black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    # Add grid for readability
    ax.grid(True, alpha=0.3, color='black', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    return fig, ax


if __name__ == '__main__':
    fig, ax = plot_wsus_cumulative()
    plt.savefig('wsus_cumulative.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('wsus_cumulative.png', dpi=300, bbox_inches='tight')
    print("Plots saved as 'wsus_cumulative.pdf' and 'wsus_cumulative.png'")
    plt.show()
