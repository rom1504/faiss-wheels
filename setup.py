from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_py import build_py
import sys
import os
import numpy as np

NAME = 'faiss-cpu-noavx2'

LONG_DESCRIPTION = """
Faiss is a library for efficient similarity search and clustering of dense
vectors. It contains algorithms that search in sets of vectors of any size, up
to ones that possibly do not fit in RAM. It also contains supporting code for
evaluation and parameter tuning. Faiss is written in C++ with complete wrappers
for Python/numpy. It is developed by Facebook AI Research.
"""

FAISS_INCLUDE = os.getenv('FAISS_INCLUDE', '/usr/local/include')
FAISS_LDFLAGS = os.getenv('FAISS_LDFLAGS', '-L/usr/local/lib -lfaiss')

INCLUDE_DIRS = [np.get_include(), FAISS_INCLUDE]
LIBRARY_DIRS = []
EXTRA_COMPILE_ARGS = [
    '-std=c++11', '-msse4', '-mpopcnt', '-m64', '-Wno-sign-compare', '-fopenmp',
]
EXTRA_LINK_ARGS = ['-fopenmp'] + FAISS_LDFLAGS.split()
SWIG_OPTS = ['-c++', '-Doverride=', '-I' + FAISS_INCLUDE]

if os.getenv('ENABLE_AVX2'):
    EXTRA_COMPILE_ARGS += ['-mavx2', '-mf16c']

if os.getenv('ENABLE_CUDA'):
    NAME = 'faiss-gpu'
    CUDA_HOME = os.getenv('CUDA_HOME', '/usr/local/cuda')
    INCLUDE_DIRS += [CUDA_HOME + '/include']
    LIBRARY_DIRS += [CUDA_HOME + '/lib64']
    SWIG_OPTS += ['-I' + CUDA_HOME + '/include', '-DGPU_WRAPPER']

if sys.platform == 'linux':
    EXTRA_COMPILE_ARGS += ['-fdata-sections', '-ffunction-sections']
    EXTRA_LINK_ARGS += ['-s', '-Wl,--gc-sections']
    SWIG_OPTS += ['-DSWIGWORDSIZE64']
elif sys.platform == 'darwin':
    EXTRA_LINK_ARGS += ['-dead_strip']


class CustomBuildPy(build_py):
    def run(self):
        self.run_command("build_ext")
        return build_py.run(self)


_swigfaiss = Extension(
    'faiss._swigfaiss',
    sources=['faiss/python/swigfaiss.i'],
    define_macros=[('FINTEGER', 'int')],
    language='c++',
    include_dirs=INCLUDE_DIRS,
    library_dirs=LIBRARY_DIRS,
    extra_compile_args=EXTRA_COMPILE_ARGS,
    extra_link_args=EXTRA_LINK_ARGS,
    swig_opts=SWIG_OPTS,
)


setup(
    name=NAME,
    version='1.6.3',
    description=(
        'A library for efficient similarity search and clustering of dense '
        'vectors.'
    ),
    long_description=LONG_DESCRIPTION,
    url='https://github.com/kyamagu/faiss-wheels',
    author='Kota Yamaguchi',
    author_email='KotaYamaguchi1984@gmail.com',
    license='MIT',
    keywords='search nearest neighbors',
    setup_requires=['numpy'],
    package_dir={'faiss': 'faiss/python'},
    packages=['faiss'],
    ext_modules=[_swigfaiss],
    cmdclass={'build_py': CustomBuildPy},
)
