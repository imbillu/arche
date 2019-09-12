import arche.rules.compare as compare
from arche.rules.result import Level
from conftest import *
import pytest


@pytest.mark.parametrize(
    ["source", "target", "fields", "expected"],
    [
        (
            {
                "one": list(range(50)) + [42] * 50,
                "two": list(range(100)),
                "three": [np.nan] * 50 + list(range(50)),
            },
            {
                "one": list(range(50, 100)) + [42] * 500,
                "two": list(range(550)),
                "three": [np.nan] * 500 + list(range(50)),
            },
            ["one", "two", "three"],
            {
                Level.INFO: [
                    ("100 `non NaN ones` - 49 new, 51 same",),
                    (
                        "50 `ones` are missing",
                        None,
                        {"50, 51, 52, 53, 54... `ones` are missing": set(range(50))},
                    ),
                    ("100 `non NaN twos` - 0 new, 100 same",),
                    ("50 `non NaN threes` - 0 new, 50 same",),
                ],
                Level.ERROR: [
                    (
                        "450 `twos` are missing",
                        None,
                        {
                            "100, 101, 102, 103, 104... `twos` are missing": set(
                                range(100, 550)
                            )
                        },
                    )
                ],
            },
        )
    ],
)
def test_fields(source, target, fields, expected):
    assert compare.fields(
        pd.DataFrame(source), pd.DataFrame(target), fields
    ) == create_result("Fields Difference", expected)
