# # conda's current version of pandas raises these warnings, but they are safe
# # see: https://stackoverflow.com/questions/40845304
# import warnings
# warnings.filterwarnings("ignore", message="numpy.dtype size changed")
# warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

from io import StringIO
import pandas
import casm
from casm.misc import compat


def query(proj,
          columns,
          selection_path,
          selection_type,
          verbatim=True,
          all=False):
    """Return a pandas.DataFrame with `casm query` output

    Arguments
    ---------
    proj: casm.project.Project
        The project to query

    columns: iterable of str
        Corresponds to `casm query -k` arguments listing the values to be queried. Use `casm query --help properties` and `casm query --help operators` to list options.

    selection_path: str
        The `-c,--selection` option, a path to a selection file, or a standard selection name ("MASTER", "ALL", "CALCULATED", "NONE")

    selection_type: str
        The `-t,--type` option, indicates the type of object being selected. Expected to be one of:

            "config": to select configurations
            "scel": to select supercells

    verbatim: bool
        If True, use `-v,--verbatim` option to exclude 'name' and 'selected' columns from the query output.

    all: bool
        If True, use `-a,--all` to include unselected objects in the output

    Returns
    -------
    data: pandas.DataFrame
        A DataFrame containing the query results. Note that no columns are loaded as bool dtype.
    """
    args = query_args(columns, selection_path, selection_type, verbatim, all)

    stdout, stderr, returncode = proj.capture(args)

    try:
        sout = StringIO(stdout)
        if compat.peek(sout) == '#':
            sout.read(1)
        return pandas.read_csv(sout, sep=compat.str(' +'), engine='python')
    except:
        print("Error in casm.query")
        print("  proj:", proj.path)
        print("  Attempted to execute: '" + args + "'")
        print("---- stdout: ---------------------")
        print(stdout)
        print("---- stderr: ---------------------")
        print(stderr)
        print("----------------------------------")
        raise


def query_args(columns,
               selection_path,
               selection_type,
               verbatim=True,
               all=False):
    """Constructs a string appropriate for use by `casm query`

    Arguments
    ---------
    columns: iterable of str
        Corresponds to `casm query -k` arguments listing the values to be queried. Use `casm query --help properties` and `casm query --help operators` to list options.

    selection_path: str
        The `-c,--selection` option, a path to a selection file, or a standard selection name ("MASTER", "ALL", "CALCULATED", "NONE")

    selection_type: str
        The `-t,--type` option, indicates the type of object being selected. Expected to be one of:

            "config": to select configurations
            "scel": to select supercells

    verbatim: bool
        If True, use `-v,--verbatim` option to exclude 'name' and 'selected' columns from the query output.

    all: bool
        If True, use `-a,--all` to include unselected objects in the output

    Returns
    -------
    args: str
        A string appropriate for use by `casm query`. The `-o STDOUT` option is always included. Example:

            "query -k 'comp_n scel_size' -c MASTER -t config -v -o STDOUT"
    """
    args = "query -k "
    args += "'"
    for k in columns:
        args += k + " "
    args += "'"
    args += " -c " + selection_path
    args += " -t " + selection_type
    if verbatim == True:
        args += " -v"
    if all:
        args += " -a"
    args += " -o STDOUT"
    return args
