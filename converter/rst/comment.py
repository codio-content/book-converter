import re


class Comment(object):
    def __init__(self, source_string):
        self.str = source_string
        self._comment_re = re.compile(r"""^\.\.\s+[^\n]+(?:(?:(?!\n^$|\n\S)\s+[^\n]+\n*(?=\n\S))*)""",
                                      flags=re.MULTILINE)

    @staticmethod
    def _comment(matchobj):
        return ''

    def convert(self):
        output = self.str
        output = self._comment_re.sub(self._comment, output)
        return output
