import os.path
import pytest
import shutil
import subprocess

from casm.misc.contexts import captured_output, print_stringIO
import casm.vasp


def test_vasp_relax(vasp_cmd, ZrO_vasp_rundir):
    """ Test vasp.Relax.run() (Work in progress) """
    rundir = str(ZrO_vasp_rundir)
    # print("rundir:", rundir)

    # additional vasp.Relax settings
    settings = {"vasm_cmd": vasp_cmd}

    with captured_output() as (sout, serr):
        subprocess.run("ls", cwd=rundir)
        # calculation = casm.vasp.Relax(rundir, case["settings"])
        # calculation.run()
        # assert True
    #print_stringIO(sout) # print stdout from captured_output context
    #print_stringIO(serr) # print stderr from captured_output context
