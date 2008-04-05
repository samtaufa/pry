from distutils.core import setup

long_description = """
A unit testing framework for Python.

Features
========

    * Built-in coverage analysis and profiling
    * Assertion-based tests - no ugly failUnless*, failIf*, etc. methods
    * Tree-based test structure for better fixture management
    * No implicit instantiation of test suits
    * Powerful command-line interface

Pry requires Python 2.5.2 or newer.
"""

version = "0.2.1"

setup(
        name = "pry",
        version = version,
        description = "A unit testing framework and coverage engine.",
        long_description = long_description,
        author = "Aldo Cortesi",
        author_email = "aldo@nullcube.com",
        url = "http://dev.nullcube.com",
        download_url="http://dev.nullcube.com/download/pry-%s.tar.gz"%version,
        packages = ["libpry"],
        scripts = ["pry"],
        classifiers = [
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Development Status :: 4 - Beta",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Testing",
            "Topic :: Software Development :: Quality Assurance",
        ]
)
