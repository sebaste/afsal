import re

from afsal.colors.AnsiEscapeCode import AnsiEscapeCode


# Find the regular expression matches in a string and sort the matches based on their index/position
# in the string. Then, if there are any matches, create and return an altered line by inserting the
# correct ANSI escape codes at each of the match positions.
def coloring_alg(line, regexpcs, use_glob_regexps, stdout_is_redirected):
    matches = []


    def __glob_regexp_search(e):
        nonlocal matches
        for m in e[0].finditer(line):
            matches.append( ("start", m.start(), e[2]) )
            matches.append( ("end", m.end(), e[2]) )


    if use_glob_regexps:
        for e in regexpcs:
            __glob_regexp_search(e)
    else:
        for e in regexpcs:
            if e[1]:
                __glob_regexp_search(e)
            else:
                result = re.search(e[0], line)
                if result:
                    matches.append( ("start", result.start(), e[2]) )
                    matches.append( ("end", result.end(), e[2]) )

    if not matches:
        return line

    # Sort matches based on the position (match.start() / end()).
    matches = sorted(matches, key=lambda x: x[1])


    def __add_ansi_escape_seq(to_add):
        nonlocal line, line_incr
        len_to_add = len(to_add)
        line = line[:e[1] + line_incr] + to_add + line[line_incr + e[1]:]
        line_incr += len_to_add


    def __attr_end_if_fin(i, l):
        nonlocal attr_removed
        if attr_removed[i] and not l:
            nonlocal reconstruction_req
            __add_ansi_escape_seq(AnsiEscapeCode.END)
            reconstruction_req = True, True, True


    # Lists are maintained for all color and text attributes, in order to be able to deduce
    # when a given color or text attribute should be expressed.
    class __List:
        # The main list, containing all the starting elements, no matter if they are colors or text attributes.
        # If this is empty, all the other lists herein should be empty as well.
        starts = []

        # For foreground and background colors, the last color in the list will always be the one expressed.
        fgs = []
        bgs = []

        # For text attributes, the given text attribute will be expressed for as long as the given list is
        # not empty.
        bolds = []
        dims = []
        italics = []
        underlineds = []
        

    line_incr = 0
    for e in matches:
        if e[0] == "start":
            to_add = ""

            __List.starts.append(e[2])

            if e[2].color_str:
                if e[2].fgbg == 0:
                    __List.fgs.append(e[2])
                else:
                    __List.bgs.append(e[2])
                to_add += AnsiEscapeCode.START + e[2].color_str

            if e[2].bold:
                to_add += AnsiEscapeCode.ATTR_BOLD
                __List.bolds.append(e[2])
            if e[2].dim:
                to_add += AnsiEscapeCode.ATTR_DIM
                __List.dims.append(e[2])
            if e[2].italic:
                to_add += AnsiEscapeCode.ATTR_ITALIC
                __List.italics.append(e[2])
            if e[2].underlined:
                to_add += AnsiEscapeCode.ATTR_UNDERLINED
                __List.underlineds.append(e[2])

            __add_ansi_escape_seq(to_add)
        else:
            # Find the starting point that the end point corresponds to.
            for i, f in enumerate(__List.starts):
                if f is e[2]:
                    c = __List.starts.pop(i)

                    if c.fgbg == 0:
                        __List.fgs.remove(c)
                    elif c.fgbg == 1:
                        __List.bgs.remove(c)

                    # If there is a removal of one of the text attributes, this change needs to be stored.
                    # Later on, it will be checked if this one removal leads to a complete termination of the attribute expression.
                    attr_removed = [False, False, False, False]
                    if c.bold:
                        __List.bolds.remove(c)
                        attr_removed[0] = True
                    if c.dim:
                        __List.dims.remove(c)
                        attr_removed[1] = True
                    if c.italic:
                        __List.italics.remove(c)
                        attr_removed[2] = True
                    if c.underlined:
                        __List.underlineds.remove(c)
                        attr_removed[3] = True

                    if not __List.starts:
                        # Revert back to the default terminal state.
                        __add_ansi_escape_seq(AnsiEscapeCode.END)
                        break

                    # If any of the text attributes should be cleared, it is necessary to terminate all ANSI codes
                    # and then reactivate the ones that should be active.
                    reconstruction_req = False, False, False
                    __attr_end_if_fin(0, __List.bolds)
                    __attr_end_if_fin(1, __List.dims)
                    __attr_end_if_fin(2, __List.italics)
                    __attr_end_if_fin(3, __List.underlineds)

                    if c.fgbg == 0:
                        reconstruction_req = False, True, True
                        if __List.fgs:
                            __add_ansi_escape_seq(AnsiEscapeCode.START + __List.fgs[-1].color_str)
                        else:
                            # Disable foreground color.
                            __add_ansi_escape_seq(AnsiEscapeCode.RESET_FG)
                    elif c.fgbg == 1:
                        reconstruction_req = True, False, True
                        if __List.bgs:
                            __add_ansi_escape_seq(AnsiEscapeCode.START + __List.bgs[-1].color_str)
                        else:
                            # Disable background color.
                            __add_ansi_escape_seq(AnsiEscapeCode.RESET_BG)

                    # If needed, reconstruct the color state.
                    if reconstruction_req[0]:
                        if __List.fgs:
                            __add_ansi_escape_seq(AnsiEscapeCode.START + __List.fgs[-1].color_str)
                    if reconstruction_req[1]:
                        if __List.bgs:
                            __add_ansi_escape_seq(AnsiEscapeCode.START + __List.bgs[-1].color_str)
                        
                    # If needed, reconstruct the text attribute state.
                    if reconstruction_req[2]:
                        if __List.bolds:
                            __add_ansi_escape_seq(AnsiEscapeCode.ATTR_BOLD)
                        if __List.dims:
                            __add_ansi_escape_seq(AnsiEscapeCode.ATTR_DIM)
                        if __List.italics:
                            __add_ansi_escape_seq(AnsiEscapeCode.ATTR_ITALIC)
                        if __List.underlineds:
                            __add_ansi_escape_seq(AnsiEscapeCode.ATTR_UNDERLINED)

                    break

    # This is required to prevent the issue where background color in wrapped lines overflows
    # to fill all horizontal space.
    # This is similar to the issue for grep described here:
    # https://savannah.gnu.org/bugs/index.php?func=detailitem&item_id=11022
    # As described in the grep source code (grep.c), a solution to this problem is to explicitly
    # clear the line again after a \x1b[0m with \x1b[K.
    if not stdout_is_redirected:
        line += AnsiEscapeCode.CLEAR_LINE_FROM_CURRENT_CURSOR_POS_TO_END_OF_LINE

    return line
