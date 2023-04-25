from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import *

import json
import os
import math
import tempfile
import warnings
from os.path import join
from string import ascii_lowercase

import numpy as np
import six

from casm.project import syminfo
from casm.api import API, casm_command, casm_capture
from casm.api.api import _project_path as _api_project_path


def project_path(dir=None):
    """
    Crawl up from dir to find '.casm'. If found returns the directory containing the '.casm' directory.
    If not found, return None.

    Args:
    If dir == None, set to os.getcwd()
    """
    return _api_project_path(dir=dir)


class ClexDescription(object):
    """
    Settings for a cluster expansion

    Attributes
    ----------

      name: str
        Cluster expansion name

      property: str
        Name of the property being cluster expanded

      calctype: str
        Calctype name

      ref: str
        Reference state name

      bset: str
        Basis set

      eci: str
        ECI set name

    """
    def __init__(self, name, property, calctype, ref, bset, eci):
        self.name = name
        self.property = property
        self.calctype = calctype
        self.ref = ref
        self.bset = bset
        self.eci = eci

    def to_dict(self):
        return {
            "bset" : self.bset,
            "calctype" : self.calctype,
            "eci" : self.eci,
            "name" : self.name,
            "property" : self.property,
            "ref" : self.ref}


class ProjectSettings(object):
    """
    Settings for a CASM project

    Attributes:
      path: Path to CASM project
      data: Dict storing contents of project_settings.json

    """
    def __init__(self, path=None):
        """
        Construct a CASM ProjectSettings representation.

        Args:
            path: path to CASM project (Default=None, uses project containing current directory).

        """
        if project_path(path) is None:
            if path is None:
                raise Exception("No CASM project found using " + os.getcwd())
            else:
                raise Exception("No CASM project found using " + path)
        self.path = project_path(path)
        dir = DirectoryStructure(self.path)
        self.data = json.load(open(dir.project_settings()))

        d = self.data["cluster_expansions"][self.data["default_clex"]]
        self._default_clex = ClexDescription(d["name"], d["property"],
                                             d["calctype"], d["ref"],
                                             d["bset"], d["eci"])

        self._clex = [
            ClexDescription(d[1]["name"], d[1]["property"], d[1]["calctype"],
                            d[1]["ref"], d[1]["bset"], d[1]["eci"])
            for d in six.iteritems(self.data["cluster_expansions"])
        ]

        d = self.data["cluster_expansions"].get("formation_energy", None)
        self._formation_energy_clex = None
        if d is not None:
            self._formation_energy_clex = ClexDescription(
                d["name"], d["property"], d["calctype"], d["ref"], d["bset"],
                d["eci"])

    # -- Accessors --

    @property
    def cluster_expansions(self):
        return self._clex

    @property
    def default_clex(self):
        return self._default_clex

    @property
    def formation_energy_clex(self):
        return self._formation_energy_clex


class DirectoryStructure(object):
    """Standard file and directory locations for a CASM project"""
    def __init__(self, path=None):
        """
        Construct a CASM Project DirectoryStructure representation.

        Args:
            path: path to CASM project (Default=None, uses project containing current directory).

        """
        if project_path(path) is None:
            if path is None:
                raise Exception("No CASM project found using " + os.getcwd())
            else:
                raise Exception("No CASM project found using " + path)
        self.path = project_path(path)
        self.__casm_dir = ".casm"
        self.__casmdb_dir = "jsonDB"
        self.__bset_dir = "basis_sets"
        self.__calc_dir = "training_data"
        self.__set_dir = "settings"
        self.__sym_dir = "symmetry"
        self.__clex_dir = "cluster_expansions"

    # ** Query filesystem **

    def all_bset(self):
        """Check filesystem directory structure and return list of all basis set names"""
        return self.__all_settings("bset", join(self.path, self.__bset_dir))

    def all_calctype(self):
        """Check filesystem directory structure and return list of all calctype names"""
        return self.__all_settings(
            "calctype", join(self.path, self.__calc_dir, self.__set_dir))

    def all_ref(self, calctype):
        """Check filesystem directory structure and return list of all ref names for a given calctype"""
        return self.__all_settings("ref", self.calc_settings_dir(calctype))

    def all_clex_name(self):
        """Check filesystem directory structure and return list of all cluster expansion names"""
        return self.__all_settings("clex", join(self.path, self.__clex_dir))

    def all_eci(self, property, calctype, ref, bset):
        """Check filesystem directory structure and return list of all eci names"""
        return self.__all_settings(
            "eci",
            join(self.path, self.__clex_dir, self.__clex_name(property),
                 self.__calctype(calctype), self.__ref(ref),
                 self.__bset(bset)))

    # ** File and Directory paths **

    # -- Project directory --------

    def root_dir(self):
        """Return casm project directory path"""
        return self.path

    def prim(self):
        """Return prim.json path"""
        return join(self.path, "prim.json")

    # -- Hidden .casm directory --------

    def casm_dir(self):
        """Return hidden .casm dir path"""
        return join(self.path, self.__casm_dir)

    def casmdb_dir(self):
        """Return .casm/jsonDB path"""
        return join(self.casm_dir(), self.__casmdb_dir)

    def project_settings(self):
        """Return project_settings.json path"""
        return join(self.casm_dir(), "project_settings.json")

    def scel_list(self, scelname):
        """Return master scel_list.json path"""
        return join(self.casmdb_dir(), "scel_list.json")

    def config_list(self):
        """Return master config_list.json file path"""
        return join(self.casm_dbdir(), "config_list.json")

    def master_selection(self, type):
        """Return location of MASTER selection file

        Arguments
        ---------
        type: str
            One of "config" or "scel"
        """
        querydir = join(self.casm_dir(), "query")
        if type == "config":
            return join(querydir, "Configuration", "master_selection")
        elif type == "scel":
            return join(querydir, "Supercell", "master_selection")
        else:
            raise Exception("Unsupported type: " + str(type))

    # -- Symmetry --------

    def symmetry_dir(self):
        """Return symmetry directory path"""
        return join(self.path, self.sym_dir)

    def lattice_point_group(self):
        """Return lattice_point_group.json path"""
        return join(self.symmetry_dir(), "lattice_point_group.json")

    def factor_group(self):
        """Return factor_group.json path"""
        return join(self.symmetry_dir(), "factor_group.json")

    def crystal_point_group(self):
        """Return crystal_point_group.json path"""
        return join(self.symmetry_dir(), "crystal_point_group.json")

    # -- Basis sets --------

    def bset_dir(self, clex):
        """Return path to directory contain basis set info"""
        return join(self.path, self.__bset_dir, self.__bset(clex.bset))

    def bspecs(self, clex):
        """Return basis function specs (bspecs.json) file path"""
        return join(self.bset_dir(clex), "bspecs.json")

    def clust(self, clex):
        """Returns path to the clust.json file"""
        return join(self.bset_dir(clex), "clust.json")

    def basis(self, clex):
        """Returns path to the basis.json file"""
        return join(self.bset_dir(clex), "basis.json")

    def clexulator_dir(self, clex):
        """Returns path to directory containing global clexulator"""
        return join(self.bset_dir(clex))

    def clexulator_src(self, project, clex):
        """Returns path to global clexulator source file"""
        return join(self.bset_dir(clex), (project + "_Clexulator.cc"))

    def clexulator_o(self, project, clex):
        """Returns path to global clexulator.o file"""
        return join(self.bset_dir(clex), (project + "_Clexulator.o"))

    def clexulator_so(self, project, clex):
        """Returns path to global clexulator so file"""
        return join(self.bset_dir(clex), (project + "_Clexulator.so"))

    # -- Calculations and reference --------

    def settings_path_crawl(self, filename, configname, clex, calc_subdir=""):
        """
        Returns the path to the first file named 'filename' found in the settings
        directories.

        Searches:
          1) self.configuration_calc_settings_dir(configname, clex)
          2) self.supercell_calc_settings_dir(scelname, clex)
          3) self.calc_settings_dir(clex)
          DirectoryStructure.configuration_calc_settings_dir(configname, clex)Crawl casm directory structure starting at configdir and moving upwards

        Returns None if file named 'filename' not found in any of the three directories.


        Arguments
        ---------
          filename: str
            The name of the file being searched for

          configname: str
            The name of the configuration

          clex: a casm.project.ClexDescription instance
            Used to specify the calctype to find settings for


        Returns
        ---------
          filepath: str or None
            The path to the first file named 'filename' found in the settings
            directories, or None if not found.

        """
        filepath = join(
            self.configuration_calc_settings_dir(configname, clex,
                                                 calc_subdir), filename)
        if os.path.exists(filepath):
            return filepath

        scelname = configname.split('/')[0]
        filepath = join(
            self.supercell_calc_settings_dir(scelname, clex, calc_subdir),
            filename)
        if os.path.exists(filepath):
            return filepath

        filepath = join(self.calc_settings_dir(clex), filename)
        if os.path.exists(filepath):
            return filepath

        return None

    def supercell_dir(self, scelname, calc_subdir=""):
        """Return supercell directory path (scelname has format SCELV_A_B_C_D_E_F)"""
        return join(self.path, self.__calc_dir, calc_subdir, scelname)

    def configuration_dir(self, configname, calc_subdir=""):
        """Return configuration directory path (configname has format SCELV_A_B_C_D_E_F/I)"""
        return join(self.path, self.__calc_dir, calc_subdir, configname)

    def POS(self, configname, calc_subdir=""):
        """Return path to POS file"""
        return join(self.configuration_dir(configname, calc_subdir), "POS")

    def config_json(self, configname, calc_subdir=""):
        """Return path to structure.json file"""
        return join(self.configuration_dir(configname, calc_subdir),
                    "structure.json")

    def structure_json(self, configname, calc_subdir=""):
        """Return path to structure.json file"""
        return join(self.configuration_dir(configname, calc_subdir),
                    "structure.json")

    def calctype_dir(self, configname, clex, calc_subdir=""):
        """Return calctype directory path (e.g. training_data/$(calc_subdir)/SCEL_...../0/calctype.default"""
        return join(self.configuration_dir(configname, calc_subdir),
                    self.__calctype(clex.calctype))

    def calc_settings_dir(self, clex):
        """Return calculation settings directory path, for global settings from clex"""
        return join(self.path, self.__calc_dir, self.__set_dir,
                    self.__calctype(clex.calctype))

    def calctype_settings_dir(self, calctype):
        """Return calculation settings directory path, for global settings from calctype"""
        return join(self.path, self.__calc_dir, self.__set_dir,
                    self.__calctype(calctype))

    def supercell_calc_settings_dir(self, scelname, clex, calc_subdir=""):
        """Return calculation settings directory path, for supercell specific settings"""
        return join(self.supercell_dir(scelname, calc_subdir), self.__set_dir,
                    self.__calctype(clex.calctype))

    def configuration_calc_settings_dir(self,
                                        configname,
                                        clex,
                                        calc_subdir=""):
        """Return calculation settings directory path, for configuration specific settings"""
        return join(self.configuration_dir(configname, calc_subdir),
                    self.__set_dir, self.__calctype(clex.calctype))

    def calculated_properties(self, configname, clex, calc_subdir=""):
        """Return calculated properties file path"""
        return join(self.configuration_dir(configname, calc_subdir),
                    self.__calctype(clex.calctype), "properties.calc.json")

    def ref_dir(self, clex):
        """Return calculation reference settings directory path, for global settings"""
        return join(self.calc_settings_dir(clex.calctype),
                    self.__ref(clex.ref))

    def composition_axes(self):
        """Return composition axes file path"""
        return join(self.casm_dir(), "composition_axes.json")

    def chemical_reference(self, clex):
        """Return chemical reference file path"""
        return join(self.ref_dir(clex), "chemical_reference.json")

    # -- Cluster expansions --------

    def property_dir(self, clex):
        """Returns path to eci directory"""
        return join(self.path, self.__clex_dir,
                    self.__clex_name(clex.property))

    def eci_dir(self, clex):
        """
      Returns path to eci directory

      Arguments
      ---------
        clex: a casm.project.ClexDescription instance
          Specifies the cluster expansion to get the eci directory for

      Returns
      -------
        p: str
          Path to the eci directory
      """
        return join(self.property_dir(clex), self.__calctype(clex.calctype),
                    self.__ref(clex.ref), self.__bset(clex.bset),
                    self.__eci(clex.eci))

    def eci(self, clex):
        """
      Returns path to eci.json

      Arguments
      ---------
        clex: a casm.project.ClexDescription instance
          Specifies the cluster expansion to get the eci.json for

      Returns
      -------
        p: str
          Path to the eci directory
      """
        return join(self.eci_dir(clex), "eci.json")

    # private:

    def __bset(self, bset):
        return "bset." + bset

    def __calctype(self, calctype):
        return "calctype." + calctype

    def __ref(self, ref):
        return "ref." + ref

    def __clex_name(self, clex_name):
        return "clex." + clex_name

    def __eci(self, eci):
        return "eci." + eci

    def __all_settings(self, pattern, location):
        """
      Find all directories at 'location' that match 'pattern.something'
      and return a std::vector of the 'something'
      """

        all = []
        pattern += "."

        # get all
        if not os.path.exists(location):
            return all

        for item in os.listdir(location):
            if os.path.isdir(os.path.join(
                    location, item)) and item[:len(pattern)] == pattern:
                all.append(item[len(pattern):])
        return sorted(all)


class Project(object):
    """The Project class contains information about a CASM project

    Attributes
    ----------

      path: str
        Path to project root directory

      name: str
        Project name

      settings: casm.project.ProjectSettings instance
        Contains project settings

      dir: casm.project.DirectoryStructure instance
        Provides file and directory locations within the project

      prim: casm.project.Prim instance
        Represents the primitive crystal structure

      composition_axes: casm.project.CompositionAxes or None
        Currently selected composition axes, or None

      all_composition_axes: dict(str:casm.project.CompositionAxes)
        Dict containing name:CompositionAxes pairs, including both standard and custom composition axes

      verbose: bool
        How much to print to stdout

      out: str or None
        Contains last output of Project.command calls if capturing output. Use Project.command_options to set options.

      err: str or None
        Contains last error output of Project.command calls if capturing output. Use Project.command_options to set options.

      code: int or None
        Contains last return code of Project.command calls.

    """
    def __init__(self, path=None, verbose=True):
        """
        Construct a CASM Project representation.

        Arguments
        ----------

          path: str, optional, default=None
            Path to project root directory. Default=None uses project containing
            current working directory

          verbose: bool, optional, default=True
            How much to print to stdout

        """

        # will hold a ctypes.c_void_p when loading CASM project into memory
        self._ptr = None

        # will keep a casm.API instance
        self._api = None

        # set path to this CASM project
        if project_path(path) is None:
            if path is None:
                raise Exception("No CASM project found using " + os.getcwd())
            else:
                raise Exception("No CASM project found using " + path)

        self.path = project_path(path)
        self.__refresh()

        self.verbose = verbose
        self._streamptr = None
        self._errstreamptr = None

        # set default command output options
        self.out = None
        self.err = None
        self.code = None
        self.command_options()

    def __del__(self):
        self.__unload()

    def __load(self):
        """
        Explicitly load CASM project into memory.
        """
        if self._ptr is None:
            self._api = API()
            if self.verbose:
                self._streamptr = self._api.stdout()
            else:
                self._streamptr = self._api.nullstream()

            if self.verbose:
                self._errstreamptr = self._api.stderr()
            else:
                self._errstreamptr = self._api.nullstream()

            self._ptr = self._api.primclex_new(self.path, self._streamptr,
                                               self._errstreamptr)

    def __unload(self):
        """
        Explicitly unload CASM project from memory.
        """
        if self._ptr is not None:
            self._api.primclex_delete(self._ptr)
            self._ptr = None

    def __refresh(self):
        """
        Reload self.settings and self.dir

        Use this after adding or modifying files in the CASM project but no
        special call to refresh PrimClex properties is required
        """
        self.dir = DirectoryStructure(self.path)
        self.settings = ProjectSettings(self.path)
        self._prim = None
        self.all_composition_axes = {}
        if os.path.exists(self.dir.composition_axes()):
            with open(self.dir.composition_axes(), 'r') as f:
                data = json.load(f)
                if "possible_axes" in data:
                    for key, val in six.iteritems(data["possible_axes"]):
                        self.all_composition_axes[key] = CompositionAxes(
                            key, val)
                if "custom_axes" in data:
                    for key, val in six.iteritems(data["custom_axes"]):
                        self.all_composition_axes[key] = CompositionAxes(
                            key, val)
                self.composition_axes = None
                if "current_axes" in data:
                    self.composition_axes = self.all_composition_axes[
                        data["current_axes"]]

    @property
    def prim(self):
        if self._prim is None:
            self._prim = Prim(self)
        return self._prim

    @property
    def name(self):
        return self.settings.data['name']

    def refresh(self,
                read_settings=False,
                read_composition=False,
                read_chem_ref=False,
                read_configs=False,
                clear_clex=False):
        """
        Refresh PrimClex properties to reflect changes to CASM project files.
        """
        if read_settings:
            self.__refresh()
        if self._ptr is not None:
            self._api.primclex_refresh(self.data(), self._streamptr,
                                       self._errstreamptr, read_settings,
                                       read_composition, read_chem_ref,
                                       read_configs, clear_clex)

    def data(self):
        """
        Returns a 'ctypes.c_void_p' that points to a CASM project. (PrimClex)
        """
        self.__load()
        return self._ptr

    def command_options(self,
                        capture=True,
                        print_output=True,
                        combine_output=True):
        """
        Set options for Project.command

        Arguments
        ---------
        capture: bool
            If True, capture stdout, stderr, and return code in self.out and self.err, and self.code. If False, will print to stdout and stderr directrly (if self.verbose==True), or to nullstream (if self.verbose==False).

        print_ouput: bool
            If print_output==True and capture==True, then print self.out after executing.

        combine_output: bool
            If combine_output==true, err stream is set equal to out stream.

        """
        self._capture = capture
        self._print_output = print_output
        self._combine_output = combine_output

    def command(self, args, out=None, err=None):
        """
        Execute a command via the c api, writing output to stdout/stderr.

        Args:
          args: A string containing the command to be executed.
            Ex: "select --set-on -o /abspath/to/my_selection"

          out: Path to output file for standard out

          err: Path to file for standard error.

        Returns:
          returncode: The returncode of the command via the CASM C API.

        """
        # this also ensures self._api is not None
        data = self.data()

        if out is not None:
            fs = self._api.fstream_new(out)
            if out == err or err is None:
                fs_err = fs
            else:
                fs_err = self._api.ostringstream_new(err)
            self.code = self._api.capi(args, self.data(), self.path,
                                       fs, fs_err)
            self._api.fstream_delete(fs)
            if out != err and err is not None:
                self._api.fstream_delete(fs_err)
            self.__refresh()

        elif self._capture:
            if self._combine_output:
                self.out, self.code = self.capture(args, combine_output=True)
            else:
                self.out, self.err, self.code = self.capture(args)
            if self._print_output:
                print(self.out)
        else:
            self.code = self._api.capi(args, self.data(), self.path,
                                       self._streamptr, self._errstreamptr)
            self.__refresh()
        return self.code

    def capture(self, args, combine_output=False):
        """
        Execute a command via the c api and store stdout/stderr result as str.

        Args:
          args: A string containing the command to be executed.
            Ex: "select --set-on -o /abspath/to/my_selection"

        Returns
        -------
          (stdout, stderr, returncode): The result of running the command via the
            command line iterface. 'stdout' and 'stderr' are in text type ('unicode'/'str'). If
            'combine_output' is True, then returns (combined_output, returncode).

        """
        # this also ensures self._api is not None
        data = self.data()

        # construct stringstream objects to capture stdout, debug, stderr
        ss = self._api.ostringstream_new()
        if combine_output:
            ss_err = ss
        else:
            ss_err = self._api.ostringstream_new()

        returncode = self._api.capi(args, self.data(), self.path, ss, ss_err)

        # copy strings and delete stringstreams
        stdout = self._api.ostringstream_to_str(ss)
        self._api.ostringstream_delete(ss)

        if combine_output:
            res = (stdout.decode('utf-8'), returncode)
        else:
            stderr = self._api.ostringstream_to_str(ss_err)
            self._api.ostringstream_delete(ss_err)

            res = (stdout.decode('utf-8'), stderr.decode('utf-8'), returncode)

        self.__refresh()
        return res

    @classmethod
    def init(cls,
             root=None,
             prim_path=None,
             prim_str=None,
             verbose=True,
             subproject=False,
             config_selection_path=None,
             confignames=None,
             dofs=None,
             relaxed=False,
             include_va=False,
             as_molecules=False):
        """ Calls `casm init` to create a new CASM project in the given directory

        Arguments
        ---------

          root: str (optional, default=os.getcwd())
            A string giving the path to the root directory of the new CASM
            project. Raises if a project already exists at this location.

          prim_path: str (optional, default="prim.json")
            A string giving the path to a `prim.json` file to initialize the
            CASM project with.

          prim_str: str (optional, default=None)
            A string with the `prim.json` file contents used to initialize the
            CASM project with.

          verbose: bool (optional, default=True)
            Passed to casm.project.Project constructor. How much to print to
            stdout.

          subproject: bool (optional, default=False)
            Initialize a project in sub-directory of an existing project. After
            initialization, commands executed below the sub-directory will act
            on the sub-directory project; commmands executed above the sub-
            directory act on the original project.

          config_selection_path: str (optional, default=None)
            If not None, initialize subprojects using existing configurations
            from the given selection file. Options are: {'<filename>', 'MASTER'
            (default), 'ALL', 'NONE', 'EMPTY', 'CALCULATED'}.

          confignames: list of str (optional, default=None)
            If not None, initialize subprojects using the configurations
            specified by name.

          dofs: list of str (optional, deafult=None)
            One or more DoF types to use casm init with, such as 'disp' or
            'EAstrain'.

          relaxed: bool (optional, default=False)
            Utilize relaxed coordinates for writing configuration-specific
            prim.json files.

          include_va: bool (optional, default=False)
            Print sites that can only be vacancies; otherwise these sites are
            excluded.

          as_molecules: bool (optional, default=False)
            Keep multi-atom species as molecules. By default, multi-atom
            species are split into constituent atoms.

        Returns
        -------
          proj: A casm.project.Project instance for the new CASM project. The new project has composition axes calculated and the first axes choice selected.

        Raises
        ------
          An exception is raised if a new project could not be initialized. This could be due to an already existing project, bad or missing input file, or other cause.

        """
        if root is None:
            root = os.getcwd()
        root = str(root)

        if os.path.exists(root) and subproject is False:
            if project_path(root) is not None:
                raise Exception("A CASM project already exists at " + root)

        os.makedirs(root, exist_ok=True)

        tmpdir = None

        if prim_path is not None:
            prim_path = str(prim_path)
        elif prim_path is None and prim_str is not None:
            # write "prim.json" file
            tmpdir = tempfile.TemporaryDirectory()
            prim_path = os.path.join(tmpdir.name, "prim.json")
            with open(prim_path, 'w') as f:
                f.write(prim_str)

        def raise_on_fail(output, returncode):
            if returncode != 0:
                print(output)
                raise Exception("Could not initialize the project")

        args = "init --path=" + str(root)
        if prim_path is not None:
            args += " --prim=" + str(prim_path)
        if subproject:
            args += " --sub"
        if config_selection_path is not None or confignames is not None:
            args += " --write-prim"
            if config_selection_path is not None:
                args += " -c " + str(config_selection_path)
            if confignames is not None:
                args += " --confignames " + " ".join(confignames)
        if dofs is not None:
            args += " --dofs " + " ".join(dofs)
        if relaxed is True:
            args += " --relaxed"
        if include_va is True:
            args += " --include_va"
        if as_molecules is True:
            args += " --as-molecules"
        raise_on_fail(*casm_capture(args, combine_output=True))
        proj = Project(root, verbose=verbose)
        raise_on_fail(*proj.capture("composition --calc", combine_output=True))
        raise_on_fail(
            *proj.capture("composition --select 0", combine_output=True))
        return proj


class Prim(object):
    """The Primitive Crystal Structure

    Attributes
    ----------

        proj: casm.Project
          the CASM project the Prim belongs to

        lattice_matrix: np.array of shape (3, 3)
          lattice vectors as matrix columns

        lattice_parameters: dict
          Lattice parameters and angles (in degrees), as:
            {'a':a, 'b':b, 'c':c, 'alpha':alpha, 'beta':beta, 'gamma':gamma}

        basis: List(dict)
          crystal basis, as read directly from prim.json (format may change)

        coordinate_mode: str
          crystal basis coordinate_mode, as read directly from prim.json (format
          may change)

        lattice_symmetry_s: str
          lattice point group, in Schoenflies notation

        lattice_symmetry_hm: str
          lattice point group, in Hermann-Mauguin notation

        lattice_system: str
          lattice system name, ('cubic', 'hexagonal', 'rhombohedral', etc.)

        crystal_symmetry_s: str
          crystal point group, in Schoenflies notation

        crystal_symmetry_hm: str
          crystal point group, in Hermann-Mauguin notation

        crystal_system: str
          crystal system name, ('cubic', 'hexagonal', 'trigonal', etc.)

        crystal_family: str
          crystal family name, ('cubic', 'hexagonal', etc.)

        space_group_number: str
          range of possible space group number
    """

    # TODO: update prim composition info
    #
    # components: List[str]
    #   occupational components
    #
    # elements: List[str]
    #   all allowed elements
    #
    # n_independent_compositions: int
    #   number of independent composition axes
    #
    # degrees_of_freedom: List[str]
    #   allowed degrees of freedom, from:
    #     'occupation'
    def __init__(self, proj):
        """
        Construct a CASM Prim

        Arguments
        ---------

          proj: casm.Project, optional, default=Project containing the current working directory
            the CASM project the Prim belongs to

        """
        if proj == None:
            proj = Project()
        elif not isinstance(proj, Project):
            raise Exception(
                "Error constructing Prim: proj argument is not a CASM Project")
        self.proj = proj

        # raw prim.json (for some properties not yet supported in the API)
        with open(self.proj.dir.prim()) as f:
            raw_prim = json.load(f)
        self.lattice_matrix = np.array(raw_prim['lattice_vectors']).transpose()
        self.basis = raw_prim['basis']
        self.coordinate_mode = raw_prim['coordinate_mode']

        def _angle(a, b):
            return math.degrees(
                math.acos(
                    np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))))

        def _lattice_parameters(L):
            a = np.linalg.norm(L[:, 0])
            b = np.linalg.norm(L[:, 1])
            c = np.linalg.norm(L[:, 2])
            alpha = _angle(L[:, 1], L[:, 2])
            beta = _angle(L[:, 0], L[:, 2])
            gamma = _angle(L[:, 0], L[:, 1])
            return {
                'a': a,
                'b': b,
                'c': c,
                'alpha': alpha,
                'beta': beta,
                'gamma': gamma
            }

        self.lattice_parameters = _lattice_parameters(self.lattice_matrix)

        (stdout, stderr, returncode) = proj.capture("sym")

        # lattice symmetry
        self.lattice_symmetry_s = syminfo.lattice_symmetry(stdout)
        self.lattice_symmetry_hm = syminfo.hm_symmetry(self.lattice_symmetry_s)
        self.lattice_system = syminfo.lattice_system(self.lattice_symmetry_s)

        # crystal symmetry
        self.crystal_symmetry_s = syminfo.crystal_symmetry(stdout)
        self.crystal_symmetry_hm = syminfo.hm_symmetry(self.crystal_symmetry_s)
        self.crystal_system = syminfo.crystal_system(self.crystal_symmetry_s)
        self.crystal_family = syminfo.crystal_family(self.crystal_symmetry_s)
        self.space_group_number = syminfo.space_group_number_map[
            self.crystal_symmetry_s]

        # # composition (v0.2.X: elements and components are identical, only 'occupation' allowed)
        # with open(self.proj.dir.composition_axes()) as f:
        #     raw_composition_axes = json.load(f)
        #
        # print(raw_composition_axes)
        #
        # self.components = raw_composition_axes['possible_axes']['0'][
        #     'components']
        # self.elements = self.components
        # self.n_independent_compositions = raw_composition_axes[
        #     'possible_axes']['0']['independent_compositions']
        # self.degrees_of_freedom = ['occupation']


class CompositionAxes(object):
    """A composition axes object

    Attributes
    ----------

        name: str
          composition axes name

        components: List[str]
          occupational components

        n_independent_compositions: int
          number of independent composition axes

        mol_formula: str
          number of each component in terms of the parametric compositions

        param_formula: str
          parametric compositions in terms of the number of components

        end_members: dict of np.array of shape=(n_components,)
          the number of components per unit cell in each end member state, in form:
          {'origin':np.array, 'a':np.array, 'b', np.array, ...}. Order matches
          that given by self.components.


    """
    def __init__(self, name, data):
        self._name = name
        self._data = data

        self._end_members = {}
        for c in ascii_lowercase:
            if c in self._data:
                self.end_members[c] = np.ravel(self._data[c])
            else:
                break
        self._end_members['origin'] = np.ravel(self._data['origin'])

    @property
    def name(self):
        return self._name

    @property
    def components(self):
        return self._data['components']

    @property
    def n_independent_compositions(self):
        return self._data['independent_compositions']

    @property
    def mol_formula(self):
        return self._data['mol_formula']

    @property
    def param_formula(self):
        return self._data['param_formula']

    @property
    def origin(self):
        return self._origin

    @property
    def end_members(self):
        return self._end_members
