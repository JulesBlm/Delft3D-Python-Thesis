"""
Read/write Delft3D-FLOW *.mdf input files to/from dictionary
Todo:
* Split and write Runtxt correctly
"""
from JulesD3D.utils import formatSci
from collections import OrderedDict

#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2012 Deltares
#       Gerben J. de Boer
#
#       gerben.deboer@deltares.nl
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

# $Id: mdf.py 7870 2012-12-31 13:33:52Z boer_g $
# $Date: 2012-12-31 14:33:52 +0100 (Mon, 31 Dec 2012) $
# $Author: boer_g $
# $Revision: 7870 $
# $HeadURL: https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/OpenEarthTools/openearthtools/io/delft3d/mdf.py $
# $Keywords: $


def _RHS2val_(line, verbose=False):
    """parse 1(!) RHS line value from *.mdf file to a str, '' or float"""
    
    if verbose: print("_RHS2val_:", line)
    
    if "#" in line:
        # its a string!
        _, value, _ = line.split("#", 2)
    elif "[" in line:
        value = ""
    else:
        value = line.strip()
        split_value = value.split()
        
        if verbose: print("split value", split_value) 
        
        value = [float(value) for value in split_value]
        
    return value

def read(mdf_file, verbose=False):
    """Read Delft3D-Flow *.mdf file into dictionary.
      >> inp = mdf.read('a.mdf')
   Note that all comment lines and keyword formatting are not preserved.
    """

    keywords = OrderedDict()

    f = open(mdf_file, "r")

    columnwise_list = [
        "Thick",
        "Rettis",
        "Rettib",
        "u0",
        "v0",
        "s0",
        "t0",
        "C01",
        "C02",
        "C03",
        "C04",
    ]
    
    for line in f.readlines():
        if "=" in line:
            # make new entry in dict
            keyword, value = line.split("=", 1)
            keyword = keyword.strip()
            
            value = value.strip()
            keywords[keyword] = []
            new = True

        elif not (keyword == "Commnt"):
            value = line.lstrip()
            new = False

        if not (keyword == "Commnt"):
            value = _RHS2val_(value)
            if new:
                keywords[keyword] = value # either do [value] here
            else:
                if type(value) is str:
                    keywords[keyword] = keywords[keyword] + value
                else:
                    # append a lone value to existing keyword
                    keywords[keyword].append(value[0])

    f.close()

    return keywords


def _val2RHS_(f, keyword, value):
    """parse a list of str, '' or floats to multiple (!, if needed) RHS *.mdf lines"""
    # values that need to be written column-wise rather than row wise (although short row vectors are allowed)
    columnwise_list = [
        "Thick",
        "Rettis",
        "Rettib",
        "u0",
        "v0",
        "s0",
        "t0",
        "C01",
        "C02",
        "C03",
        "C04",
    ]

    if type(value) is str:
        if keyword == "Runtxt":
            # Mangles the runtext
            width = 30
            f.write(f"{keyword.ljust(7)}= #{str(value[:width])}#\n")
            for i in range(width, len(value), width):
                f.write(f"         #{value[i : i + width]}#\n")
        else:
            # Write these as strings
            f.write(f"{keyword.ljust(7)}= #{value}#\n")
    else:
        # Write these in scientific notation and column-wise
        if keyword in columnwise_list:
            f.write(f"{keyword.ljust(7)}=  {formatSci(value[0])}\n")
            for val in value[1:]:
                f.write(f"          {formatSci(val)}\n")
        else: 
            # Write these as simple integers
            if keyword in ['MNKmax', 'Iter', 'ncFormat', 'ncDeflate', 'Dt', 'Tzone', 'Restid_timeindex']: 
                joined_integer_values = " ".join(("%g" % x) for x in value)
                integer_string_to_write = f"{keyword.ljust(7)}= {joined_integer_values}\n"
                f.write(integer_string_to_write)
                return
            # Write these in scientific notation
            joined_values = "  ".join(formatSci(x) for x in value)
            sci_string_to_write = f"{keyword.ljust(7)}=  {joined_values}\n"
            f.write(sci_string_to_write)

def write(keywords, mdf_filename=None, exclude=[]):

    """Write dictionary to Delft3D-FLOW *.mdf file.
   The keywords are written in order,
      >> mdf.write(inp, 'b.mdf')
      >> inp = mdf.read('a.mdf')
      >> mdf.write(keywords, 'b.mdf')
      
   To ignore a keyword use keyword 'exclude' with list of keywords to ignore, e.g. to enforce cold start:
      >> mdf.write(inp,'c.mdf',exclude=['Restid']) 
      
   Example: modify time step Dt of collection Delft3D-FLOW simulations:
      >> import mdf, glob, os
      >> mdf_list = glob.glob('*.mdf');
      >> for mdf_file in mdf_list:
      >>    inp = mdf.read(mdf_file)
      >>    inp['Dt'] = [1]
      >>    mdf_base, ext = os.path.splitext(mdf_file)
      >>    mdf.write(inp, mdf_base + '_dt=1' + ext)
      """
    if not mdf_filename:
        print("No filename provided, file will be written is new.mdf in current folder")
        mdf_filename = "new.mdf"

    f = open(mdf_filename, "w")

    for keyword in keywords:
        if not (keyword in exclude):
            value = keywords[keyword]
            _val2RHS_(f, keyword, value)

    f.close()