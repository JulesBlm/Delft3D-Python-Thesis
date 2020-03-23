from JulesD3D.utils import formatSci
"""read/write Delft3D-FLOW *.dep files"""

__version__ = "$Revision: 7870 $"

#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2013 Deltares
#       Willem Ottevanger
#
#       willem.ottevanger@deltares.nl
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------
#
# This tool is part of <a href="http://www.OpenEarth.eu">OpenEarthTools</a>.
# OpenEarthTools is an online collaboration to share and manage data and
# programming tools in an open source, version controlled environment.
# Sign up to recieve regular updates of this function, and to contribute
# your own tools.

# $Id: dep.py 7870 2012-12-31 13:33:52Z ottevan $
# $Date: 2012-12-31 14:33:52 +0100 (Mon, 31 Dec 2012) $
# $Author: ottevan $
# $Revision: 7870 $
# $HeadURL: https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/OpenEarthTools/openearthtools/io/delft3d/dep.py $
# $Keywords: $

import numpy as np

class Depth(object):
    """Create a Delft3D dep file
    Create an dep grid
        dep = Depth()
    
    Load a dep from file (grid has to be loaded first)
        grid = Grid.read('filename.grd')
        dep  = Depth.read('filename.dep',grid.shape)
    
    Write dep to file
        Depth.write(dep,'filename.dep')"""

    def __init__(self, *args, **kwargs):
        self.properties = {}
        self.shape = None
        self.dep   = None

    def copy(self):
        copy = Depth()
        copy.shape = self.shape
        copy.values = self.values.copy()

        return copy

    # maybe i should rename all 'read' methods to 'fromFile' 🤔
    @staticmethod
    def read(filename, gridshape, **kwargs):
        dep = Depth()
        with open(filename, 'r') as f:
            strings = f.read()
            
            dep.values = np.array([float(s) for s in strings.split()])
            dep.values[dep.values == -999.0] = np.nan

            dep.shape = (gridshape[0] + 1, gridshape[1] + 1)
            dep.values = np.reshape(dep.values, dep.shape)

            return dep

    @staticmethod
    def write(dep, filename, **kwargs):
        
        print("Writing .dep file with shape", dep.shape)
        dep.values[np.isnan(dep.values)] = -999.0

        mDim, nDim  = dep.shape

        # Original : 42 strings in lines max 12 values
        with open(filename, 'w') as f:
            nrOfRows = int(np.ceil(mDim / 12))
            # print('------------------------------')
            # print("Loop ", mDim, "times")
            # print("Rowlength: ", nrOfRows)
            # print('------------------------------')

            for rowIndex in range(0, mDim):
                lowerBound = 0
                upperBound = min(12, mDim)
                # print('---------------')
                # print("Loop", rowIndex)
                # print(lowerBound, "to", upperBound)
                # print('---------------')
                for n in range(0, nrOfRows):
                    lowerBound = n * 12
                    upperBound = min((n + 1) * 12, mDim)
                    # print(lowerBound, "to", upperBound)
                    valuesList = dep.values[rowIndex][lowerBound:upperBound]
                    valueString = '  '.join(formatSci(value) for value in valuesList)
                    # print(valueString)
                    if valueString:
                        f.write("  " + valueString + '\n')

        f.close()