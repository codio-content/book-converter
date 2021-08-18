import re


class Ignore(object):
    def __init__(self, source_string):
        self.str = source_string
        self._index_re = re.compile(r"""^ *\.\.\s+index:: ?(.*?)?\n.*?\n(?=\S)""", flags=re.MULTILINE + re.DOTALL)
        self._qnum_re = re.compile(r"""^ *\.\.\s+qnum:: ?(.*?)?\n.*?\n(?=\S)""", flags=re.MULTILINE + re.DOTALL)
        self._toctree_re = re.compile(r"""^ *\.\.\s+toctree:: ?(.*?)?\n.*?\n(?=\S)""", flags=re.MULTILINE + re.DOTALL)
        self._comment_re = re.compile(r"""^( *\.\. \.\..*?)\n(?=\S)""", flags=re.MULTILINE + re.DOTALL)

    def _ignore(self, matchobj):
        return ''

    def convert(self):
        output = self.str
        output = self._index_re.sub(self._ignore, output)
        output = self._toctree_re.sub(self._ignore, output)
        output = self._comment_re.sub(self._ignore, output)
        output = self._qnum_re.sub(self._ignore, output)
        return output
