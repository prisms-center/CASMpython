import json
import os


class AttributeInfoError(Exception):
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


class AttributeInfo:
    """Contains the atom and molecule attributes' information
       self.atom_type: List[str] - Contains the atom types
       self.atom_dofs: Dict{Dict{List[float or int]}} - Contains dofs for all the atoms in the structure.json
       self.mol_type: List[str] - Contains the molecule types
       self.mol_dofs: Dict{Dict{List[float or int]}} - Contains dofs for the molecules
       Look the example below for clarity regarding object properties

       For example consider a Cmagspin dof for NaFeO2 system
       self.atom_type: [Na, Fe, O, O]
       self.atom_dofs: {'Cmagspin':{'value': [[0],[-1],[0],[0]]}}
       self.mol_type: [Na, Fe-, O, O]
       self.mol_dofs: {'Cmagspin': {'value': [[0],[0],[0],[0]]}}"""
    def __init__(self, filename):
        """Constructs the AttributeInfo object by reading the structure.json file

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
                config_data = json.load(f)

            self.atom_dofs = config_data["atom_dofs"]
            self.atom_type = config_data["atom_type"]
            self.mol_dofs = config_data["mol_dofs"]
            self.mol_type = config_data["mol_type"]

        except:
            self.atom_dofs = None
            self.atom_type = None
            self.mol_dofs = None
            self.mol_type = None
            print("No dof information found in " + filename)
