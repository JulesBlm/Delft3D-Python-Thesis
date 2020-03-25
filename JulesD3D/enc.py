import pandas as pd

# check yDim, xDim are off by one or not

class Enclosure():
    '''
    Create a Delft3D enclosure file
    Enclosure excludes gridcells from computation
    
    Create a new enclosure
        enc = Enclosure()
    
    Load a enclosure from .enc file
        enc = Enclosure.read('channelonly.enc')
    
    Write enclosure to .enc file
        Enclosure.writeSimpleEnc(enc, 'complete.enc')
    
    Remember: Enclosure needs to be larger than boundary locations!
    '''
    def __init__(self, *args, **kwargs):
        self.dims = kwargs.get('dims')
        if not self.dims:
            raise Exception("No tuple of dimenstinos provided?")
        self.filename = kwargs.get('filename')
        xDim, yDim = self.dims
        
        if 'channel_length_index' in kwargs:
            self.channel_length_index = kwargs.get("channel_length_index")
            self.bank_left = kwargs.get('bank_left')
            self.bank_right = kwargs.get('bank_right')
            self.x = [1, self.bank_left, self.bank_left, self.bank_right, self.bank_right, xDim+1, xDim+1, 1, 1]
            self.y = [self.channel_length_index, self.channel_length_index, 1, 1, self.channel_length_index, self.channel_length_index, yDim+1, yDim+1, self.channel_length_index]
        elif 'read_filename' in kwargs:
            self.x = kwargs.get('x') # list of x coords
            self.y = kwargs.get('y') # list of y coords
        else: 
            self.x = [1, xDim + 1, xDim + 1, 1, 1]
            self.y = [1, 1, yDim + 1, yDim + 1, 1]

    def __repr__(self):
        repr_string = f"New Enclosure with xDim {self.dims[0]} and yDim {self.dims[1]}"
        
        # if self.channel_length_index and self.bank_left and self.bank_right: # can't acces these properties if they are not arguments to Enclosure
        #     repr_string += f" with channel at y = {self.channel_length_index} from {self.bank_left} to {self.bank_right}"
            
        return repr_string
    
    def display(self):
        enc_coords = {'x': self.x, 'y': self.y}
        enc_coords_df = pd.DataFrame(data=enc_coords)

        return display(enc_coords_df)

    @staticmethod
    def read(filename=None):
        '''Read a Delft3d enclosure file. Return list of x coordinates and list of y coordinates for easy plotting of enclosure'''
        if not filename:
            raise Exception("No file name supplied!")
                
        with open(filename, 'r') as f:
            enc_coords = [(int(line.split("   ")[1]), int(line.split("   ")[2])) for line in f]

            enc_x, enc_y = zip(*enc_coords) # unzip
        
            xDim = max(enc_x)
            yDim = max(enc_y)
            dims = (xDim, yDim)
            
            # how do i know from read file wether is has channel
            
            enc = Enclosure(dims=dims, read_filename=True, x=enc_x, y=enc_y)
            
            enc.x = enc_x
            enc.y = enc_y

            enc_coords = {'x': enc_x, 'y': enc_y}
            enc_coords_df = pd.DataFrame(data=enc_coords)
            
            print("Enclosure values")
            display(enc_coords_df)
            
            Enclosure.filename = filename
            
            return enc

    def getXY(self):
#         if self.x or not self.y:
#             raise Exception("No coords in this object")
        
        return self.x, self.y
        
        
    def write(self): # Add channel_width argument
        '''
        Write enclosure file,
        * with_channel: option to ignore 'banks' around channel
        '''
        if not self.filename:
            raise Exception("No enclosure filename supplied!")
        
        if not self.channel_length_index or not self.bank_left or not self.bank_right:
            raise Exception("bank_left, bank_right, and channel_length_index keyword arguments have to be provided when excluding areas from enclosure!")
            print(" ----- Writing enclosure file excluding channel -----")
        else:
            print(" ----- Writing simple (rectangular) enclosure -----")
        
        with open(self.filename, 'w') as enclosureOutfile:
            zipped = list(zip(self.x, self.y))
            enclosureLines = [('{:>6}{:>6}\n'.format(line[0], line[1])) for line in zipped] # pad both to 6 characters wide
            enclosureOutfile.writelines(enclosureLines)

        print(" ----- Wrote new .enc file to", self.filename)

        return [self.x, self.y]
