from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import *
from casm import vasp

from casm import vasp
import os, shutil, six, re, subprocess, json
import warnings
import casm.vasp.io


class VaspWrapperError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def read_settings(filename):
    """Returns a JSON object reading JSON files containing settings for VASP PBS jobs.

   Returns:
        settings = a JSON object containing the settings file contents
                     This can be accessed like a dict: settings["account"], etc.
                     ** All values are expected to be 'str' type. **

    The required keys are:
        "queue": queue to submit job in
        "ppn": processors (cores) per node to request
        "walltime": walltime to request (ex. "48:00:00")

    The optional keys are:
        "atom_per_proc": max number of atoms per processor (core)
        "account": account to submit job under (default None)
        "pmem": string for requested memory (default None)
        "priority": requested job priority (default "0")
        "constraint": constraint. ex: ``"haswell"`` (default None)
        "exclude": nodes to exclude (slurm only). ex: ``"node01,node02,node03"`` (default None)
        "gpus": how many gpus to request (slurm only). ex: 4 (default None)
        "message": when to send messages about jobs (ex. "abe", default "a")
        "email": where to send messages (ex. "me@fake.com", default None)
        "qos": quality of service, 'qos' option (ex. "fluxoe")
        "npar": vasp incar setting (default None)
        "ncore": vasp incar setting (default None)
        "kpar": vasp incar setting (default None)
        "vasp_cmd": vasp execution command (default is "vasp" (ncpus=1) or "mpirun -np {NCPUS} vasp" (ncpus!=1))
        "ncpus": number of cpus (cores) to run on (default $PBS_NP)
        "run_limit": number of vasp runs until "not_converging" (default 10)
        "nrg_convergence": converged if last two runs complete and differ in energy by less than this amount (default None)
        "move": files to move at the end of a run (ex. ["POTCAR", "WAVECAR"], default ["POTCAR"])
        "copy": files to copy from run to run (ex. ["INCAR", "KPOINTS"], default ["INCAR, KPOINTS"])
        "remove": files to remove at the end of a run (ex. ["IBZKPT", "CHGCAR"], default ["IBKZPT", "CHG", "CHGCAR", "WAVECAR", "TMPCAR", "EIGENVAL", "DOSCAR", "PROCAR", "PCDAT", "XDATCAR", "LOCPOT", "ELFCAR", "PROOUT"]
        "compress": files to compress at the end of a run (ex. ["OUTCAR", "vasprun.xml"], default [])
        "backup": files to compress to backups at the end of a run, used in conjunction with move (ex. ["WAVECAR"])
        "extra_input_files": extra input files to be copied from the settings directory, e.g., a vdW kernel file.
        "initial" : location of INCAR with tags for the initial run, if desired (e.g. to generate a PBE WAVECAR for use with M06-L)
        "final" : location of INCAR with tags for the final run, if desired (e.g. "ISMEAR = -5", etc). Otherwise, the settings enforced are ("ISMEAR = -5", "NSW = 0", "IBRION = -1", "ISIF = 2")
        "err_types" : list of errors to check for. Allowed entries are "IbzkptError" and "SubSpaceMatrixError". Default: ["SubSpaceMatrixError"]
        "preamble" : a text file containing anything that MUST be run before python is invoked (e.g. module.txt which contains "module load python", or "source foo")
        "prerun" : bash commands to run before vasp.Relax.run (default None)
        "postrun" : bash commands to run after vasp.Relax.run completes (default None)
        "prop": USED IN vasp.converge ONLY. Property to converge with respect to (current options are "KPOINT" and "ENCUT")
        "prop_start": USED IN vasp.converge ONLY. Starting value of "prop", e.g. 450 (for ENCUT) or 5 (for KPOINTS) or [4 4 4] (for KPOINTS)
        "prop_stop": USED IN vasp.converge ONLY. Ending value of "prop", e.g. 550 (for ENCUT) or 20 (for KPOINTS).
        "prop_step": USED IN vasp.converge ONLY. Delta value of "prop", e.g. 10 (for ENCUT) or 2 (for KPOINTS) or [1 1 2] (for KPOINTS)
        "tol" : USED IN vasp.converge ONLY. Tolerance type for convergence, e.g. relaxed_energy. Optional
        "tol_amount" : USED IN vasp.converge ONLY. Tolerance criteria convergence, e.g. 0.001. If the abs difference between two runs in their "tol" is smaller than "tol_amount", the "prop" is considered converged.
        "name" : USED IN vasp.converge ONLY. Name used in the .../config/calctype.calc/NAME/property_i directory scheme, where, if not specified, "prop"_converge is used as NAME
    """
    try:
        with open(filename, 'rb') as file:
            settings = json.loads(file.read().decode('utf-8'))
    except (IOError, ValueError) as e:
        print("Error reading settings file:", filename)
        raise e

    required = ["queue", "ppn", "walltime"]

    select_one = [["nodes", "atom_per_proc", "nodes_per_image"]]

    optional = [
        "account", "pmem", "priority", "constraint", "exclude", "gpus", "message", "email", "qos",
        "npar", "ncore", "kpar", "ncpus", "vasp_cmd", "run_limit",
        "nrg_convergence", "encut", "kpoints", "extra_input_files", "move",
        "copy", "remove", "compress", "backup", "initial", "final",
        "strict_kpoints", "err_types", "preamble", "prerun", "postrun", "prop",
        "prop_start", "prop_stop", "prop_step", "tol", "tol_amount", "name",
        "fine_ngx", "CI_neb", "n_images", "software", "method",
        "endstate_calctype", "initial_deformation"
    ]

    if "gpus" in settings:
        # user must supply their own run command
        if not "vasp_cmd" in settings or len(settings["vasp_cmd"]) == 0:
            raise VaspWrapperError("gpu setting requires you to set vasp_cmd manually")
    
    for key in required:
        if not key in settings:
            raise VaspWrapperError(key + "' missing from: '" + filename + "'")

    if len(select_one):
        for key_list in select_one:
            if not [key in settings for key in key_list].count(True) == 1:
                raise VaspWrapperError(
                    "Declare one and only of the following options: '" +
                    "' or '".join(key_list) + "' in file: '" + filename + "'")
            for key in key_list:
                if not key in settings:
                    settings[key] = None

    for key in optional:
        if not key in settings:
            if key.lower() in [
                    "extra_input_files", "remove", "compress", "backup"
            ]:
                settings[key] = []
            elif key.lower() in ["move"]:
                settings[key] = casm.vasp.io.DEFAULT_VASP_MOVE_LIST
            elif key.lower() in ["copy"]:
                settings[key] = casm.vasp.io.DEFAULT_VASP_COPY_LIST
            # elif key.lower() in ["remove"]:
            #     settings[key] = casm.vasp.io.DEFAULT_VASP_REMOVE_LIST
            else:
                settings[key] = None

    if type(settings["remove"]) == list:
        if 'default' in settings["remove"]:
            settings["remove"] += casm.vasp.io.DEFAULT_VASP_REMOVE_LIST
    elif type(settings["remove"]) == str:
        if settings["remove"].lower() == 'default':
            settings["remove"] = casm.vasp.io.DEFAULT_VASP_REMOVE_LIST
        else:
            settings["remove"] = [settings["remove"]]
    if settings["priority"] == None:
        settings["priority"] = 0
    if settings["extra_input_files"] == None:
        settings["extra_input_files"] = []
    if settings["strict_kpoints"] == None:
        settings["strict_kpoints"] = False
    if settings["fine_ngx"] == None:
        settings["fine_ngx"] = False
    for k in settings.keys():
        if k not in required + optional + [
                key for key_list in select_one for key in key_list
        ]:
            raise VaspWrapperError("unknown key '" + k + "' found in: '" +
                                   filename + "'")

    return settings


def write_settings(settings, filename):
    """ Write 'settings' as json file, 'filename' """
    with open(filename, 'wb') as file:
        file.write(six.u(json.dump(settings, file, indent=4)).encode('utf-8'))


def vasp_input_file_names(dir, configname, clex, calc_subdir="", is_neb=False):
    """
    Collect casm.vaspwrapper input files from the CASM project hierarchy

    Looks for:

      INCAR:
        The base INCAR file used for calculations. Found via:
          DirectoryStructure.settings_path_crawl

      KPOINTS:
        The KPOINTS file specifying the k-point grid for a reference structure
        which is then scaled to be approximately the same density for other
        structures. Found via:
          DirectoryStructure.settings_path_crawl

      KPOINTS_REF: (optional)
        The reference structure used to determine the k-point density, if not
        running in Auto mode. If running VASP with AUTO KPOINTS mode, this file
        is not necessary. Found via:
          DirectoryStructure.settings_path_crawl

      structurefile:
        The CASM structure.json or VASP POSCAR file giving the initial structure to be calculated.

      SPECIES:
        The SPECIES file specifying Vasp settings for each species in the structure.


    Arguments
    ---------

      dir: casm.project.DirectoryStructure instance
        CASM project directory hierarchy

      configname: str
        The name of the configuration to be calculated

      clex: casm.project.ClexDescription instance
        The cluster expansion being worked on. Used for the 'calctype' settings.


    Returns
    -------

      filepaths: tuple(INCAR, KPOINTS, KPOINTS_REF, structurefile, SPECIES)
        A tuple containing the paths to the vaspwrapper input files


    Raises
    ------
      If any required file is not found.

    """
    # Find required input files in CASM project directory tree
    incarfile = dir.settings_path_crawl("INCAR", configname, clex)
    ref_kpointsfile = dir.settings_path_crawl("KPOINTS", configname, clex)
    ref_structurefile = dir.settings_path_crawl("POSCAR", configname, clex)
    structurefile = dir.structure_json(configname, calc_subdir)
    speciesfile = dir.settings_path_crawl("SPECIES", configname, clex)

    # Verify that required input files exist
    if incarfile is None:
        raise vasp.VaspError(
            "vasp_input_file_names failed. No INCAR file found in CASM project."
        )
    if ref_kpointsfile is None:
        raise vasp.VaspError(
            "vasp_input_file_names failed. No KPOINTS file found in CASM project."
        )
    if ref_structurefile is None:
        warnings.warn(
            "No reference POSCAR file found in CASM project. I hope your KPOINTS mode is A/AUTO/Automatic or this will fail!",
            vasp.VaspWarning)
    if structurefile is None and not is_neb:
        raise vasp.VaspError(
            "vasp_input_file_names failed. No structure.json file found for this configuration."
        )
    if speciesfile is None:
        raise vasp.VaspError(
            "vasp_input_file_names failed. No SPECIES file found in CASM project."
        )

    return (incarfile, ref_kpointsfile, ref_structurefile, structurefile,
            speciesfile)


def read_properties(filename):
    """ Read a properties.calc.json"""
    required = [
        "atom_type", "atoms_per_type", "coordinate_mode", "relaxed_basis",
        "relaxed_energy", "relaxed_forces", "relaxed_lattice"
    ]
    optional = ["relaxed_magmom", "relaxed_mag_basis"]

    with open(filename, 'rb') as myfile:
        properties = json.loads(myfile.read().decode('utf-8'))

    for key in required:
        if not key in properties:
            raise VaspWrapperError(key + "' missing from: '" + filename + "'")

    for key in optional:
        if not key in properties:
            properties[key] = None

    return properties
