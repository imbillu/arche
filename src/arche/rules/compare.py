from typing import List

from arche.readers.schema import TaggedFields
from arche.rules.result import *
import pandas as pd


MAX_MISSING_VALUES = 6


def fields(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    names: List[str],
    err_thr: float = 0.25,
) -> Result:
    """Return fields values difference between dataframes"""

    result = Result("Fields Difference")
    for field in names:
        source = source_df[field].dropna()
        target = target_df[field].dropna()
        try:
            same = source[source.isin(target)]
            new = source[~(source.isin(target))]
            missing = target[~(target.isin(source))]
        except SystemError:
            source = source.astype(str)
            target = target.astype(str)
            same = source[source.isin(target)]
            new = source[~(source.isin(target))]
            missing = target[~(target.isin(source))]

        result.add_info(
            f"{len(source)} `non NaN {field}s` - {len(new)} new, {len(same)} same"
        )
        if len(missing) == 0:
            continue

        if len(missing) < MAX_MISSING_VALUES:
            msg = ", ".join(missing.unique().astype(str))
        else:
            msg = f"{', '.join(missing.unique()[:5].astype(str))}..."
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


def tagged_fields(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    tagged_fields: TaggedFields,
    tags: List[str],
) -> Result:
    """Compare fields tagged with `tags` between two dataframes."""
    name = f"{', '.join(tags)} Fields Difference"
    result = Result(name)
    fields_names = list()
    for tag in tags:
        if tagged_fields.get(tag):
            fields_names.extend(tagged_fields.get(tag))
    if not fields_names:
        result.add_info(Outcome.SKIPPED)
        return result
    result = fields(source_df, target_df, fields_names)
    result.name = name
    return result
