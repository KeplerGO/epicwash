"""Prevents new K2 EPIC catalogs from containing duplicate entries."""
import os
import re
import argparse
import logging

logging.basicConfig(level=logging.INFO)

# How to execute java on the command line?
JAVA = "nice java -XX:+UseConcMarkSweepGC -Xmx2000m"

# Where is stilts.jar?
PACKAGEDIR = os.path.dirname(os.path.abspath(__file__))
STILTS = os.path.join(PACKAGEDIR, "lib", "stilts.jar")

# Where to store temporary data?
TMPDIR = "/tmp"


def syscall(cmd, silent=False):
    """Calls a system command and returns its status."""
    logging.debug(cmd)
    status = os.system(cmd)
    if status != 0 and not silent:
        logging.error("System call returned {}\n"
                  "command was: {}".format(status, cmd))
    return status


def convert_to_csv(input_fn, output_fn):
    """Converts a file from pipe-delimited to comma-delimited."""
    syscall("""sed "s/|/,/g" {0} > {1}""".format(input_fn, output_fn))


def remove_duplicates(input_fn, output_fn, matching_radius=0.1):
    """Removes any source appearing more than once at the same position."""
    cfg = {
            "java": JAVA,
            "stilts": STILTS,
            "input_fn": input_fn,
            "output_fn": output_fn,
            "matching_radius": matching_radius
           }
    cmd = """{java} -jar {stilts} tmatch1 \
             in={input_fn} ifmt=csv \
             matcher=sky params={matching_radius} \
             values="col10 col11" \
             action=keep1 out={output_fn} ofmt=csv""".format(**cfg)
    # silent because "no duplicates" returns error code
    status = syscall(cmd, silent=True)
    if status != 0:
        syscall("cp {input_fn} {output_fn}".format(**cfg))


def remove_existing_epic_sources(input_fn, output_fn, epic_fn,
                                 matching_radius=0.1):
    cfg = {
            "java": JAVA,
            "stilts": STILTS,
            "input_fn": input_fn,
            "output_fn": output_fn,
            "epic_fn": epic_fn,
            "matching_radius":  matching_radius
           }
    cmd = """{java} -jar {stilts} tmatch2 \
             in1={input_fn} ifmt1=csv \
             in2={epic_fn} ifmt2=fits \
             matcher=sky params={matching_radius} \
             values1="col10 col11" values2="col1 col2" \
             join=1not2 out={output_fn} ofmt=csv""".format(**cfg)
    syscall(cmd)


def assign_epicids(input_fn, output_fn):
    """Assigns EPIC IDs to each row in the catalog.

    This is pretty memory intense at present :-(
    """
    # Open the input
    logging.info("Opening {}".format(input_fn))
    infile = open(input_fn, "r")
    # Open the output
    logging.info("Writing {}".format(output_fn))
    outfile = open(output_fn, "w")
    # Start numbering!
    epic_id = EPIC_START
    for line in infile.readlines():
        # We assume that the EPIC ID is the first column
        # in a pipe-delimited csv file
        outfile.write(re.sub("^.[^,]*", str(epic_id), line))
        epic_id += 1
    # Clean up
    outfile.close()
    infile.close()


def convert_to_dmc(input_fn, output_fn):
    """Convert from csv to pipe-delimited."""
    syscall("""sed "s/,/|/g" {} > {}""".format(input_fn, output_fn))


def epicwash(input_fn, output_fn=None, epic_fn=None, matching_radius=0.1):
    """Main function to carry out the wasching task."""
    if output_fn is None:
        output_fn = input_fn + ".epicwash"

    logging.info("Converting the DMC file into CSV format.")
    csv_fn = os.path.join(TMPDIR, "epicwash.csv")
    convert_to_csv(input_fn, csv_fn)

    logging.info("Removing duplicate entries from the input DMC file.")
    csv_nodupes_fn = csv_fn + ".nodupes"
    remove_duplicates(csv_fn, csv_nodupes_fn, matching_radius=matching_radius)

    if epic_fn is not None:
        logging.info("Removing objects that pre-exist in {}.".format(epic_fn))
        csv_noepic_fn = csv_nodupes_fn + ".noepic"
        remove_existing_epic_sources(input_fn=csv_nodupes_fn,
                                     output_fn=csv_noepic_fn,
                                     epic_fn=epic_fn,
                                     matching_radius=matching_radius)
    else:
        csv_noepic_fn = csv_nodupes_fn

    logging.info("Writing {}".format(output_fn))
    convert_to_dmc(input_fn=csv_noepic_fn, output_fn=output_fn)

    logging.info("Cleaning up temporary files.")
    os.remove(csv_fn)
    os.remove(csv_nodupes_fn)
    if epic_fn is not None:
        os.remove(csv_noepic_fn)


def epicwash_main(args=None):
    """Exposes the epicwash() function to the command line using argparse."""
    parser = argparse.ArgumentParser(
                    description="Removes duplicate or pre-existing entries "
                                "from a new EPIC catalog.")
    parser.add_argument('-o', '--output', metavar='FILENAME',
                        type=str, default=None,
                        help="output filename, defaults to the input path "
                             "with the '.epicwash' suffix added.")
    parser.add_argument('-m', '--matching-radius',
                        type=float, default=0.1,
                        help="cross-matching distance in arcsec "
                             "(default: 0.1)")
    parser.add_argument('-e', '--epic', metavar='FITSFILE',
                        type=str, default=None,
                        help="FITS table containing coordinates of pre-existing "
                             "EPIC entries in col1 (ra) and col2 (dec)")
    parser.add_argument('filename',
                        help='path to a new EPIC catalog in DMC format')
    args = parser.parse_args(args)

    epicwash(input_fn=args.filename,
             output_fn=args.output,
             epic_fn=args.epic,
             matching_radius=args.matching_radius)


def epicwash_prepare(inputfiles, output_fn, matching_radius=0.1):
    """Extract ra/dec from a set of EPIC catalogs and write them to FITS."""
    if inputfiles[0].endswith("gz"):
        mycat = "zcat"
    else:
        mycat = "cat"
    tmp_csv_fn = os.path.join(TMPDIR, "epicwash-prepare-tmp.csv")
    tmp_fits_fn = os.path.join(TMPDIR, "epicwash-prepare-tmp.fits")

    logging.info("Extracting ra & dec from {} catalog files.".format(len(inputfiles)))
    cmd = """{} {} | csvcut -d"|" -c 10,11 > {}""".format(mycat,
                                                          " ".join(inputfiles),
                                                          tmp_csv_fn)
    syscall(cmd, silent=True)

    logging.info("Converting to a binary FITS table.")
    cfg = {
            "java": JAVA,
            "stilts": STILTS,
            "input_fn": tmp_csv_fn,
            "output_fn": tmp_fits_fn
           }
    cmd = """{java} -jar {stilts} tcopy \
             ifmt=csv ofmt=fits \
             {input_fn} {output_fn}""".format(**cfg)
    syscall(cmd)

    logging.info("Removing duplicates from the binary FITS table.")
    cfg = {
            "java": JAVA,
            "stilts": STILTS,
            "input_fn": tmp_fits_fn,
            "output_fn": output_fn,
            "matching_radius": matching_radius
           }
    cmd = """{java} -jar {stilts} tmatch1 \
             in={input_fn} ifmt=fits \
             matcher=sky params={matching_radius} \
             values="col1 col2" \
             action=keep1 out={output_fn} ofmt=fits""".format(**cfg)
    # silent because "no duplicates" returns error code
    status = syscall(cmd, silent=True)
    if status != 0:
        syscall("cp {input_fn} {output_fn}".format(**cfg))

    logging.info("Processing finished. Output saved as {}.".format(output_fn))
    # Clean up
    os.remove(tmp_csv_fn)
    os.remove(tmp_fits_fn)


def epicwash_prepare_main(args=None):
    """Exposes the epicwash_prepare() function to the command line."""
    parser = argparse.ArgumentParser(
                    description="Extract ra & dec from a set of EPIC catalogs "
                                "and write them to a FITS table. "
                                "Such a table can then be used as input "
                                "for the `epicwash` command.")
    parser.add_argument('-o', '--output', metavar='FILENAME',
                        type=str, default="epic.fits",
                        help="output filename (default: epic.fits)")
    parser.add_argument('-m', '--matching-radius',
                        type=float, default=0.1,
                        help="cross-matching distance in arcsec "
                             "(default: 0.1)")
    parser.add_argument('filename', nargs="+",
                        help='EPIC catalog in DMC format')
    args = parser.parse_args(args)

    epicwash_prepare(inputfiles=args.filename,
                     output_fn=args.output,
                     matching_radius=args.matching_radius)


if __name__ == "__main__":
    epicwash_main()
