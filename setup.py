from setuptools import setup, find_packages
from ngi_reports import __version__
import sys, os


try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

try:
    with open("dependency_links.txt", "r") as f:
        dependency_links = [x.strip() for x in f.readlines()]
except IOError:
    dependency_links = []

setup(
    name='ngi_reports',
    version=__version__,
    description="Report generation for NGI Sweden",
    long_description='This package is used to generate different types of '
                   'reports for both the NGI Stockholm and Uppsala nodes.',
    keywords='bioinformatics',
    author='Phil Ewels',
    author_email='phil.ewels@scilifelab.se',
    url='https://portal.scilifelab.se/genomics/',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    scripts=['scripts/ngi_reports'],
    install_requires=install_requires,
    dependency_links=dependency_links
)
