"""
Modified from https://github.com/spmls/pydelft
The MIT License (MIT)

Copyright (c) 2014 spmls

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pandas as pd
from IPython.display import Markdown as md

class Boundaries():
    '''
    Delft3D boundary definition file .bnd
    '''
    def __init__(self, filename=None):
        # self.read(self, filename) # one way or the doesnt work with this way
        self.filename = filename
        self.coords = []

    @staticmethod
    def read(filename=None):
        '''Read a Delft3d boundary definition file, return list of coordinated for plotting'''
        if not filename:
            raise Exception("No boundary filename given!")

        bnd = Boundaries()
        column_names = ['name','type','forcing','m1','n1','m2','n2',
                        'reflection coefficient','vertical profile',
                        'label1','label2']
        
        bnd_df = pd.read_csv(filename, delim_whitespace=True,
                                header=None, names=column_names)
        
        bnd.bnd_df = bnd_df
        
        print("Boundary file")
        display(bnd_df)
        
        bc_coords = []
        nr_of_bounds = bnd_df.shape[0]
        for i in range(nr_of_bounds):
            bc_coords.append(([bnd_df.m1[i], bnd_df.n1[i]], [bnd_df.m2[i], bnd_df.n2[i]]))

        bnd.coords = bc_coords
        return bnd
    
    def display(self):
        if not self.bnd_df:
            print("No DataFrame present for this boundary file")

        display(self.bnd_df)
        
        return self.bnd_df

    # for plotting boundary locations 
    def getXY(self):
        if not self.coords:
            raise Exception("The list of boundaries coords is empty")
        
        bc_x_coords, bc_y_coords = [[], []]
        for bnd in self.coords:
            x_coords, y_coords = list(zip(*bnd))
            bc_x_coords.append(x_coords)  # -1 ?
            bc_y_coords.append(y_coords)  # -1 ?
            
        return bc_x_coords, bc_y_coords