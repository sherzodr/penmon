import os
from setuptools import setup

setup(
    name="penmon",
    version="0.1.0",
    description="Implementation of Penman-Monteith equation to calculate ET for a reference crop",
    author="Sherzod RUZMETOV",
    author_email="sherzodr@gmail.com",
    license = "MIT",
    py_modules=["penmon.eto"],
    package_dir={'': 'src'},
    packages=["penmon"],
    keywords=[ "Penman-Monteith", "ET", "evapotranspiration", "plant water demand", "reference crop", "FAO 56" ])

