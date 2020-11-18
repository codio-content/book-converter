import re


class Tip(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._tip_re = re.compile(
            r"""^\.{2} tip:{2} *\n(?P<content>(?:\n* +[^\n]+\n*)*)""", flags=re.MULTILINE)

    def _tip(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**Tip**{caret_token}{caret_token}{content}' \
               f'</div><br/>{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._tip_re.sub(self._tip, output)
        return output
