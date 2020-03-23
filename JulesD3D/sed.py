# from https://github.com/spmls/pydelft
import pandas as pd

class Sed():
    '''Delft3d boundary sediment file'''
    # def __init__(self, fname=None):
    #     self.read(fname)
    #     # self.read_bnd(fname)

    def readSed(sed_filename=None): # self?
        if not sed_filename:
            raise Exception("No file name supplied!")

        f = open(sed_filename, "r")
        sediments = []
        keywords = {}  # empty dictionary

        for line in f.readlines():
            #start new columns
            if line == "[Sediment]":
                
                sediments.append()
                
            # these should form the rows
            if "=" in line:
                keyword, value = line.split("=", 1)
                keyword = keyword.strip()
                value = value.strip()
                keywords[keyword] = []
                new = True

        sed_df = pd.DataFrame(keywords)
        display(sed_df)

        # column_names = ['name','type','forcing','m1','n1','m2','n2',
        #                 'reflection coefficient','vertical profile',
        #                 'label1','label2']
        
        # data = pd.read_csv(fname, delim_whitespace=True,
        #                 header=None, names=column_names)
        
        # display(data)
        
        # return boundary_coords
