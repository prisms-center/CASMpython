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
       This object will be constructed from casm.project.structure.StructureInfo class
       which digests its information.

       self.atom_props: List[Dict] - Contains the list of atom properites (with atom name and it's value)
       Look at the example below for detailed description of object properties

       Consider the example of NaFeO2 with Fe having a +5 magnetic moment and rest all being 0
       self.atom_props: [{"site_index":0, "atom": "Na", "value":0},{"site_index":1,"atom":"Fe", "value":5},{"site_index":2, "atom":"O","value":0},{"site_index":3, "atom":"O","value":0}]"""
    def __init__(self, structure_info):
        """Constructs the CmagspinAttr object from StructureInfo object

        Parameters
        ----------
        structure_info : casm.project.structure.StructureInfo

        """
        try:
            self.atom_props = [{
                "site_index":
                x,
                "atom":
                structure_info.atom_type[x],
                "value":
                structure_info.atom_properties["Cmagspin"]["value"][x]
            } for x in range(0, len(structure_info.atom_type))]
        except:
            raise DofClassError(
                "Could not construct CmagspinAttr class!! Check if you're dealing with Cmagspin dof calculations"
            )

    def vasp_input_tags(self, sort=True):
        """Returns a dictionary of VASP input tags specific to collinear magnetic spin calculations.
        The collinear magnetic spin specific tags are as follows:

        MAGMOM, ISPIN

        Parameters
        ----------
        sort: bool (This should match the sort used to write POSCAR file (whether the basis atoms are sorted))

        Returns
        -------
        dict{"vasp_input_tag": "value"}

        """
        #TODO: Group together atoms of same MAGMOM together
        #TODO: Also add ISPIN default tag which is required if missed in INCAR.base

        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        magmom_value = ""
        for atom_props in self.atom_props:
            magmom_value = magmom_value + str(atom_props["value"][0]) + " "

        tags = dict()
        tags["MAGMOM"] = magmom_value
        return tags

    def vasp_output_dictionary(self, outcar, sort=True):
        """Returns the attribute specific vasp output dictionary which can be updated
        to the whole output dictionary which will be printed as properties.calc.json.

        For Cmagspin, this will be magnetic moment of each individual species

        Parameters
        ----------
        outcar : casm.vasp.io.outcar (Class containing information about magmom of individual species from OUTCAR)
        sort : bool (This should be the same sort used while writing POSCAR)

        Returns
        -------
        dict{"Cmagspin":{"value":[list]}}

        """
        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        permutation_vector_to_unsort = [
            x["site_index"] for x in self.atom_props
        ]

        output = {}
        output["Cmagspin"] = {}
        output["Cmagspin"]["value"] = [[mag] for site_index, mag in sorted(
            zip(permutation_vector_to_unsort, outcar.mag))]

        return output
