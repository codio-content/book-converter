import re


class Term(object):
    def __init__(self, source_string):
        self.str = source_string
        self._term_re = re.compile(r""":term:`(?P<name>.*?)(<(?P<label_name>.*?)>)?`""", flags=re.DOTALL)

    @staticmethod
    def _term(matchobj):
        name = matchobj.group('name')
        name = name.strip()
        label_name = matchobj.group('label_name')
        return f'**{name}**'

    def convert(self):
        output = self.str
        output = self._term_re.sub(self._term, output)
        return output
