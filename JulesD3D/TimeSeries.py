import os
import re
import numpy as np
import pandas as pd
from JulesD3D.utils import formatSci
from JulesD3D.mdf import read
from IPython.display import Markdown as md

# from https://github.com/Carlisle345748/Delft3D-Toolbox/blob/master/delft3d/TimeSeriesFile.py

class TimeSeries(object):
    """Read, modify and export Delft3D time series."""
    def __init__(self, time_series: list):
        self.time_series = None
        self.header = None
        self.load_header(time_series)
        self.load_time_series(time_series)

    def load_header(self, time_series: list):
        """Read and interpret the header of a time series."""
        header_dict = {}
        parameter = {}
        records_in_table = None
        header_re = re.compile(r"^([^-][\w-]+)\s+('?[\w\d (),./:-]+'?)")
        unit_re = re.compile(r"([\s]+unit '\[[\w/]+\]')")
        for line in time_series:
            matches = header_re.search(line)  # search for header
            if matches:
                if matches[1] == 'parameter':
                    # parameters have the same header name. So store all parameters
                    # in one dict
                    unit_match = unit_re.search(line)  # search for unit
                    key_name = matches[2].strip('\'')  # reformat unit
                    key_name = key_name.strip(' ')
                    parameter[key_name] = Parameter(matches[2], unit_match[1])
                elif matches[1] == 'records-in-table':
                    # records-in-table should be the last header. Store it hera and
                    # then put it at the end of headers by the end.
                    records_in_table = Parameter(matches[2])
                else:
                    # regular header
                    header_dict[matches[1]] = Parameter(matches[2])
            else:  # end of the header
                header_dict['parameter'] = parameter
                header_dict['records-in-table'] = records_in_table
                break
        self.header = header_dict

    def load_time_series(self, time_series: list):
        """Read and interpret time series"""
        is_header = True  # whether the pointer at the header
        reference_time = pd.to_datetime(self.header['reference-time'].value)
        # read the time series data
        time, relative_time, parm1, parm2 = [], [], [], []
        for line in time_series:
            if not is_header:
                # prepossess
                data = [float(i) for i in line.split()]
                time.append(reference_time + pd.to_timedelta(data[0], unit="minutes"))
                # store the data
                relative_time.append(data[0])
                parm1.append(data[1])
                parm2.append(data[2])
            if 'records-in-table' in line:
                is_header = False
        else:
            # converts lists to DataFrame
            colname = list(self.header['parameter'].keys())
            time_series = pd.DataFrame(
                {colname[0]: relative_time, colname[1]: parm1, colname[2]: parm2}, index=time)
        self.time_series = time_series

    def set_header(self, data: dict, unit=False) -> None:
        """Set new content of header. Called by TimeSeriesFile.set_header()"""
        header = self.header.copy()
        for key, new_parm in data.items():
            if key != 'parameter':
                # regular header
                header[key].value = str(new_parm)
            else:
                # parameter
                for key_, new_parm_ in new_parm.items():
                    if unit:
                        header[key][key_].unit = str(new_parm_)
                    else:
                        header[key][key_].value = str(new_parm_)
        self.header = header

    def set_time_series(self, reference_time: str,
                        data1: pd.core.frame.Series,
                        data2: pd.core.frame.Series):
        """
        Replace the old time series with the new one. Called by TimeSeriesFile.set_time_series()
        """
        time_series = pd.concat([data1, data2], axis=1)
        # calculate the absolute time and  relative time
        reference_time = pd.to_datetime(reference_time)
        relative_time = time_series.index - reference_time
        relative_time = [time.total_seconds() / 60 for time in relative_time]  # 单位：minute
        relative_time = pd.Series(relative_time, index=time_series.index, name='time')
        # combine time absolute time, relative time and data
        time_series = pd.concat([relative_time, time_series], axis=1)
        # store new time series
        self.time_series = time_series.copy()
        # change the 'reference time' and 'records-in-table' in the header
        reference_time = reference_time.strftime("%Y%m%d")
        self.set_header({'records-in-table': len(time_series), "reference-time": reference_time})

    def export_header(self):
        """Export the header as a list in the format of Delft3D time series file"""
        header = []
        for key, parm in self.header.items():

            if key != 'parameter':
                # parameter header
                head = key.ljust(21) + parm.export() + '\n'
                header.append(head)
            else:
                # regular header
                for i in parm:
                    head = key.ljust(21) + parm[i].export() + '\n'
                    header.append(head)
        return header

    def export_time_series(self):
        """Export the time series as a list in the format of Delft3D time series files"""
        time_series = []
        for index, row in self.time_series.iterrows():
            time_series.append(" {:.7e} {:.7e} {:.7e}\n".format(row[0], row[1], row[2]))
            pass
        return time_series

    def export(self):
        """Export all data as a list in the format of Delft3D time series files"""
        return self.export_header() + self.export_time_series()


class Parameter(object):
    """
    Read and export the content of header in Delft3D Time Series. The function of this class
    is to keep the original format of Delft3D Time Series in order to prevent unexpected errors.
    """
    def __init__(self, value, unit=None):
        """Read the store the format, type and unit of a header"""
        value_re = re.compile(r'[\w() /:,.-]+\b\)?')  # search for the value
        value_match = value_re.search(value)
        self.value = value_match[0]
        if '\'' in value:
            # string type
            self.value_length = len(value) - 2  # length of the string
            self.type = 'str'
        else:
            # number type
            self.value_length = len(value)  # length of the number
            self.type = 'num'

        self.unit = None
        # store the unit
        if unit:
            # search for unit
            unit_re = re.compile(r"unit '\[([\w/]+)\]'")
            unit_match = unit_re.search(unit)
            # store the unit
            self.unit = unit_match[1]
            self.unit_length = len(unit)

    def export(self):
        """export the header in its original format"""
        if self.type == 'str':
            content = "'{}'".format(self.value.ljust(self.value_length))
            if self.unit:
                content += ("unit '[{}]'".format(self.unit)).rjust(self.unit_length)
        else:
            content = "{}".format(self.value.ljust(self.value_length))

        return content

    def __repr__(self):
        if self.unit:
            return "{} unit={}".format(self.value, self.unit)
        else:
            return "{}".format(self.value)

        
#         """
# UNFINISHED! Doesnt do anything yet

# Modified from https://github.com/spmls/pydelft
# The MIT License (MIT)

# Copyright (c) 2014 spmls

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# """

# class TimeSeries():
#     '''Delft3d boundary conditions time-series file'''
#     def __init__(self,filename=None, bnd_filename=None):
#         if filename:
#             self.read_bct(filename)
#         if bnd_filename:
#             self.bnd = Boundaries.read(bnd_filename)

#     def read_bct(self, filename=None):
#         '''Read a Delft3d boundary conditions time-series file'''
#         if not filename:
#             raise Exception("No boundary filename given!")
#         else:
#             filename = filename

#         self.filename = filename

#         self.name = ""
#         self.contents = ""
#         self.location = ""
#         self.time_function = ""
#         self.reference_time = ""
#         self.time_unit = ""
#         self.interpolation = ""
#         self.parameter = ""
#         self.data = ""