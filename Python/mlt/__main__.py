#!/usr/bin/env python3

import argparse
import logging
import mlt


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="mlt",
        usage="mlt <command> <options>",
    )

    parser.add_argument("--version", action="version", version=mlt.__version__)
    parser.add_argument(
        "--debug",
        help="More verbose logging, and less file cleaning",
        action="store_true",
    )

    subparsers = parser.add_subparsers(title="Available commands", help="", metavar="")

    # ------------------------ download data -----------------------------------
    subparser_download_data = subparsers.add_parser(
        "download_data",
        help="Download reads",
        usage="mlt download_data [options] <samples_tsv> <outdir>",
        description="Download reads",
    )

    subparser_download_data.add_argument(
        "--cpus",
        help="Number of CPUs [%(default)s]",
        type=int,
        default=1,
        metavar="INT",
    )
    subparser_download_data.add_argument(
        "samples_tsv",
        help="TSV of sample info",
    )
    subparser_download_data.add_argument(
        "outdir",
        help="Output directory",
    )
    subparser_download_data.set_defaults(func=mlt.tasks.download_data.run)

    # ------------------------ run mykrobe -------------------------------------
    subparser_run_mykrobe = subparsers.add_parser(
        "run_mykrobe",
        help="Run mykrobe on each sample",
        usage="mlt run_mykrobe [options] <samples_tsv> <data_dir> <outdir>",
        description="Run mykrobe on each sample",
    )

    subparser_run_mykrobe.add_argument(
        "--panels_dir",
        help="Use specified panels_dir instead of mykrobes default",
        metavar="PATH",
    )
    subparser_run_mykrobe.add_argument(
        "--cpus",
        help="Number of CPUs [%(default)s]",
        type=int,
        default=1,
        metavar="INT",
    )
    subparser_run_mykrobe.add_argument(
        "samples_tsv",
        help="TSV of sample info",
    )
    subparser_run_mykrobe.add_argument(
        "data_dir",
        help="data directory (made by mlt download_data)",
    )
    subparser_run_mykrobe.add_argument(
        "outdir",
        help="Output directory",
    )
    subparser_run_mykrobe.set_defaults(func=mlt.tasks.run_mykrobe.run)

    # ------------------------ summary -----------------------------------------
    subparser_summary = subparsers.add_parser(
        "summary",
        help="Summarise results of species/lineage calls",
        usage="mlt summary [options] <samples_tsv> <data_dir> <mykrobe_dir> <outfile>",
        description="Summarise results of species/lineage calls",
    )

    subparser_summary.add_argument(
        "samples_tsv",
        help="TSV of sample info",
    )
    subparser_summary.add_argument(
        "data_dir",
        help="data directory (made by mlt download_data)",
    )
    subparser_summary.add_argument(
        "mykrobe_dir",
        help="Mykrobe results dir (made by mlt run_mykrobe)",
    )
    subparser_summary.add_argument(
        "outfile",
        help="output TSV file",
    )
    subparser_summary.set_defaults(func=mlt.tasks.summary.run)

    args = parser.parse_args()

    log = logging.getLogger()
    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
