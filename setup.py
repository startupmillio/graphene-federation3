import ast
import os
import re
from datetime import datetime

from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("graphene_federation3/__init__.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )
    version += f".{int(datetime.now().timestamp())}"

setup(
    name="graphene-federation3",
    packages=["graphene_federation3"],
    version=version,
    license="MIT",
    description="Federation implementation for graphene3",
    long_description=(read("README.md")),
    long_description_content_type="text/markdown",
    author="Yorsh Siarhei",
    author_email="myrik260138@gmail.com",
    url="https://gitlab.com/live-art-project/graphene-federation3",
    keywords=["graphene", "gql", "federation"],
    install_requires=["graphene>=3"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
    ],
)
