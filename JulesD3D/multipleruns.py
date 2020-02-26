import os, fileinput, shutil, copy #, pprint
from numpy import format_float_scientific
import JulesD3D.mdf as mdf
from JulesD3D.utils import formatSci

# TODO: split into more composable functions
def replaceText(filename, new_filename, text_to_find, replacement_text):   
    with fileinput.FileInput(filename) as file, open(new_filename, 'w') as outfile: # inplace=True, backup='.bak')
        for line in file:
            outfile.write(line.replace(text_to_find, replacement_text))

# example: makeMultipleRuns(read_folder='/Users/julesblom/Dropbox/TU/Master/Thesis/Runs/2_5050/Run',\
# restId_base='trim-60km_300m_W60Channel', number_of_runs=5)
def makeMultipleRuns(read_folder=None, restId_base=None, number_of_runs=2, old_spin_up_time="9.0000000e+000", removeNetCdf=False, mor_smoothing_time=True):
    '''
    Takes a 'template' read folder and writes 'number_of_runs' new folders with times and some other parameters adjusted for subsequent restarts.
    restId_base: string value that is added to "RestId" keyword in all subsequent runs. Only if restartId is not equal to the mdf file(?)
    Smoothing time is changed to 0 for all subsequent runs, default string to replace is '9.0000000e+000'
    old_spin_up_time: String containing old initial value for 'Tlfsmo' keyword, "9.0000000e+000" is the default
    Only thing that has to be copied manually is the output from the previous run. This HAS to be in Deltares' own NEFIS output form.
    removeNetCdf flag to omit NetCDF flags in MDF file; False by default
    RunTXT is kind of mangled in subsequent MDF files because joins alls runtxt strings
    '''
    if not read_folder:
        raise Exception('No read folder supplied, aborting')
    elif not os.path.exists(read_folder):
        raise Exception('Looks like read folder does not exist, aborting')
    
    base_folder = os.path.dirname(read_folder)

    copy_extensions = ('xml', 'ini', 'enc', 'grd', 'sh', 'dep', 'bnd', 'sed', 'tra', 'log')
    bc_extension = ('bct', 'bcc', 'dis')
    copy_filenames = [] # These files just need to be copied to the next runs folder
    bc_filenames = [] # In these files, times are changed for subsequent runs

    # Find filenames in template/read folder
    for root, dirs, files in os.walk(read_folder):
        for file in files:
            if file.endswith(copy_extensions):
                copy_filenames.append(file)
            elif file.endswith(bc_extension):
                bc_filenames.append(file)
            elif file.endswith('.mdf'):
                mdf_filename = file
                print('mdf_filename', mdf_filename)
            elif file.endswith('.mor'):
                morph_filename = file
                
    if not restId_base:
        restId_base = 'trim-' + os.path.splitext(mdf_filename)[0]
        print("No restart Id string provided. Got it from mdf filename: ", restId_base)
    elif 'trim-' not in restId_base:
        print("Restart Id must start with substring 'trim-'. Aborting")
        return
                
    if not copy_filenames:
        print('Missing one of these files', ' '.join(copy_ext for copy_ext in copy_extensions))
    elif not bc_filenames:
        print('Missing one of these files', ' '.join(copy_ext for copy_ext in copy_extensions))
    elif not mdf_filename:
        print('Can\'t find .mdf file in folder')    
    elif not morph_filename:
        print('Can\'t find .mor file in folder')

    mdf_filepath = os.path.join(read_folder, mdf_filename)
    mdf_dict, inp_order = mdf.read(mdf_filepath)
    inp_order.append('Restid') # Append a restart ID tag to the MDF
    inp_order.append('Restid_timeindex')

    exclude_flags = []
    if 'FlNcdf' in mdf_dict and removeNetCdf == True:
        print('MDF file has Netcdf flags! Removing this key to ensure DEF/DAT output')
        print("Note that the template .mdf file will remain untouched, remove Netcdf flags manually from this file")
        exclude_flags = ['FlNcdf', 'ncFormat', 'ncDeflate']
    
    # init_start_time = formatSci(mdf_dict['Tstart'][0])
    init_end_time = mdf_dict['Tstop'][0] # this is also the duration of each flow (of course!)
    output_timestep = mdf_dict['Flmap'][1]
    original_run_text = mdf_dict['Runtxt']

    nr_outputsteps = int(init_end_time/output_timestep)
    print(f"Number of output timesteps is {nr_outputsteps}")
    
    mdf_dict['Restid_timeindex'] = [nr_outputsteps + 1]
    
    for run in range(number_of_runs):
        print('**--------- RUN' + str(run + 1) + '-----------**')

        new_start_time = run * init_end_time
        new_end_time = (run + 1) * init_end_time
        
        if run > 0:
            new_mdf_dict = copy.deepcopy(mdf_dict)

            run_folder = f'Run{run+1:02d}' 
            
            new_run_folder = os.path.join(base_folder, run_folder)
            print("New folder:", new_run_folder)
            
            try:  
                os.mkdir(new_run_folder)
            except OSError:
                if os.path.exists(new_run_folder):
                    print (f"Creation of the directory '{new_run_folder}' failed, because it already exists! Carrying on")
                else:
                    print (f"Creation of the directory '{new_run_folder}' failed for unknown reasons, abort")
                    break
                    
            # Simply copy these files to new run folder
            for file_to_copy in copy_filenames:
                old_file = os.path.join(read_folder,file_to_copy)
                new_copied_file = os.path.join(new_run_folder, file_to_copy)
                shutil.copy(old_file, new_copied_file)

            # Change things in new MDF File
            new_mdf_dict['Tstart'] = [new_start_time]   # Start time
            new_mdf_dict['Tstop'] = [new_end_time]      # End time
            new_mdf_dict['Flmap'][0] = new_start_time   # Start of writing map file
            new_mdf_dict['Flmap'][2] = new_end_time     # End of writing map file
            new_mdf_dict['Flhis'][0] = new_start_time   # Start of writing history file
            new_mdf_dict['Flhis'][2] = new_end_time     # End of writing history file
            new_mdf_dict['FlRst'] = 0                   # Dont write restart files
            
            # Set more frequent outputtime every 5th run
            # Pass as argument and check wether multiple of dt
#             if run % 5 == 0:
#                 new_mdf_dict['Flmap'] = short_outputtime
            
            new_mdf_dict['Runtxt'] = f'{original_run_text} Run {run+1:02}'

            new_mdf_dict['Restid'] = f'{restId_base}Run{run:02}'
            
            new_mdf_dict['Tlfsmo'] = [float(0.0e+0)]    # Change smoothing time to zero
            
            new_mdf_filename = os.path.join(new_run_folder, mdf_filename)
            mdf.write(new_mdf_dict, new_mdf_filename, selection=inp_order, exclude=exclude_flags)
            
            # Change spin-up interval (MorStt) for morphological changes to 0 in .mor file            
            template_morph_filename = os.path.join(read_folder, morph_filename)
            new_morph_filename = os.path.join(new_run_folder, morph_filename)
            
            old_spin_up_time_str = f"MorStt           =  {old_spin_up_time}"
            new_spin_up_time_str = "MorStt           =  0.0000000e+000"
            
            if mor_smoothing_time == True:
                print("Removing morphology smoothing time in subsequent runs")
                replaceText(template_morph_filename, new_morph_filename, old_spin_up_time_str, new_spin_up_time_str)
            else:
                # hacky but dont want to think about it
                replaceText(template_morph_filename, new_morph_filename, old_spin_up_time_str, old_spin_up_time_str)
                print("NOT removing morphology smoothing time in subsequent runs, I guess a MORFAC is on")
                
            # Add runtime in boundary conidition & transport files
            for bc_filename in bc_filenames:
                print(f"\tChanging times in {bc_filename}")
                # Create new filename with run folder prefix
                template_filename = os.path.join(read_folder, bc_filename)
                new_filename = os.path.join(new_run_folder, bc_filename)

                # Add end times and write to new file
                # its ugly but it works
                with open(template_filename,'r') as bc_template, open(new_filename, 'w') as new_bc_file:
                    lines = bc_template.readlines()
                    records_line_nrs = []

                    # Get line numbers of 'records'
                    for i, line in enumerate(lines):
                        if 'records-in-table' in line:
                            records_in_table = int(line.split()[1]) # number of records in table
                            start_end_line_nrs = (i + 1, i + 1 + records_in_table) # tuple containing first and last line nr's containing records
                            records_line_nrs.append(start_end_line_nrs)

                    # Use line numbers of 'records' to add runtime
                    for start_line_nr, end_line_nr in records_line_nrs:
                        for line_nr in range(start_line_nr, end_line_nr):
                            split_line = lines[line_nr].split('  ')
                            time = float(split_line[0]) + run * init_end_time
                            split_line[0] = formatSci(time)
                            lines[line_nr] = ' ' + '  '.join(value for value in split_line)
                            
                    new_bc_file.writelines(lines)
                
        print("Start time:", new_start_time, "\nEnd time:  ", new_end_time)