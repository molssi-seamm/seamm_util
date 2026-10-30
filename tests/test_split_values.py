"""split_values keeps backslashes: shlex.split treated them as escapes, so the Z
double bonds of SMILES such as 'C/C=C\\C' were lost (thermo, ChemAI 5523,
2026-10-30)."""

import pytest

from seamm_util import split_values


@pytest.mark.parametrize(
    "text, values",
    [
        (r"O/C=C\O C/C=C\N", [r"O/C=C\O", r"C/C=C\N"]),
        (r"'O/C=C\O' 'C/C=C\N'", [r"O/C=C\O", r"C/C=C\N"]),
        (r'"C/C=N\C"  [Na+]', [r"C/C=N\C", "[Na+]"]),
        ("C#N CC", ["C#N", "CC"]),  # '#' is a triple bond, not a comment
        ('"two words" three', ["two words", "three"]),
        ("  1 2\n3\t4 ", ["1", "2", "3", "4"]),
        ("", []),
    ],
)
def test_split_values(text, values):
    assert split_values(text) == values


def test_round_trip_through_shlex_join():
    """Lists joined with shlex.join (e.g. by the MCP server) split back unchanged."""
    import shlex

    values = [r"C/C=C\C", "it's", "two words", "C#N"]
    assert split_values(shlex.join(values)) == values
