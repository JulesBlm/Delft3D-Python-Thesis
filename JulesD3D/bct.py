"""
UNFINISHED! Doesnt do anything yet

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

import numpy as np
from JulesD3D.grd import Grid
from JulesD3D.bnd import Boundaries
import pandas as pd

class bct():
    '''Delft3d boundary conditions time-series file'''
    def __init__(self,filename=None, bnd_filename=None):
        if filename:
            self.read_bct(filename)
        if bnd_filename:
            self.bnd = Boundaries.read(bnd_filename)

    def read_bct(self, filename=None):
        '''Read a Delft3d boundary conditions time-series file'''
        if not filename:
            raise Exception("No boundary filename given!")
        else:
            filename = filename

        self.filename = filename

        self.name = ""
        self.contents = ""
        self.location = ""
        self.time_function = ""
        self.reference_time = ""
        self.time_unit = ""
        self.interpolation = ""
        self.parameter = ""
        self.data = ""