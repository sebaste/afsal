import sys

from afsal.aux.inclrange import range_incl, range_incl_s
from afsal.colors.AnsiEscapeCode import AnsiEscapeCode


def __print_prefixes():
    sys.stdout.write("\nPrefixes:\n  " +
            "'b': \x1b[1mbold\x1b[0m, " +
            "'d': \x1b[2mdim\x1b[0m, " +
            "'i': \x1b[3mitalic\x1b[0m, " +
            "'u': \x1b[4munderlined\x1b[0m\n\n")


# Print all possible color values for the given terminal.
# The values printed are stated as integers and not ANSI color strings ("38;5;128", etc),
# in order to increase the simplicity for the user.
def print_colors(term_nm_colors):
    if term_nm_colors == 0:
        raise Exception("terminal has 0 color capabilities - nothing to print")
    elif term_nm_colors == 8:
        __print_prefixes()

        for fgbg in range_incl(3, 4):
            for normalbold in range_incl(0, 1):
                for color in range_incl(0, 7):
                    sys.stdout.write(
                            # Color coding.
                            AnsiEscapeCode.START + str(normalbold) + ";" + str(fgbg) + str(color) + "m " +
                            # Text to print.
                            str(color + (8 if normalbold else 0) + (16 if fgbg == 4 else 0)) + "\t" + AnsiEscapeCode.END + "\n")
    elif term_nm_colors == 256:
        __print_prefixes()

        for fgbg in [38, 48]:
            for i in range_incl_s(0, 248, 8):
                color_row = []
                for j in range_incl(0, 7):
                    sys.stdout.write(
                            # Color coding.
                            AnsiEscapeCode.START + str(fgbg) + ";5;" + str(i + j) + "m" +
                            # Text to print (format columns to be of the same width).
                            "{0:<8}".format(str(i + j + (256 if fgbg == 48 else 0))) + AnsiEscapeCode.END)
                sys.stdout.write("\n")
    else:
        raise Exception("terminal color capabilities value " + str(term_nm_colors) + " is not recognized - cannot print colors")
