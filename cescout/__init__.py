from pkg_resources import get_distribution, DistributionNotFound

# This is from setuptools_scm.
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:    # pragma: no cover
    pass
