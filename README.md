# K2 EPIC Catalog Washer

***Prevents K2 EPIC catalogues from containing pre-existing or duplicate entries.***

This Python module adds three tools to the command line,
`epicwash`, `epicwash-prepare`, and `epicwash-renumber`,
that allow pre-existing or duplicate entries to be removed
from new K2 EPIC catalogs, and renumber the EPIC IDs of the others.

This repository is unlikely to be of any interest to you,
unless you are the soul in charge of producing the EPIC catalog
for a new K2 Campaign!

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
The `setup.py` script will automatically take care of installing two required dependencies (`stilts` and `csvkit`).

## Example usage

The following steps demonstrate how to *wash* the K2 EPIC Campaign 12 catalog,
starting from the original catalog file produced by the EPIC IDL code
which we call `c12.dmc.dat` in this example.

Because C12 overlaps with C3, we first need to create a special binary table
that contains all the coordinates of sources previously added to the C3 EPIC catalog.
This is done on the command line using the `epicwash-prepare` tool as follows:

```
$ epicwash-prepare --output epic.fits d14273_01_epic_c3_dmc.mrg.gz d1497_01_epic_c23_dmc.mrg.gz
```

... where the *.gz files are the EPIC catalog files [obtained from MAST](https://archive.stsci.edu/pub/k2/catalogs/) that overlap with C12, and `epic.fits` is the name of the binary table that the tool will produce.

Next, we use this newly-created `epic.fits` file to remove overlapping sources from `c12.dmc.dat` using the `epicwash` command.:

```
$ epicwash --epic epic.fits --output c12-fixed.dmc.dat c12.dmc.dat
```

This produces the file `c12-fixed.dmc.dat`, which should not contain
any duplicates.

Finally, we use the `epicwash-renumber` command to re-assign the EPIC IDs
from a given EPIC ID starting point, e.g. 24589908:

```
$ epicwash-renumber --output c12-fixed-and-renumbered.dmc.dat c12-fixed.dmc.dat 24589908
```

Next step: party, we're done!


## Documentation

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

`epicwash-renumber` is used as follows:
```
epicwash-renumber --help
usage: epicwash-renumber [-h] [-o FILENAME] filename epicid

Assigns new EPIC IDs to all catalog entries.

positional arguments:
  filename              EPIC catalog in DMC format
  epicid                Desired EPIC ID of the first entry.

optional arguments:
  -h, --help            show this help message and exit
  -o FILENAME, --output FILENAME
                        output filename. Adds suffix '-renumbered' by default.
```
