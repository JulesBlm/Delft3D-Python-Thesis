import re
from collections import OrderedDict

def read(mor_file):
    groups = {}
    keyword_order = []

    f = open(mor_file, "r")

    group_names = ['[MorphologyFileInformation]', '[Morphology]', '[Underlayer]', '[Output]']
    
    for line in f.readlines():
        if line.strip() in group_names:
            group_name = line.strip()
            groups[group_name] = OrderedDict()
            
        if "=" in line:
            # make new entry in dict
            keyword, values = line.split("=", 1)
            
            list_of_values = re.split(r'\s{2,}', values.strip())
  
            # sort these into value, unit, description
            # hard to get right if some have units and other don't
#             if len(list_of_values) == 3:
#                 value = list_of_values[0]
#                 unit = list_of_values[1]
#                 description = list_of_values[2] 
#             elif len(list_of_values) == 2:
#                 print(list_of_values)
#             elif len(list_of_values) == 1:                
#                 value = list_of_values[0]            
            
            keyword = keyword.strip()
            groups[group_name][keyword] = list_of_values[0]

    f.close()

    return groups

def write(morkeywords, mor_filename=None, exclude=[]):

    """Write and OrderedDict to Delft3D-FLOW *.mor file.
   To ignore a keyword use keyword 'exclude', e.g. to enforce cold start:
      >> mdf.write(inp,'c.mdf',exclude=['Restid']) 
      """
    if not mor_filename:
        print("No filename provided, file will be written is new.mor in current folder")
        mor_filename = "new.mor"

    with open(mor_filename, 'w') as new_mor_file:

        for keyword in morkeywords:
            if not (keyword in exclude):
                new_mor_file.write(f"{keyword}\n")
                for subkey in morphology[keyword]:
                    new_mor_file.write(f"   {subkey.ljust(16)} = {morphology[keyword][subkey]}\n")