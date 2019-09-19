import arche.rules.compare as compare
from arche.rules.result import Level
from conftest import *
import pytest


@pytest.mark.parametrize(
    ["source", "target", "fields", "normalize", "expected"],
    [
        (
            {
                "one": list(range(50)) + ["42"] * 50,
                "two": list(range(100)),
                "three": [np.nan] * 50 + list(range(50)),
            },
            {
                "one": list(range(50, 100)) + [42] * 500,
                "two": list(range(550)),
                "three": [np.nan] * 500 + list(range(50)),
            },
            ["one", "two", "three"],
            False,
            {
                Level.INFO: [
                    ("100 `non NaN ones` - 99 new, 1 same",),
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
        ),
        (
            {
                "four": [{i} for i in range(10)]
                + [{"K": {"k": i}} for i in range(10)]
                + ["l"] * 80
            },
            {
                "four": [{i} for i in range(20)]
                + [{"k": {"k": i}} for i in range(10)]
                + ["L"] * 520
            },
            ["four"],
            True,
            {
                Level.INFO: [
                    ("100 `non NaN fours` - 0 new, 100 same",),
                    (
                        "10 `fours` are missing",
                        None,
                        {
                            "{10}, {11}, {12}, {13}, {14}... `fours` are missing": set(
                                range(10, 20)
                            )
                        },
                    ),
                ]
            },
        ),
    ],
)
def test_fields(source, target, fields, normalize, expected):
    assert compare.fields(
        pd.DataFrame(source), pd.DataFrame(target), fields, normalize
    ) == create_result("Fields Difference", expected)
