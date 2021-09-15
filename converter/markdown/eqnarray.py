import re


class EqnArray(object):
    def __init__(self, latex_str):
        self.str = latex_str

        self._eqnarray_re = re.compile(r"""\\begin{(?P<block_name>eqnarray\*)}
                                    (?P<block_contents>.*?)
                                    \\end{(?P=block_name)}""", flags=re.DOTALL + re.VERBOSE)

    def _eqnarray_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"^&& {1,2}", "", block_contents, flags=re.MULTILINE)
        block_contents = re.sub(r"^& ", "", block_contents, flags=re.MULTILINE)
        block_contents = re.sub(r" &$", "", block_contents, flags=re.MULTILINE)
        block_contents = re.sub(r" & \\\\$", " \\\\\\\\", block_contents, flags=re.MULTILINE)
        return "$${}$$".format(block_contents, flags=re.MULTILINE)

    def convert(self):
        output = self.str

        output = self._eqnarray_re.sub(self._eqnarray_block, output)

        return output
