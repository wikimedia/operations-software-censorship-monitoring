import os

from setuptools import setup, find_packages


current_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_path, 'README.md')) as f:
    long_description = f.read()

setup(
    name='censorshipmonitoring',
    version='0.0.1',
    description='Scripts to monitor censorship',
    long_description=long_description,
    url='https://github.com/wikimedia/censorship-monitoring/',
    author='Sukhbir Singh',
    author_email='ssingh@wikimedia.org',
    keywords=['censorship', 'research', 'ooni', 'ioda'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],

    install_requires=[
        "psycopg2-binary>=2.8.4",
        "Jinja2>=2.10.1",
    ],
    packages=find_packages(exclude=("test*",)),
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'iodafetch = ioda.iodafetch:main',
            'oonifetch = ooni.oonifetch:main',
        ],
    },
)
