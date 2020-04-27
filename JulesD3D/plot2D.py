import xarray as xr
from JulesD3D.processNetCDF import makeVelocity, addDepth

# layer averaged only!
def makeVerticalLengthSlice(dataset, keyword):
    '''
    Return xarray DataArray that is edited for vertical plotting
    '''
    if keyword not in dataset:
        raise Exception(f"Can't find {keyword} in DataSet")
    if not 'depth_center' in dataset or not 'depth' in dataset:
        print("Adding depths to DataSet...")
        dataset = addDepth(dataset)
        
    # check if this DataArray is really at centers
    if 'KMAXOUT_RESTR' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth_center=(
            ('time', 'M', 'N', 'KMAXOUT_RESTR'), dataset.depth_center.values)
        )

        # make a mesh grid
        mesh_N_lyr, _ = xr.broadcast(dataset.YZ[0], dataset.SIG_LYR)

        N_KMAXOUT_RESTR = xr.DataArray(mesh_N_lyr, dims=['N', 'KMAXOUT_RESTR'], 
                                coords={'N': dataset.N, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                attrs={'units':'m', 'long_name': 'Y-SIG_LYR Meshgrid'})

        vertical_slice.coords["N_KMAXOUT_RESTR"] = N_KMAXOUT_RESTR   
    elif 'KMAXOUT' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth=(
            ('time', 'M', 'N', 'KMAXOUT'), dataset.depth.values)
        )

        mesh_N_intf, _ = xr.broadcast(trim.YZ[0], trim.SIG_INTF)

        N_KMAXOUT = xr.DataArray(mesh_N_intf, dims=['N', 'KMAXOUT'], 
                                coords={'N': dataset.N, 'KMAXOUT': dataset.KMAXOUT},
                                attrs={'units':'m', 'long_name': 'Y-SIG_INTF Meshgrid'})

        vertical_slice.coords["N_KMAXOUT"] = N_KMAXOUT
    else:
        raise Exception('This DataArray does not have the right dimensions')
    
    return vertical_slice

# matplotib function here