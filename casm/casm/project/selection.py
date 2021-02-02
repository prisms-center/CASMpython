from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import *

# conda's current version of pandas raises these warnings, but they are safe
# see: https://stackoverflow.com/questions/40845304
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import copy
from io import StringIO
import json
import os
import subprocess

import numpy as np
import pandas
import six

from casm.project.project import Project
from casm.project.query import query
from casm.misc import compat


class Selection(object):
    """
    A Selection object contains information about a CASM project

    Attributes
    ----------

      proj: casm.Project, optional, default=Project containing the current working directory
        the CASM project the selection belongs to

      path: string, optional, default="MASTER"
        path to selection file, or "MASTER" (Default="MASTER")

      type: string, optional, default="config"
        type of selected object: "config" or "scel"

      all: bool, optional, default=True
        if True, self.data will include all configurations, whether selected or
        not. If False, only selected configurations will be included.

      data: pandas.DataFrame
        A pandas.DataFrame describing the selected configurations. Has at least
        'configname' and 'selected' (automatically converted to bool) columns.

    """
    def __init__(self, proj=None, path="MASTER", type="config", all=True):
        """
        Construct a CASM Project representation.

        Arguments
        ---------

          proj: casm.Project, optional, default=Project containing the current working directory
            the CASM project the selection belongs to

          path: string, optional, default="MASTER"
            path to selection file, or "MASTER" (Default="MASTER")

          type: string, optional, default="config"
            type of selected object: "config" or "scel"

          all: bool, optional, default=True
            if True, self.data will include all configurations, whether selected or
            not. If False, only selected configurations will be included.


        """
        if proj == None:
            proj = Project()
        elif not isinstance(proj, Project):
            raise Exception(
                "Error constructing Selection: proj argument is not a CASM project"
            )
        self.proj = proj

        self.path = path
        if os.path.isfile(path):
            self.path = os.path.abspath(path)

        self.type = type
        self.all = all

        self._data = None

        # reserved for use by casm.plotting
        self.src = None

    @property
    def data(self):
        """
        Get Selection data as a pandas.DataFrame

        If the data is modified, 'save' must be called for CASM to use the modified selection.
        """
        if self._data is None:
            if self.path in ["MASTER", "ALL", "CALCULATED"]:
                self._data = query(self.proj, ['name', 'selected'],
                                   self.path,
                                   self.type,
                                   verbatim=True,
                                   all=self.all)
            elif self._is_json():
                self._data = pandas.read_json(self.path, orient='records')
            else:
                with open(self.path, compat.pandas_rmode()) as f:
                    if compat.peek(f) == '#':
                        f.read(1)
                    self._data = pandas.read_csv(f,
                                                 sep=compat.str(' +'),
                                                 engine='python')

            self._clean_data()

            if not self.all:
                self._data = self._data[self._data['selected'] == True]

        return self._data

    @data.setter
    def data(self, input):
        self._data = input

    def save(self, data=None, force=False):  #make it generalized ##todo
        """Save the current selection.

        This method also allows completely replacing the 'data' describing the selected configurations.

        Arguments
        ---------
        data: pandas.DataFrame
            If provided, it replaces `self.data` before writing. It must have `"name"` and `"selected"` columns to be opened later.

        force: bool
            Force overwrite existing files

        Raises
        ------
        Exception
            - If attempting to overwrite an existing file and `force==False`
            - If `self.path in ["ALL", "CALCULATED"]`
        """
        if self.path == "MASTER":

            self.path = self.proj.dir.master_selection(self.type)
            self.save(data=data, force=force)
            self.path = "MASTER"

        elif self.path in ["ALL", "CALCULATED"]:
            raise Exception("Cannot save the '" + self.path + "' Selection")

        else:

            if data is not None:
                self._data = data.copy()
                self._clean_data()

            if self._data.columns[0] != "name":
                raise Exception(
                    "The first column in Selection.data must be 'name'")
            if self._data.columns[1] != "selected":
                raise Exception(
                    "The second column in Selection.data must be 'selected'")

            if os.path.exists(self.path) and not force:
                raise Exception("File: " + self.path + " already exists")

            backup = self.path + ".tmp"
            if os.path.exists(backup):
                raise Exception("File: " + backup + " already exists")

            if self._is_json():
                self._data.to_json(backup, orient='records')
            else:
                self.astype("selected", np.int_)
                with open(backup, compat.pandas_wmode()) as f:
                    f.write('# ')  # TODO: make this optional
                    self._data.to_csv(f, sep=compat.str(' '), index=False)
                self.astype("selected", bool)
            os.rename(backup, self.path)

    def saveas(self, path="MASTER", force=False):
        """
        Create a new Selection from this one, save and return it

        Arguments
        ---------
        path: str
            Path to a selection file or standard selection name.

        force: bool
            Force overwrite existing files

        Returns
        -------
        sel: Selection
            The new Selection created from this one
        """
        sel = Selection(self.proj, path, type=self.type, all=self.all)
        sel._data = self.data.copy()
        sel.save(force=force)
        return sel

    def _is_json(self):
        return self.path[-5:].lower() == ".json"

    def astype(self, columnname, dtype):
        """Convert a column to another type

        Example: Convert column of int (0 / 1) to bool:

            selection.astype('selected', bool)

        Arguments
        ---------
        columns: List(str)
            Data requested, will be added as columns in `self.data`. This corresponds to the `-k` option of `casm query`. A list of options can be obtained from `casm query --help properties`.

        force: bool
            If `force==False`, input `columns` that already exist in `self.data.columns` will be ignored and those columns will not be updated. If `force==True`, those columns will be overwritten with new data.

        """
        self._data.loc[:,
                       columnname] = self._data.loc[:,
                                                    columnname].astype(dtype)

    def _clean_data(self):
        self.astype('selected', bool)

    def query(self, columns, force=False, verbose=False):
        """ Query requested columns and store them in 'data'.

        Will not overwrite columns that already exist, unless 'force'==True. Will query data for all configurations, whether selected or not, if `self.all == True`.

        Arguments
        ---------
        columns: List(str)
            Data requested, will be added as columns in `self.data`. This corresponds to the `-k` option of `casm query`. A list of options can be obtained from `casm query --help properties`.

        force: bool
            If `force==False`, input `columns` that already exist in `self.data.columns` will be ignored and those columns will not be updated. If `force==True`, those columns will be overwritten with new data.

        verbose: bool
            How much to print to stdout.
        """

        if force == False:
            _col = [x for x in columns if x not in self.data.columns]
        else:
            _col = columns

        if verbose:
            print("# Query requested:", columns)
            if force == False:
                print("# Use existing:",
                      [x for x in columns if x in self.data.columns])
            else:
                print("# Overwrite existing:",
                      [x for x in columns if x in self.data.columns])
            if len(_col) == 0:
                print("# No query necessary")
            else:
                print("# Querying:", _col)

        if len(_col) == 0:
            return

        df = query(self.proj,
                   _col,
                   self.path,
                   self.type,
                   verbatim=True,
                   all=self.all)

        if verbose:
            print("#   DONE\n")

        msg = "querying different numbers of records: {0}, {1}".format(
            self.data.shape, df.shape)
        assert self.data.shape[0] == df.shape[0], msg

        for c in df.columns:
            self.data.loc[:, c] = df.loc[:, c].values

    def write_pos(self, all=False):
        """Write POS file for selected configurations

        Equivalent to `casm query -c <selection> --write-pos`. This writes a POS file for selected configurations at `<root>/training_data/<configname>/POS`.

        Arguments
        ---------

        all: bool, optional, default=False
            If True, will write POS file for all configurations in the selection whether selected or not. If False, only write POS file for selected configurations.
        """
        self.proj.capture("query -c " + self.path + " --write-pos")

    def add_data(self, name, data=None, force=False):
        """Add selection data, either by query or from an existing DataFrame

        Equivalent to:

            if name not in sel.data.columns or force == True:
                if data is None:
                    sel.query([name], force)
                else:
                    sel.data.loc[:,name] = data

        Arguments
        ---------
        columns: List(str)
            The data requested. This corresponds to the `-k` option of `casm query`, or a column in `data`. A list of options can be obtained from `casm query --help properties`.

        data: pandas.DataFrame
            May be provided as a data source as an alternative to `casm query`.

        force: bool
            If True, overwrite existing data in `self.data`.
        """
        if name not in self.data.columns or force == True:
            if data is None:
                self.query([name], force)
            else:
                self.data.loc[:, name] = data
