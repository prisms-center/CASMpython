import pytest

import casm.project


def test_query(ZrO_project_ConfigEnumAllOccupations_max4):
    proj = ZrO_project_ConfigEnumAllOccupations_max4
    columns = ["name", "selected", "comp_n", "scel_size"]
    df = casm.project.query(proj,
                            columns,
                            "ALL",
                            "config",
                            verbatim=True,
                            all=True)

    n_total = 336
    assert df.shape == (n_total, 6)
    assert df.columns.tolist() == [
        'name', 'selected', 'comp_n(Zr)', 'comp_n(Va)', 'comp_n(O)',
        'scel_size'
    ]
    assert df.dtypes.tolist() == [
        'object', 'int64', 'float64', 'float64', 'float64', 'int64'
    ]
