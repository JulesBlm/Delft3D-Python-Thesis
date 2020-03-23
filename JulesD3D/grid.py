# TODO: If uniform grid read grid cell size
import numpy as np
from numpy import format_float_scientific
import datetime
from JulesD3D.utils import formatSci, formatInt

class Grid(object):
    """Create a Delft3D grid file
	# Create an empty grid
	grid = Grid()
	# Load a grid from file
	grid = Grid.read('filename.grd')
	# Write grid to file
	Grid.write(grid,'filename.grd')
	"""

    def __init__(self, **kwargs):
        self.properties = kwargs.get("properties", {})
        self.shape = kwargs.get("shape", None)
        self.x = kwargs.get("x", None)
        self.y = kwargs.get("y", None)
#         self.x_gridstep =
#         self.y_gridstep = 

    @staticmethod
    def read(filename=None, **kwargs):
        if not filename:
            raise Exception("No grid filename given!")
        
        grid = Grid()
        grid.filename = filename
        grid.shape = None
        rows = []
        
        with open(filename) as f:
            for line in f:
                line = line.strip()
                # skip comments and empty lines
                if line.startswith("*") or not line:
                    continue
                elif "=" in line:
                    key, value = line.split("=")
                    if "Coordinate" in key:
                        grid.properties[key.strip()] = value.strip()
                    if "ETA" in key:
                        row = value.split()
                        n, row = row[0], row[1:]
                        while len(row) < grid.shape[1]:
                            line = f.readline()
                            row.extend(line.split())
                        rows.append(row)
                # Read grid size
                elif grid.shape == None:
                    # line should contain size
                    # convert to nrow x ncolumns
                    grid.shape = tuple(np.array(line.split()[::-1], dtype="int"))
                    assert (len(grid.shape) == 2), f"Expected shape (2,), got {grid.shape}, (subgrids not supported)"
                    
                    # also read next line
                    line = f.readline()
                    grid.properties["xori"], grid.properties["yori"], grid.properties["alfori"] = np.array(line.split(), dtype="float")
                    
        # rows now contain [X Y]
        data = np.array(rows, dtype="double")
        assert (data.shape[0], data.shape[1]) == (grid.shape[0] * 2, grid.shape[1]), f"Expected shape of data:{(grid.shape[0] * 2, grid.shape[1])} , got {(data.shape[0], data.shape[1])}"
        
        X, Y = data[: grid.shape[0], :], data[grid.shape[0] :, :]
        grid.x = np.ma.MaskedArray(X, mask=X == 0.0)  # apply standard nodatavalue of 0
        grid.y = np.ma.MaskedArray(Y, mask=Y == 0.0)  # apply standard nodatavalue of 0
        return grid

    def write(self, filename, **kwargs):

        f = open(filename, "w")

        nDim, mDim = np.shape(self.x)

        f.write("* Created at " + str(datetime.datetime.now()) + "\n")
        f.write(
            "* by Jules' modified OpenEarth Tools \n" + 
            "* Git url: https://github.com/JulesBlm/Delft3D-Python-Tools/Jules/grid.py $\n"
        )
        f.write("Coordinate System = " + self.properties["Coordinate System"] + "\n")
        coordinatesString = '      {}      {}\n'.format( self.formatInt(mDim), self.formatInt(nDim) )
        f.write(coordinatesString)
        properties = ' {} {} {}\n'.format(self.formatInt(self.properties["xori"]), self.formatInt(self.properties["yori"]), self.formatInt(self.properties["alfori"]) )
        f.write(properties)

        max_m_lines = 5
        
        nrow = int(np.ceil(mDim / max_m_lines))  # max 5 m-values per line

        for n in range(nDim):
            lowerBound = 0
            upperBound = min(5, mDim)
            nstr = self.formatInt(n + 1)

            # Write values with ETA = x prepended            
            ETAstring = " ETA= {:>4}   {}\n".format(nstr, "   ".join(self.formatSci(x) for x in self.x[n][lowerBound:upperBound]))
            f.write(ETAstring)

            # Write remaining values in ETA = m
            for i in range(1, nrow):
                lowerBound = i * max_m_lines
                upperBound = min((i + 1) * max_m_lines, mDim)
                f.write("             {}\n".format("   ".join(self.formatSci(x) for x in self.x[n][lowerBound:upperBound] )))

        # ?
        for n in range(nDim):
            lowerBound = 0
            upperBound = min(max_m_lines, mDim)
            nstr = self.formatInt(n + 1)
        
            lastETAstring = ' ETA= {:>4}   {}\n'.format(nstr, "   ".join(self.formatSci(y) for y in self.y[n][lowerBound:upperBound]))
            f.write(lastETAstring)
            
            for i in range(1, nrow):
                lowerBound = i * max_m_lines
                upperBound = min((i + 1) * max_m_lines, mDim)
                f.write('             {}\n'.format("   ".join(self.formatSci(y) for y in self.y[n][lowerBound:upperBound])))

        f.close()
