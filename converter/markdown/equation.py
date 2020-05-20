import re

equation_re = re.compile(r"""\\begin{equation}(?P<block_contents>.*?)\\end{equation}""", flags=re.DOTALL)


class Equation(object):
    def __init__(self, latex_str, caret_token):
        self._caret_token = caret_token
        self.str = latex_str

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = block_contents.strip()
        caret_token = self._caret_token
        return f'{caret_token}<center>{caret_token}$${caret_token}{block_contents}' \
               f'{caret_token}$${caret_token}</center>{caret_token}'

    def convert(self):
        return equation_re.sub(self.make_block, self.str)
