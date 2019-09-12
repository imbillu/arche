from arche.readers.schema import TaggedFields
from arche.rules.result import Result, Outcome
from arche.tools.helpers import is_number, ratio_diff
import pandas as pd


def compare_was_now(df: pd.DataFrame, tagged_fields: TaggedFields):
    """Compare price_was and price_now tagged fields"""

    price_was_fields = tagged_fields.get("product_price_was_field")
    price_fields = tagged_fields.get("product_price_field")
    items_number = len(df.index)

    result = Result("Compare Price Was And Now")

    if not price_was_fields or not price_fields:
        result.add_info(Outcome.SKIPPED)
        return result

    price_field = price_fields[0]
    price_was_field = price_was_fields[0]
    prices = df.copy()
    prices[price_was_field] = prices[price_was_field].astype(float)
    prices[price_field] = prices[price_field].astype(float)

    df_prices_less = pd.DataFrame(
        prices[prices[price_was_field] < prices[price_field]],
        columns=[price_was_field, price_field],
    )

    price_less_percent = "{:.2%}".format(len(df_prices_less) / items_number)

    if not df_prices_less.empty:
        error = f"Past price is less than current for {len(df_prices_less)} items"
        result.add_error(
            f"{price_less_percent} ({len(df_prices_less)}) of "
            f"items with {price_was_field} < {price_field}",
            errors={error: set(df_prices_less.index)},
        )

    df_prices_equals = pd.DataFrame(
        prices[prices[price_was_field] == prices[price_field]],
        columns=[price_was_field, price_field],
    )
    price_equal_percent = "{:.2%}".format(len(df_prices_equals) / items_number)

    if not df_prices_equals.empty:
        result.add_warning(
            (
                f"{price_equal_percent} ({len(df_prices_equals)}) "
                f"of items with {price_was_field} = {price_field}"
            ),
            errors=(
                {
                    f"Prices equal for {len(df_prices_equals)} items": set(
                        df_prices_equals.index
                    )
                }
            ),
        )

    result.items_count = len(df.index)
    return result


def compare_prices_for_same_urls(
    source_df: pd.DataFrame, target_df: pd.DataFrame, tagged_fields: TaggedFields
) -> Result:
    """For each pair of items that have the same `product_url_field` tagged field,
    compare `product_price_field` field

    Returns:
        A result containing pairs of items from `source_df` and `target_df`
        which `product_price_field` differ.
    """
    result = Result("Compare Prices For Same Urls")
    url_field = tagged_fields.get("product_url_field")
    if not url_field:
        result.add_info(Outcome.SKIPPED)
        return result

    url_field = url_field[0]

    source_df = source_df.dropna(subset=[url_field])
    target_df = target_df.dropna(subset=[url_field])

    same_urls = source_df[(source_df[url_field].isin(target_df[url_field].values))][
        url_field
    ]

    price_field = tagged_fields.get("product_price_field")
    if not price_field:
        result.add_info("product_price_field tag is not set")
    else:
        price_field = price_field[0]
        detailed_messages = []
        for url in same_urls:
            if url.strip() != "nan":
                source_price = source_df[source_df[url_field] == url][price_field].iloc[
                    0
                ]
                target_price = target_df[target_df[url_field] == url][price_field].iloc[
                    0
                ]

                if (
                    is_number(source_price)
                    and is_number(target_price)
                    and ratio_diff(source_price, target_price) > 0.1
                ):
                    source_key = source_df[source_df[url_field] == url].index[0]
                    target_key = target_df[target_df[url_field] == url].index[0]
                    msg = (
                        f"different prices for url: {url}\nsource price is {source_price} "
                        f"for {source_key}\ntarget price is {target_price} for {target_key}"
                    )
                    detailed_messages.append(msg)

        res = f"{len(same_urls)} checked, {len(detailed_messages)} errors"
        if detailed_messages:
            result.add_error(res, detailed="\n".join(detailed_messages))
        else:
            result.add_info(res)

    return result


def compare_names_for_same_urls(
    source_df: pd.DataFrame, target_df: pd.DataFrame, tagged_fields: TaggedFields
):
    """For each pair of items that have the same `product_url_field` tagged field,
    compare `name_field` field"""

    result = Result("Compare Names Per Url")
    url_field = tagged_fields.get("product_url_field")
    name_field = tagged_fields.get("name_field")
    if not url_field or not name_field:
        result.add_info(Outcome.SKIPPED)
        return result

    name_field = name_field[0]
    url_field = url_field[0]
    diff_names_count = 0

    same_urls = source_df[(source_df[url_field].isin(target_df[url_field].values))][
        url_field
    ]

    detailed_messages = []
    for url in same_urls:
        if url.strip() != "nan":
            source_name = source_df[source_df[url_field] == url][name_field].iloc[0]
            target_name = target_df[target_df[url_field] == url][name_field].iloc[0]

            if (
                source_name != target_name
                and source_name.strip() != "nan"
                and target_name.strip() != "nan"
            ):
                diff_names_count += 1
                source_key = source_df[source_df[url_field] == url].index[0]
                target_key = target_df[target_df[url_field] == url].index[0]
                msg = (
                    f"different names for url: {url}\nsource name is {source_name} "
                    f"for {source_key}\ntarget name is {target_name} for {target_key}"
                )
                detailed_messages.append(msg)

    res = f"{len(same_urls)} checked, {diff_names_count} errors"
    if detailed_messages:
        result.add_error(res, detailed="\n".join(detailed_messages))
    else:
        result.add_info(res)

    return result


def compare_prices_for_same_names(
    source_df: pd.DataFrame, target_df: pd.DataFrame, tagged_fields: TaggedFields
):
    result = Result("Compare Prices For Same Names")
    name_field = tagged_fields.get("name_field")
    if not name_field:
        result.add_info(Outcome.SKIPPED)
        return result

    name_field = name_field[0]
    source_df = source_df[source_df[name_field].notnull()]
    target_df = target_df[target_df[name_field].notnull()]

    same_names = source_df[(source_df[name_field].isin(target_df[name_field].values))][
        name_field
    ]

    price_field = tagged_fields.get("product_price_field")
    if not price_field:
        result.add_info("product_price_field tag is not set")
        return result
    price_field = price_field[0]

    detailed_messages = []
    for name in same_names:
        if name.strip() != "nan":
            source_price = source_df[source_df[name_field] == name][price_field].iloc[0]
            target_price = target_df[target_df[name_field] == name][price_field].iloc[0]
            if is_number(source_price) and is_number(target_price):
                if ratio_diff(source_price, target_price) > 0.1:
                    source_key = source_df[source_df[name_field] == name].index[0]
                    target_key = target_df[target_df[name_field] == name].index[0]
                    msg = (
                        f"different price for {name}\nsource price is {source_price} "
                        f"for {source_key}\ntarget price is {target_price} for {target_key}"
                    )
                    detailed_messages.append(msg)

    result_msg = f"{len(same_names)} checked, {len(detailed_messages)} errors"
    if detailed_messages:
        result.add_error(result_msg, detailed="\n".join(detailed_messages))
    else:
        result.add_info(result_msg)

    return result
