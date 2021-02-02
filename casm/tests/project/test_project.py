import os
import pytest

import casm.api
import casm.project


def test_casm_init(clean_ZrO_dir):
    """Just to catch api errors before testing casm.project"""
    project_path, prim_path = clean_ZrO_dir
    args = "init --path=" + str(project_path) + " --prim=" + str(prim_path)
    stdout, stderr, returncode = casm.api.casm_capture(args, root=None)

    if returncode != 0:
        print(stdout)
        print(stderr)
    assert returncode == 0
    for filename in [
            ".casm", "basis_sets", "cluster_expansions", "symmetry",
            "training_data"
    ]:
        assert os.path.exists(project_path.join(filename))


def test_project_init(clean_ZrO_project):
    project_path, prim_path = clean_ZrO_dir
    args = "init --path=" + str(project_path) + " --prim=" + str(prim_path)
    stdout, stderr, returncode = casm.api.casm_capture(args, root=None)

    if returncode != 0:
        print(stdout)
        print(stderr)
    assert returncode == 0

    proj = casm.project.Project(project_path, verbose=False)
    for filename in [
            ".casm", "basis_sets", "cluster_expansions", "symmetry",
            "training_data"
    ]:
        assert os.path.exists(project_path.join(filename))


def test_project_class_init(clean_ZrO_dir):
    """Just to catch api errors before testing casm.project"""
    project_path, prim_path = clean_ZrO_dir
    proj = casm.project.Project.init(project_path, prim_path, verbose=False)

    for filename in [
            ".casm", "basis_sets", "cluster_expansions", "symmetry",
            "training_data"
    ]:
        assert os.path.exists(os.path.join(proj.path, filename))


def test_project_init(initialized_ZrO_project):
    proj = initialized_ZrO_project
    # assert proj.path == str(clean_ZrO_dir)
    assert proj.name == "ZrO"
    assert isinstance(proj.dir, casm.project.DirectoryStructure)
    assert isinstance(proj.settings, casm.project.ProjectSettings)

    # No composition axes in v1.0.X until `casm composition --calc` done (may change)
    assert proj.composition_axes is None
    assert isinstance(proj.all_composition_axes, dict)
    assert len(proj.all_composition_axes) == 0


#     def test_composition_axes(self):
#         """Test CompositionAxes"""
#         if not self.has_projects:
#             pytest.skip("No test projects")
#         proj = project.Project(self.ZrO_dir, verbose=False)
#         comp_axes = proj.composition_axes
#         self.assertIs(proj.composition_axes, comp_axes)
#         self.assertEqual(comp_axes.name, '0')
#         self.assertEqual(comp_axes.components, ['Zr', 'Va', 'O'])
#         self.assertEqual(comp_axes.n_independent_compositions, 1)
#         self.assertEqual(comp_axes.mol_formula, 'Zr(2)Va(2-2a)O(2a)')
#         self.assertEqual(comp_axes.param_formula, 'a(0.5-0.25Va+0.25O)')
#         self.assertTrue(
#             np.allclose(comp_axes.end_members['origin'],
#                         np.array([2., 2., 0.])))
#         self.assertTrue(
#             np.allclose(comp_axes.end_members['a'], np.array([2., 0., 2.])))
