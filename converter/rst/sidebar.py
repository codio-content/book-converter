import re


class Sidebar(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._sidebar_re = re.compile(r"""\.\. sidebar:: (?P<name>.*?)\n^$\n(?P<content>.*?)\n^$(?=\S*)""",
                                      flags=re.MULTILINE + re.DOTALL)

    def _sidebar(self, matchobj):
        caret_token = self._caret_token
        name = matchobj.group('name')
        content = matchobj.group('content')
        content = content.strip()
        return f'{caret_token}|||xdiscipline{caret_token}{caret_token}**{name}**{caret_token}{caret_token}' \
               f'{content}{caret_token}{caret_token}|||{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._sidebar_re.sub(self._sidebar, output)
        return output
