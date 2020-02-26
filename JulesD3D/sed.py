import pandas as pd

class sed():
    '''Delft3d boundary sediment file'''
    # def __init__(self, fname=None):
    #     self.readBnd(fname)
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

        df2 = pd.DataFrame(keywords)
        display(df2)

        # column_names = ['name','type','forcing','m1','n1','m2','n2',
        #                 'reflection coefficient','vertical profile',
        #                 'label1','label2']
        
        # data = pd.read_csv(fname, delim_whitespace=True,
        #                 header=None, names=column_names)
        
        # display(data)
        
        # boundary_coords = []
        # nr_of_bounds = data.shape[0]
        # for i in range(nr_of_bounds):
        #     boundary_coords.append(([data.m1[i], data.n1[i]], [data.m2[i], data.n2[i]]))

        # return boundary_coords
