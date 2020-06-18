class DofClassError(Exception):

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


class CmagspinAttr:

    """Class containing information specific to Cmagspin dof.
       This object will be constructed from casm.project.attribute_info.AttributeInfo class
       which digests its information.

       self.atom_props: List[Dict] - Contains the list of atom properites (with atom name and it's value)
       self.mol_props: List[Dict] - Contains the list of molecule properties (with mol name and it's value)
       Look at the example below for detailed description of object properties

       Consider the example of NaFeO2 with Fe having a +5 magnetic moment and rest all being 0
       self.atom_props: [{"atom": "Na", "value":0},{"atom":"Fe", "value":5},{"atom":"O","value":0},{"atom":"O","value":0}]
       self.mol_props: [{"mol": "Na", "value":0},{"mol":"Fe", "value":0},{"mol":"O","value":0},{"mol":"O","value":0}]"""

    def __init__(self, dof_info):
        """Constructs the CmagspinAttr object from AttributeInfo object

        Parameters
        ----------
        dof_info : casm.project.attribute_info.AttributeInfo

        """
        try:
            self.atom_props = [{"atom": dof_info.atom_type[x], "value": dof_info.atom_dofs["Cmagspin"]
                                ["value"][x]} for x in range(0, len(dof_info.atom_type))]

            self.mol_props = [{"mol": dof_info.mol_type[x], "value": dof_info.mol_dofs["Cmagspin"]
                               ["value"][x]} for x in range(0, len(dof_info.mol_type))]
        except:
            raise DofClassError(
                "Could not construct CmagspinAttr class!! Check if you're dealing with Cmagspin dof calculations")

    def vasp_input_tags(self, sort=True):
        """Returns a dictionary of VASP input tags specific to collinear magnetic spin calculations.
        The collinear magnetic spin specific tags are as follows:
        MAGMOM

        Parameters
        ----------
        sort: bool (This should match the sort used to write POSCAR file)

        Returns
        -------
        dict{"vasp_input_tag": "value"}

        """
        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        magmom_value = ""
        for atom_props in self.atom_props:
            magmom_value = magmom_value + str(atom_props["value"][0]) + " "

        tags = dict()
        tags["MAGMOM"] = magmom_value
        return tags
