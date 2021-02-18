import re


class Only(object):
    def __init__(self, source_string):
        self.str = source_string
        self._only_re = re.compile(r"""\.\. only:: [a-zA-z\d]+\n\n*((?:\s+[^\n]+\n*)*)""")

    @staticmethod
    def _only(matchobj):
        return ''

    def convert(self):
        output = self.str
        output = self._only_re.sub(self._only, output)
        return output
