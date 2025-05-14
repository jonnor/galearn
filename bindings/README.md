
# Python module

## Prerequisites

The following packages are needed.
Install with pip or via OS package manager.

    pybind11
    numpy
    setuptools
    soundfile
    matplotlib

Debian:
    apt install python3-pybind11 python3-numpy python3-setuptools python3-soundfile python3-matplotlib

## Building

To build the module

    python setup.py build_ext --inplace

This will produce a shared library (`.so` on Linux) in PWD, that Python can load.

## Test

To use the module, see the .py file

    python test_galearn_pdm.py


