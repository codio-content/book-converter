import re
from collections import namedtuple

RawHtmlData = namedtuple('RawHtmlData', ['id', 'content'])


class RawHtml(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._links = list()
        self._raw_html_re = re.compile(
            r"""\.\.\s*(\|(?P<id>.*?)\|\s+)?raw:: html\n(?P<content>.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL)

    def _raw_html(self, matchobj):
        id = matchobj.group('id')
        content = matchobj.group('content').strip()
        if id:
            self._links.append(RawHtmlData(id, content))
            return ''
        else:
            split_content = [item.lstrip() for item in content.split('\n')]
            return '\n'.join(split_content)

    def convert(self):
        output = self._raw_html_re.sub(self._raw_html, self.str)
        return output, self._links
