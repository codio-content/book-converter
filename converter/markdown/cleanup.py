import re


class Cleanup(object):
    def __init__(self, latex_str):
        self.str = latex_str

        self._small_re = re.compile(r"""\\begin{small}
                                    (?P<block_contents>.*?)
                                    \\end{small}""",
                                    flags=re.DOTALL + re.VERBOSE)

    def convert(self):
        output = self.str

        output = self._small_re.sub(r"\1", output)
        output = re.sub(r"\\tbd{(.*?)}", r"\1", output)

        output = re.sub(r"\\'{(.*?)}", r"\1&#x301;", output)

        output = re.sub(r"(\S+)(~)(\S+)", r"\1 \3", output)
        output = re.sub(r"(~)(\S+)", r" \2", output)
        output = re.sub(r"(\S+)(~)", r"\1 ", output)

        return output
