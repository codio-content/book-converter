import re

cite_re = re.compile(r"""~?\\cite{(?P<ref>.*?)}""", flags=re.DOTALL + re.VERBOSE)


class Cite(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def make_block(self, matchobj):
        ref = matchobj.group('ref')
        return '{}'.format(ref)

    def convert(self):
        return cite_re.sub(self.make_block, self.str)
