import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np
from JulesD3D.dep import Depth
from JulesD3D.grid import Grid
from JulesD3D.enc import Enclosure
from JulesD3D.bnd import Boundaries
from os import path, walk
from cmocean.cm import deep

colormap = deep

# Make this class containing objects of grid, bnd, enc, depth, mdf, sed files, bcc, bct

class D3DModel(object):
    '''
    Read a folder containing Delft3D4-FLOW files
    '''
    def __init__(self, *args, **kwargs):
        print("Ayyyyeyeyeye")
    
    def __repr__(self):
        return "Reads all Delft3D files in a folder"
    
    @staticmethod
    def readFolder(folderpath):
        if not path.exists(folderpath):
            raise Exception('Looks like read folder does not exist, aborting')
    
        basename = path.basename(folderpath)
        plot_title, _ = path.splitext(basename)
        title = basename

        all_filenames = []

        # Find filenames in template/read folder
        for root, dirs, files in walk(folderpath):
            for file in files:
                if file.endswith('bnd'):
                    bnd_filename = path.join(folderpath, file)
                    all_filenames.append({"type": "Boundary", "filename": path.split(bnd_filename)[1]})
                elif file.endswith('dep'):
                    dep_filename =  path.join(folderpath, file)
                    all_filenames.append({"type": "Depth", "filename": path.split(dep_filename)[1]})
                elif file.endswith('enc'):
                    enc_filename =  path.join(folderpath, file)
                    all_filenames.append({"type": "Enclosure", "filename":path.split(enc_filename)[1]})
                elif file.endswith('grd'):
                    grid_filename = path.join(folderpath, file)
                    all_filenames.append({"type": "Grid", "filename":path.split(grid_filename)[1]})

        files_df  = pd.DataFrame(data=all_filenames)
        display(files_df)
        
        self.filenames = all_filenames
        
    # def readGrid(self):
        
    #     grid = Grid.read(grid_filename)
    #     grid.shape

    #     dep = Depth.read(dep_filename, grid.shape)
    #     depth = dep.values[0:-1,0:-1]
        
    #     boundary_coords = bnd.readBnd(fname=bnd_filename)
        
        # enclosure_x, enclosure_y = readEnc(enc_filename)

