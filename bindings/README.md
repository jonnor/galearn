
# Python module

## Prerequisites

The following packages are needed.
Install with pip or via OS package manager.

    pybind11
    numpy
    setuptools


## Building

To build the module

    python setup.py build_ext --inplace

This will produce a shared library (`.so` on Linux) in PWD, that Python can load.

## Test

To use the module, see the .py file

    python test_galearn_pdm.py


