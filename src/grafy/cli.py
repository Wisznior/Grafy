"""Punkt wejscia: python -m grafy <zestaw> <komenda> [opcje].

Szkielet - kazda osoba dopisuje komende dla swojego zadania (parser + wywolanie modulu).
Jedna komenda na zadanie ulatwia demo na prezentacji.
"""
from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="grafy", description="Grafy i ich zastosowania - lab AGH")
    sub = parser.add_subparsers(dest="cmd")

    # --- zestaw 1 ---
    c = sub.add_parser("convert", help="Z1.1: konwersja reprezentacji")
    c.add_argument("input")
    c.add_argument("--from", dest="src", choices=["matrix", "list", "incidence"], required=True)
    # TODO: draw (Z1.2), gnl / gnp (Z1.3)
    # --- zestaw 2 --- TODO: graphic, randomize, components, euler, kregular, hamilton
    # --- zestaw 3 --- TODO: wgraph, dijkstra, distances, centers, mst
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0
    raise NotImplementedError(f"komenda '{args.cmd}' jeszcze nie podpieta")
