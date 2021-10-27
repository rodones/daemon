import importlib
import pathlib


def load(ignore=[]):
    for f in pathlib.Path(__file__).parent.glob("*.py"):
        if "__" not in f.stem and f.stem not in ignore:
            importlib.import_module(f".{f.stem}", __package__)
