import pytest

import casm.project


def test_composition_axes_calculated(ZrO_project_calc_composition_axes):
    proj = ZrO_project_calc_composition_axes

    # No composition axes in v1.0.X until `casm composition --calc` done (may change)
    assert proj.composition_axes is None
    assert isinstance(proj.all_composition_axes, dict)
    assert len(proj.all_composition_axes) == 2
    for name, axes in proj.all_composition_axes.items():
        assert isinstance(axes, casm.project.CompositionAxes)


def test_composition_axes_selected(ZrO_project):
    proj = ZrO_project

    # No composition axes in v1.0.X until `casm composition --calc` done (may change)
    assert isinstance(proj.composition_axes, casm.project.CompositionAxes)
    assert isinstance(proj.all_composition_axes, dict)
    assert len(proj.all_composition_axes) == 2
    for name, axes in proj.all_composition_axes.items():
        assert isinstance(axes, casm.project.CompositionAxes)
