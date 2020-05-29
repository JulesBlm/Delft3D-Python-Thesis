# A bunch of hacky functions to prepare Delft3D-FLOW output for plotting and
# TODO: READ ABOUT OOP
# merge some functions into a class?
# leave it as is?
# Use unfunctions for vector sums

from JulesD3D.processing_2d import vector_sum
import xarray as xr
import numpy as np
from os import path
from IPython.display import Markdown as md 

# def renameConstituents
# # attempt to rename constituents dict of indexes to sediment names for more intuitive selection
# but doesnt work yet
## Also for turbulent quantities!
# sediments = [sed.decode('UTF-8').strip() for sed in trim.NAMCON.values]
# # # just for loop on size of seds
# aye_dict = {
#     0: sediments[0],
#     1: sediments[1]
# }
# trim['LSTSCI'] = sediments
# renamed = trim.rename_dims({'LSTSCI': 'sed'})
# renamed.sed

# Or just check the dummy cells out
def fixCORs(dataset):
    '''
    Last column and row of XCOR and YCOR are 0, this fixes that. Nice for plotting
    '''
    dataset.XCOR.load()
    dataset.YCOR.load()    
    
    dataset.XCOR[-1,:] = dataset.XCOR.isel(MC=-2).values + dataset.XCOR.isel(MC=1).values
    dataset.XCOR[:,-1] = dataset.XCOR.isel(NC=-2).values

    dataset.YCOR[:,-1] = dataset.YCOR.isel(NC=-2).values  + dataset.YCOR.isel(NC=1).values
    dataset.YCOR[-1,:] = dataset.YCOR.isel(MC=-2).values
    
    return dataset

def makeMeshGrid(length=45000, width=18000, x_gridstep=300, y_gridstep=300):
    '''
    Make a uniform meshgrid using given parameters
    TODO
    * Non-uniform meshgrids?
    * These default arguments only make sense for my current model
    '''
    
    # print("length:", length)
    # print("width:", width)
    # print("x_gridstep:", x_gridstep)
    # print("y_gridstep", y_gridstep)
    
    first_x_center = int(x_gridstep/2)
    xList = [0] + [i for i in range(first_x_center, int(width) + 1 * int(x_gridstep), int(x_gridstep))] #prepend a zero

    first_y_center = int(100 - y_gridstep/2)
    yList = [i for i in range(first_y_center, int(length) + 1 * int(y_gridstep), int(y_gridstep))] 

    xDim, yDim = [len(xList), len(yList)]
    print(xDim, "x", yDim, "grid")
 
    XZ, YZ = np.meshgrid(xList, yList) 
    
    return XZ.T, YZ.T # Why transpose again tho?

def fixMeshGrid(dataset, mystery_flag=False):
    '''
    Maybe this is not necessary if masks are applied properly
    Derives gridsteps and dimensions from passed DataSet
    Assumes uniform grid, curvilinear grid wont work here!
    Reference to XZ and YZ need to be passed explicitly because Dask loads the netCDF lazily
    The mystery flag is a Boolean because sometimes 1 and sometimes 2 gridsteps need to be subtracted from the length ¯\_(ツ)_/¯ , don't really know why (even vs uneven?)
    '''
    print("● Fixing mesh grid, assuming a uniform grid ")
    dataset.XZ.load()
    dataset.YZ.load()    
    
    x_gridstep = dataset.XZ.values[2][-1] - dataset.XZ.values[1][-1]
    y_gridstep = dataset.YZ.values[-2][-1] - dataset.YZ.values[-2][-2]
    
    width = (dataset.XZ.shape[0]-2) * x_gridstep
    if mystery_flag:
        length = (dataset.XZ.shape[1] - 1) * y_gridstep # eeehhh hmmmm -1? sometimes -2?
    else: 
        length = (dataset.XZ.shape[1] - 2) * y_gridstep # eeehhh hmmmm -1? sometimes -2?        
    
    md(f"""
    # Times
    | Name | Value |
    | --- | --- |
    | x gridstep | {x_gridstep} |
    | y gridstep | {y_gridstep} |
    | Width | {width} |
    | Length | {length} |
    
    """)    
    
    XZ, YZ = makeMeshGrid(length=length, width=width, x_gridstep=x_gridstep, y_gridstep=y_gridstep)

    # for debugging
    # print('original XZ', dataset.XZ.shape)
    # print('original YZ', dataset.YZ.shape)
    # print('new XZ', XZ.shape)
    # print('new YZ', YZ.shape)
    dataset.XZ.values = XZ
    dataset.YZ.values = YZ
    
    return dataset

def addDepth(dataset):
    '''
    Add true depth coords to dataset for plotting
    TODO: Test if LAYER_INTERFACE works
    '''

    #### depth at cell interfaces ####    
    # Set LayOut = #Y# in mdf to get LAYER_INTERFACE in map netcdf output file written during simulation 
    # But it's a trade-off between file size and processing time  ¯\_(ツ)_/¯

    if 'LAYER_INTERFACE' in dataset:
        print("LAYER_INTERFACE property alread in DataSet, renaming it to depth...")
        # LAYER_INTERFACE has masked values set to -999
        depth = dataset.LAYER_INTERFACE 
#         dataset.rename_vars({'LAYER_INTERFACE': 'depth'}) # does this even do anyhting?
    else:
        print("Calculating depth of interfaces...")
        depth = dataset.SIG_INTF @ dataset.DPS
        depth = depth.assign_attrs({"unit": "m", "long_name": "Depth at Sigma-layer interfaces"})

    depth = depth.transpose('time', 'M', 'N', 'SIG_INTF', transpose_coords=True)
   
    
    dataset.coords['depth'] = depth
    
    ##### depth at cell centers #####
    depth_center = dataset.SIG_LYR @ dataset.DPS
    
    depth_center = depth_center.transpose('time', 'M', 'N', 'SIG_LYR', transpose_coords=True)
    depth_center = depth_center.assign_attrs({"unit": "m", "long_name": "Depth at Sigma-layer centers"})

    dataset.coords['depth_center'] = depth_center
    # dataset.set_coords('depth_center') # hmmmm eeeehh 
    
#     ##### Add layer thickness DataArray to Data #####
    layer_thickness = np.diff(-depth.values)
    dataset['layer_thickness'] = (depth_center.dims, layer_thickness)
    dataset['layer_thickness'].attrs = {'long_name': 'Sigma-layer thickness', 'units': 'm'}
    
    return dataset


# This is not that useful as there are no coords to describe the positiion of the underlayer props
# Now it just plots it how it written to file, which is different from the what it's like in the model
def addUnderlayerCoords(dataset):
    '''
    Add underlayer coordinates to these data variables, which is nice for interactive plotting with Holoviews/hvPlot
    This is not that useful as there are 
    TODO: Use DP_BEDLYR to set for MSED and LYRFRAC as underlayer depth coords as depth
    '''
    
    dataset['MSED'] = dataset.MSED.assign_coords(nlyr=dataset.nlyr.values)
    dataset['LYRFRAC'] = dataset.LYRFRAC.assign_coords(nlyr=dataset.nlyr.values)
    dataset['DP_BEDLYR'] = dataset.DP_BEDLYR.assign_coords(nlyrp1=dataset.nlyrp1.values)
    
    dataset['nlyrp1'].attrs = {'standard_name': 'Interfaces of underlayers', 'long_name': 'Number of interfaces of underlayers'}
    dataset['nlyr'].attrs = {'standard_name': 'Number of underlayers', 'long_name': 'Number of underlayers'}
    
    return dataset

# This only works for sets that don;t have nested values
def addVectorSum(dataset, U_comp, V_comp, key="summed", attrs={}, dims=('time', 'M', 'N')):
    '''Adds summed DataArray to new key in DataSet and drops components from DataSet'''
    summed = vector_sum(dataset[U_comp].values, dataset[V_comp].values)
    dataset[key] = (dims, summed)
    dataset[key].attrs = attrs
        
    dataset = dataset.drop_vars([U_comp, V_comp])

    return dataset

# velocity is special thats why it gets its own function
# TODO add velocity angle here too
def makeVelocity(dataset, transpose=True, angle=False):
    
    # Make Horizontal velocity sum per layer
    velocity_sum = vector_sum(dataset.U1.values, dataset.V1.values) # Velocity per layer
    dataset['velocity'] = (('time', 'KMAXOUT_RESTR', 'M', 'N'), velocity_sum) # xr.DataArray
    dataset['velocity'].attrs = {'long_name': 'Horizontal velocity per layer', 'units': 'm/s', 'grid': 'grid', 'location': 'edge1'}
    
    # So it matches depth_center order of coords and add depth_center as coords
    # Saves time and processing power too if depth_center isn't already in dataset
    if transpose:
        print("makeVelocity: transposing dimensions to match those of depth.")
        if not 'depth_center' in dataset:
            print("Depth is not in DataSet already, adding it now...")
            dataset = addDepth(dataset)
        
        dataset['velocity'] = dataset.velocity.transpose('time', 'M', 'N', 'KMAXOUT_RESTR', transpose_coords=False)
        dataset['velocity'] = dataset.velocity.assign_coords(depth_center=(('time', 'M', 'N', 'KMAXOUT_RESTR'), dataset['depth_center'].values))
        
#     if angle:
        # TODO
        
    return dataset

def makeVectorSumsSediments(dataset, sediment_dicts=[]):
    '''
    Loops of all constituents (sediments) found in DataSet and sums their vector components and add them to DataSet,
    sediment_dicts is a list of dicts; each dict should have these keys
        'U_V_keys': ['U1', 'V1'],
        'attrs': {'long_name': 'Some long name', 'units': 'm', 'grid': 'grid', 'location': 'edge1'},
        'dims': ('time', 'M', 'N'),
        'new_key': 'susp_load', 
        
    TODO: Make more efficient with dask?
    '''
    if not sediment_dicts:
        raise Exception("The provided list of sediment components is empty. Stopping")
        return
    
    sediments = [str(sediment.rstrip()) for sediment in dataset.NAMCON.isel(time=0).values]

    for i, sediment in enumerate(sediments):
        print('------', sediment, '------')
        for datavar in sediment_dicts:
            U, V = datavar['U_V_keys']
            
            if U in dataset and V in dataset:
                new_summed_key = f"{datavar['new_key']}_{sediment[11:-1]}" # TODO: bad because this expects all constituents to be prefixed with sediment but who cares only i use this junk
                print("Adding to DataSet with key:", new_summed_key)
                key['attrs']['long_name'] = f"{kdatavarey['attrs']['long_name']} {sediment[2:-1]}"
                # print("New long name:", datavar['attrs']['long_name'])
                print(f"Summing {U} and {V} for {sediment}")
                dataset = addVectorSum(dataset, U, V, key=new_summed_key, attrs=datavar['attrs'], dims=key['dims'])
            else:
                print(f"⚠️ Keywords {U} and {V} are not present in given DataSet ⚠️")
                return dataset
    
    print("Done adding summed DataArrays for ", *(sed[2:-1] for sed in sediments), "to DataSet")    
    return dataset

def dropJunk(dataset, drop_list=[
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
    # dataset_clean = dataset.drop_vars(['ALFAS', 'KCU', 'KCV', 'KCS', 'GSQS', 'PPARTITION', 'KFU', 'KFV', 'TAUKSI', 'DICWW', 'VICWW',
    #                 'TAUETA', 'TAUMAX', 'UMNLDF', 'VMNLDF', 'SBUUA', 'SBVVA', 'SSUUA', 'SSVVA', 'MORFAC', 'MFTAVG', 'MORAVG', 'TAUETA',
    #                            'R1', 'DG', 'MORFT', 'DM', 'VICUV', 'DPU0', 'DPV0', 'WPHY', 'DMSEDCUM', 'LYRFRAC', 'MSED', 'W', 'WS', 'RICH', 'RTUR1'], errors='ignore')

    #     dataset_clean.load().to_netcdf('clean_compressed_sampleD3D.dataset', mode='w', engine='netcdf4', format='NETCDF4')     
    
    # Remove component DataArrays from DataSet
    print("Dropping a bunch of DataArrays from DataSet...", end='')
    
    dataset = dataset.drop_vars(drop_list, errors='ignore')    
    print('Done dropping variables.')    

    return dataset

# WORK IN PROGRESS: need to figure out how to pass DataSet as argument maintaining referedatasete, ie allowing fudatasettions to access DataArrays in passed DataSet
def processNetCDF(dataset, mystery_flag=True, bottom_stress=True, sum_sediments=True, sum_velocities=True, drop_junk=True):
    '''
    Chains all the dataset processing steps
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
    dataset = fixMeshGrid(dataset, dataset.XZ.values, dataset.YZ.values, mystery_flag=mystery_flag)
    print("● Fixed mesh grid") # find a way to nicely chain these. just mutate dataset for sake of ease?    
    dataset = addDepth(dataset) # needs to be done BEFORE makeVelocity!
    print("● Added depth & depth_center to DataSet")    
    dataset = addVectorSum(dataset, 'TAUKSI', 'TAUETA', key="bottom_stress", attrs=bottom_stress_attrs, dims=bottom_stres_dims) if bottom_stress else print("● Skipping bottom stress")
    dataset = makeVectorSumsSediments(dataset, sediment_dicts=sediment_vect_component) if sum_sediments else print("● Skippin¡g sediment sums")
    dataset = makeVelocity(dataset) if sum_velocities  else print("● Skipping velocity sum") # dataset.U1.values, dataset.V1.values
    print("● Summed horizontal velocity")
    dataset = addUnderlayerCoords(dataset)
    print("● Assigned underlayer coordinates")
    dataset['bottom_diff'] = dataset.DPS.isel(time=0) - dataset.DPS
    print("● Made cumulative deposition/erosion")
    dataset = dropJunk(dataset)

    return dataset
    
# add flags for what vector sums to write
# dict for each vector sum? [{'dims': , 'attrs': , 'key': '', }
def writeCleanDataset(dataset_filename, chunks=10, mystery_flag=False):
    '''
    Add vector sum for velocities and sediment transport DataArrays to DataSet
    Remove useless stuff and save new netCDF to disk
    TODO: Whats a good chunk number? Can determining chunk size be automated?
    '''
    
    with xr.open_dataset(dataset_filename, chunks={'time': chunks}) as dataset:
        clean_dataset = processNetCDF(dataset)
        
#         dataset = fixMeshGrid(dataset, dataset.XZ.values, dataset.YZ.values, mystery_flag=True)
#         dataset = addDepth(dataset)
#         dataset = makeVelocity(dataset)
# #         dataset = makeBottomStress(dataset)
# #         dataset = addVectorSum(dataset, 'TAUKSI', 'TAUETA', key="bottom_stress", attrs=bottom_stress_attrs, dims=bottom_stres_dims)
#         print("Calculated bottom stress sum")
#         dataset = addUnderlayerCoords(dataset)
#         dataset = dropJunk(dataset)
#         print("Dropped variables from DataSet")
        
        root, ext = path.splitext(dataset_filename)
        new_filename = root + '_clean' + ext
        
        print("Start writing netCDF to disk...", end='')
        dataset.load().to_netcdf(new_filename, mode='w', engine='netcdf4', format='NETCDF4') 
        print("Succesfully written new file as ", new_filename)
        
        return new_filename


# Why is this a seperate function and not in addDepth by default again?
# Could't I add depth coords to every data_var there with .map? 
# Things blew up when there are many multi-dimensional coords I think? eg depth, depth_center, N_KMAXOUT_RESTR, M_KMAXOUT_RESTR, N_KMAXOUT, M_KMAXOUT
# Think holoviews gets confused about which coords to take when there are 6 different multi-dimensional options
# How to add multiple kwargs that do the kinda the same thing? ie along_length along_width
def makeVerticalSlice(dataset, keyword, along_length=True, along_width=False, N=0, M=0):
    '''
    Returns DataArray that has extra coords meshgrid for convenient vertical plotting
    By default along length, set to along_length=False to get section along width
    TODO: proper time-dependant vertical meshgrid
    TODO: selecting the 0th index of YZ or XZ only works if the grid is uniform rectilinear
    '''
    if keyword not in dataset:
        raise Exception(f"Can't find {keyword} in DataSet")
    if not 'depth_center' in dataset or not 'depth' in dataset:
        print("Adding depths to DataSet...")
        dataset = addDepth(dataset)
    if along_width: # kinda ugly solution
        along_length = False
        
    # check if this DataArray is really at centers
    if 'KMAXOUT_RESTR' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth_center=(
            ('time', 'M', 'N', 'KMAXOUT_RESTR'), dataset.depth_center.values)
        )

        if along_length:
            # make a mesh grid along length
            mesh_N_siglyr, _ = xr.broadcast(dataset.YZ[0], dataset.SIG_LYR)

            N_KMAXOUT_RESTR = xr.DataArray(mesh_N_siglyr, dims=['N', 'KMAXOUT_RESTR'], 
                                    coords={'N': dataset.N, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                    attrs={'units':'m', 'long_name': 'Y-SIG_LYR Meshgrid'})

            vertical_slice.coords["N_KMAXOUT_RESTR"] = N_KMAXOUT_RESTR   
        else: 
            mesh_M_siglyr, _ = xr.broadcast(dataset.XZ[:,0], dataset.SIG_LYR)

            M_KMAXOUT_RESTR = xr.DataArray(mesh_M_siglyr, dims=['M', 'KMAXOUT_RESTR'], 
                                        coords={'M': dataset.M, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                        attrs={'units':'m', 'long_name': 'X-SIG_LYR Meshgrid'})

            vertical_slice.coords["M_KMAXOUT_RESTR"] = M_KMAXOUT_RESTR   

    elif 'KMAXOUT' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth=(
            ('time', 'M', 'N', 'KMAXOUT'), dataset.depth.values)
        )

        if along_length:
            mesh_N_intf, _ = xr.broadcast(dataset.YZ[0], dataset.SIG_INTF)

            N_KMAXOUT = xr.DataArray(mesh_N_intf, dims=['N', 'KMAXOUT'], 
                                    coords={'N': dataset.N, 'KMAXOUT': dataset.KMAXOUT},
                                    attrs={'units':'m', 'long_name': 'Y-SIG_INTF Meshgrid'})

            vertical_slice.coords["N_KMAXOUT"] = N_KMAXOUT
        else:
            mesh_M_lyr, _ = xr.broadcast(dataset.XZ[:,0], dataset.SIG_INTF)

            M_KMAXOUT = xr.DataArray(mesh_N_lyr, dims=['M', 'KMAXOUT'], 
                                        coords={'M': dataset.M, 'KMAXOUT': dataset.KMAXOUT},
                                        attrs={'units':'m', 'long_name': 'X-SIG_INTF Meshgrid'})

            vertical_slice.coords["M_KMAXOUT"] = M_KMAXOUT
    else:
        raise Exception('This DataArray does not have the right dimensions (KMAXOUT or KMAXOUT_RESTR)')
    
    return vertical_slice