from typing import List

from arche.rules.result import Result
import pandas as pd


def fields(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    fields: List[str],
    err_thr: float = 0.25,
) -> Result:
    """Return field values difference between jobs"""

    result = Result("Fields Difference")

    for field in fields:
        source = source_df[field].dropna()
        target = target_df[field].dropna()
        same = source[source.isin(target)]
        new = source[~(source.isin(target))]
        result.add_info(
            f"{len(source)} `non NaN {field}s` - {len(new)} new, {len(same)} same"
        )
        missing = target[~(target.isin(source))]
        missing_values = missing.values
        if len(missing_values) == 0:
            continue

        if len(missing) < 6:
            msg = ", ".join(missing_values.astype(str))
        else:
            missing_values = missing[:5].values
            msg = f"{', '.join(missing_values.astype(str))}..."
        msg = f"{msg} `{field}s` are missing"
        if len(missing) / len(target_df) >= err_thr:
            result.add_error(
                f"{len(missing)} `{field}s` are missing",
                errors={msg: set(missing.index)},
            )
        else:
            result.add_info(
                f"{len(missing)} `{field}s` are missing",
                errors={msg: set(missing.index)},
            )

    return result
