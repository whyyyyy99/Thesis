import typing
import polars as pl


def __convert_index_to_uid(
    self, index: int | list[int], axis: typing.Literal["row", "column"] = "row"
):
    if isinstance(index, int):
        index = [index]
    lookup = self.get_lookup()
    if axis == "row":
        uids = [
            lookup.filter(pl.col("row_index") == id).select("uid").to_series().to_list()[0]
            for id in index
        ]
    elif axis == "column":
        uids = [
            lookup.filter(pl.col("column_index") == id)
            .select("uid")
            .to_series()
            .to_list()[0]
            for id in index
        ]
    else:
        raise ValueError('The axis must be either "row" or "column".')
    return uids


def __convert_index_to_bodyid(self, index, axis="row"):
    if isinstance(index, int):
        index = [index]
    lookup = self.get_lookup()
    if axis == "row":
        body_ids = [
            lookup.filter(pl.col("row_index") == id)
            .select("body_id")
            .to_series()
            .to_list()[0]
            for id in index
        ]
    elif axis == "column":
        body_ids = [
            lookup.filter(pl.col("column_index") == id)
            .select("body_id")
            .to_series()
            .to_list()[0]
            for id in index
        ]
    else:
        raise ValueError('The axis must be either "row" or "column".')
    return body_ids


def __get_uids_from_bodyids(self, body_ids: list[BodyId] | list[int]) -> list[UID]:
    lookup = self.get_lookup().clone()
    lookup = lookup.filter(pl.col("body_id").is_in(body_ids))
    missing = set(body_ids) - set(lookup["body_id"].to_list())
    if len(missing) > 0:
        print(f"Warning: {len(missing)} body ids not found.")
    uids = lookup["uid"].to_list()
    return uids
