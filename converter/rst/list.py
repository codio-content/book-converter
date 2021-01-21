import re

FOUR_SPACES = '    '


class List(object):
    def __init__(self, source_string):
        self.str = source_string
        self._list_re = re.compile(r"""\n(?P<tabs>[\t]+)(?P<marker>[-|]?)?""")

    @staticmethod
    def _list(matchobj):
        tabs = matchobj.group('tabs')
        marker = matchobj.group('marker')
        content = '*'
        if marker:
            content = FOUR_SPACES + content
        if tabs:
            size = len(tabs)
            content = size * FOUR_SPACES + content
        return '\n' + content

    def convert(self):
        output = self.str
        output = self._list_re.sub(self._list, output)
        return output
