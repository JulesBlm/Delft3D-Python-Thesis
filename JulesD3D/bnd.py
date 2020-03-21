import pandas as pd

class Boundaries():
    '''
    Delft3D boundary definition file .bnd
    '''
    def __init__(self, fname=None):
        self.readBnd(self, fname)

    def readBnd(fname=None): # self?
        '''Read a Delft3d boundary definition file, return list of coordinated for plotting'''
        if not fname:
            raise Exception("No boundary filename given!")

        column_names = ['name','type','forcing','m1','n1','m2','n2',
                        'reflection coefficient','vertical profile',
                        'label1','label2']
        
        bnd_data = pd.read_csv(fname, delim_whitespace=True,
                        header=None, names=column_names)
        
        display(bnd_data)
        
        boundary_coords = []
        nr_of_bounds = bnd_data.shape[0]
        for i in range(nr_of_bounds):
            boundary_coords.append(([bnd_data.m1[i], bnd_data.n1[i]], [bnd_data.m2[i], bnd_data.n2[i]]))

        return boundary_coords

    # for plotting boundary locations 
    def getXY(coords):
        bc_x_coords, bc_y_coords = [[], []]
        for bnd in coords:
            x_coords, y_coords = list(zip(*bnd))
            bc_x_coords.append(x_coords)  # -1 ?
            bc_y_coords.append(y_coords)  # -1 ?
            
        return bc_x_coords, bc_y_coords