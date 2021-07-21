
def get_casm_structure_property(casm_structure, property_type, property_name):
    """Get the value of a property from a CASM structure

    A CASM property name to find from the structure's atom, mol, or global properties. For example, property_name "disp", "magspin", or "strain" will find "<qualifier>_disp", "<qualifier>_<flavor>magspin", or "<qualifier>_<metric>strain", respectively. Finding multiple matches raises.

    Will check aliases "<property_type>_properties", "<property_type>_dofs", "<property_type>_vals", and "<property_type>_values"

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
        value: casm_structure[alias]["value"] or None
    """
    aliases = [
        property_type + "_properties",
        property_type + "_dofs",
        property_type + "_vals",
        property_type + "_values"]
    matching = []
    for alias in aliases:
        if alias not in casm_structure:
            continue
        for name in casm_structure[alias]:
            if name.split('_')[-1][-len(property_name):] == property_name:
                matching.append((alias,name))
    if len(matching) > 1:
        raise Exception("Error getting atom properties from a CASM structure: Found multiple matches for '" + property_name + "': " + str(matching))
    elif len(matching) == 1:
        alias = matching[0][0]
        name = matching[0][1]
        return casm_structure[alias][name]["value"]
    else:
        result = None

def get_all_casm_structure_properties(casm_structure, property_type):
    """Get properties from a CASM structure object

    Will check aliases "<property_type>_properties", "<property_type>_dofs", "<property_type>_vals", and "<property_type>_values" and collect all properties.

    Arguments
    ---------
      casm_structure: dict
        A CASM structure, as from JSON

      property_type: str
        One of "atom", "mol", or "global"

    Returns
    -------
        properties: dict
            Properties from all aliases collected in one dict of format:

            {
                <name>: {
                    "value": [... values ...]
                },
                ...
            }
    """
    aliases = [
        property_type + "_properties",
        property_type + "_dofs",
        property_type + "_vals",
        property_type + "_values"]
    properties = {}
    for alias in aliases:
        if alias not in casm_structure:
            continue
        for name in casm_structure[alias]:
            properties[name] = casm_structure[alias][name]
    return properties


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
        try:
            with open(filename, 'r') as f:
                casm_structure = json.load(f)

            self.atom_type = casm_structure["atom_type"]
            self.atom_properties = get_all_casm_structure_properties(casm_structure, "atom")
            self.mol_type = casm_structure["mol_type"]
            self.mol_properties = get_all_casm_structure_properties(casm_structure, "mol")


        except:
            self.atom_properties = None
            self.atom_type = None
            self.mol_properties = None
            self.mol_type = None
            print("No dof information found in " + filename)
