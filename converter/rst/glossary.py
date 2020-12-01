import re


class Glossary(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._glossary_re = re.compile(r"""\.\. glossary::\n +:(?P<type>[a-zA-Z]+):\n*(?P<content>(?:\s+[^\n]+\n*)*)""")

    def _glossary(self, matchobj):
        content = matchobj.group('content')
        content = re.sub(r':to-term: .*?\n', '', content)
        items_list = []
        match_items = list(re.finditer(r'^ +(?P<term>[^\n]+)\n?\n(?P<text>(?:[^\n]+\n)*)', content,
                                       flags=re.MULTILINE))
        for item in match_items:
            term = item.group("term")
            text = self._clearing_line_breaks(item.group("text"))
            item = f'**{term}**{self._caret_token}{text}{self._caret_token}<hr>{self._caret_token}'
            items_list.append(item)
        content = '\n'.join(items_list)
        return content

    @staticmethod
    def _clearing_line_breaks(data):
        out = []
        for line in data.split('\n'):
            out.append(line)
        return ' '.join(out)

    def convert(self):
        output = self.str
        output = self._glossary_re.sub(self._glossary, output)
        return output
