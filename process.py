import subprocess
import os.path

'''
    The code to run the workflow code on a sample
'''

def process_sample(name,current_path,args):
    '''
        Process a sample within the collection.

        This function is run within the singularity container defined in
        the WORKFLOW_CONFIG using the python3 interpreter.

        Args:
            name (str): name of the sample
            path (str): path to the sample file(s)
            args (dict): workflow parameters

        Returns:
            A python dictionary with any/all of the following keys:

            'key-val': a dictionary of key value pairs. These are accumulated
                from all the process_sample calls and placed in a csv file.
                Values must be primitives (float,int,string).

                Keys do not need to be the same across all samples. Keys missing
                from samples are set to NULL in the resulting csv file.

            'files': a list of paths to the files to include in the results.
                The files are placed in a "files" folder and compressed.

                The paths must be relative to the sample directory, which is the
                current directory when this script is called.

                Files names do not need to be unique between samples.
    '''
    settings = args['settings']['params']
    
    try:
    
    #python /opt/code/RootHairClean.py -p /work/akblab/vsm/hairyroot/
    
        cmd_line = "python /opt/code/RootHairClean.py -p " + current_path + "/"
    
        #print(cmd_line)
        
        process = subprocess.Popen(cmd_line, shell = True, stdout = subprocess.PIPE)
        
        process.wait()
        
        #print process.returncode
        
    except OSError:
        
        print("Failed ...!\n")
    
    
    
    #return {'files':[ current_path + '/hairyroots_result.csv' ]}
    return {'files':[ current_path + '/*.*' ]}
