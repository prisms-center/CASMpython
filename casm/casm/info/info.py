import json
from casm.api import casm_capture


def _check_info_output(stdout, returncode, method):
    if returncode:
        print(stdout)
        raise Exception("Error getting " + method + " info")
    try:
        return json.loads(stdout)
    except:
        print(stdout)
        raise Exception("Error parsing " + method + " info results")


def prim_info_desc():
    """
    Return CASM `info --desc PrimInfo` output.
    """
    stdout, returncode = casm_capture('info --desc PrimInfo',
                                      combine_output=True)
    return stdout


def get_prim_info(prim=None, root=None, properties=[]):
    """
    Get properties of a primitive crystal structure.

    Arguments
    ---------

      prim: dict of BasicStructure (optional, default=None)
        Dict containing the definition of a "prim", in the `CASM BasicStructure JSON format`_. May be None if `root` provided.

      root: str (optional, default=os.getcwd())
        Use the prim of a CASM project located at `root`, if it exists.

      properties: list of str (default=[])
        A list of properties to return


    Returns
    -------
      output: Dict containing results.

    .. CASM BasicStructure JSON format_: https://prisms-center.github.io/CASMcode_docs/pages/formats/casm/crystallography/BasicStructure.html
    """
    input = {}
    if prim is not None:
        input["prim"] = prim
    input["properties"] = properties
    args = "info -m PrimInfo -i '" + json.dumps(input) + "'"
    stdout, returncode = casm_capture(args, root=root, combine_output=True)
    return _check_info_output(stdout, returncode, "prim")


def supercell_info_desc():
    """
    Return CASM `info --desc SupercellInfo` output.
    """
    stdout, returncode = casm_capture('info --desc SupercellInfo',
                                      combine_output=True)
    return stdout


def get_supercell_info(prim=None, root=None, properties=[], **kwargs):
    """
    Get properties of a supercell.

    Arguments
    ---------

      prim: dict of BasicStructure (optional, default=None)
        Dict containing the definition of a "prim", in the `CASM BasicStructure JSON format`_. May be None if `root` provided.

      root: str (optional, default=os.getcwd())
        Use the prim of a CASM project located at `root`.

      properties: list of str (default=[])
        A list of properties to return

      **kwargs:  key-value pairs
        Additional key-value pairs to be added to the input. See
        `supercell_info_desc` for options.

    Returns
    -------
      output: Dict containing results.

    .. CASM BasicStructure JSON format_: https://prisms-center.github.io/CASMcode_docs/pages/formats/casm/crystallography/BasicStructure.html
    """
    input = {}
    if prim is not None:
        input["prim"] = prim
    input["properties"] = properties
    input.update(kwargs)
    args = "info -m SupercellInfo -i '" + json.dumps(input) + "'"
    stdout, returncode = casm_capture(args, root=root, combine_output=True)
    return _check_info_output(stdout, returncode, "supercell")


def neighbor_list_info_desc():
    """
    Return CASM `info --desc NeighborListInfo` output.
    """
    stdout, returncode = casm_capture('info --desc NeighborListInfo',
                                      combine_output=True)
    return stdout


def get_neighbor_list_info(prim=None, root=None, properties=[], **kwargs):
    """
    Get neighbor list information for a supercell

    Arguments
    ---------

      prim: dict of BasicStructure (optional, default=None)
        Dict containing the definition of a "prim", in the `CASM BasicStructure JSON format`_. May be None if `root` provided.

      root: str (optional, default=os.getcwd())
        Use the prim of a CASM project located at `root`.

      properties: list of str (default=[])
        A list of properties to return

      **kwargs:  key-value pairs
        Additional key-value pairs to be added to the input. See
        `neighbor_list_info_desc` for options.

    Returns
    -------
      output: Dict containing results.

    .. CASM BasicStructure JSON format_: https://prisms-center.github.io/CASMcode_docs/pages/formats/casm/crystallography/BasicStructure.html
    """
    input = {}
    if prim is not None:
        input["prim"] = prim
    input["properties"] = properties
    input.update(kwargs)
    args = "info -m NeighborListInfo -i '" + json.dumps(input) + "'"
    stdout, returncode = casm_capture(args, root=root, combine_output=True)
    return _check_info_output(stdout, returncode, "neighbor_list")
