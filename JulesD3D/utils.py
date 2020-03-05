# Just some helpful functions
import numpy as np
import pandas as pd
import xarray as xr
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import BoundaryNorm
from matplotlib.colors import LightSource
from matplotlib import cm
from numpy import format_float_scientific
import fileinput
from glob import glob
from os import path
import ipywidgets as widgets

def ncFilepicker(foldername):
    nc_files = sorted(glob(foldername + '/*.nc'))

    nc_filename = widgets.Select(
        options=nc_files,
        description='NetCDF file:',
        disabled=False,
        width='100%',
        layout=widgets.Layout(width='100%', height='120px')
    )
    
    return nc_filename
            

def formatSci(floatNr):
    return format_float_scientific(floatNr, unique=False, precision=7, exp_digits=3) 

def colorNegativeNaN(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    if val < 0:
        return 'color: red'
    elif val == 0:
        return 'color: grey'
    elif np.isnan(val):
        return 'color: grey'
    else:
        return 'color: white'

def quickDF(section):
    newDF = pd.DataFrame(section)
    s = newDF.style.applymap(colorNegativeNaN)
    display(s)
    
# Old an abondened function
def getPlotKeyword(nc):
    '''Get plot variables in nice format for ipywidgets dropdown'''
    dropdownOptions_horizontal = []
    dropdownOptions_underlayer = []
    dropdownOptions_vertical = []    
    
    for v in nc.data_vars:
        if 'long_name' in nc[v].attrs:
            # Underlayer props
            if any(keyword in nc[v].dims for keyword in ('nlyr', 'nlyrp1')): # 'LSED', 'LSEDTOT', 
                dropdownOptions_underlayer.append((nc[v].attrs['long_name'], v))
            # horizontal plottable props
            elif len(nc[v].dims) > 1:
                dropdownOptions_horizontal.append((nc[v].attrs['long_name'], v))        

            # vertical plottable properties
            if any(keyword in nc[v].dims for keyword in ('KMAXOUT_RESTR', 'KMAXOUT')):
                dropdownOptions_vertical.append((nc[v].attrs['long_name'], v))

    # Remove some junk the old fashioned hardcoded way
    remove_list = [
        ('Orientation ksi-axis w.r.t. pos.x-axis at water level point', 'ALFAS'),
        ('Partition', 'PPARTITION'),
        ('Non-active/active in U-point', 'KFU'),
        ('Non-active/active in V-point', 'KFV'),
        ('Bottom stress in U-point', 'TAUKSI'),
        ('Bottom stress in V-point', 'TAUETA'),
        ('Filtered U-velocity', 'UMNLDF'),
        ('Filtered V-velocity', 'VMNLDF'),
        ('Bed-load transport u-direction (u point)', 'SBUU'),
        ('Bed-load transport v-direction (v point)', 'SBVV'),
        ('Suspended-load transport u-direction (u point)', 'SSUU'),
        ('Suspended-load transport v-direction (v point)', 'SSVV')
    ]
    
    [dropdownOptions_horizontal.remove(item) for item in remove_list]
        
                
    return [dropdownOptions_horizontal, dropdownOptions_underlayer, dropdownOptions_vertical]

# Old and abondoned function
def plotCrossSection(plotX, plotY, section, title, units, xLabel='x', yLabel='y', minValue=None, maxValue=None):
    maskArray = np.equal(-999, section) # Remove -999 (null) values from section

#     section = ma.masked_where(section=-999, section)
    section = ma.array(section, mask = maskArray)
    section[maskArray==True] = np.NaN
    
    if not (minValue and maxValue):
        maxValue = np.amax(section)
        minValue = np.amin(section)

    print("Section shape", section.shape)
    print("Min value", minValue, "Max value", maxValue)
    
    fig, ax_plotf = plt.subplots(figsize=(4,6))
    fig.suptitle(title)
    ax_plotf.set_xlabel(xLabel)
    ax_plotf.set_ylabel(yLabel)


    levels = MaxNLocator(nbins=15).tick_values(minValue, maxValue)
    colormap = plt.get_cmap('viridis')
    norm = BoundaryNorm(levels, ncolors=colormap.N)
    
    mesh = ax_plotf.imshow(section, cmap=colormap, norm=norm)
    cbar = fig.colorbar(mesh, ax=ax_plotf, label=units)
    cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel(units, rotation=90)