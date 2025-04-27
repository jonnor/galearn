from setuptools import setup, Extension
import pybind11
import numpy

ext_modules = [
    Extension(
        'galearn_pdm',
        ['galearn_pdm.cpp'],
        include_dirs=[
            pybind11.get_include(),
            numpy.get_include(),
        ],
        language='c++',
    ),
]

setup(
    name='galearn',
    version='0.0.1',
    ext_modules=ext_modules,
    zip_safe=False,
)
