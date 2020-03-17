# todo: DRY makeStructuredGridInterfaces and makeStructuredGridInterface, merge into one function
import pyvista as pv
import xarray as xr
from pandas import to_datetime
import datetime
import numpy as np
from JulesD3D.processNetCDF import addDepth, fixCORs, fixMeshGrid

# TODO: Day is WRONG!
def easyTimeFormat(datetimestring):
    '''Formats np.datetime64 to nice string with Day hours minutes seconds'''
    t = to_datetime(str(datetimestring)) 
    timestring = t.strftime("Day %d — %H:%M:%S") #%D
    print(datetimestring)
    return timestring

# TODO Make parent MakeBottom surface function/class and inherit from that
def makeBottomSurface(trim, timestep=-1, mystery_flag=False):
    '''
    Default is last timestep
    '''
    trim = fixCORs(trim)
    if 'depth_center' not in trim:
        trim = fixMeshGrid(trim, trim.XZ.values, trim.YZ.values, mystery_flag=True)    
    
    plot_x_mesh = trim.XCOR.values[:-1,:-1]
    plot_y_mesh = trim.YCOR.values[:-1,:-1]
    plot_z_mesh = -trim.DPS.isel(time=-1).values[:-1,:-1]
    
    bottom_surface = pv.StructuredGrid(plot_x_mesh, plot_y_mesh, plot_z_mesh)
    bottom_surface["Depth"] = plot_z_mesh.ravel(order="F")
    
    return bottom_surface
    
def makeStructuredGridDepth(trim, keyword='SIG_LYR'):
    if keyword is not 'SIG_LYR' and keyword is not 'SIG_INTF':
        raise Exception("Keyword must be either 'SIG_INTF' or 'SIG_LYR'")
    
    if 'depth' not in trim: # or 'depth_center'
        print("'depth' DataArray was not found in DataSet, adding it now. It's better to use a preprocessed NetCDF!")
        trim = addDepth(trim)
    else:
        print("'depth' DataArray already found in DataSet!")
        
    nr_sigma = trim[keyword].size
    
    # Repair XCOR and YCOR anyway
    trim = fixCORs(trim)
    
    x_meshgrid = np.repeat(trim.XCOR.values[:,:, np.newaxis], nr_sigma, axis=2)
    y_meshgrid = np.repeat(trim.YCOR.values[:,:, np.newaxis], nr_sigma, axis=2)
    
    if keyword is 'SIG_LYR':
        depth = trim.depth_center.isel(time=0)         
#         depth = trim.depthcenter.isel(time=0) 
    elif keyword is 'SIG_INTF':
        depth = trim.depth.isel(time=0)
        
    ## FROM HERE ITS THE SAME AS THE ABOVE FUNCTION
    x_ravel = np.ravel(x_meshgrid)
    y_ravel = np.ravel(y_meshgrid)
    depth_ravel = np.ravel(depth.values)
    
    xyz_layers = np.column_stack((x_ravel, y_ravel, depth_ravel))
    print("xyz_layers.shape", xyz_layers.shape)
    
    depth_grid = pv.StructuredGrid()
    depth_grid.points = xyz_layers
    depth_grid.dimensions = [nr_sigma, trim.N.size, trim.M.size]
    
    return depth_grid