# K2 EPIC Catalog Washer

***Prevents K2 EPIC catalogues from containing pre-existing or duplicate entries."""

This Python module adds to tools to the command line,
`epicwash` and `epicwash-prepare`, that allow pre-existing
or duplicate entries to be removed from new K2 EPIC catalogs.

## Requirements

This tool will only work on a Linux-like system
with `sed` and `java` installed.

## Installation

```
$ git clone https://github.com/KeplerGO/epicwash.git
$ cd epicwash
$ python setup.py install
```

## Example usage

The following steps demonstrate how to remove pre-existing and duplicate
entries from the EPIC Campaign 11 catalog.

Because C11 overlaps with C3, we first need to use `epicwash-prepare` to
create a table that contains all the coordinates of sources that were previously added to the EPIC catalog for C3.
Such a table can be prepared as follows:

```
$ epicwash-prepare d14273_01_epic_c3_dmc.mrg.gz d1497_01_epic_c23_dmc.mrg.gz
```

This commands creates a binary FITS table called `epic.fits`.

Next, we use the `epicwash` command to remove any duplicates,
or any sources already appearing in `epic.fits`, as follows:

```
epicwash c11.dmc.dat -e ../../mast/epic.fits
```

This produces the file `c11.dmc.dat.epicwash`, representing the
cleaned-up catalog in DMC format.


## Documentation

`epicwash` is used as follows:
```
$ epicwash --help
usage: epicwash [-h] [-o FILENAME] [-m MATCHING_RADIUS] [-e FITSFILE] filename

Removes duplicate or pre-existing entries from a new EPIC catalog.

positional arguments:
  filename              path to a new EPIC catalog in DMC format

optional arguments:
  -h, --help            show this help message and exit
  -o FILENAME, --output FILENAME
                        output filename, defaults to the input path with the
                        '.epicwash' suffix added.
  -m MATCHING_RADIUS, --matching-radius MATCHING_RADIUS
                        cross-matching distance in arcsec (default: 0.05)
  -e FITSFILE, --epic FITSFILE
                        FITS table containing coordinates of pre-existing EPIC
                        entries in col1 (ra) and col2 (dec)
```

`epicwash-prepare` is used as follows:
```
$ epicwash-prepare --help
usage: epicwash-prepare [-h] [-o FILENAME] [-m MATCHING_RADIUS]
                        filename [filename ...]

Extract ra & dec from a set of EPIC catalogs and write them to a FITS table.
Such a table can then be used as input for the `epicwash` command.

positional arguments:
  filename              EPIC catalog in DMC format

optional arguments:
  -h, --help            show this help message and exit
  -o FILENAME, --output FILENAME
                        output filename (default: epic.fits)
  -m MATCHING_RADIUS, --matching-radius MATCHING_RADIUS
                        cross-matching distance in arcsec (default: 0.05)
```
