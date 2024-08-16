import argparse
import logging
import multiprocessing
import os
import re
import stat
import sys
import traceback

from afsal.aux.err import err_exit
from afsal.colors.AnsiColor import AnsiColor
from afsal.colors.print_colors import print_colors
from afsal.config.config import read_config_values
from afsal.multiprocessinglog.MultiprocessingLog import MultiprocessingLog
from afsal.term.color_caps import check_terminal_color_caps


def init():
    parser = argparse.ArgumentParser(description="Angry Fruit Salad v3.14")

    parser.add_argument("-c", "--printc", action="store_true",
            help="Print all possible colors for the given terminal and exit.")
    parser.add_argument("-p", "--nsubprocs", type=int,
            help="Number of processes that should be used for computation.")
    parser.add_argument("-n", "--dissubprocs", action="store_true",
            help="Disable the use of multiprocessing.")
    parser.add_argument("files", nargs="*", type=str,
            help="The file(s) to open. Opening more than one file leads to a concatenation of all files.")
    parser.add_argument("-r", "--regexpc", nargs=2, type=str, action="append",
            help="Regular expression to match for and the color and/or text attribute(s) to apply for that match.")
    parser.add_argument("-g", "--regexpcg", nargs=2, type=str, action="append",
            help="Global regular expression to match for and the color and/or text attribute(s) to apply for that match.")
    parser.add_argument("--glob", action="store_true",
            help="If enabled, all regular expressions used will be global.")
    parser.add_argument("-d", "--debug", action="store_true",
            help="Turn on debug output. This will suppress output of the processed text.")

    args = parser.parse_args()

    if args.debug:
        mpl = MultiprocessingLog("afsal-debug.log", mode="w+", maxsize=0, rotate=0)
        formatter = logging.Formatter("[%(asctime)s] %(processName)s: %(levelname)s: %(message)s")
        mpl.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(mpl)
        logger.setLevel(logging.DEBUG)

        # The global logger has now been set and can be used anywhere.
        logging.debug("Python version used: " + str(sys.version_info))
        logging.debug("sys.getdefaultencoding()=" + str(sys.getdefaultencoding()))
        logging.debug("args: " + str(args))

    term_nm_colors = check_terminal_color_caps()
    logging.debug("term_nm_colors=" + str(term_nm_colors))

    if args.printc:
        # Print the color possibilites for the given terminal and exit the program.
        try:
            print_colors(term_nm_colors)
        except Exception as e:
            err_exit(tb=traceback.format_exc())
        sys.exit(0)

    # Check if stdin is piped and if it is redirected.
    mode = os.fstat(0).st_mode
    stdin_is_piped, stdin_is_redirected = stat.S_ISFIFO(mode), stat.S_ISREG(mode)
    logging.debug("stdin_is_piped=" + str(stdin_is_piped))
    logging.debug("stdin_is_redirected=" + str(stdin_is_redirected))
    sys_stdin = stdin_is_piped or stdin_is_redirected
    # Check if stdout is redirected.
    stdout_is_redirected = not sys.stdout.isatty()
    logging.debug("stdout_is_redirected=" + str(stdout_is_redirected))

    # When not printing the color possibilities, stdin and/or file(s) and regexp(s) are needed as arguments.
    e = []
    if not args.files and not sys_stdin:
        e += ["file(s)"]
    if not args.regexpc:
        e += ["regular expression and color pair(s)"]
    if len(e) == 1:
        err_exit(msg="no " + e[0] + " provided as argument(s)\n", parser=parser)
    elif len(e) == 2:
        err_exit(msg="no " + e[0] + " and no " + e[1] + " provided as argument(s)\n", parser=parser)
    del e

    # Read values from the config file.
    config_values = read_config_values(os.path.expanduser("~") + "/.afsal", term_nm_colors)
    logging.debug("config_values: " + str(config_values))

    # Argument values override config values.
    nm_subprocs = args.nsubprocs if args.nsubprocs else config_values["NumberOfSubprocesses"]
    dis_subprocs = args.dissubprocs if args.dissubprocs else config_values["DisableSubprocesses"] == "True"

    # If the actual CPU count is 1, make sure that dis_subprocs is set to True.
    try:
        cpu_count = multiprocessing.cpu_count()
        logging.debug("cpu_count=" + str(cpu_count))
        if cpu_count == 1:
            logging.debug("cpu_count == 1 -> setting dis_subprocs to True")
            dis_subprocs = True
    except NotImplementedError:
        pass

    # Get any standard input directed to this program.
    f_data = []
    if sys_stdin:
        f_data = [line for line in sys.stdin]
    if f_data:
        logging.debug("Read " + str(len(f_data)) + " line(s) from sys.stdin")

    # If more than one file is given, concatenate them together in the sequence that they arrived.
    for f in args.files:
        f_data_prev_len = len(f_data)
        try:
            with open(f, 'r') as rf:
                f_data += [line for line in rf]
        except FileNotFoundError as e:
            err_exit(tb=traceback.format_exc())
        logging.debug("Read " + str(len(f_data) - f_data_prev_len) + " line(s) from file " + str(f))
    f_data_nm_lines = len(f_data)
    logging.debug("f_data_nm_lines=" + str(f_data_nm_lines))

    # If number of lines < numberOfLinesReqToEnableSubProcs, set number of processes to 1.
    if f_data_nm_lines < config_values["NumberOfLinesReqToEnableSubprocs"]:
        dis_subprocs = True
        logging.debug("f_data_nm_lines == " + str(f_data_nm_lines) + " < " + str(config_values["NumberOfLinesReqToEnableSubprocs"]) + " -> setting dis_subprocs to True")


    def __construct_regexpcs(r, glob):
        for e in r:
            ansi_color = None
            try:
                ansi_color = AnsiColor(term_nm_colors, e[1])
            except Exception as ex:
                err_exit(msg="\"" + str(e[1]) + "\" could not be converted to ANSI color code (\"" + str(ex) + "\")", tb=traceback.format_exc())
            try:
                regexpcs.append( (re.compile(e[0]), glob, ansi_color) )
            except re.error as ex:
                err_exit(msg="\"" + str(e[0]) + "\" is not a valid regular expression (\"" + str(ex) + "\")", tb=traceback.format_exc())


    # Create tuple list with tuples of the form (compiled regexp, global regexp, (color of match, fg/bg)).
    logging.debug("Compiling regular expressions: " + str(args.regexpc))
    regexpcs = []
    __construct_regexpcs(args.regexpc, False)
    __construct_regexpcs(args.regexpcg, True)

    use_glob_regexps = args.glob

    return term_nm_colors, f_data, f_data_nm_lines, regexpcs, use_glob_regexps, nm_subprocs, dis_subprocs, stdout_is_redirected
