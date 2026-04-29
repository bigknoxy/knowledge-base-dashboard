from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("knowledge-base-dashboard")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"
