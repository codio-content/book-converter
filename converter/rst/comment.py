import re


class Comment(object):
    def __init__(self, source_string):
        self.str = source_string
        self._comment_re = re.compile(r"""^\.\. +\.\. +.*?\n(?=\S)|^\.\. .*?\n$""", flags=re.MULTILINE + re.DOTALL)

    @staticmethod
    def _comment(matchobj):
        return ''

    def convert(self):
        output = self._comment_re.sub(self._comment, self.str)
        return output
