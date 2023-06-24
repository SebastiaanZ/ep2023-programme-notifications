"""Placeholder for the first test."""
import importlib
import types


def test_package_can_be_imported() -> None:
    """Initial test that verifies that the package is installed."""
    assert isinstance(importlib.import_module("programme_notifier"), types.ModuleType)
