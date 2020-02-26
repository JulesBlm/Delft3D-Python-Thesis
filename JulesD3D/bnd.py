import pandas as pd

class bnd():
    '''Delft3d boundary definition file'''
    # def __init__(self, fname=None):
    #     self.readBnd(fname)
    #     # self.read_bnd(fname)

    def readBnd(fname=None): # self?
        '''Read a Delft3d boundary definition file, return list of coordinated for plotting'''
        if not fname:
            print("No file name supplied!")
            return

        column_names = ['name','type','forcing','m1','n1','m2','n2',
                        'reflection coefficient','vertical profile',
                        'label1','label2']
        
        data = pd.read_csv(fname, delim_whitespace=True,
                        header=None, names=column_names)
        
        display(data)
        
        boundary_coords = []
        nr_of_bounds = data.shape[0]
        for i in range(nr_of_bounds):
            boundary_coords.append(([data.m1[i], data.n1[i]], [data.m2[i], data.n2[i]]))

        return boundary_coords

    def getXYlistFromBndCoords(coords):
        bc_x_coords, bc_y_coords = [[], []]
        for bnd in coords:
            x_coords, y_coords = list(zip(*bnd))
            bc_x_coords.append(x_coords)  # -1 ?
            bc_y_coords.append(y_coords)  # -1 ?
            
        return bc_x_coords, bc_y_coords