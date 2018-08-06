#!/usr/bin/env python3

from setuptools import setup
from sys import version_info


assert version_info >= (3, 6, 0), f" pypistats requires >= Python 3.6"


setup(
    name="pypistats",
    version="18.8.5",
    description=("Client to use PyPI stats"),
    py_modules=["pypistats"],
    url="http://github.com/cooperlees/pypistats",
    author="Cooper Lees",
    author_email="me@cooperlees.com",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 3 - Alpha",
    ),
    python_requires=">=3.6",
    install_requires=["aiohttp", "beautifulsoup4", "click", "humanfriendly"],
    tests_require=["testing-aiohttp"],
    entry_points={"console_scripts": ["pypi_stats = pypistats:main"]},
    test_suite="pypistats_test",
)
