from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import *

import os
import re
import shutil
import six
import sys
from casm.vasp.io import oszicar, outcar, species, poscar
from casm.vasp.io import kpoints as kp
from casm.vasp.io import incar as inc
from casm.project.structure import StructureInfo

VASP_INPUT_FILE_LIST = [
    "INCAR", "STOPCAR", "POTCAR", "KPOINTS", "POSCAR", "EXHCAR", "CHGCAR",
    "WAVECAR", "TMPCAR"
]

DEFAULT_VASP_MOVE_LIST = ["POTCAR"]

DEFAULT_VASP_COPY_LIST = ["INCAR", "KPOINTS"]

DEFAULT_VASP_REMOVE_LIST = [
    "IBZKPT", "CHG", "CHGCAR", "WAVECAR", "TMPCAR", "EIGENVAL", "DOSCAR",
    "PROCAR", "PCDAT", "XDATCAR", "LOCPOT", "ELFCAR", "PROOUT"
]


class VaspIOError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def job_complete(jobdir=None):
    """Return True if vasp job at path 'jobdir' is complete"""
    if jobdir is None:
        jobdir = os.getcwd()
    outcarfile = os.path.join(jobdir, "OUTCAR")
    if (not os.path.isfile(outcarfile)) and (
            not os.path.isfile(outcarfile + ".gz")):
        return False
    if outcar.Outcar(outcarfile).complete:
        return True
    return False


def get_incar_tag(key, jobdir=None):
    """Opens INCAR in 'jobdir' and returns 'key' value."""
    if jobdir is None:
        jobdir = os.getcwd()
    tincar = inc.Incar(os.path.join(jobdir, "INCAR"))
    for k in tincar.tags:
        if key.lower() == k.lower():
            return tincar.tags[k]
    return None


def set_incar_tag(tag_dict, jobdir=None, name=None):
    """Opens INCAR in 'jobdir', sets 'key' value, and writes INCAR
        If 'val' is None, the tag is removed from the INCAR.
    """
    if name is None:
        name = "INCAR"
    if jobdir is None:
        jobdir = os.getcwd()
    incarfile = os.path.join(jobdir, name)
    tincar = inc.Incar(incarfile)

    for key, val in six.iteritems(tag_dict):
        for k in tincar.tags:
            if key.lower() == k.lower():
                if (val is None) or (str(val).strip() == ""):
                    del tincar.tags[k]
                else:
                    tincar.tags[k] = val
                break

        if val != None and str(val).strip() != "":
            tincar.tags[key] = val

    tincar.write(incarfile)


def ionic_steps(jobdir=None):
    """Find the number of ionic steps completed in 'jobdir'"""
    try:
        toszicar = oszicar.Oszicar(os.path.join(jobdir, "OSZICAR"))
        return len(toszicar.E)
    except:
        raise VaspIOError("Could not read number of ionic steps from " +
                          os.path.join(jobdir, "OSZICAR"))


def write_potcar(filename, poscar, species, sort=True):
    """ Write an appropriate POTCAR """
    if sort == False:
        with open(filename, 'w') as file:
            for name in poscar.type_atoms:
                with open(os.path.join(species[name].potcardir,
                                       'POTCAR')) as potcar:
                    file.write(potcar.read())
    else:
        # dict: key = alias, value = list of Sites
        pos = poscar.basis_dict()

        with open(filename, 'w') as file:
            # for each alias
            for alias in sorted(pos.keys()):
                # find matching IndividualSpecies with write_potcar == True
                for name in species:
                    if species[name].alias == alias and species[
                            name].write_potcar:
                        # add to POTCAR file
                        with open(
                                os.path.join(species[name].potcardir,
                                             'POTCAR')) as potcar:
                            file.write(potcar.read())
                        break


def write_stopcar(mode='e', jobdir=None):
    """ Write STOPCAR file with two modes:
        mode = 'e' for 'VASP stops at the next electronic step'
        mode = 'i' for 'VASP stops at the next ionic step' """
    if jobdir is None:
        jobdir = os.getcwd()
    if mode.lower()[0] == 'e':
        stop_string = "LABORT = .TRUE."
    elif mode.lower()[0] == 'i':
        stop_string = "LSTOP = .TRUE."
    else:
        raise VaspIOError("Invalid STOPCAR mode specified: " + str(mode))

    filename = os.path.join(jobdir, 'STOPCAR')

    try:
        stopcar_write = open(filename, 'w')
    except IOError as e:
        raise e

    stopcar_write.write(stop_string)
    stopcar_write.close()


def write_vasp_input(dirpath,
                     incarfile,
                     ref_kpointsfile,
                     ref_structurefile,
                     structurefile,
                     speciesfile,
                     sort=True,
                     extra_input_files=[],
                     strict_kpoints=False):
    """ Write VASP input files in directory 'dirpath'

    Parameters
    ----------

    ref_structurefile: str
        Path to a CASM structure.json file or VASP POS/POSCAR file representing a reference structure used for scaling incar and k-point parameters.

    structurefile: str
        Path to a CASM structure.json file or VASP POS/POSCAR file representing the structure to be calculated.
    """
    print("Setting up VASP input files:", dirpath)

    # read reference structure and kpoints
    print("  Reading reference KPOINTS:", ref_kpointsfile)
    ref_kpoints = kp.Kpoints(ref_kpointsfile)
    if ref_structurefile != None:
        print("  Reading reference POSCAR:", ref_structurefile)
        ref_structure = poscar.Poscar(ref_structurefile)
    else:
        ref_structure = None

    # read species, prim structure.json/POS, and to-be-calculated
    # structure.json/POS, and use to construct incar and kpoints for
    # the to-be-calculated structure
    print("  Reading SPECIES:", speciesfile)
    species_settings = species.species_settings(speciesfile)
    if structurefile != None:
        print("  Reading structure:", structurefile)
        structure = poscar.Poscar(structurefile, species_settings)
    else:
        structure = None

    ## Reading DOF information present in the structure.json file
    ## Examples include: Cmagspin, NCmagspin, SOmagspin, etc
    ## Also contains information about atom types, and mol types
    print(" Reading DOF information from structure: ", structurefile)
    structure_info = StructureInfo(structurefile)

    print("  Reading INCAR:", incarfile)
    incar = inc.Incar(incarfile, species_settings, structure, sort, structure_info)

    print("  Generating KPOINTS")
    if strict_kpoints:
        kpoints = ref_kpoints
    else:
        kpoints = ref_kpoints.super_kpoints(ref_structure, structure)

    # write main input files
    if structurefile != None:
        print("  Writing POSCAR:", os.path.join(dirpath, 'POSCAR'))
        structure.write(os.path.join(dirpath, 'POSCAR'), sort)
    print("  Writing INCAR:", os.path.join(dirpath, 'INCAR'))
    incar.write(os.path.join(dirpath, 'INCAR'))
    print("  Writing KPOINTS:", os.path.join(dirpath, 'KPOINTS'))
    kpoints.write(os.path.join(dirpath, 'KPOINTS'))
    if structurefile != None:
        print("  Writing POTCAR:", os.path.join(dirpath, 'POTCAR'))
        write_potcar(os.path.join(dirpath, 'POTCAR'), structure,
                     species_settings, sort)
    # copy extra input files
    if len(extra_input_files):
        print("  Copying extra input files", end=' ')
    for s in extra_input_files:
        print("    ", s)
        shutil.copy(s, dirpath)

    print("  DONE\n")
    sys.stdout.flush()
