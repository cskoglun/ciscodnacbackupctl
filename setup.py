from os import path
from setuptools import setup, find_packages
import ciscodnacbackupctl

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open(
    path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding="utf-8"
) as f:
    long_description = f.read()

setup(
    name="ciscodnacbackupctl",
    author=ciscodnacbackupctl.author,
    author_email=ciscodnacbackupctl.email,
    description=ciscodnacbackupctl.description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url=ciscodnacbackupctl.repo_url, TODO
    version=ciscodnacbackupctl.version,
    packages=find_packages(),
    py_modules=["ciscodnacbackupctl"],
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        ciscodnacbackupctl=ciscodnacbackupctl.cli:cli
    """,
    python_requires=">=3.8",
)
