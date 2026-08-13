import typing
from typing import Optional

import polars as pl


def get_uids(
    self,
    sub_indices: Optional[list[int]] = None,
    axis: typing.Literal["row", "column"] = "row",
) -> list:
    if sub_indices is None:
        if axis == "row":
            self.lookup = self.lookup.sort(by="row_index")
        elif axis == "column":
            self.lookup = self.lookup.sort(by="column_index")
        return self.lookup["uid"].to_list()
    return self.__convert_index_to_uid(sub_indices, axis=axis)


def get_row_indices(
    self,
    sub_uid: Optional[list] = None,
    allow_empty: bool = True,
    input_type: typing.Literal["uid", "body_id"] = "uid",
) -> list:
    if sub_uid is None:
        self.lookup = self.lookup.sort(by="row_index")
        return self.lookup["row_index"].to_list()

    if input_type == "body_id":
        sub_uid = self.__get_uids_from_bodyids(sub_uid)
    rows, _ = self.__convert_uid_to_index(sub_uid, allow_empty=allow_empty)
    if not allow_empty and len(rows) != len(sub_uid):
        raise ValueError("Some row body ids found only in the columns.")
    return rows


def get_column_indices(
    self,
    sub_uid: Optional[list] = None,
    allow_empty: bool = True,
    input_type: typing.Literal["uid", "body_id"] = "uid",
) -> list:
    if sub_uid is None:
        self.lookup = self.lookup.sort(by="column_index")
        return self.lookup["column_index"].to_list()
    if input_type == "body_id":
        sub_uid = self.__get_uids_from_bodyids(sub_uid)
    _, columns = self.__convert_uid_to_index(sub_uid, allow_empty=allow_empty)
    if not allow_empty and len(columns) != len(sub_uid):
        raise ValueError("Some row body ids found only in the columns.")
    return columns
