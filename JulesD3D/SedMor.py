import re
from collections import OrderedDict
from datetime import date

class SedMor(object):
    '''
    Delft3d sediment or morphology file
    
    TODO:
    * Add description with units from FLOW manual and display those when a sed or mor file is loaded
    * Should check against hardcoded dict to see if options are ok and show possible options and unitss
    * Same for loading descriptions of keywords
    * ipywidget type thing?
    * parse number values
    '''

    def __init__(self, filename=None):
        self.filename = filename
        self.sedmor_dict = OrderedDict()        
        self.read(filename)

    def __repr__(self):
        return str(self.sedmor_dict)
            
    def read(self, filename=None):
        valid_extensions = (".mor", ".sed")
        if not filename:
            raise Exception("No file name supplied!")
        elif not filename.endswith(valid_extensions):
            raise Exception("Filename does not end with .mor or .sed!")
            
        sed_header_names = ["[SedimentFileInformation]", "[SedimentOverall]", "[Sediment]"]
        mor_header_name = ["[MorphologyFileInformation]", "[Morphology]", "[Underlayer]", "[Output]"]
        header_names = sed_header_names + mor_header_name

        # TODO: Add description too
        # if filename.endswith(".mor"):
        #     mor_string_keywords = ['FileCreatedBy', 'FileCreationDate', 'FileVersion', 'MorUpd', 'IHidExp', 'ISlope', 'BcFil', 'IBedCond', 'ICmpCond', 'IUnderLyr', 'TTLForm', 'ThTrLyr', 'UpdBaseLyr', 'IniComp']
        #     mor_bool_keywords = ['NeuBcSand', 'NeuBcMud', 'DensIn', 'MorUpd', 'BedUpd', 'CmpUpd', 'NeglectEntrainment', 'EqmBc', 'UpdInf', 'Multi', 'UpwindBedload'] 
        #     mor_bool_output_keywords = ['VelocAtZeta', 'VelocMagAtZeta', 'VelocZAtZeta', 'ShearVeloc','MaximumWaterdepth','BedTranspAtFlux',
        #         'BedTranspDueToCurrentsAtZeta','BedTranspDueToCurrentsAtFlux','BedTranspDueToWavesAtZeta','BedTranspDueToWavesAtFlux',
        #         'SuspTranspDueToWavesAtZeta','SuspTranspDueToWavesAtFlux','SuspTranspAtFlux','NearBedTranspCorrAtFlux','NearBedRefConcentration',
        #         'EquilibriumConcentration','SettlingVelocity','SourceSinkTerms','Bedslope', 'Taurat','Bedforms','Dm','Dg',
        #         'Frac','MudFrac','FixFac','HidExp','Percentiles','CumNetSedimentationFlux','BedLayerSedimentMass','BedLayerDepth',
        #         'BedLayerVolumeFractions','BedLayerPorosity','StatWaterDepth',
        #         ]
        #     bool_keywords = mor_bool_keywords + mor_bool_output_keywords
        #     
        #     string_keywords = bool_keywords + mor_string_keywords # temporary hack
        # elif filename.endswith(".sed"):
        #     string_keywords = ['FileCreatedBy', 'VERSION', 'IopSus', 'SedTyp', 'Name']
        #     bool_keywords = []

        with open(filename, "r") as sed_file:
            sedmor_dict = OrderedDict()            

            for line in sed_file.readlines():
                stripped_lined = line.strip()
                if stripped_lined in header_names:
                    header_name = stripped_lined[1:-1] # remove square brackets
                    sedmor_dict[header_name] = OrderedDict()

                if "=" in line:
                    keyword, values = line.split("=", 1)
                    keyword = keyword.strip()

                    list_of_values = re.split(r'\s{2,}', values.strip()) # split on more than two spaces
                    
                    # TODO: keep a list of just sediment names
                    #if keyword == "Name":
                    #    self.sediments.append(list_of_values[0][1:-1]) # add sediment to list of sediment names

                    sedmor_dict[header_name][keyword] = list_of_values[0]

                    # TODO: parse values to right types
                    # In mor file: most are floats with some booleans and string
                    # In sed file: most are floats
                    #if keyword in string_keywords:
                    # elif keyword in bool_keywords:
                        # sedmor_dict[header_name][keyword] = list_of_values[0]

            self.sedmor_dict = sedmor_dict

        return self.sedmor_dict
        
    def write(self, sed_mor_dict, filename=None, exclude=[]):
        """Write OrderedDict to Delft3D-FLOW *.sed file.
          To ignore a keyword pass a list to keyword argument 'exclude',
          >> sed.write(inp, '5050.sed',exclude=['Restid']) 
          """
        if not filename:
            raise Exception("No filename provided")
            
        # update file info
        today = date.today()
        creation_date_string = today.strftime("%m/%d/%Y, %H:%M:%S")        
        
        if filename.endswith(".sed"):
            info_header = "SedimentFileInformation" 
        elif filename.endswith(".mor"):
             info_header = "MorphologyFileInformation"    
        
        sedmor_dict[info_header]['FileCreatedBy'] = "pyDelft3D-FLOW v ????" # TODO add global version here
        sedmor_dict[info_header]['FileCreationDate'] = creation_date_string

        
        with open(filename, 'w') as new_file:
            for header_name in sedmor_dict:
                new_file.write(f"[{header_name}]\n")
                for keyword in sed_mor_dict[header_name]:
                    if not (keyword in exclude):
                        new_file.write(f"   {keyword.ljust(16)} = {sed_mor_dict[header_name][keyword]}\n")        