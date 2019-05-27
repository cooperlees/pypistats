# pypistats

**No longer maintained:** This package is no longer maintained as the PyPI Stats endpoint was not rebuilt in Warehouse. Instead, see the [Analyzing PyPI package downloads](https://packaging.python.org/guides/analyzing-pypi-package-downloads/) page.

Client to parse out stats from PyPI Stats endpoint

Simple CLI to today can:
- generate Human readable from the raw bytes
- generate bandersnatch (https://github.com/pypa/bandersnatch) backlist ini formatted output

## Usage:

```
# Human Readable Output
pypi_stats

# Bandersnatch Blacklist Format
pypi_stats --bandersnatch-ini
```
