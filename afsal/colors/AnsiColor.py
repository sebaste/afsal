from afsal.colors.AnsiEscapeCode import AnsiEscapeCode


class AnsiColor:
    def __str__(self):
        return "\n" + \
            "  color_str=" + self.color_str + "\n" + \
            "  fgbg=" + str(self.fgbg) + "\n" + \
            "  bold=" + ("Y" if self.bold else "N") + "\n" + \
            "  dim=" + ("Y" if self.dim else "N") + "\n" + \
            "  italic=" + ("Y" if self.italic else "N") + "\n" + \
            "  underlined=" + ("Y" if self.underlined else "N")

    # Convert an integer to its corresponding ANSI color string.
    def __convert_nm_to_ansi_color(self, term_nm_colors, nm):
        prefix = ""

        if nm < 0 or nm > term_nm_colors * 2 - 1:
            raise Exception("regexp color value " + str(nm) + " not in range(0, " + str(term_nm_colors * 2 - 1) + ")")

        if term_nm_colors == 8:
            if nm < 8:
                return (prefix + "3" + str(nm) + "m", 0)
            else:
                return (prefix + "4" + str(nm % 8) + "m", 1)
        elif term_nm_colors == 256:
            if nm < 256:
                return (prefix + "38;5;" + str(nm) + "m", 0)
            else:
                return (prefix + "48;5;" + str(nm % 256) + "m", 1)
        else:
            raise str(term_nm_colors) + " is an invalid terminal color number"

    # Create an ANSI color string.
    def __init__(self, term_nm_colors, color_str):
        # Py3*: need to join.
        int_value = None
        try:
            int_value = int("".join(filter(lambda x: x.isdigit(), color_str)))
        except ValueError:
            pass
        alpha_value = "".join(filter(lambda x: x.isalpha(), color_str))
        alpha_value = "".join(set(alpha_value))

        self.bold = self.dim = self.italic = self.underlined = False

        for i in range(0, len(alpha_value)):
            if alpha_value[i] == 'b':
                self.bold = True
            elif alpha_value[i] == 'd':
                self.dim = True
            elif alpha_value[i] == 'i':
                self.italic = True
            elif alpha_value[i] == 'u':
                self.underlined = True
            else:
                raise Exception("'" + alpha_value[i] + "' is an invalid text attribute - must be either 'b', 'd', 'i' or 'u'")

        self.color_str = ""
        self.fgbg = None
        if int_value:
            color_tuple = self.__convert_nm_to_ansi_color(term_nm_colors, int_value)
            self.color_str = color_tuple[0]
            self.fgbg = color_tuple[1]
