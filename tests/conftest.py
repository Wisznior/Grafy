from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data" / "examples"

# Dopoki modul jest stubem -> xfail. Po implementacji usun dekorator z danego testu.
todo = pytest.mark.xfail(raises=NotImplementedError, reason="do zaimplementowania")


def read_int_matrix(path: Path) -> list[list[int]]:
    return [[int(x) for x in line.split()] for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")]
