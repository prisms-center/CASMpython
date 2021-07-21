"""An interface to CASM projects via Python"""
from casm.project.project import project_path, ClexDescription, ProjectSettings, \
    DirectoryStructure, Project, Prim, CompositionAxes
from casm.project.selection import Selection
from casm.project.query import query
from casm.project.io import write_eci
from casm.project.structure import StructureInfo
__all__ = [
    'project_path', 'ClexDescription', 'ProjectSettings', 'DirectoryStructure',
    'Project', 'Prim', 'Selection', 'query', 'write_eci', 'StructureInfo'
]
