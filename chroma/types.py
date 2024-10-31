from pathlib import Path
from typing import Literal, Optional

Number = float | int

ColorFormat = Literal["hex"] | Literal["hexval"] | Literal["rgb"] | Literal["hsl"]

ColorTuple = tuple[Number, Number, Number]

ColorType = str | ColorTuple

FilePath = str | Path

HSLMapField = Optional[tuple[int, int] | list[tuple[int, int]]]
HSLMapValue = tuple[HSLMapField, HSLMapField, HSLMapField]
HSLMap = dict[str, HSLMapValue]
