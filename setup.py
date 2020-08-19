from setuptools import setup, find_packages
from ngi_reports import __version__
import sys, os


try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(
    name='ngi_reports',
    version=__version__,
    description="Report generation for NGI Sweden",
    long_description='This package is used to generate different types of '
                   'reports for the NGI Stockholm node.',
    keywords='bioinformatics',
    author='Phil Ewels',
    author_email='phil.ewels@scilifelab.se',
    url='https://github.com/NationalGenomicsInfrastructure/ngi_reports',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["ngi_reports=ngi_reports.ngi_reports:main"]},
    install_requires=install_requires
)
