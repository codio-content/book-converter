import re


class RawHtml(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._raw_html_re = re.compile(
            r"""^( *\.\.\sraw:: html\n)(?P<content>.*?\n)(?:(?=\S)|(?!=^$)$)""", flags=re.MULTILINE + re.DOTALL)

    def _raw_html(self, matchobj):
        content = matchobj.group('content')
        split_content = [item.lstrip() for item in content.split('\n')]
        return '\n'.join(split_content)

    def convert(self):
        output = self._raw_html_re.sub(self._raw_html, self.str)
        return output
