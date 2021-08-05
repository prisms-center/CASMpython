import json

def get_casm_structure_property(casm_structure, property_type, property_name):
    """Get the value of a property from a CASM structure

    A CASM property name to find from the structure's atom, mol, or global properties. For example, property_name "disp", "magspin", or "strain" will find "<qualifier>_disp", "<qualifier>_<flavor>magspin", or "<qualifier>_<metric>strain", respectively. Finding multiple matches raises.

    Arguments
    ---------
      casm_structure: dict
        A CASM structure, as from JSON

      property_type: str
        One of "atom", "mol", or "global"

      property_name: str
        A CASM property (i.e. "disp", "strain", "magspin", etc.)

    Returns
    -------
      value: Any or None
        Returns "value" for a found property with `property_name` as the suffix, else None.

    Raises
    ------
      Exception:
        If >1 matching property is found
    """
    key = property_type + "_properties"
    matching = []
    if key in casm_structure:
        for name in casm_structure[key]:
            if name.split('_')[-1][-len(property_name):] == property_name:
                matching.append(name)
    if len(matching) > 1:
        raise Exception("Error getting atom properties from a CASM structure: Found multiple matches for '" + property_name + "': " + str(matching))
    elif len(matching) == 1:
        name = matching[0]
        return casm_structure[key][name]["value"]
    else:
        result = None

class StructureInfoError(Exception):
    """Exception handling"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        """ Writes out the error message

        Returns
        -------
        string

        """
        return self.message

class StructureInfo:
    """Contains the atom and molecule attributes' information

    Attributes
    ----------

       self.atom_type: List[str] - Contains the atom types
       self.atom_properties: Dict{Dict{List[float or int]}} - Contains dofs for all the atoms in the structure.json
       self.mol_type: List[str] - Contains the molecule types
       self.mol_properties: Dict{Dict{List[float or int]}} - Contains dofs for the molecules
       Look the example below for clarity regarding object properties

       For example consider a Cmagspin dof for NaFeO2 system
       self.atom_type: [Na, Fe, O, O]
       self.atom_properties: {'Cmagspin':{'value': [[0],[-1],[0],[0]]}}
       self.mol_type: [Na, Fe-, O, O]
       self.mol_properties: {'Cmagspin': {'value': [[0],[0],[0],[0]]}}

    Notes
    -----

    This class should be considered experimental and subject to change.

    """
    def __init__(self, filename):
        """Constructs the StructureInfo object by reading the structure.json file

        Parameters
        ----------
        filename : string (structure.json file)

        """
        self.read(filename)

    def read(self, filename):
        """Reads the attribute information from a CASM structure.json file

        Will set attributes to None, with message "No dof information found in <filename>", if the file cannot be read as a CASM structure.json file.

        Parameters
        ----------
        filename : string (structure.json file)

        """
        with open(filename, 'r') as f:
            casm_structure = json.load(f)

        self.atom_type = casm_structure["atom_type"]
        self.atom_properties = casm_structure.get("atom_properties", {})
        self.mol_type = casm_structure["mol_type"]
        self.mol_properties = casm_structure.get("mol_properties", {})
