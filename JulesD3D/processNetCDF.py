# TODO: READ ABOUT OOP
# turn this into a class
# turn seperate functions into classes?
# leave it as is?
# TODO: Use ufuncs for vector sums

from JulesD3D.processing_2d import vector_sum
import xarray as xr
import numpy as np
from os import path

# def magnitude(a, b):
#     func = lambda x, y: np.sqrt(x ** 2 + y ** 2)
#     return xr.apply_ufunc(func, a, b)

def fixCORs(nc):
    '''
    Last column and row of XCOR and YCOR are 0, this fixes that. Nice for plotting
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
    Derives gridsteps and dimensions from passed DataSet
    Assumes uniform grid, curved grid wont work!
    References to XZ and YZ need to be passed explicitly because xarray loads the netCDF lazily
    The mystery flag is a Boolean because sometimes 1 and sometimes 2 gridsteps need to be subtracted from the length ¯\_(ツ)_/¯ , don't know why
    '''
    print("------ Fixing mesh grid, assuming a uniform grid ------")
    x_gridstep = XZ[2][-1] - XZ[1][-1]
    y_gridstep = YZ[-2][-1] - YZ[-2][-2]
    
    width = (XZ.shape[0]-2) * x_gridstep
    if mystery_flag:
        length = (XZ.shape[1] - 1) * y_gridstep # eeehhh hmmmm -1? sometimes -2?
    else: 
        length = (XZ.shape[1] - 2) * y_gridstep # eeehhh hmmmm -1? sometimes -2?        
    
    print("x_gridstep:\t", x_gridstep, "m")
    print("y_gridstep:\t", y_gridstep, "m")
    print("width:\t\t", width, "m")
    print("length:\t\t", length, "m")
    
    XZ, YZ = makeMeshGrid(length=length, width=width, x_gridstep=x_gridstep, y_gridstep=y_gridstep)

    # for debugging
    # print('original XZ', nc.XZ.shape)
    # print('original YZ', nc.YZ.shape)
    # print('new XZ', XZ.shape)
    # print('new YZ', YZ.shape)
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
    Add underlayer coordinates to these data variables, which is nice for interactive plotting with Holoviews
    '''
    
    nc['MSED'] = nc.MSED.assign_coords(nlyr=nc.nlyr.values)
    nc['MSED'] = nc.MSED.assign_coords(nlyr=nc.nlyr.values)
    nc['LYRFRAC'] = nc.LYRFRAC.assign_coords(nlyr=nc.nlyr.values)
    nc['DP_BEDLYR'] = nc.DP_BEDLYR.assign_coords(nlyrp1=nc.nlyrp1.values)
    
    nc['nlyrp1'].attrs = {'standard_name': 'Interfaces of underlayers', 'long_name': 'Number of interfaces of underlayers'}
    nc['nlyr'].attrs = {'standard_name': 'Number of underlayers', 'long_name': 'Number of underlayers'}
    
    return nc

# This only works for sets that don;t have nested values
def addVectorSum(nc, U_comp, V_comp, key="summed", attrs={}, dims=('time', 'M', 'N')):
    '''Adds summed DataArray to new key in DataSet and drops components from DataSet'''
    summed = vector_sum(nc[U_comp].values, nc[V_comp].values)
    nc[key] = (dims, summed)
    nc[key].attrs = attrs
        
    nc = nc.drop_vars([U_comp, V_comp])

    return nc

def makeVelocity(nc): # , U1, V1 directly pass component values
    # Make Horizontal velocity sum per layer
    velocity_sum = vector_sum(nc.U1.values, nc.V1.values) # Velocity per layer
    nc['velocity'] = (('time',  'KMAXOUT_RESTR', 'M', 'N',), velocity_sum)
    nc['velocity'].attrs = {'long_name': 'Horizontal velocity per layer', 'units': 'm/s', 'grid': 'grid', 'location': 'edge1'}
    
    # why am i doing this again? For pyvista right?
    nc['velocity']  = nc.velocity.transpose('time', 'M', 'N', 'KMAXOUT_RESTR', transpose_coords=False)
    nc['velocity'] = nc.velocity.assign_coords(depth=(('time', 'M', 'N', 'KMAXOUT_RESTR'), nc['depth_center'].values)) # for pyvista?
    
    return nc

def makeVectorSumsSediments(nc, sediment_dicts=[]):
    '''
    Loops of all constituents (sediments) found in DataSet and sums their vector components and add them to DataSet,
    sediment_dicts is a list of dicts; each dict should have these keys
        'U_V_keys': ['U', 'V'],
        'attrs': {'long_name': 'Some long name', 'units': 'm', 'grid': 'grid', 'location': 'edge1'},
        'dims': ('time', 'M', 'N'),
        'new_key': 'susp_load', 
    '''
    if not sediment_dicts:
        raise Exception("The provided list of sediment components is empty. Stopping")
        return
    
    sediments = [str(sediment.rstrip()) for sediment in nc.NAMCON.isel(time=0).values]

    for i, sediment in enumerate(sediments):
        print('------', sediment, '------')
        for datavar in sediment_dicts:
            U, V = datavar['U_V_keys']
            
            if U in nc and V in nc:
                new_summed_key = f"{datavar['new_key']}_{sediment[11:-1]}" # TODO: bad because this expects all constituents to be prefixed with sediment but who cares only i use this junk
                print("Adding to DataSet with key:", new_summed_key)
                key['attrs']['long_name'] = f"{kdatavarey['attrs']['long_name']} {sediment[2:-1]}"
                # print("New long name:", datavar['attrs']['long_name'])
                print(f"Summing {U} and {V} for {sediment}")
                nc = addVectorSum(nc, U, V, key=new_summed_key, attrs=datavar['attrs'], dims=key['dims'])
            else:
                print(f"⚠️ Keywords {U} and {V} are not present in given DataSet ⚠️")
                return nc
    
    print("Done adding summed DataArrays for ", *(sed[2:-1] for sed in sediments), "to DataSet")    
    return nc

def dropJunk(nc, drop_list=[
         'SBUU', 'SBVV',
         'SSVV', 'SSUU',
         'TAUKSI', 'TAUETA',
         'SBUUA, SBVVA',
         'SSUUA', 'SSVVA',
         'GSQS', 'ALFAS',
         'DPU0', 'DPV0',
         'DXX01', 'DXX02', 'DXX03', 'DXX04', 'DXX05',
         'PPARTITION',
         'TAUMAX', 'UMNLDF',
         'VMNLDF',
         'MIN_H1', 'MAX_H1', 'MEAN_H1',
         'STD_H1', 'MIN_UV', 'MAX_UV', 'MEAN_UV', 'STD_UV',
         'MIN_SBUV', 'MAX_SBUV', 'MEAN_SBUV', 'STD_SBUV', # stat junk
         'MIN_SSUV', 'MAX_SSUV', 'MEAN_SSUV', 'STD_SSUV', 
         'KCS', 'KFU', 'KFV', 'KCU', 'KCV', # masks
#          'W'
         'MORFAC', 'MORFT', 'MFTAVG', 'MORAVG'
    ]):
    
    #### Clean for mr Barker
    # trim_clean = trim.drop_vars(['ALFAS', 'KCU', 'KCV', 'KCS', 'GSQS', 'PPARTITION', 'KFU', 'KFV', 'TAUKSI', 'DICWW', 'VICWW',
    #                 'TAUETA', 'TAUMAX', 'UMNLDF', 'VMNLDF', 'SBUUA', 'SBVVA', 'SSUUA', 'SSVVA', 'MORFAC', 'MFTAVG', 'MORAVG', 'TAUETA',
    #                            'R1', 'DG', 'MORFT', 'DM', 'VICUV', 'DPU0', 'DPV0', 'WPHY', 'DMSEDCUM', 'LYRFRAC', 'MSED', 'W', 'WS', 'RICH', 'RTUR1'], errors='ignore')

    #     trim_clean.load().to_netcdf('clean_compressed_sampleD3D.nc', mode='w', engine='netcdf4', format='NETCDF4')     
    
    # Remove component DataArrays from DataSet
    print("Dropping a bunch of DataArrays from DataSet...", end='')
    
    nc = nc.drop_vars(drop_list, errors='ignore')    
    print('Done dropping variables.')    

    return nc

# WORK IN PROGRESS: need to figure out how to pass DataSet as argument maintaining reference, ie allowing functions to access DataArrays in passed DataSet
def processNetCDF(nc, mystery_flag=True, bottom_stress=True, sum_sediments=True, sum_velocities=True, drop_junk=True):
    '''
    Chains all the nc processing steps
    Add drop_list and sediment_dicts as keyword arguments
    '''
    
    sediment_vect_component = [
        { # suspended load
            'U_V_keys': ['SSUU', 'SSVV'],
            'attrs': {'long_name': 'Suspended-load transport', 'units': 'm3/(s m)', 'grid': 'grid', 'location': 'edge1'}, # sediment name is added to this
            'dims': ('time', 'M', 'N'),
            'new_key': 'susp_load', # sediment name is appended to this
        },
        { # bed load
            'U_V_keys': ['SBUU', 'SBVV'],
            'attrs': {'long_name': 'Bed-load transport', 'units': 'm3/(s m)', 'grid': 'grid', 'location': 'edge1'}, # sediment name is added to this
            'dims': ('time', 'M', 'N'),
            'new_key': 'bed_load', # key for DataSet sediment name is appended to this
        }    
    ]
    
    bottom_stress_attrs = {'long_name': 'Bottom stress', 'units': 'N/m2', 'grid': 'grid', 'location': 'edge1'}
    bottom_stres_dims = ('time', 'M', 'N')
    
    # The processing chain
    nc = fixMeshGrid(nc, nc.XZ.values, nc.YZ.values, mystery_flag=mystery_flag)
    print("● Fixed mesh grid") # find a way to nicely chain these. just mutate nc for sake of ease?    
    nc = addDepth(nc) # needs to be done BEFORE makeVelocity!
    print("● Added depth & depth_center to DataSet")    
    nc = addVectorSum(nc, 'TAUKSI', 'TAUETA', key="bottom_stress", attrs=bottom_stress_attrs, dims=bottom_stres_dims) if bottom_stress else print("● Skipping bottom stress")
    nc = makeVectorSumsSediments(nc, sediment_dicts=sediment_vect_component) if sum_sediments else print("● Skippin¡g sediment sums")
    nc = makeVelocity(nc) if sum_velocities  else print("● Skipping velocity sum") # nc.U1.values, nc.V1.values
    print("● Summed horizontal velocity")
    nc = addUnderlayerCoords(nc)
    print("● Assigned underlayer coordinates")
    nc['bottom_diff'] = nc.DPS.isel(time=0) - nc.DPS
    print("● Made accumulated deposition/erosion")
    nc = dropJunk(nc)

    return nc
    
# add flags for what vector sums to write
# dict for each vector sum? [{'dims': , 'attrs': , 'key': '', }
def writeCleanCDF(ncfilename, chunks=10, mystery_flag=False):
    '''
    Add vector sum for velocities and sediment transport DataArrays to DataSet
    Remove useless stuff and save new netCDF to disk
    TODO: Whats a good chunk number?
    '''
    
    with xr.open_dataset(ncfilename, chunks={'time': chunks}) as nc:
        nc = fixMeshGrid(nc, nc.XZ.values, nc.YZ.values, mystery_flag=True)
        nc = addDepth(nc)
        nc = makeVelocity(nc)
#         nc = makeBottomStress(nc)
#         nc = addVectorSum(nc, 'TAUKSI', 'TAUETA', key="bottom_stress", attrs=bottom_stress_attrs, dims=bottom_stres_dims)
        print("Calculated bottom stress sum")
        nc = addUnderlayerCoords(nc)
        nc = dropJunk(nc)
        print("Dropped variables from DataSet")
        
        root, ext = path.splitext(ncfilename)
        new_filename = root + '_clean' + ext
        
        # TODO overwrite old NetCDF so we don't have to calculate vector sums again U SURE THO?
        print("Start writing netCDF to disk...", end='')
        nc.load().to_netcdf(new_filename, mode='w', engine='netcdf4', format='NETCDF4') 
        print("Succesfully written new file as ", new_filename)
        
        return new_filename

