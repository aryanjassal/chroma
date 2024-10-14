from pathlib import Path
from typing import Literal

Number = float | int

ColorFormat = Literal["hex"] | Literal["hexval"] | Literal["rgb"] | Literal["hsl"]

ColorTuple = tuple[Number, Number, Number]

ColorType = str | ColorTuple

FilePath = str | Path
