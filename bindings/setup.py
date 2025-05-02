from setuptools import setup, Extension
import pybind11
import numpy
import os.path

verilated_build_dir = '../verilator_lib/obj_dir/'

ext_modules = [
    Extension(
        'galearn_pdm',
        sources=[
            'galearn_pdm.cpp',
        ],
        include_dirs=[
            pybind11.get_include(),
            numpy.get_include(),
            verilated_build_dir,
        ],
        extra_objects=[
            os.path.join(verilated_build_dir, 'libsim.so')
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
