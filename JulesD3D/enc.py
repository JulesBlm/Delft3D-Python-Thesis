import pandas as pd

# TODO turn into class with these functions as its methods
def readEnc(filename=None):
    '''Read a Delft3d enclosure file. Return list of x coordinates and list of y coordinates for easy plotting of enclosure'''
    if not filename:
        print("No file name supplied!")
        return
    enclosure_x = []
    enclosure_y = []
    with open(filename,'r') as f:
        for i, line in enumerate(f):
            # boy this is hacky change to list comprehension?
            enclosure_x.append(int(line.split("   ")[1]))
            enclosure_y.append(int(line.split("   ")[2]))
            
    enc_coords = {'x': enclosure_x, 'y': enclosure_y}
    coords_df = pd.DataFrame(data=enc_coords)            
    
    display(coords_df)
    
    return enclosure_x, enclosure_y

# Remember: Enclosure needs to be larger than boundary locations!


# SIMPLE ENCLOSURE FILE spanning complete domain
def writeSimpleEncFile(xDim, yDim, new_enc_filename=None):
    ''' Write rectangular enclosure'''
    if not new_enc_filename:
        print("No .enc filename specified aborting!")
    
    enclosureX = [1, xDim + 1, xDim + 1, 1, 1]
    enclosureY = [1, 1, yDim + 1, yDim + 1, 1]
    
    print(" ----- Writing simple rectangular enclosure -----")    
    with open(new_enc_filename, 'w') as enclosureOutfile:
        zipped = list(zip(enclosureX, enclosureY)) # merge x and y lists
        enclosureLines = [('{:>6}{:>6}\n'.format(line[0], line[1])) for line in zipped] # would line for line in work as well?
        enclosureOutfile.writelines(enclosureLines)

def writeEncFileWithChannel(xDim, yDim, new_enc_filename=None, bank_left=None, bank_right=None, channel_length_index=None): # Add channel_width argument
    ''' Write enclosure file, ignoring 'banks' around channel'''
    if not new_enc_filename:
        raise Exception("No enclosure file name supplied!")
    
    print(" ----- Writing enclosure file with channel -----")
    enclosureX = [1, bank_left, bank_left, bank_right, bank_right, xDim+1, xDim+1, 1, 1]  
    enclosureY = [channel_length_index, channel_length_index, 1, 1, channel_length_index, channel_length_index, yDim+1, yDim+1, channel_length_index]
    
    with open(new_enc_filename, 'w') as enclosureOutfile:
        zipped = list(zip(enclosureX, enclosureY))
        enclosureLines = [('{:>6}{:>6}\n'.format(line[0], line[1])) for line in zipped] # print both padded to 6 characters wide
#         [print(enclosureLine) for enclosureLine in enclosureLines]
        enclosureOutfile.writelines(enclosureLines)

    return [enclosureX, enclosureY]
