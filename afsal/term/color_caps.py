import curses


def check_terminal_color_caps():
    curses.setupterm()
    return curses.tigetnum("colors")
