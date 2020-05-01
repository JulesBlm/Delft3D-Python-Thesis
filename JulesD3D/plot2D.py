import xarray as xr
from JulesD3D.processNetCDF import makeVelocity, addDepth

def makeVerticalLengthSlice(dataset, keyword, along_length=True):
    '''
    Return xarray DataArray that is edited for vertical plotting
    By default along length, set to along_length=False to get section along width
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

        if along_length:
            # make a mesh grid along length
            mesh_N_lyr, _ = xr.broadcast(dataset.YZ[0], dataset.SIG_LYR)

            N_KMAXOUT_RESTR = xr.DataArray(mesh_N_lyr, dims=['N', 'KMAXOUT_RESTR'], 
                                    coords={'N': dataset.N, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                    attrs={'units':'m', 'long_name': 'Y-SIG_LYR Meshgrid'})

            vertical_slice.coords["N_KMAXOUT_RESTR"] = N_KMAXOUT_RESTR   
        else: 
            mesh_M_lyr, _ = xr.broadcast(dataset.XZ[0], dataset.SIG_LYR)

            M_KMAXOUT_RESTR = xr.DataArray(mesh_N_lyr, dims=['M', 'KMAXOUT_RESTR'], 
                                        coords={'M': dataset.M, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                        attrs={'units':'m', 'long_name': 'X-SIG_LYR Meshgrid'})

            vertical_slice.coords["M_KMAXOUT_RESTR"] = M_KMAXOUT_RESTR   

    elif 'KMAXOUT' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth=(
            ('time', 'M', 'N', 'KMAXOUT'), dataset.depth.values)
        )

        if along_length:
            mesh_N_intf, _ = xr.broadcast(trim.YZ[0], trim.SIG_INTF)

            N_KMAXOUT = xr.DataArray(mesh_N_intf, dims=['N', 'KMAXOUT'], 
                                    coords={'N': dataset.N, 'KMAXOUT': dataset.KMAXOUT},
                                    attrs={'units':'m', 'long_name': 'Y-SIG_INTF Meshgrid'})

            vertical_slice.coords["N_KMAXOUT"] = N_KMAXOUT
        else:
            mesh_M_lyr, _ = xr.broadcast(dataset.XZ[0], dataset.SIG_INTF)

            M_KMAXOUT = xr.DataArray(mesh_N_lyr, dims=['M', 'KMAXOUT'], 
                                        coords={'M': dataset.M, 'KMAXOUT': dataset.KMAXOUT},
                                        attrs={'units':'m', 'long_name': 'X-SIG_INTF Meshgrid'})

            vertical_slice.coords["M_KMAXOUT"] = M_KMAXOUT
            
    else:
        raise Exception('This DataArray does not have the right dimensions')
    
    return vertical_slice

# matplotib function here

