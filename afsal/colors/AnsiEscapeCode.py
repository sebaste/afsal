class AnsiEscapeCode:
    __PREFIX = "\x1b["

    START = __PREFIX
    END = __PREFIX + "0m"

    RESET_FG = __PREFIX + "39m"
    RESET_BG = __PREFIX + "49m"

    ATTR_BOLD = __PREFIX + "1m"
    ATTR_DIM = __PREFIX + "2m"
    ATTR_ITALIC = __PREFIX + "3m"
    ATTR_UNDERLINED = __PREFIX + "4m"

    CLEAR_LINE_FROM_CURRENT_CURSOR_POS_TO_END_OF_LINE = __PREFIX + "K"
