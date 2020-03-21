import numpy as np
import sys
import os
import pandas as pd

class bnd():
    '''Delft3d boundary definition file'''
    def __init__(self, fname=None):
        self.read_bnd(fname)
        
    def read_bnd(self, fname=None):
        '''Read a Delft3d boundary definition file'''
        if not fname:
            raise Exception("No boundary filename given!")

        column_names = ['name','type','forcing','m1','n1','m2','n2',
                        'reflection coefficient','vertical profile',
                        'label1','label2']
        bnd_data = pd.read_csv(fname, delim_whitespace=True,header=None,
                           names = column_names)

        display(bnd_data)
        for n in bnd_data.columns:
            setattr(self, n, np.array(bnd_data[n]))

        self.num_bnds = np.size(self.name)

    def read_grd(self, fname=None):
        self.grid = grd(fname)
        print('loaded %s' %self.grid.filename)

    def get_xy(self):
        '''Get x,y coordinates of each boundary section from associated
        grid.'''
        x1 = []
        for i in self.m1:
            # m,n indices in .bnd start from 1 and are 1 greater than
            # the array size...
            if i-1 == self.grid.x[0].size:
                x1.append(self.grid.x[0][i-2])
            else:
                x1.append(self.grid.x[0][i-1])
        x2 = []
        for i in self.m2:
            if i-1 == self.grid.x[0].size:
                x2.append(self.grid.x[0][i-2])
            else:
                x2.append(self.grid.x[0][i-1])
        y1 = []
        for i in self.n1:
            if i-1 == self.grid.y[:,0].size:
                y1.append(self.grid.y[:,0][i-2])
            else:
                y1.append(self.grid.y[:,0][i-1])
        y2 = []
        for i in self.n2:
            if i-1 == self.grid.y[:,0].size:
                y2.append(self.grid.y[:,0][i-2])
            else:
                y2.append(self.grid.y[:,0][i-1])
        self.x1 = np.array(x1)
        self.x2 = np.array(x2)
        self.y1 = np.array(y1)
        self.y2 = np.array(y2)
