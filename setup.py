import os
from setuptools import setup

setup(
    name="penmon",
    version="0.2.0",
    description="Implementation of Penman-Monteith equation to calculate ET for a reference crop",
    # long_description_content_type="text/markdown",
    # long_description=long_description,
    author="Sherzod RUZMETOV",
    author_email="sherzodr@gmail.com",
    license="MIT",
    url="https://github.com/sherzodr/penmon",
    download_url="https://github.com/sherzodr/penmon/archive/0.2.0.tar.gz",
    py_modules=["penmon.eto"],
    package_dir={'': 'src'},
    packages=["penmon"],
    keywords=[ "Penman-Monteith", "ET", "evapotranspiration", "plant water demand", "reference crop", "FAO 56" ],
    python_required='>=3.6',
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Hydrology",
        "Topic :: Scientific/Engineering :: Atmospheric Science"
        ]
    )

