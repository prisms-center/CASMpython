import numpy as np


def get_incar_magmom_from_magmom_values(magmom_values):
    """Returns an INCAR magmom string from a
    list of magmom values. The magmom values should
    be listed in the order of atoms in POSCAR
    Parameters
    ----------
    magmom_values : np.ndarray
    Returns
    -------
    str
    """

    magmom = ""
    for i, value in enumerate(magmom_values):
        if i == 0:
            number_of_same_magmoms = 1
        elif np.isclose(value, magmom_values[i - 1]):
            number_of_same_magmoms += 1
        else:
            magmom += (
                str(number_of_same_magmoms) + "*" + str(magmom_values[i - 1]) + " "
            )
            number_of_same_magmoms = 1
        if i == len(magmom_values) - 1:
            magmom += str(number_of_same_magmoms) + "*" + str(magmom_values[i]) + " "

    return magmom


class NCunitmagspinAttr:
    """Class containing information specific to Cmagspin dof.
    This object will be constructed from casm.project.structure.StructureInfo class
    which digests its information.

    self.atom_props: List[Dict] - Contains the list of atom properites (with atom name and it's value)
    Look at the example below for detailed description of object properties

    Consider the example of NaFeO2 with Fe having a +5 magnetic moment and rest all being 0
    self.atom_props:
    [
        {"site_index":0, "atom": "Na", "value":0},
        {"site_index":1, "atom":"Fe", "value":5},
        {"site_index":2, "atom":"O","value":0},
        {"site_index":3, "atom":"O","value":0}
    ]
    """

    def __init__(self, structure_info):
        """Constructs the CmagspinAttr object from StructureInfo object

        Parameters
        ----------
        structure_info : casm.project.structure.StructureInfo

        """
        if "NCunitmagspin" not in list(structure_info.atom_properties.keys()):
            raise RuntimeError(
                "Could not construct NCunitmagspinAttr class. "
                "Check if you're dealing with Cmagspin dof calculations."
            )

        self.atom_props = [
            {"site_index": site_index, "atom": atom_type, "value": magmom_value}
            for site_index, (atom_type, magmom_value) in enumerate(
                zip(
                    structure_info.atom_type,
                    structure_info.atom_properties["NCunitmagspin"]["value"],
                )
            )
        ]

    def vasp_input_tags(self, sort=True):
        """Returns a dictionary of MAGMOM, ISPIN input tags
        specific to collinear magnetic VASP calculations.

        Parameters
        ----------
        sort: bool, optional
            This should match the sort used to write
            POSCAR file (whether the basis atoms are sorted))

        Returns
        -------
        dict
            {
                "MAGMOM": magmom_string,
                "ISPIN": 2
            }

        """
        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        magmom_values = np.ravel(
            np.array([atom_prop["value"] for atom_prop in self.atom_props])
        )

        return dict(
            MAGMOM=get_incar_magmom_from_magmom_values(magmom_values),
            ISPIN=2,
            LSORBIT=False,
            LNONCOLLINEAR=True,
        )

    @staticmethod
    def vasp_output_dictionary(outcar, unsort_dict):
        """Returns the attribute specific vasp output
        dictionary which can be updated to the whole output
        dictionary which will be printed as properties.calc.json.
        For Cmagspin, this will be magnetic moment of each individual species

        Parameters
        ----------
        outcar : casm.vasp.io.outcar
            Outcar containing magmom information
        unsort_dict : dict
            ``Poscar.unsort_dict()`` useful for reordering
            the magmom values

        Returns
        -------
        dict
            {
              "Cmagspin":{
                "value":[]
              }
            }

        """
        output = {}
        # output["Cmagspin"] = {}
        # output["Cmagspin"]["value"] = [None] * len(unsort_dict)
        # output["Cunitmagspin"] = {}
        # output["Cunitmagspin"]["value"] = [None] * len(unsort_dict)
        # for i in range(len(outcar.mag)):
        #    output["Cmagspin"]["value"][unsort_dict[i]] = [outcar.mag[i]]
        #    output["Cunitmagspin"]["value"][unsort_dict[i]] = [
        #        outcar.mag[i] / abs(outcar.mag[i])
        #    ]

        raise NotImplementedError("Not implemented this part yet")


class SOunitmagspinAttr:
    """Class containing information specific to Cmagspin dof.
    This object will be constructed from casm.project.structure.StructureInfo class
    which digests its information.

    self.atom_props: List[Dict] - Contains the list of atom properites (with atom name and it's value)
    Look at the example below for detailed description of object properties

    Consider the example of NaFeO2 with Fe having a +5 magnetic moment and rest all being 0
    self.atom_props:
    [
        {"site_index":0, "atom": "Na", "value":0},
        {"site_index":1, "atom":"Fe", "value":5},
        {"site_index":2, "atom":"O","value":0},
        {"site_index":3, "atom":"O","value":0}
    ]
    """

    def __init__(self, structure_info):
        """Constructs the CmagspinAttr object from StructureInfo object

        Parameters
        ----------
        structure_info : casm.project.structure.StructureInfo

        """
        if "SOunitmagspin" not in list(structure_info.atom_properties.keys()):
            raise RuntimeError(
                "Could not construct SOunitmagspinAttr class. "
                "Check if you're dealing with Cmagspin dof calculations."
            )

        self.atom_props = [
            {"site_index": site_index, "atom": atom_type, "value": magmom_value}
            for site_index, (atom_type, magmom_value) in enumerate(
                zip(
                    structure_info.atom_type,
                    structure_info.atom_properties["SOunitmagspin"]["value"],
                )
            )
        ]

    def vasp_input_tags(self, sort=True):
        """Returns a dictionary of MAGMOM, ISPIN input tags
        specific to collinear magnetic VASP calculations.

        Parameters
        ----------
        sort: bool, optional
            This should match the sort used to write
            POSCAR file (whether the basis atoms are sorted))

        Returns
        -------
        dict
            {
                "MAGMOM": magmom_string,
                "ISPIN": 2
            }

        """
        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        magmom_values = np.ravel(
            np.array([atom_prop["value"] for atom_prop in self.atom_props])
        )

        return dict(
            MAGMOM=get_incar_magmom_from_magmom_values(magmom_values),
            ISPIN=2,
            LSORBIT=True,
            LNONCOLLINEAR=True,
        )

    @staticmethod
    def vasp_output_dictionary(outcar, unsort_dict):
        """Returns the attribute specific vasp output
        dictionary which can be updated to the whole output
        dictionary which will be printed as properties.calc.json.
        For Cmagspin, this will be magnetic moment of each individual species

        Parameters
        ----------
        outcar : casm.vasp.io.outcar
            Outcar containing magmom information
        unsort_dict : dict
            ``Poscar.unsort_dict()`` useful for reordering
            the magmom values

        Returns
        -------
        dict
            {
              "Cmagspin":{
                "value":[]
              }
            }

        """
        output = {}
        # output["Cmagspin"] = {}
        # output["Cmagspin"]["value"] = [None] * len(unsort_dict)
        # output["Cunitmagspin"] = {}
        # output["Cunitmagspin"]["value"] = [None] * len(unsort_dict)
        # for i in range(len(outcar.mag)):
        #    output["Cmagspin"]["value"][unsort_dict[i]] = [outcar.mag[i]]
        #    output["Cunitmagspin"]["value"][unsort_dict[i]] = [
        #        outcar.mag[i] / abs(outcar.mag[i])
        #    ]

        raise NotImplementedError("Not implemented this part yet")


class CunitmagspinAttr:
    """Class containing information specific to Cmagspin dof.
    This object will be constructed from casm.project.structure.StructureInfo class
    which digests its information.

    self.atom_props: List[Dict] - Contains the list of atom properites (with atom name and it's value)
    Look at the example below for detailed description of object properties

    Consider the example of NaFeO2 with Fe having a +5 magnetic moment and rest all being 0
    self.atom_props:
    [
        {"site_index":0, "atom": "Na", "value":0},
        {"site_index":1, "atom":"Fe", "value":5},
        {"site_index":2, "atom":"O","value":0},
        {"site_index":3, "atom":"O","value":0}
    ]
    """

    def __init__(self, structure_info):
        """Constructs the CmagspinAttr object from StructureInfo object

        Parameters
        ----------
        structure_info : casm.project.structure.StructureInfo

        """
        if "Cunitmagspin" not in list(structure_info.atom_properties.keys()):
            raise RuntimeError(
                "Could not construct CunitmagspinAttr class. "
                "Check if you're dealing with Cmagspin dof calculations."
            )

        self.atom_props = [
            {"site_index": site_index, "atom": atom_type, "value": magmom_value}
            for site_index, (atom_type, magmom_value) in enumerate(
                zip(
                    structure_info.atom_type,
                    structure_info.atom_properties["Cunitmagspin"]["value"],
                )
            )
        ]

    def vasp_input_tags(self, sort=True):
        """Returns a dictionary of MAGMOM, ISPIN input tags
        specific to collinear magnetic VASP calculations.

        Parameters
        ----------
        sort: bool, optional
            This should match the sort used to write
            POSCAR file (whether the basis atoms are sorted))

        Returns
        -------
        dict
            {
                "MAGMOM": magmom_string,
                "ISPIN": 2
            }

        """
        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        magmom_values = np.ravel(
            np.array([atom_prop["value"] for atom_prop in self.atom_props])
        )

        return dict(MAGMOM=get_incar_magmom_from_magmom_values(magmom_values), ISPIN=2)

    @staticmethod
    def vasp_output_dictionary(outcar, unsort_dict):
        """Returns the attribute specific vasp output
        dictionary which can be updated to the whole output
        dictionary which will be printed as properties.calc.json.
        For Cmagspin, this will be magnetic moment of each individual species

        Parameters
        ----------
        outcar : casm.vasp.io.outcar
            Outcar containing magmom information
        unsort_dict : dict
            ``Poscar.unsort_dict()`` useful for reordering
            the magmom values

        Returns
        -------
        dict
            {
              "Cmagspin":{
                "value":[]
              }
            }

        """
        output = {}
        output["Cmagspin"] = {}
        output["Cmagspin"]["value"] = [None] * len(unsort_dict)
        output["Cunitmagspin"] = {}
        output["Cunitmagspin"]["value"] = [None] * len(unsort_dict)
        for i in range(len(outcar.mag)):
            output["Cmagspin"]["value"][unsort_dict[i]] = [outcar.mag[i]]
            if abs(outcar.mag[i]) < 1:
                output["Cunitmagspin"]["value"][unsort_dict[i]] = [0.0]
            else:
                output["Cunitmagspin"]["value"][unsort_dict[i]] = [
                    outcar.mag[i] / abs(outcar.mag[i])
                ]

        return output


class CmagspinAttr:
    """Class containing information specific to Cmagspin dof.
    This object will be constructed from casm.project.structure.StructureInfo class
    which digests its information.

    self.atom_props: List[Dict] - Contains the list of atom properites (with atom name and it's value)
    Look at the example below for detailed description of object properties

    Consider the example of NaFeO2 with Fe having a +5 magnetic moment and rest all being 0
    self.atom_props:
    [
        {"site_index":0, "atom": "Na", "value":0},
        {"site_index":1, "atom":"Fe", "value":5},
        {"site_index":2, "atom":"O","value":0},
        {"site_index":3, "atom":"O","value":0}
    ]
    """

    def __init__(self, structure_info):
        """Constructs the CmagspinAttr object from StructureInfo object

        Parameters
        ----------
        structure_info : casm.project.structure.StructureInfo

        """
        if "Cmagspin" not in list(structure_info.atom_properties.keys()):
            raise RuntimeError(
                "Could not construct CmagspinAttr class. "
                "Check if you're dealing with Cmagspin dof calculations."
            )
        self.atom_props = [
            {"site_index": site_index, "atom": atom_type, "value": magmom_value}
            for site_index, (atom_type, magmom_value) in enumerate(
                zip(
                    structure_info.atom_type,
                    structure_info.atom_properties["Cmagspin"]["value"],
                )
            )
        ]

    def vasp_input_tags(self, sort=True):
        """Returns a dictionary of MAGMOM, ISPIN input tags
        specific to collinear magnetic VASP calculations.

        Parameters
        ----------
        sort: bool, optional
            This should match the sort used to write
            POSCAR file (whether the basis atoms are sorted))

        Returns
        -------
        dict
            {
                "MAGMOM": magmom_string,
                "ISPIN": 2
            }

        """
        if sort is True:
            self.atom_props.sort(key=lambda x: x["atom"])

        magmom_values = np.ravel(
            np.array([atom_prop["value"] for atom_prop in self.atom_props])
        )

        return dict(MAGMOM=get_incar_magmom_from_magmom_values(magmom_values), ISPIN=2)

    @staticmethod
    def vasp_output_dictionary(outcar, unsort_dict):
        """Returns the attribute specific vasp output
        dictionary which can be updated to the whole output
        dictionary which will be printed as properties.calc.json.
        For Cmagspin, this will be magnetic moment of each individual species

        Parameters
        ----------
        outcar : casm.vasp.io.outcar
            Outcar containing magmom information
        unsort_dict : dict
            ``Poscar.unsort_dict()`` useful for reordering
            the magmom values

        Returns
        -------
        dict
            {
              "Cmagspin":{
                "value":[]
              }
            }

        """
        output = {}
        output["Cmagspin"] = {}
        output["Cmagspin"]["value"] = [None] * len(unsort_dict)
        for i in range(len(outcar.mag)):
            output["Cmagspin"]["value"][unsort_dict[i]] = [outcar.mag[i]]

        return output
