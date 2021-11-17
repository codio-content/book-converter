import re


class Comment(object):
    def __init__(self, source_string):
        self.str = source_string
        self._comment1_re = re.compile(r"""^\.\.[ ]+\.\.[ ]+.*?\n(?=\S|(?!^$)$)""", flags=re.MULTILINE + re.DOTALL)
        self._comment2_re = re.compile(r"""^\.\.[ ]+(?:[^\n]+\n)+""", flags=re.MULTILINE)

    @staticmethod
    def _comment(matchobj):
        return ''

    def convert(self):
        output = self.str
        output = self._comment1_re.sub(self._comment, output)
        output = self._comment2_re.sub(self._comment, output)
        return output
