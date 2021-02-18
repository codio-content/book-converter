import re


class Numref(object):
    def __init__(self, source_string):
        self.str = source_string
        self._numref_re = re.compile(r""":?numref:?`<?(?P<name>.*)>?`""")

    @staticmethod
    def _numref(matchobj):
        name = matchobj.group('name')
        return name

    def convert(self):
        output = self.str
        output = self._numref_re.sub(self._numref, output)
        return output
