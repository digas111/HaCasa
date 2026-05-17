import importlib
import sys
import types
from pathlib import Path


def import_generator_module(module_name):
    source_dir = Path(__file__).resolve().parents[2] / "HaCasa/custom_components/hacasa_generator"
    package_name = "hacasa_generator_under_test"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(source_dir)]
        sys.modules[package_name] = package
    return importlib.import_module(f"{package_name}.{module_name}")
