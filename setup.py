from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="penmon",
    version="1.5",
    author="Sherzod RUZMETOV",
    author_email="sherzodr@gmail.com",
    description="Implementation of weather station that calculates daily ETo for a reference crop using Penman-Monteith equation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sherzodr/penmon",
    download_url="https://github.com/sherzodr/penmon/archive/1.5.tar.gz",
    license="MIT",
    keywords="Penman-Monteith, ET, evapotranspiration, plant water demand, reference crop, FAO 56 , ETo",
    project_urls={
        "Bug Tracker": "https://github.com/sherzodr/penmon/issues"
    },
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    python_requires=">=3.6",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)