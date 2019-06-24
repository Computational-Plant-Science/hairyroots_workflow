'''
    Unit tests for the workflow that test:
    * process_sample()
    * correct formatting and values in WORKFLOW_CONFIG
    * correct foramtting and values in workflow.parameters
'''
from os import getcwd
from os.path import join, isfile, exists
import shutil, errno
import json
import subprocess
import tempfile
import pickle

from helpers import fake_args, check_group_format


def test_workflow_name():
    from workflow import WORKFLOW_CONFIG
    assert WORKFLOW_CONFIG['name'] != None

def test_workflow_app_name():
    from workflow import WORKFLOW_CONFIG
    assert WORKFLOW_CONFIG['name'] != None
    assert WORKFLOW_CONFIG['app_name'].isidentifier()

def test_workflow_description():
    from workflow import WORKFLOW_CONFIG
    assert WORKFLOW_CONFIG['description'] != None

def test_workflow_icon_loc():
    from workflow import WORKFLOW_CONFIG
    assert WORKFLOW_CONFIG['icon_loc'] != None

def test_workflow_singularity_url():
    from workflow import WORKFLOW_CONFIG
    assert WORKFLOW_CONFIG['singularity_url'] != None

def test_workflow_api_version():
    from workflow import WORKFLOW_CONFIG
    assert WORKFLOW_CONFIG['api_version'] >= 0.1

def test_parameter_formatting():
    from workflow import parameters

    for group in parameters:
        check_group_format(group)

def test_process_sample(tmp_path,fake_args):
    '''
        Test processing a sample. process_sample is run just like it will be
        in production. That is, inside the singularity container
        at WORKFLOW_CONFIG['singularity_url'].

        This test passes if:
         * process_sample completes with a run code of 0
         * A results file is created
    '''
    from workflow import WORKFLOW_CONFIG

    sample_name = 'Fake'
    sample_path = join(tmp_path,'fake_sample')

    #Copy a file into fake_sample. by default, the test passes a junk data file
    # to process_sample. It is recommended that the empty file is replaced with
    # a real sample, and my be necessary to get the test to pass
    src = join(getcwd(),'tests','sample','fake_sample')
    try:
        shutil.copytree(src,sample_path)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, sample_path)
        else:
            raise


    with open(join(tmp_path,'params.json'),'w') as fout:
        args = {
            'sample_path': sample_path,
            'sample_name': sample_name,
            'args': fake_args
        }
        json.dump(args,fout)

    if('pre_commands' in WORKFLOW_CONFIG.keys()):
        cmd = [s.format(workdir=getcwd()) for s in WORKFLOW_CONFIG['pre_commands']]
        ret = subprocess.run(cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    extra_flags = [s.format(workdir=getcwd()) for s in WORKFLOW_CONFIG.get('singularity_flags',[])]
    ret = subprocess.run(["singularity",
                          "exec"
                          ] + extra_flags + [
                          "--containall",
                          "--home", tmp_path,
                          "--bind", "%s:/user_code/"%(getcwd()),
                          "--bind", "%s:/bootstrap_code/"%(join(getcwd(),'tests')),
                          "--bind", "%s:/results/"%(tmp_path),
                          WORKFLOW_CONFIG['singularity_url'],
                          "python3", "/bootstrap_code/bootstrapper.py"
                         ],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    print(ret.stdout)
    print(ret.stderr)

    assert ret.returncode == 0

    results = pickle.load(open(join(tmp_path,'results.pkl'),'rb'))

    #More advanced testing of results could be performed by inspecting the
    #data in results. This is left to the workflow developer (you).
    assert isinstance(results,dict)