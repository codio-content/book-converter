import re


class Ref(object):
    def __init__(self, source_string):
        self.str = source_string
        self._ref_re = re.compile(r""":(ref|chap):`(?P<name>.*?)(?P<label_name><.*?>)?`""", flags=re.DOTALL)

    @staticmethod
    def _ref(matchobj):
        name = matchobj.group('name')
        name = name.strip()
        return f'Chapter: **{name}**'

    def convert(self):
        output = self.str
        output = self._ref_re.sub(self._ref, output)
        return output
