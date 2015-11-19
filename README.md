# K2 EPIC Catalog Washer

***Prevents K2 EPIC catalogues from containing pre-existing or duplicate entries.***

This Python module adds two tools to the command line,
`epicwash` and `epicwash-prepare`, that allow pre-existing
or duplicate entries to be removed from new K2 EPIC catalogs.

## Installation

This tool requires a Linux-like system
with `java` and `sed` available on the command line,
and a working `python` installation.

If these requirements are met, you can install the tool from this git repository as follows:
```
$ git clone https://github.com/KeplerGO/epicwash.git
$ cd epicwash
$ python setup.py install
```

## Example usage

The following steps demonstrate how to *wash* the K2 EPIC Campaign 12 catalog,
starting from the original catalog file produced by the EPIC IDL code,
which we will call `c12.dmc.dat`.

Because C12 overlaps with C3, we need to create a special table
that lists all the coordinates of sources already added to the EPIC catalog for C3.
This is done using the `epicwash-prepare` tool as follows:

```
$ epicwash-prepare --output epic.fits d14273_01_epic_c3_dmc.mrg.gz d1497_01_epic_c23_dmc.mrg.gz
```

... where the *.gz files are the EPIC catalog files [obtained from MAST](https://archive.stsci.edu/pub/k2/catalogs/) that overlap with C12, and `epic.fits` is the name of the binary table that the tool will produce.

Next, we use the `epicwash` command to take our `c12.dmc.dat` file
and remove any sources that already appear in `epic.fits`:

```
epicwash --epic epic.fits --output c11-fixed.dmc.dat c11.dmc.dat
```

This produces the file `c11-fixed.dmc.dat`, which should not contain
any duplicates.

Next step: party, we're done!


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
