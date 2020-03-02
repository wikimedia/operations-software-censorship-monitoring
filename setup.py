import os

from setuptools import find_packages, setup


current_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_path, "README.md")) as f:
    long_description = f.read()

extras_require = {
    "tests": [
        "coverage>=5.0.3",
        "flake8-import-order>=0.18.1"
    ],
}

install_requires = [
    "psycopg2-binary>=2.8.4",
    "Jinja2>=2.10.1",
    "requests>=2.22.0",
    "pyyaml>=5.3",
    "iso3166>=1.0.1",
]

setup(
    name="cescout",
    version="0.1.0",
    description="Censorship monitoring toolkit",
    long_description=long_description,
    url="https://github.com/wikimedia/censorship-monitoring/",
    author="Sukhbir Singh",
    author_email="ssingh@wikimedia.org",
    keywords=["censorship", "research", "ooni", "ioda", "ripe"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],

    packages=find_packages(exclude=("tests*",)),
    data_files=[
        ("/etc/cescout", ["config/cescout.cfg", "config/report.template"]),
    ],
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "cescout = cescout.main:run",
        ],
    },
)
