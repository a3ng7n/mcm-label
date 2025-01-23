import pathlib
from dataclasses import dataclass


@dataclass
class Part:
    pn: int
    name: str
    image: pathlib.Path


@dataclass
class Label:
    part: Part


@dataclass
class Order:
    filename: pathlib.Path
    parts: list[Part]
    labels: list[Label]


def main():
    print("main")
