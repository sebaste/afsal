#!/usr/bin/env python3


import sys
if sys.version_info < (3, 0):
    sys.stderr.write("ERROR: Python 2.x is not supported - Python >= 3.0 required\n")
    sys.exit(1)


import logging
import traceback

from afsal.init import init


def main():
    try:
        term_nm_colors, f_data, f_data_nm_lines, regexpcs, use_glob_regexps, nm_subprocs, dis_subprocs, stdout_is_redirected = init()

        final_str = None

        if not dis_subprocs:
            from afsal.main_subprocs import start_with_subprocs
            logging.debug("Using subprocesses -> starting subprocesses")
            final_str = start_with_subprocs(f_data, f_data_nm_lines, regexpcs, use_glob_regexps, stdout_is_redirected, nm_subprocs)
        else:
            from afsal.main_nosubprocs import start_without_subprocs
            logging.debug("Not using subprocesses -> starting without subprocesses")
            final_str = start_without_subprocs(f_data, f_data_nm_lines, regexpcs, use_glob_regexps, stdout_is_redirected)

        # End by writing all lines in the processed text to stdout.
        # If debugging, printing is suppressed.
        if logging.getLogger().getEffectiveLevel() != 10:
            sys.stdout.write(final_str)
        else:
            logging.debug("(Writing all processed lines to stdout here)")

    except Exception as e:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
