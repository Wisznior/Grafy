from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "examples"


def read_int_matrix(path):
    return [[int(x) for x in l.split()] for l in path.read_text().splitlines()
            if l.strip() and not l.startswith("#")]