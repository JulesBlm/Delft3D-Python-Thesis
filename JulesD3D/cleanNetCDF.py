# TODO: READ ABOUT OOP BOY

from JulesD3D.processing_2d import vector_sum
import xarray as xr
import numpy as np
from os import path

# def magnitude(a, b):
#     func = lambda x, y: np.sqrt(x ** 2 + y ** 2)
#     return xr.apply_ufunc(func, a, b)

def fixCORs(nc):
    '''
    Last column and row of XCOR and YCOR are 0, this fixes that
    '''
    nc.XCOR[-1,:] = nc.XCOR.isel(MC=-2).values + nc.XCOR.isel(MC=1).values
    nc.XCOR[:,-1] = nc.XCOR.isel(NC=-2).values

    nc.YCOR[:,-1] = nc.YCOR.isel(NC=-2).values  + nc.YCOR.isel(NC=1).values
    nc.YCOR[-1,:] = nc.YCOR.isel(MC=-2).values
    
    return nc

def makeMeshGrid(length=45000, width=18000, x_gridstep=300, y_gridstep=300):
#     print("length:", length)
#     print("width:", width)
#     print("x_gridstep:", x_gridstep)
#     print("y_gridstep", y_gridstep)
    
    first_x_center = int(x_gridstep/2)
    xList = [0] + [i for i in range(first_x_center, int(width) + 1 * int(x_gridstep), int(x_gridstep))] #prepend a zero

    first_y_center = int(100 - y_gridstep/2)
    yList = [i for i in range(first_y_center, int(length) + 1 * int(y_gridstep), int(y_gridstep))] 

    xDim, yDim = [len(xList), len(yList)]
    print(xDim, "x", yDim, "grid")

    XZ, YZ = np.meshgrid(xList, yList) 
    
    return XZ.T, YZ.T # Why transpose again tho?

def fixMeshGrid(nc, XZ, YZ, mystery_flag=False):
    '''
    Remake mesh grid to plot because delft3d cuts gridmesh values outside of enclosure out causing matplotlib and hvplot to go haywire
    Get gridsteps and lengths from nc file
    Assumes unifrom
    '''
    print("Fixing mesh grid, assuming a uniform grid")
    x_gridstep = XZ[2][-1] - XZ[1][-1]
    y_gridstep = YZ[-2][-1] - YZ[-2][-2]
    
    width = (XZ.shape[0]-2) * x_gridstep
    if mystery_flag:
        length = (XZ.shape[1]-1) * y_gridstep # eeehhh hmmmm -1? sometimes -2?
    else: 
        length = (XZ.shape[1]-2) * y_gridstep # eeehhh hmmmm -1? sometimes -2?        
    
    print("x_gridstep", x_gridstep)
    print("y_gridstep", y_gridstep)
    print("width", width)
    print("length", length)
    
    XZ, YZ = makeMeshGrid(length=length, width=width, x_gridstep=x_gridstep, y_gridstep=y_gridstep)

    print('original XZ', nc.XZ.shape)
    print('original YZ', nc.YZ.shape)
    print('new XZ', XZ.shape)
    print('new YZ', YZ.shape)
    nc.XZ.values = XZ
    nc.YZ.values = YZ
    
    return nc

def addDepth(nc):
    # Could have set LayOut = #Y# in mdf to get lay interfaces in map nc file written during simulation and worked with those values
    ##### depth at interfaces #####
    # nc.LAYER_INTERFACE.isel(time=-1, SIG_INTF=-1).hvplot.quadmesh('XZ', 'YZ',
    #                         height=600, width=400,
    #                         rasterize=True,
    #                         dynamic=True,
    #                         grid=False,
    #                         legend=True,
    #                         )    
    
    depth = nc.SIG_INTF @ nc.DPS
    
    depth = depth.transpose('time', 'M', 'N', 'SIG_INTF', transpose_coords=True)
    depth = depth.assign_attrs({"unit": "m", "long_name": "Depth at Sigma-layer interfaces"})
    
    nc.coords['depth'] = depth
#     nc = nc.rename_dims({'SIG_INTF': 'KMAXOUT'}) # rename SIG_INTF to KMAXOUT
    
    ##### depth at cell centers #####
    depth_center = nc.SIG_LYR @ nc.DPS
    
    depth_center = depth_center.transpose('time', 'M', 'N', 'SIG_LYR', transpose_coords=True)
    depth_center = depth_center.assign_attrs({"unit": "m", "long_name": "Depth at Sigma-layer centers"})

    nc.coords['depth_center'] = depth_center
#     nc = nc.rename_dims({'SIG_LYR': 'KMAXOUT_RESTR'}) # rename SIG_LYR to KMAXOUT_RESTR        

    ##### Add layer thickness DataArray to Data #####
    layer_thickness = np.diff(-depth.values)
    nc['layer_thickness'] = (depth_center.dims, layer_thickness)
    nc['layer_thickness'].attrs = {'long_name': 'Sigma-layer thickness', 'units': 'm'}
    
    return nc

def addUnderlayerCoords(nc):
    '''
    Add underlayer coordinates to these data variables, which is nice for plotting with Holoviews
    '''
    
    nc['MSED'] = nc.MSED.assign_coords(nlyr=nc.nlyr.values)
    nc['MSED'] = nc.MSED.assign_coords(nlyr=nc.nlyr.values)
    nc['LYRFRAC'] = nc.LYRFRAC.assign_coords(nlyr=nc.nlyr.values)
    nc['DP_BEDLYR'] = nc.DP_BEDLYR.assign_coords(nlyrp1=nc.nlyrp1.values)
    
    return nc

def makeBottomStress(nc):
    # Bottom stress ( ('Bottom stress in U-point', 'TAUKSI'), ('Bottom stress in V-point', 'TAUETA'))
    bottom_stress_sum = vector_sum(nc.TAUKSI.values, nc.TAUETA.values)
    nc['bottom_stress'] = (('time', 'M', 'N'), bottom_stress_sum)  
    nc['bottom_stress'].attrs = {'long_name': 'Bottom stress', 'units': 'N/m2', 'grid': 'grid', 'location': 'edge1'}            

    return nc

def makeVelocity(nc):
    # Make Horizontal velocity sum per layer
    velocity_sum = vector_sum(nc.U1.values, nc.V1.values) # Velocity per layer
    nc['velocity'] = (('time',  'KMAXOUT_RESTR', 'M', 'N',), velocity_sum)
    nc['velocity'].attrs = {'long_name': 'Velocity per layer', 'units': 'm/s', 'grid': 'grid', 'location': 'edge1'}
    nc['velocity']  = nc.velocity.transpose('time', 'M', 'N', 'KMAXOUT_RESTR', transpose_coords=False)
    nc['velocity'] = nc.velocity.assign_coords(depth=(('time', 'M', 'N', 'KMAXOUT_RESTR'), nc['depth_center'].values))
    
    return nc

def makeVectorSumsSediments(nc):
    #### Make vector sums for each sediment
    bed_load_dims = nc.SSVV.isel(LSED=0).dims
    susp_load_dims = nc.SSUU.isel(LSED=0).dims

    sediments = [str(sediment.rstrip()) for sediment in nc.NAMCON.values]

    for i, sediment in enumerate(sediments):
        print ('----------------', sediment, i, '----------------')
        # Add bed load transport vector sum for each sediment
        bed_load_values = vector_sum(nc.SBUU.isel(LSEDTOT=i).values, nc.SBVV.isel(LSEDTOT=i).values)
        long_name_bed_load = 'Bed load transport ' + sediment[2:-1].lower()
        bed_load_name = 'bl_transp_' + sediment[2:-1]

        nc[bed_load_name] = (bed_load_dims, bed_load_values)
        nc[bed_load_name].attrs = {'long_name': long_name_bed_load, 'units': 'm3/(s m)', 'grid': 'grid', 'location': 'edge1'}

        # Add suspended load transport vector sum for each sediment
        susp_load_values = vector_sum(nc.SSVV.isel(LSED=i).values, nc.SSUU.isel(LSED=i).values) # Suspended-load transport   
        long_name_susp_load = 'Suspended-load transport ' + sediment[2:-1].lower()
        susp_load_name = 'sp_transport_' + sediment[2:-1]

        nc[susp_load_name] = (susp_load_dims, susp_load_values)
        nc[susp_load_name].attrs = {'long_name': long_name_susp_load, 'units': 'm3/(s m)', 'grid': 'grid', 'location': 'edge2'}
    
    return nc

def dropJunk(nc):
    # Remove component DataArrays from DataSet
    print("Dropping a bunch of DataArrays from DataSet...", end='') # SBUUA, SBVVA NOT DROPPED?
    drop_list = [\
         'SBUU', 'SBVV',\
         'SSVV', 'SSUU',\
         'TAUKSI', 'TAUETA',\
         'SBUUA, SBVVA',\
         'SSUUA', 'SSVVA',\
         'GSQS', 'ALFAS',\
         'DPU0', 'DPV0',\
         'DXX01', 'DXX02', 'DXX03', 'DXX04', 'DXX05',\
         'PPARTITION',\
         'TAUMAX', 'UMNLDF',\
         'VMNLDF',\
         'MIN_H1', 'MAX_H1', 'MEAN_H1',\
         'STD_H1', 'MIN_UV', 'MAX_UV', 'MEAN_UV', 'STD_UV',\
         'MIN_SBUV', 'MAX_SBUV', 'MEAN_SBUV', 'STD_SBUV',\
         'MIN_SSUV', 'MAX_SSUV', 'MEAN_SSUV', 'STD_SSUV',\
         'KCS', 'KFU', 'KFV', 'KCU', 'KCV',\
         'MORFAC', 'MORFT', 'MFTAVG', 'MORAVG'
    ]
     #DPS0', 
    
    nc = nc.drop(drop_list, errors='ignore')    
    print('Done dropping variables.')    

    # im not sure which to use?
    # nc = nc.drop_sel(drop_list, errors='ignore')
    # nc = nc.drop_vars(drop_list, errors='ignore')
    # for drop_var in drop_list:
    #     if drop_var in nc:
    #         dropped = nc.drop_vars(drop_var)
    #         print("Dropping", drop_var, 'from DataSet', dropped)

    return nc

# arguments: gridstep, width, length
def writeCleanCDF(ncfilename, mystery_flag=False):
    '''
    Add vector sum for velocities and sediment transport DataArrays to DataSet
    Remove useless stuff and save new netCDF to disk
    '''
    
    with xr.open_dataset(ncfilename, chunks={'time': 80}) as nc:
        nc = fixMeshGrid(nc, nc.XZ.values, nc.YZ.values, mystery_flag=True)
        print("* Fixed mesh grid") # find a way to nicely chain these. just mutate nc for sake of ease?
        nc = addDepth(nc)
        print("Added depth & depth_center to DataSet")
        nc = makeVelocity(nc)
        print("Calculated velocity")
        nc = makeBottomStress(nc)
        print("Calculated bottom stress sum")
        nc = addUnderlayerCoords(nc)
        print("Assigned underlayer coordinates")
        nc = dropJunk(nc)
        print("Dropped variables from DataSet")
        
        root, ext = path.splitext(ncfilename)
        new_filename = root + '_clean' + ext
        
        # TODO overwrite old NetCDF so we don't have to calculate vector sums again U SURE THO?
        print("Start writing netCDF to disk...", end='')
        nc.load().to_netcdf(new_filename, mode='w', engine='netcdf4', format='NETCDF4') 
        print("Succesfully written new file as ", new_filename)
        
        return new_filename
